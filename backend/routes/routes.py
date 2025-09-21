from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from ..neo4j_service import get_neo4j_service
from ..enhanced_chat_service import enhanced_chat_service
from ..solr_service import solr_service
import logging
from datetime import datetime
import json
import asyncio
import os

# Initialize services
neo4j_service = get_neo4j_service()

logger = logging.getLogger(__name__)

async def ensure_neo4j_initialized():
    """Ensure Neo4j driver is initialized before use"""
    if not neo4j_service.driver:
        logger.info("Neo4j driver not initialized, initializing now...")
        await neo4j_service.initialize_driver()

router = APIRouter()

@router.get("/graph")
async def get_graph():
    """Get graph data from Neo4j"""
    try:
        logger.info("Received request to /api/graph")
        await ensure_neo4j_initialized()
        graph_data = await neo4j_service.get_graph_data()
        logger.info(f"getGraphData returned: nodes={len(graph_data.get('nodes', []))}, edges={len(graph_data.get('edges', []))}")
        return graph_data
    except Exception as error:
        logger.error(f"Error in /api/graph: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch graph data: {str(error)}")

@router.get("/graph/all")
async def get_graph_all():
    """Get expanded graph data"""
    try:
        await ensure_neo4j_initialized()
        query = """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT 100
        """
        result = await neo4j_service.execute_query(query, {})
        return result
    except Exception as error:
        logger.error(f"Error fetching expanded graph data: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch expanded graph data: {str(error)}")

@router.get("/graph/expand/{node_id}")
async def get_graph_expand(node_id: str):
    """Get nodes connected to a specific node"""
    try:
        await ensure_neo4j_initialized()
        query = """
        MATCH (n)-[r]-(connected)
        WHERE elementId(n) = $nodeId OR id(n) = toInteger($nodeId)
        RETURN n, r, connected
        LIMIT 50
        """
        result = await neo4j_service.execute_query(query, {"nodeId": node_id})
        return result
    except Exception as error:
        logger.error(f"Error fetching node expansion data: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch node expansion data: {str(error)}")

@router.get("/graph/search")
async def get_graph_search(
    q: Optional[str] = Query(None, alias="q"),
    type: Optional[str] = None,
    limit: int = 20
):
    """Get graph data based on search/filter criteria"""
    try:
        await ensure_neo4j_initialized()
        params = {"limit": limit}

        if q:
            params["searchTerm"] = f".*{q}.*"
            query = """
            MATCH (n)-[r]-(m)
            WHERE n.name =~ $searchTerm OR m.name =~ $searchTerm
               OR any(label IN labels(n) WHERE label =~ $searchTerm)
               OR any(label IN labels(m) WHERE label =~ $searchTerm)
            RETURN n, r, m
            LIMIT $limit
            """
        elif type:
            params["nodeType"] = type
            query = """
            MATCH (n)-[r]-(m)
            WHERE $nodeType IN labels(n) OR $nodeType IN labels(m)
            RETURN n, r, m
            LIMIT $limit
            """
        else:
            query = """
            MATCH (n)-[r]-(m)
            RETURN n, r, m
            LIMIT $limit
            """

        result = await neo4j_service.execute_query(query, params)
        return result
    except Exception as error:
        logger.error(f"Error searching graph data: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to search graph data: {str(error)}")

@router.post("/chat")
async def post_chat(request: Dict[str, Any]):
    """Process chat query with offline LLM"""
    try:
        user_query = request.get("query")
        if not user_query:
            raise HTTPException(status_code=400, detail="User query is required")

        logger.info(f"Processing enhanced chat query: {user_query}")

        # Process with enhanced service
        response = await enhanced_chat_service.process_chat_query(user_query)

        # Add help information for new users
        if "help" in user_query.lower() or len(enhanced_chat_service.get_conversation_history()) <= 2:
            response["textResponse"] += """

💡 Try these commands:
• 'show suppliers' - Display supplier nodes
• 'analyze patterns' - Get graph insights
• 'find connections' - Explore relationships
• 'refresh' - Reload graph data
• 'expand' - Show more data
"""

        return response

    except Exception as error:
        logger.error(f"Error in enhanced chat endpoint: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to process chat message",
                "details": str(error),
                "textResponse": f"Sorry, I encountered an error processing your query: {str(error)}",
                "graphData": {"nodes": [], "edges": []}
            }
        )

@router.post("/query")
async def post_query(request: Dict[str, Any]):
    """Execute a custom Cypher query"""
    try:
        query = request.get("query")
        params = request.get("params", {})

        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        await ensure_neo4j_initialized()
        result_data = await neo4j_service.execute_query(query, params)
        return result_data
    except Exception as error:
        logger.error(f"Error executing query: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to execute query",
                "details": str(error),
                "code": getattr(error, 'code', None)
            }
        )

@router.post("/solr/index")
async def post_index_solr():
    """Index current graph data into Solr for search"""
    try:
        logger.info("Starting Solr indexing process")
        await ensure_neo4j_initialized()

        # Get current graph data from Neo4j
        graph_data = await neo4j_service.get_graph_data()

        # Index the data into Solr
        result = await solr_service.index_graph_data(graph_data)

        return {
            "message": "Successfully indexed graph data into Solr",
            "result": result,
            "status": "completed"
        }

    except Exception as error:
        logger.error(f"Error indexing to Solr: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to index data to Solr",
                "details": str(error)
            }
        )

@router.get("/solr/search")
async def get_solr_search(
    q: str = Query(..., description="Search query"),
    type: Optional[str] = Query(None, description="Filter by type (node/relationship)"),
    group: Optional[str] = Query(None, description="Filter by node group"),
    limit: int = Query(20, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Search indexed data in Solr"""
    try:
        logger.info(f"Solr search query: {q}, filters: type={type}, group={group}")

        # Build filters
        filters = {}
        if type:
            filters["type"] = type
        if group:
            filters["group"] = group

        # Perform search
        result = await solr_service.search(q, filters, limit, offset)

        return {
            "query": q,
            "filters": filters,
            "total": result.get("total", 0),
            "results": result.get("docs", []),
            "limit": limit,
            "offset": offset
        }

    except Exception as error:
        logger.error(f"Error searching Solr: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to search Solr",
                "details": str(error)
            }
        )

@router.post("/solr/clear")
async def post_clear_solr():
    """Clear all documents from Solr index"""
    try:
        logger.info("Clearing Solr index")

        success = await solr_service.clear_index()

        if success:
            return {
                "message": "Successfully cleared Solr index",
                "status": "completed"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear Solr index")

    except Exception as error:
        logger.error(f"Error clearing Solr index: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to clear Solr index",
                "details": str(error)
            }
        )

@router.get("/solr/stats")
async def get_solr_stats():
    """Get Solr index statistics"""
    try:
        stats = await solr_service.get_index_stats()
        return {
            "solr_stats": stats,
            "collection": "neoboi_graph",
            "solr_url": os.getenv("SOLR_URL", "http://localhost:8983")
        }

    except Exception as error:
        logger.error(f"Error getting Solr stats: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get Solr statistics",
                "details": str(error)
            }
        )

@router.get("/vector/search")
async def get_vector_search(
    q: str = Query(..., description="Search query for vector similarity"),
    limit: int = Query(10, description="Maximum number of similar chunks to return"),
    threshold: float = Query(0.7, description="Similarity threshold (0.0-1.0)")
):
    """Search document chunks using vector similarity"""
    try:
        logger.info(f"Vector search query: {q}, limit: {limit}, threshold: {threshold}")
        await ensure_neo4j_initialized()

        # Perform vector similarity search
        search_results = await neo4j_service.vector_similarity_search(q, limit, threshold)

        return {
            "query": q,
            "results": search_results.get("results", []),
            "total_found": len(search_results.get("results", [])),
            "threshold": threshold,
            "limit": limit,
            "search_type": "vector_similarity"
        }

    except Exception as error:
        logger.error(f"Error in vector search: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to perform vector search",
                "details": str(error)
            }
        )

@router.get("/data/combined")
async def get_combined_data(include_unstructured: bool = True, include_search: bool = True) -> Dict[str, Any]:
    """Get combined structured and unstructured data for frontend display"""
    try:
        logger.info("Fetching combined data for frontend")

        # Get Neo4j graph data
        await ensure_neo4j_initialized()
        graph_data = await neo4j_service.get_graph_data()

        combined_data = {
            'structured_data': {
                'nodes': graph_data.get('nodes', []),
                'edges': graph_data.get('edges', []),
                'count': len(graph_data.get('nodes', []))
            },
            'unstructured_data': {
                'documents': [],
                'chunks': [],
                'embeddings': []
            },
            'search_results': [],
            'timestamp': datetime.now().isoformat()
        }

        if include_unstructured:
            try:
                # Get unstructured documents
                from routes.unstructured import ingestion_service
                documents = ingestion_service.list_processed_documents()

                all_chunks = []
                all_embeddings = []

                for doc in documents:
                    if doc.get('success'):
                        # Add document info
                        doc_info = {
                            'filename': doc.get('filename', ''),
                            'processed_at': doc.get('processed_at', ''),
                            'content_length': len(doc.get('content', '')),
                            'chunks_count': len(doc.get('chunks', [])),
                            'has_embeddings': len(doc.get('chunk_embeddings', [])) > 0,
                            'processing_type': doc.get('processing_type', 'unknown')
                        }
                        combined_data['unstructured_data']['documents'].append(doc_info)

                        # Collect chunks and embeddings
                        if 'chunks' in doc:
                            for chunk in doc['chunks']:
                                chunk['document_filename'] = doc.get('filename', '')
                                all_chunks.append(chunk)

                        if 'chunk_embeddings' in doc:
                            for embedding in doc['chunk_embeddings']:
                                embedding['document_filename'] = doc.get('filename', '')
                                all_embeddings.append(embedding)

                combined_data['unstructured_data']['chunks'] = all_chunks
                combined_data['unstructured_data']['embeddings'] = all_embeddings

                logger.info(f"Added {len(documents)} documents, {len(all_chunks)} chunks, {len(all_embeddings)} embeddings")

            except Exception as e:
                logger.error(f"Failed to fetch unstructured data: {str(e)}")
                combined_data['unstructured_data']['error'] = str(e)

        if include_search:
            try:
                # Get recent search results from Solr
                search_results = await solr_service.search("*", limit=20)  # Get recent results
                combined_data['search_results'] = search_results.get('docs', [])

                logger.info(f"Added {len(combined_data['search_results'])} search results")

            except Exception as e:
                logger.error(f"Failed to fetch search results: {str(e)}")
                combined_data['search_results'] = []
                combined_data['search_error'] = str(e)

        # Add summary statistics
        combined_data['summary'] = {
            'total_structured_nodes': len(combined_data['structured_data']['nodes']),
            'total_unstructured_documents': len(combined_data['unstructured_data']['documents']),
            'total_chunks': len(combined_data['unstructured_data']['chunks']),
            'total_embeddings': len(combined_data['unstructured_data']['embeddings']),
            'total_search_results': len(combined_data['search_results'])
        }

        return {
            'success': True,
            'data': combined_data,
            'message': 'Combined data retrieved successfully'
        }

    except Exception as error:
        logger.error(f"Error fetching combined data: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch combined data: {str(error)}")

@router.get("/data/table")
async def get_table_data(
    data_type: str = "all",
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Get data formatted for table display"""
    try:
        # Get combined data
        combined_result = await get_combined_data()

        if not combined_result.get('success'):
            raise HTTPException(status_code=500, detail="Failed to fetch combined data")

        combined_data = combined_result['data']

        table_rows = []

        # Add structured nodes
        if data_type in ["all", "structured"]:
            for node in combined_data['structured_data']['nodes'][offset:offset+limit]:
                table_rows.append({
                    'id': node.get('id', ''),
                    'type': 'structured',
                    'subtype': node.get('group', 'node'),
                    'label': node.get('label', ''),
                    'content': json.dumps(node.get('properties', {}), indent=2),
                    'source': 'Neo4j Graph',
                    'processed_at': datetime.now().isoformat(),
                    'metadata': {
                        'connections': len([edge for edge in combined_data['structured_data']['edges']
                                          if edge.get('from') == node.get('id') or edge.get('to') == node.get('id')])
                    }
                })

        # Add unstructured documents
        if data_type in ["all", "unstructured"]:
            for doc in combined_data['unstructured_data']['documents'][offset:offset+limit]:
                table_rows.append({
                    'id': f"doc_{doc['filename']}",
                    'type': 'unstructured',
                    'subtype': 'document',
                    'label': doc['filename'],
                    'content': f"Document with {doc['content_length']} characters, {doc['chunks_count']} chunks",
                    'source': f"Document Processing ({doc['processing_type']})",
                    'processed_at': doc['processed_at'],
                    'metadata': {
                        'chunks_count': doc['chunks_count'],
                        'has_embeddings': doc['has_embeddings']
                    }
                })

        # Add search results
        if data_type in ["all", "search"]:
            for result in combined_data['search_results'][offset:offset+limit]:
                table_rows.append({
                    'id': f"search_{result.get('id', '')}",
                    'type': 'search',
                    'subtype': 'search_result',
                    'label': result.get('name', result.get('label', 'Search Result')),
                    'content': result.get('content', result.get('description', ''))[:200] + "...",
                    'source': 'Solr Search Index',
                    'processed_at': result.get('indexed_at', datetime.now().isoformat()),
                    'metadata': {
                        'score': result.get('score', 0),
                        'type': result.get('type', 'unknown')
                    }
                })

        return {
            'success': True,
            'data': table_rows,
            'total_count': len(table_rows),
            'data_types': ['structured', 'unstructured', 'search'],
            'current_data_type': data_type,
            'limit': limit,
            'offset': offset
        }

    except Exception as error:
        logger.error(f"Error fetching table data: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch table data: {str(error)}")

@router.get("/neo4j/status")
async def get_neo4j_status():
    """Check Neo4j connection status"""
    try:
        # Get deployment info
        deployment_info = neo4j_service.get_deployment_info()

        # Try to verify connectivity
        await ensure_neo4j_initialized()
        driver = neo4j_service.get_driver()
        await asyncio.get_event_loop().run_in_executor(None, driver.verify_connectivity)

        # Try a simple query to verify database access
        test_query = "MATCH (n) RETURN count(n) as node_count LIMIT 1"
        result = await neo4j_service.execute_query(test_query, {})

        return {
            "status": "connected",
            "deployment_type": deployment_info.get("deployment_type"),
            "uri": deployment_info.get("uri"),
            "database": deployment_info.get("database"),
            "vector_supported": deployment_info.get("vector_supported"),
            "embedding_model_loaded": deployment_info.get("embedding_model_loaded"),
            "node_count": result.get("rawRecords", [{}])[0].get("node_count", 0) if result.get("rawRecords") else 0,
            "message": f"Neo4j {deployment_info.get('deployment_type')} deployment is running and accessible"
        }

    except Exception as error:
        logger.error(f"Neo4j status check failed: {error}")
        deployment_info = neo4j_service.get_deployment_info()
        return {
            "status": "disconnected",
            "deployment_type": deployment_info.get("deployment_type"),
            "uri": deployment_info.get("uri"),
            "database": deployment_info.get("database"),
            "error": str(error),
            "message": f"Neo4j {deployment_info.get('deployment_type')} deployment is not accessible"
        }

# Import and include unstructured data routes
try:
    from .unstructured import router as unstructured_router
    router.include_router(unstructured_router)
    logger.info("Unstructured data routes loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load unstructured routes: {e}")
except Exception as e:
    logger.error(f"Error loading unstructured routes: {e}")

@router.post("/search/integrated")
async def post_integrated_search(request: Dict[str, Any]):
    """
    Unified search endpoint that orchestrates across Solr, Neo4j, and LLM systems
    """
    try:
        user_query = request.get("query")
        if not user_query:
            raise HTTPException(status_code=400, detail="Search query is required")

        conversation_context = request.get("conversation_context", [])
        search_options = request.get("options", {})

        logger.info(f"Processing integrated search query: {user_query}")

        # Initialize services
        await ensure_neo4j_initialized()

        # Import LLM service for orchestration
        from ..unstructured_pipeline.llm_service import OfflineLLMService
        llm_service = OfflineLLMService()

        # Step 1: Analyze query intent
        intent_analysis = llm_service.analyze_query_intent(user_query)
        if not intent_analysis.get('success'):
            logger.warning(f"Query intent analysis failed: {intent_analysis.get('error')}")
            # Fall back to hybrid search
            intent_analysis = {
                'query_type': 'general',
                'recommended_strategy': 'hybrid_search',
                'key_entities': [],
                'search_depth': 'shallow'
            }

        # Step 2: Generate system-specific queries
        system_queries = llm_service.generate_system_queries(user_query, intent_analysis.get('analysis', {}))

        # Step 3: Execute parallel searches across systems
        search_tasks = []
        search_results = {
            'solr_results': [],
            'neo4j_results': [],
            'graph_results': [],
            'vector_results': []
        }

        # Solr search
        if system_queries.get('system_queries', {}).get('solr_query'):
            try:
                solr_query = system_queries['system_queries']['solr_query']
                solr_result = await solr_service.search(solr_query, limit=20)
                search_results['solr_results'] = solr_result.get('docs', [])
            except Exception as e:
                logger.error(f"Solr search failed: {e}")
                search_results['solr_results'] = []

        # Neo4j vector search
        if system_queries.get('system_queries', {}).get('vector_query'):
            try:
                vector_description = system_queries['system_queries']['vector_query']
                vector_result = await neo4j_service.vector_similarity_search(vector_description, limit=10)
                search_results['vector_results'] = vector_result.get('results', [])
            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                search_results['vector_results'] = []

        # Neo4j graph search
        if system_queries.get('system_queries', {}).get('graph_query'):
            try:
                graph_query = system_queries['system_queries']['graph_query']
                graph_result = await neo4j_service.execute_query(graph_query, {})
                search_results['graph_results'] = graph_result.get('rawRecords', [])
            except Exception as e:
                logger.error(f"Graph search failed: {e}")
                search_results['graph_results'] = []

        # Step 4: Fuse multi-system results
        fused_results = llm_service.fuse_multi_system_results(user_query, search_results)

        # Step 5: Generate integrated response
        integrated_response = llm_service.generate_integrated_response(
            user_query,
            fused_results,
            conversation_context
        )

        # Prepare comprehensive response
        response_data = {
            'query': user_query,
            'intent_analysis': intent_analysis.get('analysis', {}),
            'system_queries': system_queries.get('system_queries', {}),
            'search_results': {
                'solr': {
                    'count': len(search_results['solr_results']),
                    'results': search_results['solr_results'][:5]  # Limit for response size
                },
                'vector': {
                    'count': len(search_results['vector_results']),
                    'results': search_results['vector_results'][:5]
                },
                'graph': {
                    'count': len(search_results['graph_results']),
                    'results': search_results['graph_results'][:5]
                }
            },
            'fused_results': fused_results.get('fused_analysis', {}),
            'response': integrated_response.get('integrated_response', {}),
            'processing_time': {
                'intent_analysis': intent_analysis.get('processing_time', 0),
                'fused_results': fused_results.get('processing_time', 0),
                'integrated_response': integrated_response.get('processing_time', 0)
            },
            'model_used': integrated_response.get('model', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }

        return response_data

    except Exception as error:
        logger.error(f"Error in integrated search endpoint: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to process integrated search",
                "details": str(error),
                "query": request.get("query", ""),
                "response": {
                    "response_text": f"I apologize, but I encountered an error processing your search: {str(error)}",
                    "confidence": 0,
                    "suggestions": ["Try rephrasing your query", "Check if all services are running"]
                }
            }
        )