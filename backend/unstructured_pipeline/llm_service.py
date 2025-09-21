"""
Offline LLM Service for document understanding and question answering
"""
import requests
import json
import logging
import os
from typing import Dict, Any, List, Optional
import time
from datetime import datetime
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class OfflineLLMService:
    """Service for offline LLM processing using Ollama or similar"""

    def __init__(self, base_url: str = None, model: str = None):
        """
        Initialize offline LLM service

        Args:
            base_url: Base URL of the LLM service (e.g., Ollama)
            model: Default model to use
        """
        # Load environment variables if not already loaded
        if not os.getenv("OLLAMA_HOST"):
            load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env.local'))
        
        if base_url is None:
            base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        if model is None:
            model = os.getenv("OLLAMA_DEFAULT_MODEL", "llama2")

        self.base_url = base_url.rstrip('/')
        self.default_model = model
        self.timeout = 60  # seconds

    def is_service_available(self) -> bool:
        """
        Check if the LLM service is available

        Returns:
            True if service is responding
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def list_available_models(self) -> List[str]:
        """
        List available models

        Returns:
            List of available model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []

    def generate_response(self, prompt: str, model: Optional[str] = None,
                         temperature: float = 0.7, max_tokens: int = 500) -> Dict[str, Any]:
        """
        Generate response from LLM

        Args:
            prompt: Input prompt
            model: Model to use (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response dictionary
        """
        if not self.is_service_available():
            return {
                'success': False,
                'error': 'LLM service not available',
                'response': '',
                'model': model or self.default_model
            }

        try:
            payload = {
                'model': model or self.default_model,
                'prompt': prompt,
                'temperature': temperature,
                'num_predict': max_tokens,
                'stream': False
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'response': result.get('response', ''),
                    'model': result.get('model', model or self.default_model),
                    'total_duration': result.get('total_duration', 0),
                    'load_duration': result.get('load_duration', 0),
                    'prompt_eval_count': result.get('prompt_eval_count', 0),
                    'eval_count': result.get('eval_count', 0),
                    'eval_duration': result.get('eval_duration', 0)
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'response': '',
                    'model': model or self.default_model
                }

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': '',
                'model': model or self.default_model
            }

    def analyze_document(self, document_content: str, document_type: str = "general") -> Dict[str, Any]:
        """
        Analyze document content using LLM

        Args:
            document_content: Full text content of the document
            document_type: Type of document (e.g., 'pdf', 'docx', 'txt')

        Returns:
            Analysis results
        """
        prompt = f"""
        Please analyze the following document and provide a comprehensive summary:

        Document Type: {document_type}
        Content:
        {document_content[:2000]}  # Limit content length

        Please provide:
        1. A brief summary (2-3 sentences)
        2. Main topics or themes
        3. Key entities mentioned (people, organizations, locations)
        4. Document type classification
        5. Any important dates or time references
        6. Overall sentiment or tone

        Format your response as a JSON object with these keys: summary, topics, entities, document_type, dates, sentiment
        """

        response = self.generate_response(prompt, max_tokens=1000)

        if response['success']:
            try:
                # Try to parse JSON response
                analysis = json.loads(response['response'])
                return {
                    'success': True,
                    'analysis': analysis,
                    'model': response['model'],
                    'processing_time': response.get('total_duration', 0) / 1e9  # Convert to seconds
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw response
                return {
                    'success': True,
                    'analysis': {'raw_response': response['response']},
                    'model': response['model'],
                    'processing_time': response.get('total_duration', 0) / 1e9
                }
        else:
            return {
                'success': False,
                'error': response['error'],
                'analysis': {},
                'model': response['model']
            }

    def answer_question(self, question: str, context: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Answer questions about document content

        Args:
            question: Question to answer
            context: Document context
            model: Model to use

        Returns:
            Answer with confidence and explanation
        """
        prompt = f"""
        Based on the following document content, please answer the question accurately and concisely.

        Document Content:
        {context[:3000]}  # Limit context length

        Question: {question}

        Please provide:
        1. A direct answer
        2. Confidence level (high/medium/low)
        3. Brief explanation supporting your answer
        4. Any relevant quotes from the document

        Format as JSON with keys: answer, confidence, explanation, quotes
        """

        response = self.generate_response(prompt, model=model, max_tokens=800)

        if response['success']:
            try:
                qa_result = json.loads(response['response'])
                return {
                    'success': True,
                    'qa_result': qa_result,
                    'model': response['model'],
                    'processing_time': response.get('total_duration', 0) / 1e9
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'qa_result': {'raw_response': response['response']},
                    'model': response['model'],
                    'processing_time': response.get('total_duration', 0) / 1e9
                }
        else:
            return {
                'success': False,
                'error': response['error'],
                'qa_result': {},
                'model': response['model']
            }

    def extract_entities_llm(self, text: str) -> Dict[str, Any]:
        """
        Extract entities using LLM (alternative to spaCy)

        Args:
            text: Text to analyze

        Returns:
            Extracted entities
        """
        prompt = f"""
        Extract all named entities from the following text. Categorize them into:
        - PERSON: Names of people
        - ORG: Organizations, companies, institutions
        - GPE: Countries, cities, locations
        - DATE: Dates and time expressions
        - MONEY: Monetary values
        - PERCENT: Percentage values
        - OTHER: Any other important entities

        Text:
        {text[:2000]}

        Return as JSON with categories as keys and lists of entities as values.
        """

        response = self.generate_response(prompt, max_tokens=600)

        if response['success']:
            try:
                entities = json.loads(response['response'])
                return {
                    'success': True,
                    'entities': entities,
                    'model': response['model']
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'entities': {'raw_response': response['response']},
                    'model': response['model']
                }
        else:
            return {
                'success': False,
                'error': response['error'],
                'entities': {},
                'model': response['model']
            }

    def classify_document(self, content: str) -> Dict[str, Any]:
        """
        Classify document type and content

        Args:
            content: Document content

        Returns:
            Classification results
        """
        prompt = f"""
        Classify the following document content:

        Content:
        {content[:1500]}

        Please classify:
        1. Document type (e.g., report, article, email, contract, manual, etc.)
        2. Primary topic/domain
        3. Content category (technical, business, academic, personal, etc.)
        4. Language
        5. Estimated reading level

        Return as JSON with keys: document_type, primary_topic, content_category, language, reading_level
        """

        response = self.generate_response(prompt, max_tokens=400)

        if response['success']:
            try:
                classification = json.loads(response['response'])
                return {
                    'success': True,
                    'classification': classification,
                    'model': response['model']
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'classification': {'raw_response': response['response']},
                    'model': response['model']
                }
        else:
            return {
                'success': False,
                'error': response['error'],
                'classification': {},
                'model': response['model']
            }

    def generate_search_query(self, natural_query: str) -> Dict[str, Any]:
        """
        Convert natural language query to structured search query

        Args:
            natural_query: Natural language search query

        Returns:
            Structured search parameters
        """
        prompt = f"""
        Convert this natural language search query into structured search parameters:

        Query: "{natural_query}"

        Generate:
        1. Keywords to search for
        2. Entity types to look for (person, organization, location, etc.)
        3. Date ranges if mentioned
        4. Boolean operators (AND, OR, NOT)
        5. Search filters or constraints

        Return as JSON with keys: keywords, entity_types, date_range, boolean_logic, filters
        """

        response = self.generate_response(prompt, max_tokens=500)

        if response['success']:
            try:
                search_params = json.loads(response['response'])
                return {
                    'success': True,
                    'search_params': search_params,
                    'original_query': natural_query,
                    'model': response['model']
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'search_params': {'raw_response': response['response']},
                    'original_query': natural_query,
                    'model': response['model']
                }
        else:
            return {
                'success': False,
                'error': response['error'],
                'search_params': {},
                'original_query': natural_query,
                'model': response['model']
            }

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze query intent and determine optimal search strategy

        Args:
            query: Natural language query

        Returns:
            Query analysis with routing recommendations
        """
        prompt = f"""
        Analyze this search query and determine the optimal search strategy:

        Query: "{query}"

        Classify the query into one of these types:
        - factual_lookup: Simple factual questions (e.g., "What is X?", "Who is Y?")
        - semantic_similarity: Finding similar content (e.g., "Find documents like this")
        - relationship_analysis: Understanding connections (e.g., "How are X and Y related?")
        - complex_analysis: Multi-faceted analysis (e.g., "Analyze the impact of X on Y")
        - conversational: General conversation or clarification

        For each query type, recommend which systems to use:
        - solr_primary: Use Solr inverted index for keyword search
        - neo4j_primary: Use Neo4j graph/vector search
        - graph_primary: Focus on graph relationships
        - hybrid_search: Use all systems with LLM coordination
        - llm_orchestrated: LLM handles the entire response

        Also identify:
        - Key entities mentioned
        - Required search depth (shallow/deep)
        - Expected result format

        Return as JSON with keys: query_type, recommended_strategy, key_entities, search_depth, result_format, confidence
        """

        response = self.generate_response(prompt, max_tokens=600)

        if response['success']:
            try:
                analysis = json.loads(response['response'])
                return {
                    'success': True,
                    'analysis': analysis,
                    'query': query,
                    'model': response['model'],
                    'processing_time': response.get('total_duration', 0) / 1e9
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'analysis': {'raw_response': response['response'], 'query_type': 'general'},
                    'query': query,
                    'model': response['model']
                }
        else:
            return {
                'success': False,
                'error': response['error'],
                'analysis': {'query_type': 'general', 'recommended_strategy': 'hybrid_search'},
                'query': query,
                'model': response['model']
            }

    def generate_system_queries(self, query: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate optimized queries for each search system based on intent analysis

        Args:
            query: Original query
            intent_analysis: Analysis from analyze_query_intent

        Returns:
            Optimized queries for each system
        """
        strategy = intent_analysis.get('recommended_strategy', 'hybrid_search')
        query_type = intent_analysis.get('query_type', 'general')

        system_queries = {
            'solr_query': None,
            'neo4j_query': None,
            'graph_query': None,
            'vector_query': None
        }

        # Generate Solr query for keyword search
        if strategy in ['solr_primary', 'hybrid_search']:
            solr_prompt = f"""
            Convert this query to an optimal Solr search query:

            Original Query: "{query}"
            Query Type: {query_type}
            Strategy: {strategy}

            Create a Solr query that will find relevant documents efficiently.
            Consider synonyms, fuzzy matching, and field-specific searches.

            Return just the Solr query string, no explanation.
            """
            solr_response = self.generate_response(solr_prompt, max_tokens=200)
            if solr_response['success']:
                system_queries['solr_query'] = solr_response['response'].strip()

        # Generate Neo4j vector similarity query
        if strategy in ['neo4j_primary', 'hybrid_search']:
            vector_prompt = f"""
            Convert this query to a semantic search description for vector similarity:

            Original Query: "{query}"
            Query Type: {query_type}

            Create a description that captures the semantic meaning for vector search.
            Focus on the core concepts and intent.

            Return just the semantic description, no explanation.
            """
            vector_response = self.generate_response(vector_prompt, max_tokens=200)
            if vector_response['success']:
                system_queries['vector_query'] = vector_response['response'].strip()

        # Generate Cypher query for graph relationships
        if strategy in ['graph_primary', 'hybrid_search'] or query_type == 'relationship_analysis':
            cypher_prompt = f"""
            Convert this query to a Cypher query for Neo4j graph search:

            Original Query: "{query}"
            Query Type: {query_type}

            Create a Cypher query that finds relevant nodes and relationships.
            Focus on graph patterns and connections.

            Return just the Cypher query, no explanation.
            Example: MATCH (n)-[r]-(m) WHERE n.name CONTAINS "search" RETURN n, r, m LIMIT 20
            """
            cypher_response = self.generate_response(cypher_prompt, max_tokens=300)
            if cypher_response['success']:
                system_queries['graph_query'] = cypher_response['response'].strip()

        return {
            'success': True,
            'system_queries': system_queries,
            'strategy': strategy,
            'query_type': query_type
        }

    def fuse_multi_system_results(self, query: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intelligently fuse results from multiple search systems

        Args:
            query: Original query
            results: Results from all search systems

        Returns:
            Fused and ranked results with explanations
        """
        # Prepare results summary for LLM
        results_summary = {
            'original_query': query,
            'solr_results': {
                'count': len(results.get('solr_results', [])),
                'sample': results.get('solr_results', [])[:3] if results.get('solr_results') else []
            },
            'neo4j_results': {
                'count': len(results.get('neo4j_results', [])),
                'sample': results.get('neo4j_results', [])[:3] if results.get('neo4j_results') else []
            },
            'graph_results': {
                'count': len(results.get('graph_results', [])),
                'sample': results.get('graph_results', [])[:3] if results.get('graph_results') else []
            },
            'vector_results': {
                'count': len(results.get('vector_results', [])),
                'sample': results.get('vector_results', [])[:3] if results.get('vector_results') else []
            }
        }

        prompt = f"""
        Analyze and fuse these multi-system search results into a coherent response:

        Original Query: "{query}"

        Search Results Summary:
        {json.dumps(results_summary, indent=2)}

        Your task:
        1. Identify the most relevant results across all systems
        2. Remove duplicates and redundant information
        3. Rank results by relevance to the query
        4. Provide a unified summary that combines insights from all sources
        5. Suggest follow-up queries if appropriate

        Return as JSON with keys: fused_results, summary, top_insights, follow_up_suggestions, confidence_score
        """

        response = self.generate_response(prompt, max_tokens=1000)

        if response['success']:
            try:
                fused_analysis = json.loads(response['response'])
                return {
                    'success': True,
                    'fused_analysis': fused_analysis,
                    'original_query': query,
                    'model': response['model'],
                    'processing_time': response.get('total_duration', 0) / 1e9
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'fused_analysis': {'raw_response': response['response']},
                    'original_query': query,
                    'model': response['model']
                }
        else:
            return {
                'success': False,
                'error': response['error'],
                'fused_analysis': {},
                'original_query': query,
                'model': response['model']
            }

    def generate_integrated_response(self, query: str, fused_results: Dict[str, Any],
                                   conversation_context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate a contextual, conversational response from fused search results

        Args:
            query: Original query
            fused_results: Fused results from fuse_multi_system_results
            conversation_context: Previous conversation turns

        Returns:
            Natural language response with structured data
        """
        context_str = ""
        if conversation_context:
            context_str = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in conversation_context[-3:]  # Last 3 messages
            ])

        prompt = f"""
        Generate a comprehensive, conversational response to this query using the fused search results:

        Original Query: "{query}"

        Conversation Context:
        {context_str}

        Fused Results Summary:
        {json.dumps(fused_results.get('fused_analysis', {}), indent=2)}

        Create a response that:
        1. Directly answers the query using the search results
        2. Provides context and explanations
        3. Highlights key insights from different sources
        4. Maintains conversational flow
        5. Suggests next steps or related questions

        Return as JSON with keys: response_text, key_insights, data_sources, confidence, suggestions
        """

        response = self.generate_response(prompt, max_tokens=800)

        if response['success']:
            try:
                integrated_response = json.loads(response['response'])
                return {
                    'success': True,
                    'integrated_response': integrated_response,
                    'query': query,
                    'model': response['model'],
                    'processing_time': response.get('total_duration', 0) / 1e9
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'integrated_response': {'response_text': response['response']},
                    'query': query,
                    'model': response['model']
                }
        else:
            return {
                'success': False,
                'error': response['error'],
                'integrated_response': {'response_text': 'I apologize, but I encountered an error processing your query.'},
                'query': query,
                'model': response['model']
            }