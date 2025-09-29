#!/usr/bin/env python3
"""
LLAMA3 Framework Optimization for NeoBoi
This module provides LLAMA3-specific optimizations and configurations
"""
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class LLAMA3Config:
    """LLAMA3-specific configuration optimizations"""
    model_name: str = "llama3"
    context_length: int = 8192  # LLAMA3's context window
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    num_predict: int = 500
    
    # LLAMA3-specific optimizations
    use_mmap: bool = True
    use_mlock: bool = True
    num_thread: int = 8
    num_gpu: int = 0  # Set to 1 if GPU available
    
    def to_ollama_params(self) -> Dict[str, Any]:
        """Convert to OLLAMA API parameters"""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repeat_penalty": self.repeat_penalty,
            "num_predict": self.num_predict,
            "options": {
                "use_mmap": self.use_mmap,
                "use_mlock": self.use_mlock,
                "num_thread": self.num_thread,
                "num_gpu": self.num_gpu
            }
        }

class LLAMA3Prompts:
    """LLAMA3-optimized prompt templates"""
    
    @staticmethod
    def system_prompt() -> str:
        """System prompt optimized for LLAMA3"""
        return """You are NeoBoi, an advanced AI assistant specialized in knowledge graph analysis and intelligent search. You have access to Neo4j graph databases, Solr search indices, and can perform complex reasoning tasks.

Your capabilities include:
- Analyzing graph relationships and patterns
- Performing semantic search across documents
- Extracting entities and relationships
- Answering complex questions using multiple data sources
- Providing insights and recommendations

Always provide accurate, helpful, and contextual responses. When uncertain, acknowledge limitations and suggest alternatives."""

    @staticmethod
    def conversation_prompt(query: str, context: str = "", conversation_history: Optional[List[Dict]] = None) -> str:
        """Conversation prompt optimized for LLAMA3"""
        history_text = ""
        if conversation_history:
            history_text = "\n".join([
                f"{'Human' if msg.get('role') == 'user' else 'Assistant'}: {msg.get('content', '')}"
                for msg in conversation_history[-3:]  # Last 3 messages
            ])
            
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{LLAMA3Prompts.system_prompt()}

Context Information:
{context}

Recent Conversation:
{history_text}

<|eot_id|><|start_header_id|>user<|end_header_id|>

{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    @staticmethod
    def analysis_prompt(data: str, analysis_type: str = "general") -> str:
        """Analysis prompt optimized for LLAMA3"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert data analyst. Analyze the provided data and provide comprehensive insights.

Analysis Type: {analysis_type}

<|eot_id|><|start_header_id|>user<|end_header_id|>

Please analyze the following data and provide:
1. Key insights and patterns
2. Important relationships
3. Notable anomalies or outliers
4. Actionable recommendations
5. Summary of findings

Data to analyze:
{data}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    @staticmethod
    def search_intent_prompt(query: str) -> str:
        """Search intent analysis prompt for LLAMA3"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a search intent analysis expert. Analyze user queries to determine the best search strategy.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze this search query and provide a JSON response with the following structure:
{{
    "query_type": "factual_lookup|semantic_similarity|relationship_analysis|complex_analysis|conversational",
    "recommended_strategy": "solr_primary|neo4j_primary|graph_primary|hybrid_search|llm_orchestrated",
    "key_entities": ["entity1", "entity2"],
    "search_depth": "shallow|deep",
    "result_format": "direct_answer|list|graph|analysis",
    "confidence": 0.0-1.0
}}

Query: "{query}"

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    @staticmethod
    def entity_extraction_prompt(text: str) -> str:
        """Entity extraction prompt optimized for LLAMA3"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert named entity recognition system. Extract all relevant entities from the provided text.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Extract all named entities from the following text and categorize them. Return as JSON with this structure:
{{
    "PERSON": ["person names"],
    "ORG": ["organizations"],
    "GPE": ["locations"],
    "DATE": ["dates and times"],
    "MONEY": ["monetary values"],
    "PERCENT": ["percentages"],
    "PRODUCT": ["products and services"],
    "EVENT": ["events"],
    "OTHER": ["other important entities"]
}}

Text:
{text}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

class LLAMA3OptimizedService:
    """LLAMA3-optimized service wrapper"""
    
    def __init__(self, base_service, config: Optional[LLAMA3Config] = None):
        self.base_service = base_service
        self.config = config or LLAMA3Config()
        self.prompts = LLAMA3Prompts()
    
    def generate_response(self, prompt: str, use_optimized_prompt: bool = True, **kwargs) -> Dict[str, Any]:
        """Generate response with LLAMA3 optimizations"""
        
        # Use LLAMA3-optimized parameters
        params = self.config.to_ollama_params()
        params.update(kwargs)
        
        # Use optimized prompt format if requested
        if use_optimized_prompt and not prompt.startswith("<|begin_of_text|>"):
            prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
        return self.base_service.generate_response(
            prompt=prompt,
            model=self.config.model_name,
            temperature=params.get('temperature'),
            max_tokens=params.get('num_predict')
        )
    
    def analyze_with_llama3(self, data: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Perform analysis using LLAMA3-optimized prompts"""
        prompt = self.prompts.analysis_prompt(data, analysis_type)
        return self.generate_response(prompt, use_optimized_prompt=False)
    
    def extract_entities_llama3(self, text: str) -> Dict[str, Any]:
        """Extract entities using LLAMA3-optimized prompts"""
        prompt = self.prompts.entity_extraction_prompt(text)
        response = self.generate_response(prompt, use_optimized_prompt=False)
        
        if response.get('success'):
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
        return response
    
    def analyze_search_intent_llama3(self, query: str) -> Dict[str, Any]:
        """Analyze search intent using LLAMA3-optimized prompts"""
        prompt = self.prompts.search_intent_prompt(query)
        response = self.generate_response(prompt, use_optimized_prompt=False)
        
        if response.get('success'):
            try:
                intent = json.loads(response['response'])
                return {
                    'success': True,
                    'analysis': intent,
                    'query': query,
                    'model': response['model']
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'analysis': {'raw_response': response['response']},
                    'query': query,
                    'model': response['model']
                }
        return response
    
    def conversational_response_llama3(self, query: str, context: str = "", 
                                      conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Generate conversational response using LLAMA3-optimized prompts"""
        prompt = self.prompts.conversation_prompt(query, context, conversation_history)
        return self.generate_response(prompt, use_optimized_prompt=False)

def create_llama3_optimized_service(base_service):
    """Factory function to create LLAMA3-optimized service"""
    config = LLAMA3Config()
    return LLAMA3OptimizedService(base_service, config)

# Configuration constants for LLAMA3
LLAMA3_SYSTEM_MESSAGES = {
    "analysis": "You are an expert data analyst specializing in knowledge graphs and information extraction.",
    "search": "You are a search specialist who understands user intent and optimizes queries for multiple search systems.",
    "conversation": "You are NeoBoi, a knowledgeable AI assistant with access to graph databases and search systems.",
    "extraction": "You are a named entity recognition expert with deep understanding of various text types."
}

LLAMA3_PERFORMANCE_TIPS = {
    "context_management": "Keep context under 6000 tokens for optimal performance",
    "prompt_engineering": "Use clear, structured prompts with specific instructions",
    "temperature_tuning": "Use 0.7 for creative tasks, 0.3 for factual responses",
    "batch_processing": "Process multiple similar requests together when possible",
    "caching": "Cache frequent query patterns and responses"
}