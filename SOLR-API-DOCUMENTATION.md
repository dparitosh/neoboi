# Solr Search and Query REST API

This document describes the Solr search and query REST API endpoints available in the Neo4j Graph Visualization application.

## Overview

The application integrates Apache Solr for full-text search and advanced querying capabilities over the Neo4j graph data. The API provides endpoints for indexing, searching, and managing the search index.

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

## Data Structure

### Indexed Documents

Each document in the Solr index represents either a node or relationship from the Neo4j graph:

#### Node Documents
```json
{
  "id": "node_123",
  "type": "node",
  "neo4j_id": "123",
  "label": "Person",
  "group": "person",
  "properties": "{\"name\":\"John Doe\",\"age\":30}",
  "content": "Person John Doe age:30",
  "prop_name": "John Doe",
  "prop_age": 30
}
```

#### Relationship Documents
```json
{
  "id": "edge_456",
  "type": "relationship",
  "neo4j_id": "456",
  "label": "WORKS_FOR",
  "source": "123",
  "target": "789",
  "properties": "{\"since\":\"2020\"}",
  "content": "WORKS_FOR since:2020",
  "prop_since": "2020"
}
```

## Search Features

### Full-Text Search
- Searches across all text content in nodes and relationships
- Supports fuzzy matching and partial matches
- Case-insensitive search

### Filtering
- Filter by document type (`node` or `relationship`)
- Filter by node group
- Filter by specific property values

### Faceting
- All properties are indexed as individual fields for precise filtering
- Support for range queries on numeric properties
- Date/time property support

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