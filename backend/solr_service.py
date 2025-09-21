import requests
import json
import logging
import os
from typing import Dict, List, Any, Optional
# Removed circular import: from neo4j_service import neo4j_service

logger = logging.getLogger(__name__)

class SolrService:
    def __init__(self, solr_url: str = None, collection: str = None):
        # Load from environment variables with defaults
        self.solr_url = solr_url or os.getenv("SOLR_URL", "http://localhost:8983/solr")
        self.collection = collection or os.getenv("SOLR_COLLECTION", "neoboi_graph")
        self.base_url = f"{self.solr_url}/{self.collection}"

        logger.info(f"SolrService initialized with URL: {self.solr_url}, Collection: {self.collection}")

    async def index_node(self, node_data: Dict[str, Any]) -> bool:
        """Index a single node into Solr"""
        try:
            # Prepare document for Solr
            doc = {
                "id": f"node_{node_data['id']}",
                "type": "node",
                "neo4j_id": node_data['id'],
                "label": node_data.get('label', ''),
                "group": node_data.get('group', ''),
                "properties": self._serialize_properties(node_data.get('properties', {})),
                "content": self._extract_searchable_content(node_data)
            }

            # Add all properties as individual fields for faceting/searching
            properties = node_data.get('properties', {})
            for key, value in properties.items():
                if isinstance(value, (str, int, float, bool)):
                    doc[f"prop_{key}"] = value
                elif hasattr(value, 'isoformat'):  # Handle DateTime objects
                    doc[f"prop_{key}"] = value.isoformat()
                else:
                    # Convert other types to string
                    doc[f"prop_{key}"] = str(value)

            response = requests.post(
                f"{self.base_url}/update/json/docs",
                json=doc,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                logger.info(f"Successfully indexed node: {node_data['id']}")
                return True
            else:
                logger.error(f"Failed to index node {node_data['id']}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error indexing node {node_data.get('id', 'unknown')}: {e}")
            return False

    async def index_graph_data(self, graph_data: Dict[str, Any]) -> Dict[str, int]:
        """Index all nodes and relationships from graph data"""
        nodes_indexed = 0
        edges_indexed = 0

        # Index nodes
        nodes = graph_data.get('nodes', [])
        for node in nodes:
            if await self.index_node(node):
                nodes_indexed += 1

        # Index relationships
        edges = graph_data.get('edges', [])
        for edge in edges:
            if await self.index_relationship(edge):
                edges_indexed += 1

        # Commit changes
        await self.commit()

        logger.info(f"Indexing complete: {nodes_indexed} nodes, {edges_indexed} relationships")
        return {
            "nodes_indexed": nodes_indexed,
            "edges_indexed": edges_indexed,
            "total_indexed": nodes_indexed + edges_indexed
        }

    async def search(self, query: str, filters: Optional[Dict[str, Any]] = None,
                    limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search the indexed data"""
        try:
            search_params = {
                "q": query,
                "rows": limit,
                "start": offset,
                "wt": "json"
            }

            # Add filters
            if filters:
                fq = []
                for key, value in filters.items():
                    if key == "type":
                        fq.append(f"type:{value}")
                    elif key == "group":
                        fq.append(f"group:{value}")
                    elif key.startswith("prop_"):
                        fq.append(f"{key}:{value}")
                    else:
                        fq.append(f"prop_{key}:{value}")
                if fq:
                    search_params["fq"] = fq

            response = requests.get(f"{self.base_url}/select", params=search_params)

            if response.status_code == 200:
                result = response.json()
                return {
                    "total": result.get("response", {}).get("numFound", 0),
                    "docs": result.get("response", {}).get("docs", []),
                    "query": query,
                    "filters": filters
                }
            else:
                logger.error(f"Search failed: {response.text}")
                return {"total": 0, "docs": [], "error": response.text}

        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"total": 0, "docs": [], "error": str(e)}

    async def commit(self):
        """Commit pending changes to Solr"""
        try:
            response = requests.get(f"{self.base_url}/update?commit=true")
            if response.status_code == 200:
                logger.info("Successfully committed changes to Solr")
                return True
            else:
                logger.error(f"Commit failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Commit error: {e}")
            return False

    async def index_relationship(self, edge_data: Dict[str, Any]) -> bool:
        """Index a single relationship into Solr"""
        try:
            # Prepare document for Solr
            doc = {
                "id": f"edge_{edge_data['id']}",
                "type": "relationship",
                "neo4j_id": edge_data['id'],
                "label": edge_data.get('label', ''),
                "source": edge_data.get('from', ''),
                "target": edge_data.get('to', ''),
                "properties": self._serialize_properties(edge_data.get('properties', {})),
                "content": self._extract_searchable_content(edge_data)
            }

            # Add all properties as individual fields
            properties = edge_data.get('properties', {})
            for key, value in properties.items():
                if isinstance(value, (str, int, float, bool)):
                    doc[f"prop_{key}"] = value
                elif hasattr(value, 'isoformat'):  # Handle DateTime objects
                    doc[f"prop_{key}"] = value.isoformat()
                else:
                    # Convert other types to string
                    doc[f"prop_{key}"] = str(value)

            response = requests.post(
                f"{self.base_url}/update/json/docs",
                json=doc,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                logger.info(f"Successfully indexed relationship: {edge_data['id']}")
                return True
            else:
                logger.error(f"Failed to index relationship {edge_data['id']}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error indexing relationship {edge_data.get('id', 'unknown')}: {e}")
            return False

    def _extract_searchable_content(self, data: Dict[str, Any]) -> str:
        """Extract searchable text content from node/relationship data"""
        content_parts = []

        # Add label/name
        if data.get('label'):
            content_parts.append(data['label'])

        # Add group/type
        if data.get('group'):
            content_parts.append(data['group'])

        # Add properties
        properties = data.get('properties', {})
        for key, value in properties.items():
            if isinstance(value, str):
                content_parts.append(f"{key}:{value}")
            elif isinstance(value, (int, float)):
                content_parts.append(f"{key}:{str(value)}")
            elif hasattr(value, 'isoformat'):  # Handle DateTime objects
                content_parts.append(f"{key}:{value.isoformat()}")

        return " ".join(content_parts)

    async def clear_index(self):
        """Clear all documents from the index"""
        try:
            response = requests.get(f"{self.base_url}/update?stream.body=<delete><query>*:*</query></delete>&commit=true")
            if response.status_code == 200:
                logger.info("Successfully cleared Solr index")
                return True
            else:
                logger.error(f"Clear index failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Clear index error: {e}")
            return False

    def _serialize_properties(self, properties: Dict[str, Any]) -> str:
        """Serialize properties to JSON, handling DateTime objects"""
        serialized = {}
        for key, value in properties.items():
            if hasattr(value, 'isoformat'):  # Handle DateTime objects
                serialized[key] = value.isoformat()
            else:
                try:
                    # Try to serialize the value
                    json.dumps(value)
                    serialized[key] = value
                except (TypeError, ValueError):
                    # If serialization fails, convert to string
                    serialized[key] = str(value)
        return json.dumps(serialized)

    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Solr index"""
        try:
            # Get collection info
            response = requests.get(f"{self.solr_url}/solr/admin/collections",
                                  params={"action": "CLUSTERSTATUS", "wt": "json"})

            if response.status_code == 200:
                data = response.json()
                collections = data.get("cluster", {}).get("collections", {})

                if self.collection in collections:
                    collection_info = collections[self.collection]
                    return {
                        "collection": self.collection,
                        "status": "active",
                        "shards": len(collection_info.get("shards", {})),
                        "replicas": sum(len(shard.get("replicas", {}))
                                       for shard in collection_info.get("shards", {}).values())
                    }

            return {"collection": self.collection, "status": "unknown"}

        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"collection": self.collection, "status": "error", "error": str(e)}

# Global service instance
solr_service = SolrService()