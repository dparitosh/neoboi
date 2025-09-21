#!/usr/bin/env python3
"""
Enhanced Chat Service with Offline LLM Integration
This replaces the mock Cypher generation with intelligent LLM-powered processing
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from backend.unstructured_pipeline.llm_service import OfflineLLMService
from backend.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class EnhancedChatService:
    """Enhanced chat service with offline LLM integration"""

    def __init__(self):
        self.llm_service = OfflineLLMService()
        self.neo4j_service = Neo4jService()
        self.conversation_history = []
        self.max_history = 10

    async def process_chat_query(self, user_query: str, graph_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a chat query using offline LLM for intelligent understanding

        Args:
            user_query: Natural language query from user
            graph_context: Current graph data context (optional)

        Returns:
            Enhanced response with LLM analysis
        """
        try:
            logger.info(f"Processing enhanced chat query: {user_query}")

            # Add to conversation history
            self._add_to_history("user", user_query)

            # Get current graph context if not provided
            if graph_context is None:
                try:
                    # Ensure Neo4j driver is initialized
                    await self.neo4j_service.initialize_driver()
                    graph_context = await self.neo4j_service.get_graph_data()
                    logger.info(f"Got graph context: {len(graph_context.get('nodes', []))} nodes")
                except Exception as e:
                    logger.warning(f"Could not get graph context: {e}")
                    graph_context = {"nodes": [], "edges": []}

            # Analyze query intent and generate response
            response = await self._analyze_and_respond(user_query, graph_context)

            # Add response to history
            self._add_to_history("assistant", response.get("textResponse", ""))

            return response

        except Exception as e:
            logger.error(f"Error processing chat query: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_response(str(e))

    async def _analyze_and_respond(self, query: str, graph_context: Dict) -> Dict[str, Any]:
        """Analyze query and generate intelligent response"""

        # Determine query type and handle accordingly
        query_type = self._classify_query_type(query)
        logger.info(f"Query type classified as: {query_type}")

        if query_type == "graph_query":
            return await self._handle_graph_query(query, graph_context)
        elif query_type == "analysis_request":
            return await self._handle_analysis_request(query, graph_context)
        elif query_type == "search_request":
            return await self._handle_search_request(query, graph_context)
        elif query_type == "command":
            return await self._handle_command(query, graph_context)
        else:
            return await self._handle_general_query(query, graph_context)

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()

        # Graph queries
        if any(word in query_lower for word in ["show", "find", "get", "list", "display"]):
            return "graph_query"

        # Analysis requests
        if any(word in query_lower for word in ["analyze", "insights", "summary", "patterns"]):
            return "analysis_request"

        # Search requests
        if any(word in query_lower for word in ["search", "look for", "query"]):
            return "search_request"

        # Commands
        if any(word in query_lower for word in ["refresh", "reload", "clear", "reset", "expand"]):
            return "command"

        return "general"

    async def _handle_graph_query(self, query: str, graph_context: Dict) -> Dict[str, Any]:
        """Handle graph-related queries"""

        # Use LLM to understand what the user wants
        understanding_prompt = f"""
        User asked: "{query}"

        Current graph contains:
        - {len(graph_context.get('nodes', []))} nodes
        - {len(graph_context.get('edges', []))} relationships

        Node types: {set(node.get('group', 'Unknown') for node in graph_context.get('nodes', []))}

        What specific data should I retrieve from the graph to answer this query?
        Provide a Cypher query that would get the relevant information.
        """

        llm_response = self.llm_service.generate_response(understanding_prompt, max_tokens=200)

        # Extract Cypher query from LLM response
        cypher_query = self._extract_cypher_from_response(llm_response.get('response', ''))

        # Execute the query
        try:
            if cypher_query:
                # Ensure Neo4j driver is initialized
                await self.neo4j_service.initialize_driver()
                query_result = await self.neo4j_service.execute_query(cypher_query)
                graph_data = query_result
            else:
                graph_data = graph_context
        except Exception as e:
            logger.error(f"Error executing Cypher query: {e}")
            graph_data = graph_context

        return {
            "textResponse": f"I found relevant information for your query: '{query}'",
            "graphData": graph_data,
            "cypher": cypher_query,
            "confidence": 0.8,
            "source": "llm-enhanced"
        }

    async def _handle_analysis_request(self, query: str, graph_context: Dict) -> Dict[str, Any]:
        """Handle analysis and insights requests"""

        analysis_prompt = f"""
        Analyze this knowledge graph and provide insights for the query: "{query}"

        Graph Statistics:
        - Nodes: {len(graph_context.get('nodes', []))}
        - Relationships: {len(graph_context.get('edges', []))}
        - Node Types: {set(node.get('group', 'Unknown') for node in graph_context.get('nodes', []))}

        Provide:
        1. Key insights about the graph structure
        2. Important patterns or clusters
        3. Recommendations for exploration
        4. Any anomalies or interesting findings
        """

        analysis = self.llm_service.generate_response(analysis_prompt, max_tokens=400)

        return {
            "textResponse": analysis.get('response', 'Analysis completed.'),
            "graphData": graph_context,
            "analysis": analysis.get('response', ''),
            "confidence": 0.85,
            "source": "llm-analysis"
        }

    async def _handle_search_request(self, query: str, graph_context: Dict) -> Dict[str, Any]:
        """Handle search requests"""

        # Use LLM to enhance the search query
        search_params = await self.llm_service.generate_search_query(query)

        # Perform enhanced search
        try:
            # Ensure Neo4j driver is initialized
            await self.neo4j_service.initialize_driver()
            search_results = await self.neo4j_service.integrated_search(
                search_params.get('search_params', {}).get('keywords', query)
            )
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            search_results = {"neo4j_results": []}

        # Get LLM analysis of results
        results_analysis = self.llm_service.generate_response(
            f"Search query: '{query}'\nFound {len(search_results.get('neo4j_results', []))} results. Summarize the key findings.",
            max_tokens=200
        )

        return {
            "textResponse": f"Search results for '{query}': {results_analysis.get('response', '')}",
            "graphData": {
                "nodes": search_results.get('neo4j_results', []),
                "edges": []
            },
            "search_results": search_results,
            "analysis": results_analysis.get('response', ''),
            "confidence": 0.8,
            "source": "llm-search"
        }

    async def _handle_command(self, query: str, graph_context: Dict) -> Dict[str, Any]:
        """Handle command-type queries"""

        query_lower = query.lower()

        if "refresh" in query_lower or "reload" in query_lower:
            # Refresh graph data
            try:
                # Ensure Neo4j driver is initialized
                await self.neo4j_service.initialize_driver()
                new_graph_data = await self.neo4j_service.get_graph_data()
            except Exception as e:
                logger.error(f"Error refreshing graph data: {e}")
                new_graph_data = {"nodes": [], "edges": []}
            return {
                "textResponse": "Graph data refreshed successfully!",
                "graphData": new_graph_data,
                "action": "refresh",
                "confidence": 1.0,
                "source": "command"
            }

        elif "expand" in query_lower or "more" in query_lower:
            # Get more data
            try:
                # Ensure Neo4j driver is initialized
                await self.neo4j_service.initialize_driver()
                expanded_query = "MATCH (n)-[r]-(m) RETURN n, r, m LIMIT 100"
                expanded_data = await self.neo4j_service.execute_query(expanded_query)
            except Exception as e:
                logger.error(f"Error expanding graph data: {e}")
                expanded_data = {"nodes": [], "edges": []}
            return {
                "textResponse": "Expanded graph view with more connections!",
                "graphData": expanded_data,
                "action": "expand",
                "confidence": 1.0,
                "source": "command"
            }

        elif "clear" in query_lower or "reset" in query_lower:
            # Reset to original data
            try:
                # Ensure Neo4j driver is initialized
                await self.neo4j_service.initialize_driver()
                original_data = await self.neo4j_service.get_graph_data()
            except Exception as e:
                logger.error(f"Error resetting graph data: {e}")
                original_data = {"nodes": [], "edges": []}
            return {
                "textResponse": "Graph reset to original state.",
                "graphData": original_data,
                "action": "reset",
                "confidence": 1.0,
                "source": "command"
            }

        else:
            return await self._handle_general_query(query, graph_context)

    async def _handle_general_query(self, query: str, graph_context: Dict) -> Dict[str, Any]:
        """Handle general conversational queries"""

        # Create context-aware response
        context_prompt = f"""
        User asked: "{query}"

        This is a conversation about a knowledge graph with:
        - {len(graph_context.get('nodes', []))} nodes
        - {len(graph_context.get('edges', []))} relationships

        Provide a helpful response that acknowledges their query and offers assistance with the graph data.
        If appropriate, suggest specific actions they can take.
        """

        response = self.llm_service.generate_response(context_prompt, max_tokens=300)

        return {
            "textResponse": response.get('response', f"I understand you're asking about: {query}"),
            "graphData": graph_context,
            "confidence": 0.7,
            "source": "llm-general"
        }

    def _extract_cypher_from_response(self, llm_response: str) -> Optional[str]:
        """Extract Cypher query from LLM response"""

        # Look for Cypher code blocks
        import re

        # Match Cypher code blocks
        cypher_match = re.search(r'```cypher\s*(.*?)\s*```', llm_response, re.DOTALL | re.IGNORECASE)
        if cypher_match:
            return cypher_match.group(1).strip()

        # Match general code blocks
        code_match = re.search(r'```\s*(.*?)\s*```', llm_response, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            # Check if it looks like Cypher
            if any(keyword in code.upper() for keyword in ['MATCH', 'RETURN', 'WHERE', 'CREATE']):
                return code

        # Look for MATCH statements
        match_match = re.search(r'(MATCH.*?RETURN.*)', llm_response, re.DOTALL | re.IGNORECASE)
        if match_match:
            return match_match.group(1).strip()

        return None

    def _add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def _create_error_response(self, error: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "textResponse": f"Sorry, I encountered an error: {error}",
            "graphData": {"nodes": [], "edges": []},
            "error": error,
            "confidence": 0.0,
            "source": "error"
        }

    def get_conversation_history(self) -> list:
        """Get conversation history"""
        return self.conversation_history.copy()

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

# Global service instance
enhanced_chat_service = EnhancedChatService()