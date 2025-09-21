# NeoBoi Services Integration Guide

## Overview
This guide provides complete instructions for integrating Neo4j, Apache Solr, Apache Tika, and Tesseract OCR with the NeoBoi application.

## Prerequisites

### System Requirements
- **OS**: Windows 10/11
- **Java**: JDK 11+ (for Solr and Tika)
- **Python**: 3.9+ (for the application)
- **Node.js**: 16+ (for frontend)
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Disk**: 20GB+ free space

### Required Services
- Neo4j 5.20.0+
- Apache Solr 9.4.1+
- Apache Tika 2.9.1+
- Tesseract OCR 5.3.0+
- **Ollama (Offline LLM)**

## Installation Order

### 1. Install Java (Required for Solr and Tika)
```batch
# Download from: https://adoptium.net/
# Install JDK 11 or later
java -version
```

### 2. Install Neo4j
Follow: `docs/installation/neo4j-installation.md`

### 3. Install Apache Solr
Follow: `docs/installation/solr-installation.md`

### 4. Install Apache Tika
Follow: `docs/installation/tika-installation.md`

### 5. Install Tesseract OCR
Follow: `docs/installation/tesseract-installation.md`

### 6. Install Ollama (Offline LLM)
Follow: `docs/installation/ollama-installation.md`

## Environment Configuration

### Create .env.local File
```env
# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

# Search Configuration
SOLR_URL=http://localhost:8983/solr/neoboi
SOLR_CORE=neoboi

# Document Processing
TIKA_URL=http://localhost:9998
TIKA_TIMEOUT=300
TIKA_MAX_FILE_SIZE=100MB

# OCR Configuration
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
TESSERACT_DATA=C:\Program Files\Tesseract-OCR\tessdata
OCR_LANGUAGES=eng

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2:7b
OLLAMA_TIMEOUT=60
OLLAMA_MAX_TOKENS=1000
OLLAMA_TEMPERATURE=0.7

# Application Settings
NODE_ENV=development
PORT=3000
BACKEND_PORT=3001
```

## Service Startup Sequence

### 1. Start Neo4j
```batch
# Using Neo4j Desktop or
neo4j start
```

### 2. Start Apache Solr
```batch
solr start -c -p 8983
```

### 3. Start Apache Tika
```batch
java -jar "C:\tika\tika-app-2.9.1.jar" --server --host 0.0.0.0 --port 9998
```

### 4. Verify Tesseract
```batch
tesseract --version
```

### 5. Start Ollama
```batch
ollama serve
```

## Application Setup

### Install Dependencies
```batch
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../my-react-frontend
npm install
```

### Initialize Services
```batch
# From project root
# Run setup script (will configure services without downloading)
powershell .\scripts\services\setup-services.ps1
```

## Verification Tests

### Test Neo4j Connection
```python
from backend.neo4j_service import neo4j_service

async def test_neo4j():
    await neo4j_service.initialize_driver()
    result = await neo4j_service.execute_query("RETURN 'Hello Neo4j!' as message")
    print(result)
```

### Test Solr Connection
```python
from backend.solr_service import solr_service

async def test_solr():
    result = await solr_service.search("*:*", limit=1)
    print(f"Found {result['numFound']} documents")
```

### Test Tika Integration
```python
import requests

def test_tika():
    response = requests.get('http://localhost:9998/version')
    print(f"Tika version: {response.text}")
```

### Test Tesseract OCR
```python
import pytesseract
from PIL import Image

def test_tesseract():
    # Create a simple test image
    img = Image.new('RGB', (100, 30), color='white')
    text = pytesseract.image_to_string(img)
    print("Tesseract OCR working")
```

### Test Ollama LLM
```python
from backend.unstructured_pipeline.llm_service import OfflineLLMService

def test_ollama():
    llm = OfflineLLMService()
    print("Ollama available:", llm.is_service_available())
    print("Available models:", llm.list_available_models())
    
    # Test simple generation
    response = llm.generate_response("Hello, test message")
    print("LLM response:", response['response'][:100])
```

## Service Management Scripts

### Start All Services
```batch
# From scripts/services directory
.\start-all.ps1
```

### Stop All Services
```batch
.\stop-all.ps1
```

### Check Status
```batch
.\status.ps1
```

### Ollama Management
```batch
# Start Ollama service
ollama serve

# List running models
ollama ps

# Stop all models
ollama stop all

# Update Ollama
ollama pull latest
```

## Troubleshooting

### Service Port Conflicts
```batch
# Check if ports are in use
netstat -ano | findstr :7474  # Neo4j Browser
netstat -ano | findstr :7687  # Neo4j Bolt
netstat -ano | findstr :8983  # Solr
netstat -ano | findstr :9998  # Tika
```

### Common Issues

#### Neo4j Connection Issues
```cypher
# Test connection in Neo4j Browser
MATCH () RETURN count(*) as nodeCount
```

#### Solr Core Issues
```bash
# Recreate core if needed
solr delete -c neoboi
solr create -c neoboi
```

#### Tika Server Issues
```batch
# Check Java version
java -version

# Restart Tika server
taskkill /f /im java.exe
java -jar tika-app-2.9.1.jar --server --port 9998
```

#### Tesseract Issues
```batch
# Verify installation
tesseract --version
tesseract --list-langs

# Test with sample image
tesseract sample.png output -l eng
```

#### Ollama Issues
```batch
# Check if Ollama is running
ollama list

# Restart Ollama service
ollama serve

# Check available models
ollama pull llama2:7b

# Test model
ollama run llama2:7b "Test message"
```

## Performance Tuning

### Neo4j Configuration
```properties
# neo4j.conf
dbms.memory.heap.max_size=4G
dbms.memory.pagecache.size=2G
```

### Solr Configuration
```xml
<!-- solrconfig.xml -->
<query>
  <maxBooleanClauses>1024</maxBooleanClauses>
  <filterCache size="512" initialSize="512" autowarmCount="0"/>
</query>
```

### Tika Configuration
```batch
# Increase heap size
java -Xmx2g -Xms512m -jar tika-app-2.9.1.jar --server
```

## Monitoring

### Health Check Endpoints
- Neo4j: http://localhost:7474/browser
- Solr: http://localhost:8983/solr/admin/ping
- Tika: http://localhost:9998/version
- **Ollama: http://localhost:11434/api/tags**
- Application: http://localhost:3001/health

### Log Locations
- Neo4j: `%NEO4J_HOME%\logs\neo4j.log`
- Solr: `%SOLR_HOME%\server\logs\solr.log`
- Tika: Console output (redirect to file for persistence)
- Application: `backend/logs/app.log`

## Backup and Recovery

### Neo4j Backup
```batch
neo4j-admin database dump neo4j --to-path=C:\backups\neo4j.dump
```

### Solr Backup
```bash
# Backup core
solr backup -c neoboi -dir C:\backups\solr
```

### Configuration Backup
```batch
# Backup all configurations
xcopy "C:\neo4j\neo4j-community-5.20.0\conf" "C:\backups\neo4j-conf" /E /I /H /Y
xcopy "C:\solr\solr-9.4.1\server\solr\neoboi" "C:\backups\solr-core" /E /I /H /Y
```

## Security Considerations

### Network Security
- Bind services to localhost only in production
- Use HTTPS for external access
- Implement authentication and authorization

### File Upload Security
- Validate file types and sizes
- Scan for malware
- Implement rate limiting

### Data Protection
- Encrypt sensitive data at rest
- Use secure connections (SSL/TLS)
- Implement access controls

## Support and Resources

### Documentation Links
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Apache Solr Guide](https://solr.apache.org/guide/)
- [Apache Tika Wiki](https://cwiki.apache.org/confluence/display/TIKA/TikaServer)
- [Tesseract Documentation](https://tesseract-ocr.github.io/tessdoc/)

### Community Support
- Neo4j Community: https://community.neo4j.com/
- Apache Solr Users: https://solr.apache.org/community.html
- Tesseract Issues: https://github.com/tesseract-ocr/tesseract/issues

## Quick Reference

### Service URLs
- Neo4j Browser: http://localhost:7474
- Neo4j Bolt: bolt://localhost:7687
- Solr Admin: http://localhost:8983
- Tika Server: http://localhost:9998
- **Ollama API: http://localhost:11434**
- Application: http://localhost:3000
- API Docs: http://localhost:3001/docs

### Default Credentials
- Neo4j: neo4j / [set on first login]
- Solr: No authentication by default

This integration guide ensures all services work together seamlessly for the NeoBoi application.