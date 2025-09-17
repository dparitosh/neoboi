from neo4j import GraphDatabase, basic_auth
import os
import logging
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jService:
    def __init__(self):
        self.driver = None
        # Read from environment variables with fallbacks
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        self.uri = os.getenv("NEO4J_URI", "neo4j+s://2cccd05b.databases.neo4j.io")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "tcs12345")

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
        rel_id = relationship.get('elementId') or relationship.get('id')
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

        query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]-(m)
        RETURN n, r, m LIMIT 50
        """

        with driver.session(database=self.database) as session:
            result = await asyncio.get_event_loop().run_in_executor(
                None, session.run, query
            )

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
                'rawRecords': raw_records
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

# Global service instance
neo4j_service = Neo4jService()