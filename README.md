# Neo4j Graph Visualization App

A modern web application for visualizing Neo4j graph databases with Apache Solr search integration and separate microservices architecture.

## Architecture

This application consists of four separate services:

- **Frontend Service** (Port 3000): React-based web interface with Express server
- **Backend API Service** (Port 3001): Python FastAPI server with Neo4j integration
- **Apache Solr** (Port 8983): Search engine for graph data indexing
- **Neo4j Database** (Port 7687): Graph database (local or cloud)

**🔥 All Solr search and query services are implemented in Python using FastAPI framework.**

## Quick Start

### Prerequisites

- Node.js 16+ (for frontend service)
- Python 3.8+ (for backend service)
- Java 11+ (for Apache Solr)
- Neo4j database (local or cloud instance)

### Installation

1. **Install Dependencies:**
   ```bash
   # Frontend dependencies
   cd frontend
   npm install

   # Backend dependencies (already configured)
   cd ../backend
   pip install -r requirements.txt
   ```

2. **Start Services Independently:**

   **Option A: Start Frontend Only**
   ```bash
   cd frontend
   npm start
   # Frontend will be available at http://localhost:3000
   ```

   **Option B: Start Backend Only**
   ```bash
   ./install/start.ps1
   # Backend API will be available at http://localhost:3001
   ```

   **Option C: Start Both Services**
   ```bash
   ./install/start-all.ps1
   # Frontend: http://localhost:3000
   # Backend: http://localhost:3001
   ```

3. **Access the Application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001
   - Solr Admin: http://localhost:8983

## Service Management

### Individual Services

**Frontend Service (Port 3000):**
```bash
# Start frontend only
cd frontend
npm start

# Or use the script
./install/start-frontend.ps1
```

**Backend API Service (Port 3001):**
```bash
# Start backend only
./install/start.ps1

# Or directly
cd backend
python main.py
```

**Solr Search Service (Port 8983):**
```bash
# Start Solr service
./start-solr.bat

# Stop Solr service
./stop-solr.bat

# Check Solr status
./status-solr.bat

# Unified management
./solr-service.bat start
./solr-service.bat stop
./solr-service.bat status
./solr-service.bat restart
```

### Start All Services Together

If you want to start both services together:
```bash
./install/start-all.ps1  # PowerShell
start-all.bat           # Windows Batch
```

### Check Status

```bash
# Check all services
./install/status.ps1
./install/status.bat

# Test all services including Solr API
./test-services.bat

# Test Solr API specifically
./test-solr-api.bat
```

### Initialize Solr Collection

Before using Solr search features, initialize the collection:
```bash
./init-solr-collection.bat
```

## Configuration

### Environment Variables

Create a `.env.local` file in the root directory:

```bash
# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# Service Configuration
FRONTEND_PORT=3000
BACKEND_URL=http://localhost:3001

# Solr Configuration
SOLR_HOME="D:\Software\solr-9.9.0"
SOLR_PORT="8983"
SOLR_BIN_PATH="D:\Software\solr-9.9.0\bin"
SOLR_URL="http://localhost:8983/solr"
SOLR_COLLECTION="neoboi_graph"
SOLR_START_COMMAND="cmd /c solr.cmd start"
SOLR_STOP_COMMAND="cmd /c solr.cmd stop"
SOLR_STATUS_COMMAND="cmd /c solr.cmd status"
```

### Service Ports

- Frontend: 3000 (configurable via FRONTEND_PORT)
- Backend: 3001 (configurable via PORT)
- Solr: 8983 (configurable via SOLR_PORT)
- Neo4j: 7687 (default)

## Features

- **Interactive Graph Visualization:** Using Cytoscape.js with modern React
- **Real-time Search:** Apache Solr integration for full-text search
- **Natural Language Queries:** AI-powered Cypher query generation
- **Microservices Architecture:** Separate, independently scalable services
- **Professional UI:** Clean, responsive design
- **RESTful API:** Well-documented endpoints
- **Health Monitoring:** Built-in service health checks

## API Documentation

### Backend Endpoints

**Graph Operations:**
- `GET /health` - Service health check
- `GET /api/graph` - Get graph data from Neo4j
- `GET /api/graph/all` - Get expanded graph data
- `GET /api/graph/expand/:nodeId` - Expand graph from specific node
- `GET /api/graph/search` - Search graph with filters

**Solr Search Operations:**
- `GET /api/solr/stats` - Get Solr index statistics
- `POST /api/solr/index` - Index current graph data into Solr
- `GET /api/solr/search` - Search indexed data with filters
- `POST /api/solr/clear` - Clear Solr index

**Query Operations:**
- `POST /api/chat` - Process natural language queries
- `POST /api/query` - Execute custom Cypher queries

### Solr Search API Examples

```bash
# Index current graph data
curl -X POST http://localhost:3001/api/solr/index

# Search for suppliers
curl "http://localhost:3001/api/solr/search?q=supplier&type=node"

# Search with pagination
curl "http://localhost:3001/api/solr/search?q=test&limit=10&offset=0"

# Get search statistics
curl http://localhost:3001/api/solr/stats

# Clear search index
curl -X POST http://localhost:3001/api/solr/clear
```

### Frontend Features

- Interactive graph visualization with Cytoscape.js
- Real-time search with Apache Solr
- Natural language query processing
- Node expansion and relationship exploration
- Responsive design for all devices

## Project Structure

```
neoboi/
├── backend/              # Python FastAPI backend service
│   ├── main.py          # Main FastAPI application
│   ├── routes.py        # API endpoints
│   ├── neo4j_service.py # Neo4j database integration
│   ├── solr_service.py  # Apache Solr integration
│   └── requirements.txt # Python dependencies
├── frontend/             # React frontend service
│   ├── server.js        # Express server for frontend
│   ├── static/          # Static assets (JS, CSS)
│   ├── templates/       # HTML templates
│   └── package.json     # Node.js dependencies
├── install/              # Service management scripts
│   ├── start*.ps1/bat   # Start scripts for all services
│   ├── stop*.ps1/bat    # Stop scripts for all services
│   ├── status*.ps1/bat  # Status checking scripts
│   └── restart*.ps1/bat # Restart scripts
├── start-solr.bat       # Start Solr service
├── stop-solr.bat        # Stop Solr service
├── status-solr.bat      # Check Solr status
├── restart-solr.bat     # Restart Solr service
├── solr-service.bat     # Unified Solr management
├── init-solr-collection.bat # Initialize Solr collection
├── test-solr-api.bat    # Test Solr API endpoints
├── test-services.bat    # General service health check
├── solr-api-examples.bat # Interactive Solr API examples
├── SOLR-README.md       # Solr service management guide
├── SOLR-API-DOCUMENTATION.md # Complete Solr API documentation
└── .env.local           # Environment configuration
```

## Troubleshooting

### Common Issues

1. **Port Conflicts:**
   - Check if ports 3000, 3001, 8983 are available
   - Use `netstat -ano | findstr :PORT` to check port usage

2. **Service Won't Start:**
   - Ensure all dependencies are installed
   - Check environment variables in `.env.local`
   - Review service logs

3. **Neo4j Connection Issues:**
   - Verify Neo4j credentials in `.env.local`
   - Ensure Neo4j is running and accessible
   - Check network connectivity for cloud instances

4. **Solr Issues:**
   - **Solr won't start:** Ensure Java 11+ is installed and in PATH
   - **Collection not found:** Run `./init-solr-collection.bat` to create the collection
   - **Search not working:** Ensure data is indexed using `/api/solr/index`
   - **Connection refused:** Verify Solr is running on port 8983
   - **Indexing fails:** Check Neo4j connectivity and data availability

### Service Logs

- Backend logs: Console output when starting backend service
- Frontend logs: Browser developer console + server console
- Solr logs: `solr/server/logs/solr.log`
- Neo4j logs: Neo4j admin interface

### Solr-Specific Troubleshooting

```bash
# Check Solr status
./status-solr.bat

# Initialize collection if missing
./init-solr-collection.bat

# Test Solr API endpoints
./test-solr-api.bat

# View Solr admin interface
# Open: http://localhost:8983
```

### Environment Variable Issues

If services fail to start due to environment variables:
1. Verify `.env.local` exists in the root directory
2. Check that all required variables are set
3. Ensure no extra spaces or quotes in variable values
4. Restart services after changing environment variables

## Development

### Adding New Features

1. **Backend Features:**
   - Add routes in `backend/routes.py`
   - Implement business logic in service files
   - Update dependencies in `backend/requirements.txt`

2. **Frontend Features:**
   - Modify `frontend/static/app-simple.js`
   - Update HTML in `frontend/templates/index.html`
   - Add dependencies to `frontend/package.json`

3. **Service Scripts:**
   - Update scripts in `install/` directory
   - Test on both Windows (PowerShell/Batch) and Unix systems

### Environment Setup

Create a `.env.local` file in the root directory:

```bash
# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# Frontend Configuration
FRONTEND_PORT=3000
BACKEND_URL=http://localhost:3001
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test all services using `./install/status.ps1`
5. Submit a pull request

## License

MIT License - see LICENSE file for details