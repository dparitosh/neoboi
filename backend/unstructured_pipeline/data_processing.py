"""
Data Processing Pipeline for extracting entities and relationships from unstructured data
"""
import re
import logging
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict
import json
from datetime import datetime
import hashlib
import math

logger = logging.getLogger(__name__)

class DataProcessingPipeline:
    """Pipeline for processing unstructured data and extracting structured information"""

    def __init__(self):
        """Initialize the data processing pipeline"""
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks
        pass  # No spaCy dependency

    def process_text(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process text to extract entities, relationships, and structured data

        Args:
            text: Input text to process
            metadata: Additional metadata about the document

        Returns:
            Dictionary containing extracted entities, relationships, and analysis
        """
        if not text or not text.strip():
            return self._create_empty_result(metadata)

        try:
            # Basic text analysis
            text_stats = self._analyze_text(text)

            # Document chunking
            chunks = self.chunk_document(text)

            # Generate embeddings for chunks
            chunk_embeddings = self.generate_chunk_embeddings(chunks)

            # Simple entity extraction (no spaCy)
            entities = self._extract_entities_simple(text)

            # Simple relationship extraction
            relationships = self._extract_relationships_simple(text, entities)

            # Simple keyword extraction
            keywords = self._extract_keywords_simple(text)

            # Create structured data
            structured_data = {
                'text_stats': text_stats,
                'chunks': chunks,
                'chunk_embeddings': chunk_embeddings,
                'entities': entities,
                'relationships': relationships,
                'keywords': keywords,
                'topics': self._identify_topics(text),
                'sentiment': self._analyze_sentiment(text),
                'summary': self._generate_summary(text),
                'processed_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }

            logger.info(f"Text processing completed: {len(entities)} entities, {len(relationships)} relationships, {len(chunks)} chunks")
            return structured_data

        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            return self._create_empty_result(metadata)

    def chunk_document(self, text: str) -> List[Dict[str, Any]]:
        """
        Split document into overlapping chunks for better retrieval

        Args:
            text: Full document text

        Returns:
            List of text chunks with metadata
        """
        if not text:
            return []

        chunks = []
        text_length = len(text)
        start = 0

        while start < text_length:
            # Calculate end position
            end = min(start + self.chunk_size, text_length)

            # If we're not at the end, try to find a good break point
            if end < text_length:
                # Look for sentence endings within the last 100 characters
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)

                # Use the latest sentence break found
                break_point = max(last_period, last_newline)
                if break_point > start + (self.chunk_size // 2):  # Only if it's not too early
                    end = break_point + 1

            # Extract chunk
            chunk_text = text[start:end].strip()

            if chunk_text:  # Only add non-empty chunks
                chunk = {
                    'id': f"chunk_{len(chunks)}",
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'length': len(chunk_text),
                    'hash': hashlib.md5(chunk_text.encode()).hexdigest()[:8]
                }
                chunks.append(chunk)

            # Move start position with overlap
            start = end - self.chunk_overlap

            # Ensure we don't get stuck
            if start >= end:
                break

        logger.info(f"Document chunked into {len(chunks)} chunks")
        return chunks

    def generate_chunk_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate simple vector embeddings for text chunks

        Args:
            chunks: List of text chunks

        Returns:
            List of embeddings with metadata
        """
        embeddings = []

        for chunk in chunks:
            # Simple embedding based on word frequencies and positions
            embedding = self._generate_simple_embedding(chunk['text'])

            chunk_embedding = {
                'chunk_id': chunk['id'],
                'embedding': embedding,
                'dimensions': len(embedding),
                'magnitude': math.sqrt(sum(x**2 for x in embedding))
            }
            embeddings.append(chunk_embedding)

        logger.info(f"Generated embeddings for {len(embeddings)} chunks")
        return embeddings

    def _generate_simple_embedding(self, text: str, dimensions: int = 128) -> List[float]:
        """
        Generate a simple vector embedding based on character n-grams

        Args:
            text: Input text
            dimensions: Number of dimensions for the embedding

        Returns:
            Vector embedding as list of floats
        """
        # Normalize text
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)

        # Generate n-grams (2-grams and 3-grams)
        ngrams = []
        words = text.split()

        # Word-level n-grams
        for i in range(len(words) - 1):
            ngrams.append(f"{words[i]}_{words[i+1]}")  # 2-gram
        for i in range(len(words) - 2):
            ngrams.append(f"{words[i]}_{words[i+1]}_{words[i+2]}")  # 3-gram

        # Character-level n-grams
        for i in range(len(text) - 1):
            ngrams.append(text[i:i+2])  # 2-char gram
        for i in range(len(text) - 2):
            ngrams.append(text[i:i+3])  # 3-char gram

        # Create embedding vector
        embedding = [0.0] * dimensions

        for ngram in ngrams:
            # Use hash of ngram to determine position in vector
            hash_val = hash(ngram) % dimensions
            # Add frequency-based weight
            weight = 1.0 / (1 + ngrams.count(ngram))  # Inverse frequency weighting
            embedding[hash_val] += weight

        # Normalize the embedding
        magnitude = math.sqrt(sum(x**2 for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    def search_similar_chunks(self, query: str, chunks: List[Dict[str, Any]],
                            embeddings: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for chunks similar to a query using vector similarity

        Args:
            query: Search query
            chunks: List of text chunks
            embeddings: List of chunk embeddings
            top_k: Number of top results to return

        Returns:
            List of similar chunks with similarity scores
        """
        # Generate embedding for query
        query_embedding = self._generate_simple_embedding(query)

        similarities = []

        for i, chunk_emb in enumerate(embeddings):
            # Cosine similarity
            chunk_vector = chunk_emb['embedding']

            dot_product = sum(a * b for a, b in zip(query_embedding, chunk_vector))
            query_magnitude = math.sqrt(sum(x**2 for x in query_embedding))
            chunk_magnitude = chunk_emb['magnitude']

            if query_magnitude > 0 and chunk_magnitude > 0:
                similarity = dot_product / (query_magnitude * chunk_magnitude)
            else:
                similarity = 0.0

            similarities.append({
                'chunk': chunks[i],
                'similarity': similarity,
                'embedding': chunk_emb
            })

        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]

    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze basic text statistics"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = re.findall(r'\b\w+\b', text.lower())

        return {
            'char_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
            'unique_words': len(set(words)),
            'lexical_density': len(set(words)) / len(words) if words else 0
        }

    def _extract_entities_simple(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using simple regex patterns"""
        entities = []

        # Simple patterns for common entities
        patterns = [
            (r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', 'PERSON'),  # Names like "John Smith"
            (r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|GmbH)\b', 'ORG'),  # Company names
            (r'\b\d{1,2}/\d{1,2}/\d{4}\b', 'DATE'),  # Dates like "12/25/2023"
            (r'\b\d{4}-\d{2}-\d{2}\b', 'DATE'),  # ISO dates
            (r'\b\d+\.\d+\.\d+\.\d+\b', 'IP_ADDRESS'),  # IP addresses
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),  # Email addresses
        ]

        for pattern, label in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    'text': match.group(),
                    'label': label,
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.8
                })

        return entities

    def _extract_relationships_simple(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships using simple pattern matching"""
        relationships = []

        # Simple relationship patterns
        patterns = [
            (r'(\w+)\s+(?:is|was|are|were)\s+(?:a|an|the)\s+(\w+)', 'is_a'),
            (r'(\w+)\s+(?:works?|worked)\s+(?:for|at|with)\s+(\w+)', 'works_for'),
            (r'(\w+)\s+(?:located?|based)\s+(?:in|at)\s+(\w+)', 'located_in'),
            (r'(\w+)\s+(?:owns?|owned)\s+(\w+)', 'owns'),
            (r'(\w+)\s+(?:created?|developed|built)\s+(\w+)', 'created')
        ]

        entity_texts = [ent['text'] for ent in entities]

        for pattern, rel_type in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                subject, obj = match
                if subject in entity_texts and obj in entity_texts:
                    relationships.append({
                        'subject': subject,
                        'relation': rel_type,
                        'object': obj,
                        'confidence': 0.8
                    })

        return relationships

    def _extract_keywords_simple(self, text: str) -> List[Dict[str, Any]]:
        """Extract keywords using simple frequency analysis"""
        # Simple stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}

        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = defaultdict(int)

        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] += 1

        # Get top keywords
        keywords = []
        for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]:
            keywords.append({
                'text': word,
                'importance': min(1.0, freq / 10),  # Normalize importance
                'frequency': freq
            })

        return keywords

    def _identify_topics(self, text: str) -> List[str]:
        """Identify main topics in the text"""
        # Simple topic identification based on keywords
        topic_keywords = {
            'technology': ['software', 'computer', 'digital', 'internet', 'data', 'system'],
            'business': ['company', 'market', 'product', 'service', 'customer', 'sales'],
            'science': ['research', 'study', 'analysis', 'experiment', 'theory', 'method'],
            'health': ['medical', 'patient', 'treatment', 'disease', 'health', 'doctor'],
            'education': ['school', 'student', 'teacher', 'learning', 'course', 'university'],
            'finance': ['money', 'bank', 'investment', 'financial', 'economy', 'market']
        }

        text_lower = text.lower()
        topics = []

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text"""
        # Simple rule-based sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'poor', 'disappointing']

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total_words = len(text.split())
        sentiment_score = (positive_count - negative_count) / max(total_words, 1)

        if sentiment_score > 0.01:
            sentiment = 'positive'
        elif sentiment_score < -0.01:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        return {
            'sentiment': sentiment,
            'score': sentiment_score,
            'positive_words': positive_count,
            'negative_words': negative_count
        }

    def _generate_summary(self, text: str) -> str:
        """Generate a simple summary of the text"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return text[:200] + "..." if len(text) > 200 else text

        # Simple extractive summarization - take first and last sentences
        summary_sentences = []
        if len(sentences) >= 1:
            summary_sentences.append(sentences[0])
        if len(sentences) > 2:
            summary_sentences.append(sentences[-1])

        summary = '. '.join(summary_sentences)
        return summary[:300] + "..." if len(summary) > 300 else summary

    def _create_empty_result(self, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create empty result structure"""
        return {
            'text_stats': {'char_count': 0, 'word_count': 0, 'sentence_count': 0},
            'entities': [],
            'relationships': [],
            'keywords': [],
            'topics': [],
            'sentiment': {'sentiment': 'neutral', 'score': 0.0},
            'summary': '',
            'processed_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

    def create_neo4j_nodes_and_relationships(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Neo4j nodes and relationships from processed data

        Args:
            processed_data: Processed document data

        Returns:
            Neo4j graph structure
        """
        try:
            # Create document node
            document_node = {
                'labels': ['Document'],
                'properties': {
                    'filename': processed_data.get('metadata', {}).get('filename', ''),
                    'processed_at': processed_data['processed_at'],
                    'word_count': processed_data['text_stats']['word_count'],
                    'sentiment': processed_data['sentiment']['sentiment'],
                    'topics': processed_data['topics']
                }
            }

            # Create entity nodes
            entity_nodes = []
            for entity in processed_data['entities']:
                entity_node = {
                    'labels': ['Entity', entity['label']],
                    'properties': {
                        'text': entity['text'],
                        'type': entity['label'],
                        'confidence': entity.get('confidence', 1.0)
                    }
                }
                entity_nodes.append(entity_node)

            # Create relationship data
            relationships = []
            for rel in processed_data['relationships']:
                relationship = {
                    'from_node': rel['subject'],
                    'to_node': rel['object'],
                    'type': rel['relation'].upper(),
                    'properties': {
                        'confidence': rel.get('confidence', 0.8)
                    }
                }
                relationships.append(relationship)

            return {
                'document_node': document_node,
                'entity_nodes': entity_nodes,
                'relationships': relationships,
                'success': True
            }

        except Exception as e:
            logger.error(f"Neo4j structure creation failed: {str(e)}")
            return {
                'document_node': None,
                'entity_nodes': [],
                'relationships': [],
                'success': False,
                'error': str(e)
            }