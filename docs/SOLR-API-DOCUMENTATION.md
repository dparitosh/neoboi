# Solr Search Integration in Neo4j GraphRAG Platform

This document describes how Apache Solr serves as the **keyword search foundation** in the integrated Neo4j GraphRAG platform, working seamlessly with Neo4j's graph database and offline LLM orchestration for comprehensive search capabilities.

## ✅ Integration Status

**🟢 FULLY INTEGRATED** - Complete system integration verified on September 21, 2025
- ✅ Solr inverted indexing from unstructured pipeline (Tika + Tesseract)
- ✅ Neo4j graph creation using Solr-processed content
- ✅ LLM orchestration across Solr and Neo4j systems
- ✅ All search types working together
- ✅ Contextual NLP queries functional
- ✅ Performance optimized for consistency

### Recent Fixes Applied
- Fixed import issues in test files
- Resolved module path problems
- Updated all service imports
- Verified API endpoint functionality

---

## Overview

Apache Solr provides the **keyword-based inverted indexing foundation** for the Neo4j GraphRAG platform. The system processes unstructured documents through the Tika/Tesseract pipeline, creates comprehensive inverted indexes in Solr, and enables Neo4j to use these indexes for graph creation and search. The offline LLM orchestrates search across both systems for contextual, NLP-driven results.

## Integrated Architecture Role

### Solr in the Data Pipeline

```
Document Upload → Tika/Tesseract Processing → Solr Inverted Indexing → Neo4j Graph Creation → LLM Orchestration → Contextual Search
```

### Component Responsibilities

- **Solr**: Creates and maintains inverted indexes for fast keyword search
- **Neo4j**: Uses Solr-processed content to build knowledge graphs and vector indexes
- **LLM**: Orchestrates queries across both systems for intelligent, contextual responses

## Enhanced Data Processing Flow

### 1. Document Ingestion & Processing
```python
# Unstructured pipeline processes documents
document_processor = DocumentIngestionService()
processed_doc = await document_processor.process_document_with_chunking(
    file_content, metadata
)

# Content goes to both Solr and Neo4j
await solr_service.index_document_chunks(processed_doc)
await neo4j_service.store_document_chunks_with_embeddings(
    processed_doc['chunks'], processed_doc['metadata']
)
```

### 2. Dual Indexing Strategy
- **Solr Indexing**: Full-text inverted index for keyword search
- **Neo4j Indexing**: Graph structure + vector embeddings for semantic search
- **Cross-Reference**: Both systems maintain document chunk relationships

### 3. Integrated Search Orchestration
```python
# LLM orchestrates search across systems
async def integrated_search(query: str):
    # LLM analyzes query intent
    analysis = await llm_service.analyze_query(query)
    
    # Parallel search execution
    solr_results = await solr_service.search(analysis['keyword_terms'])
    neo4j_results = await neo4j_service.vector_similarity_search(analysis['semantic_query'])
    
    # LLM fuses results for contextual response
    fused_results = await llm_service.fuse_search_results(
        solr_results, neo4j_results, query
    )
    
    return fused_results
```

## Configuration

The Solr integration is configured via environment variables in `.env.local`:

```bash
# Solr Configuration
SOLR_HOME="D:\Software\solr-9.9.0"
SOLR_PORT="8983"
SOLR_BIN_PATH="D:\Software\solr-9.9.0\bin"
SOLR_URL="http://localhost:8983/solr"
SOLR_COLLECTION="neoboi_graph"
```

## API Endpoints

### 1. Index Graph Data
**POST** `/api/solr/index`

Indexes the current graph data from Neo4j into Solr for search.

**Response:**
```json
{
  "message": "Successfully indexed graph data into Solr",
  "result": {
    "nodes_indexed": 25,
    "edges_indexed": 30,
    "total_indexed": 55
  },
  "status": "completed"
}
```

### 2. Search Indexed Data
**GET** `/api/solr/search`

Search the indexed graph data with various filters and options.

**Query Parameters:**
- `q` (required): Search query string
- `type` (optional): Filter by type (`node` or `relationship`)
- `group` (optional): Filter by node group
- `limit` (optional): Maximum number of results (default: 20)
- `offset` (optional): Offset for pagination (default: 0)

**Examples:**
```bash
# Basic search
GET /api/solr/search?q=supplier

# Filtered search
GET /api/solr/search?q=manufacturer&type=node&limit=10

# Search with pagination
GET /api/solr/search?q=test&offset=20&limit=10
```

**Response:**
```json
{
  "query": "supplier",
  "filters": {
    "type": "node"
  },
  "total": 15,
  "results": [
    {
      "id": "node_123",
      "type": "node",
      "neo4j_id": "123",
      "label": "Supplier",
      "group": "supplier",
      "properties": "{\"name\":\"ABC Corp\",\"location\":\"New York\"}",
      "content": "Supplier ABC Corp New York",
      "prop_name": "ABC Corp",
      "prop_location": "New York"
    }
  ],
  "limit": 20,
  "offset": 0
}
```

### 3. Clear Index
**POST** `/api/solr/clear`

Clears all documents from the Solr index.

**Response:**
```json
{
  "message": "Successfully cleared Solr index",
  "status": "completed"
}
```

### 4. Get Index Statistics
**GET** `/api/solr/stats`

Retrieves statistics about the Solr index and collection.

**Response:**
```json
{
  "solr_stats": {
    "collection": "neoboi_graph",
    "status": "active",
    "shards": 1,
    "replicas": 1
  },
  "collection": "neoboi_graph",
  "solr_url": "http://localhost:8983"
}
```

## Data Structure Evolution

### Enhanced Indexed Documents

Solr now indexes document chunks that are also stored in Neo4j, creating a **dual indexing system**:

#### Document Chunk Documents
```json
{
  "id": "chunk_doc001_005",
  "content": "processed text content from chunking pipeline...",
  "document_filename": "business_report.pdf",
  "chunk_id": "chunk_005",
  "start_pos": 4000,
  "end_pos": 5000,
  "entities": ["John Smith", "ABC Corp", "2024-01-15"],
  "keywords": ["business", "analysis", "growth", "strategy"],
  "topics": ["business_strategy", "market_analysis"],
  "sentiment": "positive",
  "neo4j_node_id": "chunk_005",
  "embedding_available": true
}
```

#### Graph Node Cross-Reference
```json
{
  "id": "node_person_john_smith",
  "type": "node",
  "neo4j_id": "123",
  "label": "Person",
  "group": "person",
  "properties": "{\"name\":\"John Smith\",\"role\":\"Manager\"}",
  "content": "Person John Smith Manager",
  "solr_chunk_refs": ["chunk_doc001_005", "chunk_doc002_012"],
  "graph_centrality": 0.85
}
```

## Integrated Search Features

### Multi-System Search Coordination

#### 1. **Keyword Search (Solr Primary)**
- Fast inverted index lookups
- Complex query support with filters
- Faceted search capabilities
- Real-time indexing updates

#### 2. **Semantic Search (Neo4j Integration)**
- Vector similarity using chunk embeddings
- Graph traversal for relationship-based results
- Cross-document relationship discovery

#### 3. **Conversational Search (LLM Orchestration)**
- Natural language query understanding
- Multi-turn conversation support
- Contextual result interpretation

#### 4. **Hybrid Search (Integrated Approach)**
```python
# Example hybrid search implementation
async def hybrid_search(query: str):
    # LLM analyzes the query
    query_analysis = await llm_service.analyze_query(query)
    
    # Parallel execution across systems
    tasks = [
        solr_service.search(query_analysis['keyword_query']),
        neo4j_service.vector_similarity_search(query_analysis['semantic_query']),
        neo4j_service.graph_traversal_search(query_analysis['entity_query'])
    ]
    
    results = await asyncio.gather(*tasks)
    solr_results, neo4j_vector_results, neo4j_graph_results = results
    
    # LLM fuses results
    fused_response = await llm_service.generate_integrated_response(
        query, solr_results, neo4j_vector_results, neo4j_graph_results
    )
    
    return fused_response
```

## Performance & Consistency

### Success Metrics

#### Contextual Accuracy
- **NLP Query Precision**: >90% relevant results for natural language queries
- **Multi-System Consistency**: Unified response format across all search types
- **Conversation Continuity**: Context maintained across multi-turn interactions

#### Performance Targets
- **Sub-second responses** for keyword searches
- **<3 second responses** for hybrid semantic searches
- **Consistent latency** regardless of search complexity

### Optimization Strategies

#### Query Routing Intelligence
```python
# LLM-based query routing
async def route_query(query: str):
    analysis = await llm_service.classify_query_type(query)
    
    if analysis['type'] == 'factual':
        return await solr_service.search(query)  # Fast keyword search
    elif analysis['type'] == 'analytical':
        return await neo4j_service.graph_analytics(query)  # Graph analysis
    elif analysis['type'] == 'conversational':
        return await integrated_search(query)  # Full hybrid search
```

#### Result Caching Strategy
- **Query Result Caching**: Frequently accessed results cached
- **Embedding Caching**: Pre-computed embeddings for common queries
- **Graph Path Caching**: Commonly traversed graph paths cached

## API Endpoints

### Enhanced Search Endpoint
**POST** `/api/search/integrated`

Unified search across all systems with LLM orchestration.

**Request Body:**
```json
{
  "query": "How does ABC Corp's business strategy impact market growth?",
  "search_type": "hybrid",
  "context": {
    "conversation_history": ["previous messages..."],
    "user_preferences": {"depth": "detailed"}
  }
}
```

**Response:**
```json
{
  "query": "How does ABC Corp's business strategy impact market growth?",
  "search_type": "hybrid",
  "results": {
    "solr_results": [...],
    "neo4j_results": [...],
    "llm_analysis": "..."
  },
  "confidence": 0.92,
  "response_time": 1.2,
  "sources": ["solr", "neo4j", "llm"]
}
```

## Management Scripts

### Service Management
- `start-solr.bat` - Start Solr service
- `stop-solr.bat` - Stop Solr service
- `status-solr.bat` - Check Solr status
- `restart-solr.bat` - Restart Solr service
- `solr-service.bat [start|stop|status|restart]` - Unified service management

### Collection Management
- `init-solr-collection.bat` - Initialize/create the required Solr collection

### Testing
- `test-solr-api.bat` - Test all Solr API endpoints
- `test-services.bat` - General service health check including Solr

## Usage Examples

### Index Current Graph Data
```bash
curl -X POST http://localhost:3001/api/solr/index
```

### Search for Suppliers
```bash
curl "http://localhost:3001/api/solr/search?q=supplier&type=node"
```

### Search with Multiple Filters
```bash
curl "http://localhost:3001/api/solr/search?q=john&type=node&group=person&limit=5"
```

### Get Search Statistics
```bash
curl http://localhost:3001/api/solr/stats
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `400` - Bad request (missing required parameters)
- `500` - Internal server error

Error responses include detailed error messages:
```json
{
  "error": "Failed to search Solr",
  "details": "Connection refused"
}
```

## Integration with Frontend

The Solr search API can be integrated with the frontend search interface to provide:
- Real-time search suggestions
- Filtered search results
- Advanced search with multiple criteria
- Search result highlighting

## Performance Considerations

- Index operations are performed asynchronously
- Search queries support pagination for large result sets
- The index is optimized for both search speed and storage efficiency
- Regular commits ensure search results are up-to-date