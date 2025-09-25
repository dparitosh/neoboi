# NeoBoi - Integrated Knowledge Graph & Search Platform

A comprehensive document processing and knowledge graph application that seamlessly integrates **Apache Solr's inverted indexing**, **Neo4j's graph database and vector search**, and **offline LLM orchestration** for intelligent document analysis, contextual search, and conversational AI.

## ✅ Codebase Status

**🟢 CLEAN & READY** - Comprehensive code review completed on September 21, 2025
- ✅ All syntax errors fixed
- ✅ All import errors resolved  
- ✅ All Python files pass compilation
- ✅ All services import successfully
- ✅ No duplicate files found
- ✅ Ready for development and deployment

### Recent Fixes Applied
- Fixed Python syntax errors (await outside async function)
- Resolved import path issues across all modules
- Updated module imports to use proper relative paths
- Fixed test file issues and missing dependencies
- Cleaned up codebase with no remaining errors

---

## 🚀 Quick Start

For a full walkthrough with screenshots and troubleshooting tips, see [`INSTALLATION.md`](./INSTALLATION.md).

### Prerequisites
Before running NeoBoi, you need to set up the following services:

1. **Neo4j Aura** (Cloud Graph Database) - Version 5.17.0+
   - Create account at: https://neo4j.com/cloud/aura/
   - Free tier available for development
2. **Apache Solr** (Search Engine) - Version 9.4.1+
3. **Apache Tika** (Document Parser) - Version 2.9.1+
4. **Tesseract OCR** (Optical Character Recognition) - Version 5.3.0+
5. **Ollama** (Offline LLM) - Version 0.1.0+

### Installation

#### 1. Setup Neo4j Aura
1. Visit https://neo4j.com/cloud/aura/
2. Create a free account and new AuraDB instance
3. Note the connection URI, username, and password

#### 2. Install Required Services
Follow the detailed installation guides in `docs/installation/`:

- [Neo4j Aura Configuration](docs/installation/neo4j-installation.md)
- [Apache Solr Installation Guide](docs/installation/solr-installation.md)
- [Apache Tika Installation Guide](docs/installation/tika-installation.md)
- [Tesseract OCR Installation Guide](docs/installation/tesseract-installation.md)

#### 2. Clone and Prepare the Application
```powershell
git clone <repository-url>
cd neoboi
```

#### 3. Configure the Environment
```powershell
Copy-Item .env.example .env.local
# Then edit .env.local with your Neo4j/Solr/Tika/Ollama settings
```

#### 4. Run Setup Scripts (from the project root)
```powershell
# Verify prerequisites and external services
powershell -ExecutionPolicy Bypass -File .\scripts\services\setup-services.ps1

# Create or refresh the backend virtual environment (run in cmd.exe)
cmd /c scripts\services\setup-python-llm.bat

# Install frontend deps and remind to pull Ollama models (run in cmd.exe)
cmd /c scripts\services\setup-offline-llm.bat
```

#### 5. Start the Application
```powershell
# Start all services
powershell -ExecutionPolicy Bypass -File .\scripts\services\start-all.ps1

# Or start individually
powershell -ExecutionPolicy Bypass -File .\scripts\services\start-backend.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\services\start-frontend.ps1
```

## 📤 How to Upload Files

### Method 1: Direct Upload on Main Page (Recommended)
The main application page now includes integrated file upload functionality:

1. **Navigate to the main page:**
   ```
   http://localhost:3000
   ```

2. **Click "Upload Files" button** in the Knowledge Graph header
   - This expands a collapsible upload panel above the graph

3. **Upload Process:**
   - **Drag & Drop**: Drag files directly onto the upload area
   - **Click to Browse**: Click the upload area to select files manually
   - **Supported Formats**: PDF, DOCX, TXT, PNG, JPG, JPEG
   - **File Size Limit**: 50MB per file
   - **Batch Upload**: Upload multiple files simultaneously

4. **Real-time Processing:**
   - Files are processed using **Tika** for text extraction
   - Content is **chunked** and **embedded** for vector search
   - Data is stored in **Neo4j** with graph relationships
   - Files are indexed in **Solr** for keyword search
   - Graph automatically refreshes after upload completion

5. **Monitor Progress:**
   - Upload progress shown for each file
   - Processing status indicators
   - Success/error feedback
   - Automatic graph refresh when complete

### Method 2: Dedicated Upload Page
For advanced document management features:

1. **Navigate to the upload page:**
   ```
   http://localhost:3000/unstructured
   ```

2. **Use the comprehensive upload interface** with additional features:
   - Document search and analysis
   - Service status monitoring
   - File management tools

### What Happens After Upload

When you upload files, they go through this integrated pipeline:

1. **Text Extraction** (Tika Server)
   - Extracts text from PDFs, images, documents
   - Handles OCR for images using Tesseract

2. **Content Processing**
   - Splits documents into manageable chunks
   - Generates vector embeddings for semantic search

3. **Multi-System Indexing**
   - **Solr**: Creates inverted indexes for keyword search
   - **Neo4j**: Stores chunks with vector embeddings and graph relationships

4. **Graph Integration**
   - Neo4j creates knowledge graph from processed content
   - Links entities and relationships across documents

5. **Search Readiness**
   - Files become immediately searchable through:
     - **Unified Search**: `/api/search/integrated` endpoint
     - **Chat Interface**: Conversational queries
     - **Graph Exploration**: Visual relationship browsing

### Quick Upload Workflow
1. **Open main page** → Click "Upload Files"
2. **Drag/drop or select files** → Watch progress indicators
3. **Wait for processing** → Graph automatically updates
4. **Start chatting** → Ask questions about uploaded content
5. **Explore relationships** → Navigate the knowledge graph

## 📋 Integrated Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT INGESTION PIPELINE                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Apache Tika   │    │  Tesseract OCR  │    │   Text Chunking │ │
│  │ Document Parser │───►│   Image Text    │───►│  & Embeddings   │ │
│  │   Port: 9998    │    │   Extraction    │    │  (Neo4j Store)  │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SEARCH & GRAPH INTEGRATION                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Apache Solr   │    │     Neo4j       │    │   Offline LLM   │ │
│  │ Inverted Index  │◄──►│ Graph Database │◄──►│  Orchestration   │ │
│  │   Port: 8983    │    │  + Vector Search│    │   Port: 11434   │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Frontend      │    │   Backend       │    │   Chat & Search │ │
│  │   (React)       │◄──►│   (FastAPI)     │◄──►│   Interface      │ │
│  │   Port: 3000    │    │   Port: 3001    │    │                 │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

1. **Document Processing** → **Solr Indexing** → **Neo4j Graph Creation**
2. **User Query** → **LLM Understanding** → **Multi-System Search**
3. **Contextual Results** → **Graph Visualization** → **Conversational Responses**

### Component Integration

- **Solr**: Creates inverted indexes from unstructured pipeline (Tika + Tesseract)
- **Neo4j**: Uses Solr indexes for graph creation, stores structured data, provides vector similarity search
- **LLM**: Orchestrates search across both systems, provides contextual NLP responses
- **All Search Types**: Keyword (Solr), Semantic (Neo4j vectors), Hybrid (combined), Conversational (LLM)

### Success Metrics
- **Contextual Accuracy**: NLP queries return relevant results
- **Performance**: Sub-second response times across all search types
- **Consistency**: Unified experience across keyword, semantic, and conversational search

## 🔧 Configuration

## 🔧 Configuration

### Environment Variables (.env.local)
```env
# Neo4j Configuration (Supports both Aura Cloud and On-Premise)
# For Neo4j Aura (Cloud) - RECOMMENDED:
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# For On-Premise Neo4j (alternative):
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your_local_password
# NEO4J_DATABASE=neo4j

# Solr Configuration
SOLR_HOME="/path/to/solr"
SOLR_PORT="8983"
SOLR_BIN_PATH="/path/to/solr/bin"
SOLR_URL="http://localhost:8983/solr"
SOLR_COLLECTION="neoboi_graph"
SOLR_START_COMMAND="solr start"
SOLR_STOP_COMMAND="solr stop"
SOLR_STATUS_COMMAND="solr status"

# Service Ports
BACKEND_PORT="3001"
FRONTEND_PORT="3000"
TEST_SERVER_PORT="3002"

# External Services
OLLAMA_HOST="http://localhost:11434"
OLLAMA_DEFAULT_MODEL="llama2:7b"
OLLAMA_PATH="$env:USERPROFILE\AppData\Local\Programs\Ollama\ollama.exe"

TIKA_SERVER_URL="http://localhost:9998"

# CORS Configuration
CORS_ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"

# Logging
LOG_LEVEL="INFO"

# Development Settings
DEBUG="true"
ENVIRONMENT="development"
```

## 📁 Project Structure

```
neoboi/
├── docs/
│   └── installation/           # Service installation guides
├── scripts/
│   └── services/              # Service management scripts
├── backend/                   # Python FastAPI backend
│   ├── neo4j_service.py       # Neo4j Aura integration & GraphRAG
│   ├── solr_service.py        # Solr integration
│   ├── tika_service.py        # Tika integration
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend application
│   ├── src/
│   ├── public/
│   └── package.json
├── .env.local                # Environment configuration
└── README.md                 # This file
```

## 🚀 Service Management

### Start Services
```bash
# Start all services
.\scripts\services\start-all.ps1

# Start individual services
.\scripts\services\start-solr.ps1
.\scripts\services\start-backend.ps1
.\scripts\services\start-frontend.ps1
```

### Stop Services
```bash
# Stop all services
.\scripts\services\stop.ps1

# Stop individual services
.\scripts\services\stop-backend.ps1
.\scripts\services\stop-frontend.ps1
```

### Check Status
```bash
.\scripts\services\status.ps1
```

## 🔍 Key Features

### Integrated Multi-System Search
- **Solr Inverted Indexing**: Full-text search over unstructured content processed through Tika/Tesseract pipeline
- **Neo4j Graph Search**: Structured data mapping with unstructured content, vector similarity search
- **LLM Orchestration**: Intelligent query understanding and multi-system search coordination
- **Hybrid Search**: Combines keyword (Solr) + semantic (Neo4j) + conversational (LLM) approaches

### Document Processing Pipeline
1. **Upload**: Support for PDF, DOCX, images, and more
2. **OCR**: Extract text from images using Tesseract
3. **Parsing**: Extract metadata and content with Apache Tika
4. **Chunking**: Intelligent text chunking for optimal retrieval (1000 chars, 200 overlap)
5. **Embeddings**: Generate vector embeddings for semantic search
6. **Dual Indexing**: Store in both Solr (keyword) and Neo4j (vector/graph)
7. **Graph Creation**: Neo4j uses Solr-processed content to build knowledge graphs
8. **Search Integration**: LLM orchestrates search across all systems

### Intelligent Analysis
- **Entity Extraction**: Identify people, organizations, dates, locations
- **Relationship Mining**: Discover connections between entities
- **Topic Modeling**: Automatic categorization and clustering
- **Sentiment Analysis**: Understand document tone and context
- **Cross-Document Analysis**: Find patterns across multiple documents
- **GraphRAG**: Retrieval-Augmented Generation using Neo4j's vector capabilities

### AI-Powered Features
- **Offline LLM Integration**: Ollama-powered chat and analysis (no API costs)
- **Natural Language Queries**: Convert conversational queries to multi-system searches
- **Contextual Responses**: Graph-aware, conversationally appropriate replies
- **Intelligent Routing**: Automatic selection of optimal search strategy
- **Query Enhancement**: LLM improves search queries for better results

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd ../my-react-frontend
npm test
```

### Integration Testing
```bash
# Test end-to-end workflow
python backend/test_integration.py
```

## 📊 Monitoring

### Health Checks
- Frontend: http://localhost:3000
- Backend API: http://localhost:3001
- API Documentation: http://localhost:3001/docs
- Neo4j Aura Browser: https://your-instance.databases.neo4j.io/browser/
- Solr Admin: http://localhost:8983

### Logs
- Backend: `backend/logs/app.log`
- Neo4j Aura: Available in Neo4j Aura console/dashboard
- Solr: `%SOLR_HOME%\server\logs\solr.log`

## 🔒 Security

### Best Practices
- Change default passwords for all services
- Use HTTPS in production
- Implement proper authentication
- Regular security updates
- File upload validation
- Rate limiting

## 🐛 Troubleshooting

### Common Issues

#### Services Won't Start
1. Check if ports are available: `netstat -ano | findstr :PORT`
2. Verify environment variables in `.env.local`
3. Check service logs for error messages
4. Ensure Java is installed (required for Solr/Tika)

#### Neo4j Aura Connection Errors
1. Verify NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD in `.env.local`
2. Check Neo4j Aura instance is running and accessible
3. Ensure your IP is whitelisted in Neo4j Aura dashboard
4. Verify Neo4j Aura instance supports vector indexes (v5.17.0+)

#### Connection Errors
1. Verify service URLs in `.env.local`
2. Check firewall settings
3. Ensure services are running: `.\scripts\services\status.ps1`

#### OCR Issues
1. Verify Tesseract installation: `tesseract --version`
2. Check language data: `tesseract --list-langs`
3. Test with sample image

### Getting Help
1. Check the [Integration Guide](docs/installation/integration-guide.md)
2. Review service-specific installation guides
3. Check logs for detailed error messages
4. Verify all prerequisites are met

## 📚 Documentation

- [Integration Guide](docs/installation/integration-guide.md)
- [Neo4j Installation](docs/installation/neo4j-installation.md)
- [Solr Installation](docs/installation/solr-installation.md)
- [Tika Installation](docs/installation/tika-installation.md)
- [Tesseract Installation](docs/installation/tesseract-installation.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review the installation guides
- Check service documentation
- Open an issue on GitHub

---

**Note**: This application requires Neo4j Aura (cloud database), Apache Solr, Apache Tika, and Tesseract OCR. Please follow the installation guides in the `docs/installation/` directory before running the application. Neo4j Aura provides vector index support for GraphRAG functionality.