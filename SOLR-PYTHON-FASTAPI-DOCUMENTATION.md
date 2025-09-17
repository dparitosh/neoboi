# Solr Search and Query REST API - Python FastAPI Implementation

## Overview

All Solr search and query services are implemented entirely in **Python using FastAPI framework**. This provides a robust, scalable, and well-documented REST API for full-text search over Neo4j graph data.

## Architecture

### Core Components

1. **SolrService Class** (`solr_service.py`)
   - Pure Python implementation of Solr operations
   - Environment-based configuration
   - Comprehensive error handling and logging
   - Async/await support for non-blocking operations

2. **FastAPI Endpoints** (`routes.py`)
   - RESTful API design
   - Proper HTTP methods and status codes
   - Request/response validation using Pydantic
   - Comprehensive error responses

3. **Main Application** (`main.py`)
   - FastAPI application setup
   - CORS middleware configuration
   - Route inclusion and service initialization

## API Endpoints

### 1. Health Check
```http
GET /api/solr/health
```

**Purpose:** Check Solr service health and connectivity

**Response:**
```json
{
  "status": "healthy",
  "service": "solr-search-api",
  "implementation": "python-fastapi",
  "collection": "neoboi_graph",
  "solr_url": "http://localhost:8983/solr"
}
```

### 2. Index Statistics
```http
GET /api/solr/stats
```

**Purpose:** Get comprehensive statistics about the Solr index

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
  "solr_url": "http://localhost:8983",
  "implementation": "python-fastapi"
}
```

### 3. Index Graph Data
```http
POST /api/solr/index
```

**Purpose:** Index current Neo4j graph data into Solr for search

**Process:**
1. Fetches current graph data from Neo4j
2. Indexes all nodes and relationships
3. Returns indexing statistics

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

### 4. Search Indexed Data
```http
GET /api/solr/search?q={query}&type={type}&group={group}&limit={limit}&offset={offset}
```

**Purpose:** Search indexed data with advanced filtering and pagination

**Query Parameters:**
- `q` (required): Search query string
- `type` (optional): Filter by type (`node` or `relationship`)
- `group` (optional): Filter by node group
- `limit` (optional): Maximum results (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Examples:**
```bash
# Basic search
GET /api/solr/search?q=supplier

# Filtered search
GET /api/solr/search?q=manufacturer&type=node

# Paginated search
GET /api/solr/search?q=test&limit=10&offset=20
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
  "offset": 0,
  "search_engine": "solr",
  "implementation": "python-fastapi"
}
```

### 5. Clear Index
```http
POST /api/solr/clear
```

**Purpose:** Clear all documents from the Solr search index

**Response:**
```json
{
  "message": "Successfully cleared Solr index",
  "status": "completed",
  "implementation": "python-fastapi"
}
```

## Python Implementation Details

### SolrService Class

```python
class SolrService:
    def __init__(self, solr_url: str = None, collection: str = None):
        # Environment-based configuration
        self.solr_url = solr_url or os.getenv("SOLR_URL", "http://localhost:8983/solr")
        self.collection = collection or os.getenv("SOLR_COLLECTION", "neoboi_graph")
        self.base_url = f"{self.solr_url}/{self.collection}"

    async def index_graph_data(self, graph_data: Dict[str, Any]) -> Dict[str, int]:
        """Index all nodes and relationships from graph data"""

    async def search(self, query: str, filters: Optional[Dict[str, Any]] = None,
                    limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search the indexed data"""

    async def clear_index(self) -> bool:
        """Clear all documents from the index"""

    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Solr index"""
```

### FastAPI Route Implementation

```python
@solr_router.get("/search")
async def search_solr(
    q: str = Query(..., description="Search query string"),
    type: Optional[str] = Query(None, description="Filter by type"),
    group: Optional[str] = Query(None, description="Filter by node group"),
    limit: int = Query(20, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination")
):
    # Implementation using SolrService
    result = await solr_service.search(q, filters, limit, offset)
    return formatted_response
```

## Configuration

### Environment Variables

```bash
# Solr Configuration
SOLR_HOME="D:\Software\solr-9.9.0"
SOLR_PORT="8983"
SOLR_BIN_PATH="D:\Software\solr-9.9.0\bin"
SOLR_URL="http://localhost:8983/solr"
SOLR_COLLECTION="neoboi_graph"
```

### Service Integration

The Solr API is fully integrated with the main FastAPI application:

```python
# main.py
from routes import router  # Includes all Solr endpoints
app.include_router(router, prefix="/api", tags=["api"])
```

## Features

### Full-Text Search
- Searches across all indexed content
- Supports fuzzy matching and partial matches
- Case-insensitive search

### Advanced Filtering
- Filter by document type (node/relationship)
- Filter by node group
- Filter by specific property values
- Multiple filter combinations

### Pagination
- Configurable result limits
- Offset-based pagination
- Total count reporting

### Index Management
- Automatic indexing of Neo4j graph data
- Index clearing and resetting
- Real-time statistics and health monitoring

### Error Handling
- Comprehensive error responses
- Detailed logging for debugging
- Graceful degradation on service failures

## Testing

### Run API Tests

```bash
# From backend directory
python test_solr_api.py
```

### Manual Testing

```bash
# Health check
curl http://localhost:3001/api/solr/health

# Get statistics
curl http://localhost:3001/api/solr/stats

# Index data
curl -X POST http://localhost:3001/api/solr/index

# Search
curl "http://localhost:3001/api/solr/search?q=test"
```

## Performance Considerations

- **Async Operations:** All Solr operations use async/await for non-blocking I/O
- **Connection Pooling:** HTTP requests use connection pooling for efficiency
- **Pagination:** Large result sets are paginated to prevent memory issues
- **Indexing Optimization:** Batch processing for large datasets
- **Caching:** Consider implementing response caching for frequently accessed data

## Security

- Input validation on all endpoints
- Proper error message sanitization
- CORS configuration for cross-origin requests
- Environment variable protection for sensitive configuration

## Monitoring

- Comprehensive logging for all operations
- Health check endpoints for service monitoring
- Statistics endpoints for performance monitoring
- Error tracking and reporting

## Future Enhancements

- **Authentication:** Add API key or token-based authentication
- **Rate Limiting:** Implement request rate limiting
- **Caching:** Add Redis caching for search results
- **Analytics:** Add search analytics and usage tracking
- **Advanced Queries:** Support for complex boolean queries
- **Relevance Scoring:** Implement custom scoring algorithms