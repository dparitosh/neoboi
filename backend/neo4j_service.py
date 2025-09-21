from neo4j import GraphDatabase, basic_auth
import os
import logging
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
import asyncio
import requests
import json
import numpy as np

# Import services
# from solr_service import solr_service  # Moved to avoid circular import
# from unstructured_pipeline.llm_service import OfflineLLMService  # Not used in this module

# Vector indexing imports (Neo4j GraphRAG only)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("SentenceTransformers not available. Vector indexing features will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jService:
    def __init__(self):
        self.driver = None
        # Read from environment variables (no fallbacks - must be configured)
        self.database = os.getenv("NEO4J_DATABASE")
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")

        # Validate required configuration
        if not self.uri:
            raise ValueError("NEO4J_URI environment variable is required")
        if not self.user:
            raise ValueError("NEO4J_USER environment variable is required")
        if not self.password:
            raise ValueError("NEO4J_PASSWORD environment variable is required")
        if not self.database:
            self.database = "neo4j"  # Default database name is reasonable

        # Deployment type detection
        self.deployment_type = self._detect_deployment_type()
        self.is_aura = self.deployment_type == "aura"
        self.is_on_premise = self.deployment_type == "on_premise"

        # Vector indexing configuration
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.vector_dimensions = 384  # Default for sentence-transformers models
        self.vector_index_name = "document_chunks_vector"
        self.vector_supported = self._check_vector_support()

        # Initialize embedding model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                logger.info(f"SentenceTransformer model '{self.embedding_model_name}' loaded for embeddings")
            except Exception as e:
                logger.warning(f"Could not load embedding model '{self.embedding_model_name}': {e}")
                self.embedding_model = None
        else:
            logger.warning(f"SentenceTransformers not available. Cannot load model '{self.embedding_model_name}'")

        logger.info(f"Neo4jService initialized for {self.deployment_type} deployment (URI: {self.uri})")

    def get_deployment_info(self) -> Dict[str, Any]:
        """
        Get information about the current Neo4j deployment

        Returns:
            Dictionary with deployment information
        """
        return {
            "deployment_type": self.deployment_type,
            "is_aura": self.is_aura,
            "is_on_premise": self.is_on_premise,
            "uri": self.uri,
            "database": self.database,
            "vector_supported": self.vector_supported,
            "embedding_model_loaded": self.embedding_model is not None,
            "embedding_model_name": self.embedding_model_name,
            "vector_dimensions": self.vector_dimensions
        }

    def _detect_deployment_type(self) -> str:
        """
        Detect Neo4j deployment type based on URI

        Returns:
            "aura" for Neo4j Aura cloud
            "on_premise" for local/on-premise installations
        """
        if self.uri.startswith("neo4j+s://") or "databases.neo4j.io" in self.uri:
            return "aura"
        elif self.uri.startswith(("bolt://", "neo4j://")):
            return "on_premise"
        else:
            # Default to on-premise for unknown formats
            logger.warning(f"Unknown URI format: {self.uri}, assuming on-premise")
            return "on_premise"

    def _check_vector_support(self) -> bool:
        """
        Check if vector indexes are supported based on deployment type and version

        Returns:
            True if vector indexes are supported
        """
        # Neo4j Aura generally supports vectors (5.17+)
        if self.is_aura:
            return True

        # For on-premise, we'd need version checking
        # For now, assume supported if Neo4j 5.17+
        # This could be enhanced with version detection
        return True

    async def initialize_driver(self):
        """Initialize Neo4j driver with connection verification"""
        if not self.password:
            error_msg = 'NEO4J_PASSWORD environment variable is not set. Cannot connect to Neo4j.'
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            logger.info(f"Attempting to connect to Neo4j at {self.uri} as user {self.user}...")
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=basic_auth(self.user, self.password)
            )

            # Verify connectivity
            await asyncio.get_event_loop().run_in_executor(None, self.driver.verify_connectivity)
            logger.info('Successfully connected to Neo4j and verified connectivity.')

        except Exception as error:
            logger.error(f'Failed to initialize or verify Neo4j driver: {error}')
            raise error

    def get_driver(self):
        """Get the Neo4j driver instance"""
        if not self.driver:
            raise RuntimeError('Neo4j driver not initialized. Call initialize_driver() first.')
        return self.driver

    async def close_driver(self):
        """Close the Neo4j driver"""
        if self.driver:
            await asyncio.get_event_loop().run_in_executor(None, self.driver.close)
            self.driver = None
            logger.info('Neo4j driver closed.')

    def _add_node_from_info(self, node_info: Dict[str, Any], nodes_map: Dict[str, Dict[str, Any]]):
        """Process a node information object and add it to the nodes map"""
        if node_info and node_info.get('id') and node_info['id'] not in nodes_map:
            node_id = node_info['id']
            labels = node_info.get('labels', [])
            properties = node_info.get('properties', {})

            # Use a more descriptive default label if name and primary label are missing
            default_label = labels[0] if labels else (properties.get('name') or f"Node ({node_id[:6]}...)")

            # Construct detailed tooltip content
            tooltip_title = f"ID: {node_id}\n"
            if labels:
                tooltip_title += f"Labels: {', '.join(labels)}\n"
            tooltip_title += "Properties:\n"
            for key, value in properties.items():
                tooltip_title += f"  {key}: {value}\n"

            nodes_map[node_id] = {
                'id': node_id,
                'label': properties.get('name') or default_label,
                'group': labels[0] if labels else 'Unknown',
                'properties': properties,
                'title': tooltip_title.strip()
            }

    def _process_relationship(self, relationship: Dict[str, Any], nodes_map: Dict[str, Dict[str, Any]], edges: List[Dict[str, Any]]):
        """Process a relationship object"""
        rel_id = relationship.get('elementId') or relationship.get('id') or relationship.get('element_id')
        if relationship and rel_id and not any(e['id'] == rel_id for e in edges):
            start_node_id = relationship.get('startNodeElementId') or relationship.get('start')
            end_node_id = relationship.get('endNodeElementId') or relationship.get('end')
            rel_type = relationship.get('type')

            # Get source and target node details from nodes_map
            source_node = nodes_map.get(start_node_id)
            target_node = nodes_map.get(end_node_id)

            tooltip_title = f"ID: {rel_id}\nType: {rel_type}\n"
            tooltip_title += f"\nSource: {source_node['label'] if source_node else start_node_id}\n"
            tooltip_title += f"Target: {target_node['label'] if target_node else end_node_id}"

            edges.append({
                'id': rel_id,
                'from': start_node_id,
                'to': end_node_id,
                'label': rel_type,
                'properties': relationship.get('properties', {}),
                'title': tooltip_title.strip()
            })

            # Add placeholder nodes if they don't exist
            if start_node_id and start_node_id not in nodes_map:
                self._add_node_from_info({
                    'id': start_node_id,
                    'labels': [],
                    'properties': {'_id_placeholder': start_node_id, 'name': f"Node {start_node_id[:6]}..."}
                }, nodes_map)

            if end_node_id and end_node_id not in nodes_map:
                self._add_node_from_info({
                    'id': end_node_id,
                    'labels': [],
                    'properties': {'_id_placeholder': end_node_id, 'name': f"Node {end_node_id[:6]}..."}
                }, nodes_map)

    async def get_graph_data(self) -> Dict[str, Any]:
        """Get graph data from Neo4j"""
        driver = self.get_driver()
        nodes_map = {}
        edges = []

        # First get all nodes
        nodes_query = "MATCH (n) RETURN n LIMIT 100"

        # Then get all relationships (directed to avoid duplicates)
        relationships_query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 200"

        with driver.session(database=self.database) as session:
            # Get all nodes first
            nodes_result = await asyncio.get_event_loop().run_in_executor(
                None, session.run, nodes_query
            )

            nodes_count = 0
            for record in nodes_result:
                n = record.get('n')
                if n:
                    self._add_node_from_info({
                        'id': n.element_id,
                        'labels': list(n.labels),
                        'properties': dict(n.items())
                    }, nodes_map)
                    nodes_count += 1

            print(f"[DEBUG] Found {nodes_count} nodes")

            # Then get all relationships
            relationships_result = await asyncio.get_event_loop().run_in_executor(
                None, session.run, relationships_query
            )

            relationships_count = 0
            for record in relationships_result:
                n = record.get('n')
                r = record.get('r')
                m = record.get('m')

                # Add any nodes we might have missed
                if n:
                    self._add_node_from_info({
                        'id': n.element_id,
                        'labels': list(n.labels),
                        'properties': dict(n.items())
                    }, nodes_map)

                if m:
                    self._add_node_from_info({
                        'id': m.element_id,
                        'labels': list(m.labels),
                        'properties': dict(m.items())
                    }, nodes_map)

                if r is not None:
                    self._process_relationship({
                        'elementId': r.element_id,
                        'startNodeElementId': r.start_node.element_id,
                        'endNodeElementId': r.end_node.element_id,
                        'type': r.type,
                        'properties': dict(r.items())
                    }, nodes_map, edges)
                    relationships_count += 1

            print(f"[DEBUG] Found {relationships_count} relationships, processed {len(edges)} edges")

            return {
                'nodes': list(nodes_map.values()),
                'edges': edges,
                'rawRecords': []
            }

    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a Cypher query"""
        if params is None:
            params = {}

        driver = self.get_driver()
        nodes_map = {}
        edges = []

        logger.info(f"Executing query: {query} with params: {params}")

        with driver.session(database=self.database) as session:
            result = await asyncio.get_event_loop().run_in_executor(
                None, session.run, query, params
            )

            # Process results based on query type
            if "AS n_info" in query:
                # Structured query with info objects
                for record in result:
                    n_info = record.get('n_info')
                    r_info = record.get('r_info')
                    m_info = record.get('m_info')

                    if n_info:
                        self._add_node_from_info(n_info, nodes_map)
                    if m_info:
                        self._add_node_from_info(m_info, nodes_map)
                    if r_info:
                        self._process_relationship(r_info, nodes_map, edges)
            else:
                # Standard Neo4j objects
                for record in result:
                    n = record.get('n')
                    r = record.get('r')
                    m = record.get('m')

                    if n:
                        self._add_node_from_info({
                            'id': n.element_id,
                            'labels': list(n.labels),
                            'properties': dict(n.items())
                        }, nodes_map)

                    if m:
                        self._add_node_from_info({
                            'id': m.element_id,
                            'labels': list(m.labels),
                            'properties': dict(m.items())
                        }, nodes_map)

                    if r:
                        self._process_relationship({
                            'elementId': r.element_id,
                            'startNodeElementId': r.start_node.element_id,
                            'endNodeElementId': r.end_node.element_id,
                            'type': r.type,
                            'properties': dict(r.items())
                        }, nodes_map, edges)

            raw_records = [record.data() for record in result]
            return {
                'nodes': list(nodes_map.values()),
                'edges': edges,
                'rawRecords': raw_records,
                'summary': str(result.consume())
            }

    async def integrated_search(self, query: str, search_type: str = "all",
                               limit: int = 20) -> Dict[str, Any]:
        """
        Integrated search that combines Neo4j graph data with Solr search

        Args:
            query: Search query string
            search_type: Type of search ("structured", "unstructured", "all")
            limit: Maximum results to return

        Returns:
            Combined search results from Neo4j and Solr
        """
        try:
            results = {
                "query": query,
                "search_type": search_type,
                "neo4j_results": [],
                "solr_results": [],
                "ollama_context": "",
                "combined_insights": []
            }

            # 1. Search Neo4j graph data
            if search_type in ["structured", "all"]:
                neo4j_data = await self.get_graph_data()
                # Filter nodes and edges based on query
                filtered_nodes = []
                for node in neo4j_data.get("nodes", []):
                    if self._matches_query(node, query):
                        filtered_nodes.append(node)

                results["neo4j_results"] = filtered_nodes[:limit]

            # 2. Search Solr (both structured and unstructured)
            if search_type in ["unstructured", "all"]:
                from solr_service import solr_service  # Import locally to avoid circular import
                solr_result = await solr_service.search(query, limit=limit)
                results["solr_results"] = solr_result.get("docs", [])

            # 3. Get Ollama context and insights
            context_prompt = f"""
            Based on the search query "{query}", analyze these results:

            Neo4j Graph Data: {json.dumps(results["neo4j_results"][:5], indent=2)}
            Solr Search Results: {json.dumps(results["solr_results"][:5], indent=2)}

            Provide insights about:
            1. Key entities and relationships found
            2. Connections between structured and unstructured data
            3. Potential patterns or insights
            """

            ollama_response = await self._query_ollama(context_prompt)
            results["ollama_context"] = ollama_response

            # 4. Generate combined insights
            results["combined_insights"] = self._generate_combined_insights(
                results["neo4j_results"],
                results["solr_results"],
                ollama_response
            )

            logger.info(f"Integrated search completed: {len(results['neo4j_results'])} Neo4j, {len(results['solr_results'])} Solr results")
            return results

        except Exception as e:
            logger.error(f"Integrated search failed: {str(e)}")
            return {
                "query": query,
                "error": str(e),
                "neo4j_results": [],
                "solr_results": [],
                "ollama_context": "",
                "combined_insights": []
            }

    async def process_document_with_context(self, document_content: str,
                                          document_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document and enrich it with Neo4j context

        Args:
            document_content: Raw document text
            document_metadata: Document metadata

        Returns:
            Processed document with Neo4j context
        """
        try:
            # 1. Extract entities and keywords from document
            doc_entities = self._extract_document_entities(document_content)
            doc_keywords = self._extract_document_keywords(document_content)

            # 2. Search for related entities in Neo4j
            related_entities = []
            for entity in doc_entities:
                # Search Neo4j for matching entities
                search_results = await self.integrated_search(entity["text"], "structured", 5)
                related_entities.extend(search_results.get("neo4j_results", []))

            # 3. Get Ollama analysis of document in context
            context_prompt = f"""
            Analyze this document in the context of the knowledge graph:

            Document: {document_content[:1000]}...

            Extracted Entities: {json.dumps(doc_entities, indent=2)}
            Related Graph Entities: {json.dumps(related_entities[:5], indent=2)}

            Provide:
            1. Document summary
            2. Key insights connecting to existing knowledge
            3. Suggested relationships to add to the graph
            """

            ollama_analysis = await self._query_ollama(context_prompt)

            # 4. Create Neo4j nodes and relationships for the document
            graph_structure = self._create_document_graph_structure(
                document_content, document_metadata, doc_entities, related_entities
            )

            return {
                "document_analysis": {
                    "entities": doc_entities,
                    "keywords": doc_keywords,
                    "summary": ollama_analysis.get("summary", ""),
                    "insights": ollama_analysis.get("insights", [])
                },
                "graph_context": {
                    "related_entities": related_entities,
                    "suggested_relationships": ollama_analysis.get("relationships", [])
                },
                "graph_structure": graph_structure,
                "ollama_analysis": ollama_analysis
            }

        except Exception as e:
            logger.error(f"Document processing with context failed: {str(e)}")
            return {"error": str(e)}

    def _matches_query(self, node: Dict[str, Any], query: str) -> bool:
        """Check if a node matches the search query"""
        query_lower = query.lower()

        # Check node labels
        if any(label.lower().find(query_lower) >= 0 for label in node.get("labels", [])):
            return True

        # Check node properties
        properties = node.get("properties", {})
        for key, value in properties.items():
            if isinstance(value, str) and query_lower in value.lower():
                return True

        return False

    async def _query_ollama(self, prompt: str) -> Dict[str, Any]:
        """Query Ollama for analysis and insights"""
        try:
            # This would integrate with Ollama API
            # For now, return mock response
            return {
                "summary": "Document analysis completed",
                "insights": ["Key entities identified", "Relationships suggested"],
                "relationships": ["Document relates to existing entities"],
                "confidence": 0.85
            }
        except Exception as e:
            logger.error(f"Ollama query failed: {str(e)}")
            return {"error": str(e)}

    def _extract_document_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities from document content using simple patterns"""
        entities = []

        # Simple entity extraction patterns
        import re

        # Email pattern
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        for email in emails:
            entities.append({"text": email, "type": "EMAIL", "confidence": 0.9})

        # Phone pattern
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
        for phone in phones:
            entities.append({"text": phone, "type": "PHONE", "confidence": 0.8})

        # Date pattern
        dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b', content)
        for date in dates:
            entities.append({"text": date, "type": "DATE", "confidence": 0.7})

        return entities

    def _extract_document_keywords(self, content: str) -> List[str]:
        """Extract keywords from document content"""
        import re

        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', content.lower())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

        keywords = [word for word in words if len(word) > 3 and word not in stop_words]

        # Get most frequent keywords
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(10)]

    def _create_document_graph_structure(self, content: str, metadata: Dict[str, Any],
                                       entities: List[Dict[str, Any]],
                                       related_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create Neo4j graph structure for document"""
        # Create document node
        document_node = {
            "labels": ["Document"],
            "properties": {
                "filename": metadata.get("filename", "unknown"),
                "content_preview": content[:500],
                "word_count": len(content.split()),
                "entity_count": len(entities),
                "processed_at": "2025-09-18T00:00:00Z"
            }
        }

        # Create entity nodes
        entity_nodes = []
        for entity in entities:
            entity_nodes.append({
                "labels": ["Entity", entity["type"]],
                "properties": {
                    "text": entity["text"],
                    "type": entity["type"],
                    "confidence": entity["confidence"]
                }
            })

        return {
            "document_node": document_node,
            "entity_nodes": entity_nodes,
            "relationships": []  # Would be populated based on analysis
        }

    def _generate_combined_insights(self, neo4j_results: List[Dict[str, Any]],
                                   solr_results: List[Dict[str, Any]],
                                   ollama_context: Dict[str, Any]) -> List[str]:
        """Generate combined insights from all sources"""
        insights = []

        # Basic insights
        if neo4j_results:
            insights.append(f"Found {len(neo4j_results)} related entities in knowledge graph")

        if solr_results:
            insights.append(f"Found {len(solr_results)} matching documents in search index")

        if ollama_context and "insights" in ollama_context:
            insights.extend(ollama_context["insights"])

        return insights

    # ===== VECTOR INDEXING METHODS =====

    async def create_vector_index(self, index_name: str = None, dimensions: int = None) -> Dict[str, Any]:
        """
        Create a vector index in Neo4j for similarity search

        Args:
            index_name: Name of the vector index
            dimensions: Number of dimensions for the vectors

        Returns:
            Index creation result
        """
        if not self.vector_supported:
            return {
                "success": False,
                "error": f"Vector indexes not supported for {self.deployment_type} deployment",
                "deployment_type": self.deployment_type
            }

        if index_name is None:
            index_name = self.vector_index_name
        if dimensions is None:
            dimensions = self.vector_dimensions

        # Different Cypher syntax for different Neo4j versions
        if self.is_aura:
            # Neo4j Aura (5.17+) syntax
            create_index_query = f"""
            CREATE VECTOR INDEX {index_name} IF NOT EXISTS
            FOR (n:DocumentChunk)
            ON (n.embedding)
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {dimensions},
                    `vector.similarity_function`: 'cosine'
                }}
            }}
            """
        else:
            # On-premise Neo4j (try both syntaxes)
            create_index_query = f"""
            CREATE VECTOR INDEX {index_name} IF NOT EXISTS
            FOR (n:DocumentChunk)
            ON n.embedding
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {dimensions},
                    `vector.similarity_function`: 'cosine'
                }}
            }}
            """

        try:
            driver = self.get_driver()
            with driver.session(database=self.database) as session:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, session.run, create_index_query
                )
                await asyncio.get_event_loop().run_in_executor(None, result.consume)

            logger.info(f"Vector index '{index_name}' created successfully on {self.deployment_type}")
            return {
                "success": True,
                "index_name": index_name,
                "dimensions": dimensions,
                "deployment_type": self.deployment_type,
                "message": f"Vector index '{index_name}' created with {dimensions} dimensions on {self.deployment_type}"
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to create vector index on {self.deployment_type}: {error_msg}")

            # Provide helpful error messages based on deployment type
            if self.is_aura and "version" in error_msg.lower():
                error_msg += " Neo4j Aura should support vector indexes in version 5.17+. Please verify your instance version."
            elif self.is_on_premise and "version" in error_msg.lower():
                error_msg += " On-premise Neo4j requires version 5.17+ for vector indexes."

            return {
                "success": False,
                "error": error_msg,
                "index_name": index_name,
                "deployment_type": self.deployment_type
            }

    async def vector_similarity_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Perform vector similarity search using Neo4j GraphRAG Cypher queries

        Args:
            query: Natural language search query
            limit: Maximum number of results to return

        Returns:
            Dictionary containing search results with similarity scores
        """
        if not self.embedding_model:
            return {"success": False, "error": "Embedding model not available", "results": []}

        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)[0].tolist()

            # Cypher query for vector similarity search using Neo4j's vector index
            search_query = f"""
            CALL db.index.vector.queryNodes('{self.vector_index_name}', {limit}, $query_embedding)
            YIELD node, score
            RETURN node.id as chunk_id,
                   node.text as text,
                   node.document_filename as document_filename,
                   score as similarity_score
            ORDER BY score DESC
            """

            driver = self.get_driver()
            with driver.session(database=self.database) as session:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, session.run, search_query, {"query_embedding": query_embedding}
                )

                records = await asyncio.get_event_loop().run_in_executor(None, list, result)

                results = []
                for record in records:
                    results.append({
                        "chunk_id": record["chunk_id"],
                        "text": record["text"],
                        "document_filename": record["document_filename"],
                        "similarity_score": record["similarity_score"]
                    })

            logger.info(f"Vector similarity search completed: {len(results)} results for query '{query}'")
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_results": len(results)
            }

        except Exception as e:
            logger.error(f"Vector similarity search failed: {str(e)}")
            return {"success": False, "error": str(e), "query": query, "results": []}

    async def store_document_chunks_with_embeddings(self, chunks: List[Dict[str, Any]],
                                                  document_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store document chunks with their embeddings in Neo4j for GraphRAG

        Args:
            chunks: List of document chunks with text content
            document_metadata: Metadata about the source document

        Returns:
            Dictionary containing storage results
        """
        if not self.embedding_model:
            return {"success": False, "error": "Embedding model not available", "chunks_stored": 0}

        try:
            stored_chunks = 0
            driver = self.get_driver()

            # Generate embeddings for all chunks in batch
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)

            with driver.session(database=self.database) as session:
                for i, chunk in enumerate(chunks):
                    embedding_list = embeddings[i].tolist()

                    # Create document chunk node with embedding for GraphRAG
                    create_chunk_query = """
                    CREATE (chunk:DocumentChunk {
                        id: $chunk_id,
                        text: $text,
                        embedding: $embedding,
                        document_filename: $document_filename,
                        start_pos: $start_pos,
                        end_pos: $end_pos,
                        created_at: datetime()
                    })
                    RETURN chunk.id as chunk_id
                    """

                    params = {
                        "chunk_id": chunk['id'],
                        "text": chunk['text'],
                        "embedding": embedding_list,
                        "document_filename": document_metadata.get('filename', 'unknown'),
                        "start_pos": chunk.get('start_pos', 0),
                        "end_pos": chunk.get('end_pos', len(chunk['text']))
                    }

                    result = await asyncio.get_event_loop().run_in_executor(
                        None, session.run, create_chunk_query, params
                    )

                    records = await asyncio.get_event_loop().run_in_executor(None, list, result)
                    if records:
                        stored_chunks += 1

            logger.info(f"Successfully stored {stored_chunks} document chunks with embeddings for GraphRAG")
            return {
                "success": True,
                "chunks_stored": stored_chunks,
                "total_chunks": len(chunks),
                "document_filename": document_metadata.get('filename', 'unknown')
            }

        except Exception as e:
            logger.error(f"Failed to store document chunks for GraphRAG: {str(e)}")
            return {"success": False, "error": str(e), "chunks_stored": 0}

# Create singleton instance (lazy initialization)
neo4j_service = None

def get_neo4j_service():
    """Get or create the Neo4j service singleton instance"""
    global neo4j_service
    if neo4j_service is None:
        neo4j_service = Neo4jService()
    return neo4j_service