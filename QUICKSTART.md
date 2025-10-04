# NeoBoi Quick Start Guide

## ✅ Codebase Status

**🟢 CLEAN & READY** - Comprehensive code review completed on September 22, 2025
- ✅ All syntax errors fixed
- ✅ All import errors resolved
- ✅ All Python files pass compilation
- ✅ All services import successfully
- ✅ No duplicate files found
- ✅ Ready for development and deployment

---

## 🚀 Quick Service Management

### Start All Services
```bash
# From project root
powershell .\scripts\services\start-all.ps1
```

### Stop All Services
```bash
powershell .\scripts\services\stop.ps1
```

### Check Status
```bash
powershell .\scripts\services\status.ps1
```

## 📍 Service URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **API Docs**: http://localhost:3001/docs
- **Solr Admin**: http://localhost:8983

## � Prerequisites Check

Before running, ensure you have:

- [ ] Neo4j Aura account and instance running
- [ ] Apache Solr installed and running
- [ ] Apache Tika server running
- [ ] Tesseract OCR installed
- [ ] Ollama installed with models
- [ ] Python dependencies installed (`pip install -r backend/requirements.txt`)
- [ ] Node.js dependencies installed (`npm install` in frontend/)
- [ ] `.env.local` configured with your service credentials

## � Individual Service Control

### Frontend (Port 3000)
```bash
powershell .\scripts\services\start-frontend.ps1
powershell .\scripts\services\stop-frontend.ps1
```

### Backend (Port 3001)
```bash
powershell .\scripts\services\start-backend.ps1
powershell .\scripts\services\stop-backend.ps1
```

### Solr (Port 8983)
```bash
powershell .\scripts\services\start-solr.ps1
powershell .\scripts\services\stop-solr.ps1
```

## � Full Documentation

For complete installation and setup instructions, see:

- **[Complete Installation Guide](INSTALLATION.md)** - **START HERE FOR NEW INSTALLS**
- [Neo4j Setup](docs/installation/neo4j-installation.md)
- [Solr Setup](docs/installation/solr-installation.md)
- [Tika Setup](docs/installation/tika-installation.md)
- [Tesseract Setup](docs/installation/tesseract-installation.md)
- [Ollama Setup](docs/installation/ollama-installation.md)

## � Quick Troubleshooting

### Services Won't Start
```bash
# Check port conflicts
netstat -ano | findstr :3000
netstat -ano | findstr :3001
netstat -ano | findstr :8983

# Verify environment variables
type .env.local

# Check service status
powershell .\scripts\services\status.ps1
```

### Common Issues
- **Port already in use**: Kill process using the port
- **Environment not configured**: Check `.env.local` file
- **Dependencies missing**: Run `pip install -r backend/requirements.txt`
- **Services not running**: Start individual services first

## � Next Steps

1. **Verify Installation**: Check all services are running
2. **Upload Documents**: Use the upload feature on the main page
3. **Test Search**: Try keyword and semantic search
4. **Explore Graph**: Navigate relationships in the knowledge graph
5. **Use Chat**: Ask questions about your documents

For detailed documentation, see the [Complete Installation Guide](INSTALLATION.md).