from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from neo4j_service import neo4j_service
from llm_service import generate_mock_cypher
from solr_service import solr_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/graph")
async def get_graph():
    """Get graph data from Neo4j"""
    try:
        logger.info("Received request to /api/graph")
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

        logger.info(f"Processing chat query with offline LLM: {user_query}")

        # Generate Cypher query using mock implementation
        cypher_query = generate_mock_cypher(user_query)
        explanation = f"Generated Cypher query for: '{user_query}' (Mock Mode)"
        confidence = 0.7

        # Prepare response
        result = {
            "textResponse": f"Processed query: \"{user_query}\"",
            "graphData": {
                "cypher": cypher_query,
                "explanation": explanation,
                "confidence": confidence,
                "source": "python-llm"
            },
            "generatedQuery": cypher_query,
            "source": "python-llm",
            "confidence": confidence
        }

        # Add generated query info
        if cypher_query:
            result["textResponse"] += f"\n\n<i>Generated Cypher query: {cypher_query}</i>"

        # Add available commands if it's a help request
        if "help" in user_query.lower() or "what can" in user_query.lower():
            result["textResponse"] += """
<b>Available commands:</b>
• "show suppliers" - Display all suppliers
• "show manufacturers" - Display all manufacturers
• "count nodes" - Count different node types
• "count relationships" - Count relationship types
• "find [term]" - Search for specific terms
• "refresh" - Reload the graph data
• "expand" - Show more graph data
• Click nodes/edges in the graph for details
• Double-click nodes to expand their connections
"""

        return result

    except Exception as error:
        logger.error(f"Error in /api/chat endpoint: {error}")
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
            "solr_url": "http://localhost:8983"
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