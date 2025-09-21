# NeoBoi Installation & Deployment Guide

## 📦 Complete Installation Package

This guide provides a comprehensive, step-by-step installation and deployment process for the NeoBoi Knowledge Graph & Search Platform.

---

## 🎯 Quick Overview

**NeoBoi** is an integrated document processing and knowledge graph application that combines:
- **Apache Solr** for inverted indexing and search
- **Neo4j** for graph database and vector search
- **FastAPI backend** for API services
- **React frontend** for user interface
- **Document processing pipeline** with Tika, OCR, and LLM integration

### System Requirements
- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: 16GB minimum, 32GB recommended
- **Disk**: 50GB+ free space
- **CPU**: Multi-core processor (Intel i5/AMD Ryzen or better)
- **GPU**: NVIDIA GPU recommended for LLM acceleration

---

## 📋 Installation Checklist

### Phase 1: Prerequisites
- [ ] Java 11+ (for Solr and Tika)
- [ ] Python 3.9+ (for backend)
- [ ] Node.js 16+ (for frontend)
- [ ] Neo4j database (local or cloud)
- [ ] Git (for cloning repository)

### Phase 2: Core Services
- [ ] Apache Solr 9.4.1+
- [ ] Apache Tika 2.9.1+
- [ ] Tesseract OCR 5.3.0+
- [ ] Ollama (Offline LLM)

### Phase 3: Application Setup
- [ ] Clone NeoBoi repository
- [ ] Install Python dependencies
- [ ] Install Node.js dependencies
- [ ] Configure environment variables
- [ ] Initialize services

### Phase 4: Verification
- [ ] Test all services
- [ ] Verify integrations
- [ ] Run sample data

---

## 🚀 Step-by-Step Installation

### Phase 1: System Prerequisites

#### 1.1 Install Java (Required)
```bash
# Windows (Chocolatey)
choco install openjdk11

# macOS (Homebrew)
brew install openjdk@11

# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-11-jdk

# Verify installation
java -version
```

#### 1.2 Install Python 3.9+
```bash
# Windows (python.org or Microsoft Store)
# Download from: https://python.org/downloads/

# macOS (Homebrew)
brew install python@3.9

# Ubuntu/Debian
sudo apt install python3.9 python3.9-venv python3-pip

# Verify installation
python --version  # Should be 3.9+
pip --version
```

#### 1.3 Install Node.js 16+
```bash
# Windows (nodejs.org)
# Download LTS version from: https://nodejs.org/

# macOS (Homebrew)
brew install node@16

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should be 16+
npm --version
```

#### 1.4 Install Git
```bash
# Windows (git-scm.com)
# Download from: https://git-scm.com/download/win

# macOS (Homebrew)
brew install git

# Ubuntu/Debian
sudo apt install git

# Verify installation
git --version
```

### Phase 2: Install Core Services

#### 2.1 Neo4j Database Setup

**Option A: Neo4j Aura (Cloud - RECOMMENDED)**
1. Visit https://neo4j.com/cloud/aura/
2. Create free account and new AuraDB instance
3. Select region and instance type
4. Note connection details:
   - URI: `neo4j+s://xxxxx.databases.neo4j.io`
   - Username: `neo4j`
   - Password: Generated password

**Option B: Neo4j Desktop (Local)**
1. Download from: https://neo4j.com/download/
2. Install and create new local database
3. Start database with default settings
4. Note connection details:
   - URI: `bolt://localhost:7687`
   - Username: `neo4j`
   - Password: Set during installation

#### 2.2 Apache Solr Installation
```bash
# Download Solr 9.4.1+
# From: https://solr.apache.org/downloads.html

# Windows
# 1. Extract to C:\solr\solr-9.4.1
# 2. Set environment variables:
setx SOLR_HOME "C:\solr\solr-9.4.1"
setx PATH "%PATH%;C:\solr\solr-9.4.1\bin"

# macOS/Linux
# 1. Extract to /opt/solr-9.4.1
# 2. Set environment variables in ~/.bashrc or ~/.zshrc:
export SOLR_HOME="/opt/solr-9.4.1"
export PATH="$PATH:/opt/solr-9.4.1/bin"

# Start Solr
solr start -c -p 8983

# Create NeoBoi collection
solr create -c neoboi_graph
```

#### 2.3 Apache Tika Installation
```bash
# Download Tika server JAR
# From: https://tika.apache.org/download.html

# Windows
# 1. Download tika-app-2.9.1.jar
# 2. Place in C:\tika\tika-app-2.9.1.jar
# 3. Start server:
java -jar "C:\tika\tika-app-2.9.1.jar" --server --host 0.0.0.0 --port 9998

# macOS/Linux
# 1. Download to /opt/tika/tika-app-2.9.1.jar
# 2. Start server:
java -jar /opt/tika/tika-app-2.9.1.jar --server --host 0.0.0.0 --port 9998
```

#### 2.4 Tesseract OCR Installation
```bash
# Windows (Chocolatey)
choco install tesseract

# macOS (Homebrew)
brew install tesseract

# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-eng

# Download additional language data if needed
# English data is included by default

# Verify installation
tesseract --version
tesseract --list-langs
```

#### 2.5 Ollama (Offline LLM) Installation
```bash
# Download from: https://ollama.ai/download

# Windows/macOS: Run installer
# Linux: Follow installation instructions

# Install models
ollama pull llama2:7b      # General purpose model
ollama pull mistral:7b     # Fast inference model

# Start Ollama service
ollama serve

# Verify installation
curl http://localhost:11434/api/tags
```

### Phase 3: Application Setup

#### 3.1 Clone Repository
```bash
git clone <repository-url>
cd neoboi
```

#### 3.2 Install Python Dependencies
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3.3 Install Node.js Dependencies
```bash
cd ../frontend
npm install
cd ..
```

#### 3.4 Configure Environment Variables
Create `.env.local` file in project root:

```env
# Database Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_generated_password
NEO4J_DATABASE=neo4j

# Search Configuration
SOLR_URL=http://localhost:8983/solr/neoboi_graph
SOLR_CORE=neoboi_graph

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
FRONTEND_PORT=3000
BACKEND_PORT=3001
TEST_SERVER_PORT=3002

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001

# Logging
LOG_LEVEL=INFO

# Development Settings
DEBUG=true
ENVIRONMENT=development
```

#### 3.5 Initialize Services
```bash
# From project root

# Setup services (configure paths and create directories)
powershell .\scripts\services\setup-services.ps1

# Initialize Solr collection
powershell .\scripts\solr\init-solr-collection.bat
```

### Phase 4: Start and Verify Services

#### 4.1 Start All Services
```bash
# Option 1: Start all services at once
powershell .\scripts\services\start-all.ps1

# Option 2: Start services individually
powershell .\scripts\services\start-neo4j.ps1
powershell .\scripts\services\start-solr.ps1
powershell .\scripts\services\start-backend.ps1
powershell .\scripts\services\start-frontend.ps1
```

#### 4.2 Verify Service Status
```bash
# Check all services
powershell .\scripts\services\status.ps1

# Test individual services
curl http://localhost:3001/health          # Backend API
curl http://localhost:3000                 # Frontend
curl http://localhost:8983/solr/admin/ping # Solr
curl http://localhost:9998/version         # Tika
curl http://localhost:11434/api/tags       # Ollama
```

#### 4.3 Test Application Features
```bash
# Test backend API
curl http://localhost:3001/api/graph

# Test document upload (replace with actual file)
curl -X POST http://localhost:3001/api/unstructured/upload \
  -F "file=@sample.pdf"

# Test search functionality
curl "http://localhost:3001/api/unstructured/search?query=test"
```

---

## 🔧 Service Management

### Starting Services

#### Individual Services
```bash
# Neo4j (if using local instance)
.\scripts\services\start-neo4j.ps1

# Solr
.\scripts\services\start-solr.ps1

# Backend API
.\scripts\services\start-backend.ps1

# Frontend
.\scripts\services\start-frontend.ps1
```

#### All Services Together
```bash
.\scripts\services\start-all.ps1
```

### Stopping Services
```bash
# Individual services
.\scripts\services\stop-backend.ps1
.\scripts\services\stop-frontend.ps1

# All services
.\scripts\services\stop.ps1
```

### Checking Status
```bash
.\scripts\services\status.ps1
```

### Restarting Services
```bash
.\scripts\services\restart.ps1
```

---

## 🧪 Testing and Validation

### Service Health Checks

#### Backend API Tests
```bash
# Health check
curl http://localhost:3001/health

# Graph data
curl http://localhost:3001/api/graph

# Unstructured data status
curl http://localhost:3001/api/unstructured/status
```

#### Solr Tests
```bash
# Solr ping
curl http://localhost:8983/solr/neoboi_graph/admin/ping

# Collection info
curl http://localhost:8983/solr/admin/collections?action=LIST
```

#### Tika Tests
```bash
# Version check
curl http://localhost:9998/version

# Test document parsing
curl -X PUT -T sample.pdf \
  -H "Content-Type: application/pdf" \
  http://localhost:9998/tika
```

#### Ollama Tests
```bash
# List models
curl http://localhost:11434/api/tags

# Test generation
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama2:7b", "prompt": "Hello, test message"}'
```

### Integration Tests
```bash
# Run backend integration tests
cd backend
python -m pytest test_integration.py -v

# Test document processing pipeline
python test_unstructured_integration.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Port Conflicts
```bash
# Check port usage
netstat -ano | findstr :3000  # Frontend
netstat -ano | findstr :3001  # Backend
netstat -ano | findstr :8983  # Solr
netstat -ano | findstr :9998  # Tika
netstat -ano | findstr :11434 # Ollama

# Kill process using port (replace PID)
taskkill /PID <PID> /F
```

#### Service Won't Start

**Backend Issues:**
```bash
# Check Python environment
python --version
pip list | grep fastapi

# Check environment variables
type .env.local

# Test imports
cd backend
python -c "import fastapi, neo4j, requests"
```

**Frontend Issues:**
```bash
# Check Node.js
node --version
npm --version

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Solr Issues:**
```bash
# Check Java
java -version

# Check Solr home
echo %SOLR_HOME%

# Restart Solr
solr stop -all
solr start -c -p 8983
```

#### Database Connection Issues

**Neo4j Aura:**
```bash
# Test connection
curl -u neo4j:password https://your-instance.databases.neo4j.io/

# Check credentials in .env.local
```

**Local Neo4j:**
```bash
# Check if running
neo4j status

# Start if stopped
neo4j start
```

#### Document Processing Issues

**Tika Server:**
```bash
# Restart Tika
taskkill /f /im java.exe
java -jar tika-app-2.9.1.jar --server --port 9998
```

**Tesseract OCR:**
```bash
# Test OCR
tesseract --version
tesseract sample.png output -l eng
```

**Ollama:**
```bash
# Restart Ollama
ollama serve

# Check models
ollama list
```

### Log Locations

- **Backend**: Console output, check terminal
- **Frontend**: Browser dev console + terminal
- **Solr**: `%SOLR_HOME%\server\logs\solr.log`
- **Neo4j**: Neo4j admin interface or local logs
- **Tika**: Console output
- **Ollama**: Console output

### Performance Issues

#### Memory Problems
```bash
# Increase JVM memory for Solr
set SOLR_JAVA_MEM=-Xms2g -Xmx4g
solr restart

# Increase JVM memory for Tika
java -Xmx2g -jar tika-app-2.9.1.jar --server
```

#### Slow Document Processing
```bash
# Use smaller models for testing
ollama pull phi:latest  # Smaller, faster model

# Adjust processing parameters in config
TIKA_TIMEOUT=600  # Increase timeout
OLLAMA_MAX_TOKENS=500  # Reduce token limit
```

---

## 📚 Advanced Configuration

### Production Deployment

#### Environment Variables for Production
```env
NODE_ENV=production
DEBUG=false
LOG_LEVEL=WARNING

# Use production URLs
NEO4J_URI=neo4j+s://prod-instance.databases.neo4j.io
SOLR_URL=http://solr-prod:8983/solr/neoboi_graph
OLLAMA_BASE_URL=http://ollama-prod:11434

# Security
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

#### Service Management (Windows Service)
```batch
# Install services (requires NSSM or similar)
# Backend
nssm install NeoBoiBackend "python" "backend/main.py"
nssm start NeoBoiBackend

# Frontend
nssm install NeoBoiFrontend "npm" "start"
nssm set NeoBoiFrontend AppDirectory "frontend"
nssm start NeoBoiFrontend
```

#### Docker Deployment (Alternative)
```dockerfile
# Dockerfile for backend
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 3001
CMD ["python", "main.py"]
```

### Backup and Recovery

#### Database Backup
```bash
# Neo4j backup (Aura handles automatically)
# For local Neo4j:
neo4j-admin database dump neo4j --to-path=./backups/neo4j.dump

# Solr backup
curl "http://localhost:8983/solr/neoboi_graph/replication?command=backup&location=./backups"
```

#### Configuration Backup
```bash
# Backup entire config
xcopy config .\backups\config /E /I /H /Y
xcopy scripts .\backups\scripts /E /I /H /Y
```

### Monitoring and Maintenance

#### Health Monitoring
```bash
# Create monitoring script
# monitor-services.bat
@echo off
echo Checking service health...

curl -s http://localhost:3001/health >nul 2>&1
if %errorlevel% neq 0 echo Backend: DOWN else echo Backend: UP

curl -s http://localhost:8983/solr/admin/ping >nul 2>&1
if %errorlevel% neq 0 echo Solr: DOWN else echo Solr: UP

# Add more checks...
```

#### Log Rotation
```bash
# Configure log rotation for Solr
# Edit solrconfig.xml to add log rotation settings
```

---

## 📞 Support and Resources

### Documentation Links
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Apache Solr Guide](https://solr.apache.org/guide/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Ollama Documentation](https://github.com/jmorganca/ollama)

### Community Support
- Neo4j Community: https://community.neo4j.com/
- Apache Solr Users: https://solr.apache.org/community.html
- FastAPI Discord: https://discord.gg/VQjSZaeJmf

### Professional Services
For enterprise deployment and support:
- Neo4j Professional Services
- Apache Solr Consulting
- Custom development services

---

## ✅ Verification Checklist

After installation, verify everything works:

- [ ] Frontend loads at http://localhost:3000
- [ ] Backend responds at http://localhost:3001/health
- [ ] Solr admin at http://localhost:8983
- [ ] Tika server at http://localhost:9998/version
- [ ] Ollama at http://localhost:11434/api/tags
- [ ] Neo4j connection working
- [ ] Document upload functionality
- [ ] Search features working
- [ ] Graph visualization working

---

## 🎉 Success!

If all checks pass, your NeoBoi installation is complete and ready for use!

**Next Steps:**
1. Upload some documents to test the pipeline
2. Explore the graph visualization
3. Try the search and chat features
4. Customize configurations as needed

For questions or issues, refer to the troubleshooting section or check the detailed documentation in the `docs/` folder.</content>
<parameter name="filePath">d:\Software\boiSoftware\neoboi\INSTALLATION.md