# Ollama Offline LLM Installation and Configuration Guide

## Overview
This guide provides complete instructions for installing and configuring Ollama, an offline Large Language Model (LLM) solution that integrates seamlessly with your NeoBoi application.

## What is Ollama?
Ollama is a tool that allows you to run large language models locally on your machine without requiring internet connectivity or cloud services. It supports various models like Llama, Mistral, and others.

## Prerequisites
- **OS**: Windows 10/11 (64-bit)
- **RAM**: Minimum 8GB, Recommended 16GB+ for larger models
- **Disk Space**: 5-20GB depending on model size
- **CPU**: Modern multi-core processor (Intel i5/AMD Ryzen or better)
- **GPU**: NVIDIA GPU with CUDA support (optional, improves performance)

## Installation Steps

### Step 1: Download Ollama
```batch
# Download from official website
# Visit: https://ollama.ai/download
# Download the Windows installer (.exe file)
```

### Step 2: Install Ollama
1. Run the downloaded installer (`OllamaSetup.exe`)
2. Follow the installation wizard
3. Choose installation directory (default is fine)
4. Complete the installation

### Step 3: Verify Installation
```batch
# Open Command Prompt or PowerShell
ollama --version
```

Expected output:
```
ollama version is 0.1.x
```

## Model Installation

### Step 4: Install Your First Model
```batch
# Install a lightweight model for testing
ollama pull llama2:7b

# Alternative smaller models
ollama pull mistral:7b
ollama pull phi:latest
ollama pull llama2:13b  # Larger model, requires more resources
```

### Step 5: List Available Models
```batch
# See all installed models
ollama list
```

### Step 6: Test the Model
```batch
# Test basic functionality
ollama run llama2:7b "Hello, how are you?"
```

## Configuration for NeoBoi

### Step 7: Configure Environment Variables
Add to your `.env.local` file:
```env
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2:7b
OLLAMA_TIMEOUT=60
OLLAMA_MAX_TOKENS=1000
OLLAMA_TEMPERATURE=0.7
```

### Step 8: Update Backend Configuration
The LLM service is already configured in your backend. Verify the settings in:
```python
# backend/unstructured_pipeline/llm_service.py
llm_service = OfflineLLMService(
    base_url="http://localhost:11434",
    model="llama2:7b"
)
```

## Service Integration

### Step 9: Start Ollama Service
```batch
# Start Ollama (runs in background)
ollama serve

# Or run it as a Windows service (recommended for production)
# Create a scheduled task or use NSSM (Non-Sucking Service Manager)
```

### Step 10: Test Integration
```python
# Test from Python
from backend.unstructured_pipeline.llm_service import OfflineLLMService

llm = OfflineLLMService()
print("Service available:", llm.is_service_available())
print("Available models:", llm.list_available_models())

# Test document analysis
result = llm.analyze_document("This is a test document about artificial intelligence.")
print("Analysis result:", result)
```

## Advanced Configuration

### Model Management

#### Install Multiple Models
```batch
# Install different models for different tasks
ollama pull llama2:7b          # General purpose
ollama pull codellama:7b       # Code generation
ollama pull mistral:7b         # Fast inference
ollama pull llama2:13b-chat    # Higher quality responses
```

#### Switch Between Models
```batch
# In your application code
llm = OfflineLLMService(model="mistral:7b")  # Use Mistral
# or
llm = OfflineLLMService(model="codellama:7b")  # Use Code Llama
```

### Performance Optimization

#### GPU Acceleration (NVIDIA)
```batch
# Ollama automatically detects and uses NVIDIA GPUs
# Verify GPU usage
nvidia-smi
```

#### Memory Management
```batch
# Monitor memory usage
# Keep models loaded for faster responses
ollama run llama2:7b  # This keeps the model in memory
```

### Custom Model Configuration
```python
# Advanced configuration in llm_service.py
llm_service = OfflineLLMService(
    base_url="http://localhost:11434",
    model="llama2:7b"
)

# Configure generation parameters
response = llm_service.generate_response(
    prompt="Analyze this document...",
    temperature=0.3,      # Lower = more focused
    max_tokens=1500       # Longer responses
)
```

## Integration with NeoBoi Services

### Document Analysis Integration
```python
# In your document processing pipeline
from unstructured_pipeline.llm_service import OfflineLLMService

llm = OfflineLLMService()

def analyze_document_with_llm(document_content):
    # Analyze document
    analysis = llm.analyze_document(document_content, "pdf")
    
    # Extract entities
    entities = llm.extract_entities_llm(document_content)
    
    # Classify document
    classification = llm.classify_document(document_content)
    
    return {
        'analysis': analysis,
        'entities': entities,
        'classification': classification
    }
```

### Search Query Enhancement
```python
# Enhance search queries with LLM
def enhance_search_query(natural_query):
    llm = OfflineLLMService()
    enhanced = llm.generate_search_query(natural_query)
    
    # Use enhanced query for Neo4j + Solr search
    search_results = neo4j_service.integrated_search(
        enhanced['search_params']['keywords']
    )
    
    return search_results
```

### Question Answering
```python
# Q&A functionality
def answer_document_question(question, document_content):
    llm = OfflineLLMService()
    answer = llm.answer_question(question, document_content)
    return answer
```

## API Endpoints

Your application already includes LLM endpoints:

### Analyze Document
```bash
POST /api/unstructured/analyze/{filename}
```

### Question Answering
```bash
POST /api/unstructured/qa
Content-Type: application/json
{
  "question": "What is the main topic?",
  "context_filename": "document.pdf"
}
```

### Enhanced Search
```bash
POST /api/unstructured/search
Content-Type: application/json
{
  "query": "artificial intelligence",
  "use_llm": true
}
```

## Monitoring and Troubleshooting

### Check Service Status
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check from application
curl http://localhost:3001/api/unstructured/status
```

### Common Issues

#### Model Download Issues
```batch
# Clear model cache and retry
ollama rm llama2:7b
ollama pull llama2:7b
```

#### Memory Issues
```batch
# Free up memory
ollama stop all

# Use smaller models
ollama pull phi:latest  # Very small model
```

#### Port Conflicts
```batch
# Change default port if 11434 is in use
set OLLAMA_HOST=0.0.0.0:11435
ollama serve
```

### Performance Monitoring
```batch
# Monitor resource usage
# Check Task Manager for CPU/GPU usage
# Monitor memory consumption

# View running models
ollama ps
```

## Production Deployment

### Windows Service Setup
```batch
# Using NSSM (Non-Sucking Service Manager)
# Download NSSM from https://nssm.cc/

# Install as service
nssm install Ollama "C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe" serve
nssm start Ollama
```

### Auto-start Configuration
```batch
# Add to Windows Startup
# Create shortcut to ollama serve in shell:startup
```

## Model Recommendations

### For Different Use Cases

#### General Document Analysis
```batch
ollama pull llama2:7b      # Balanced performance
ollama pull mistral:7b     # Fast responses
```

#### Code Analysis
```batch
ollama pull codellama:7b   # Code understanding
ollama pull llama2:13b     # Better code analysis
```

#### Lightweight/Testing
```batch
ollama pull phi:latest     # Very small, fast
ollama pull llama2:7b      # Good balance
```

## Backup and Recovery

### Model Backup
```batch
# Models are stored in:
# %USERPROFILE%\.ollama\models

# Backup the models directory
xcopy "%USERPROFILE%\.ollama\models" "C:\backups\ollama-models" /E /I /H /Y
```

### Configuration Backup
```batch
# Backup configuration
# Environment variables in .env.local
# Python configuration in llm_service.py
```

## Security Considerations

### Local Security
- Ollama runs locally, no external data exposure
- Models stay on your machine
- No internet required for inference

### Access Control
```python
# Implement access controls in your application
# Limit LLM usage per user/session
# Validate inputs to prevent prompt injection
```

## Cost Analysis

### Resource Requirements by Model

| Model | Size | RAM Required | Disk Space | Performance |
|-------|------|--------------|------------|-------------|
| phi:latest | ~2GB | 4GB | 2GB | Fast |
| llama2:7b | ~4GB | 8GB | 4GB | Good |
| mistral:7b | ~4GB | 8GB | 4GB | Fast |
| llama2:13b | ~7GB | 16GB | 7GB | Better |
| codellama:7b | ~4GB | 8GB | 4GB | Code-focused |

## Support and Resources

### Official Documentation
- [Ollama Documentation](https://github.com/jmorganca/ollama)
- [Model Library](https://ollama.ai/library)

### Community Resources
- [Ollama GitHub](https://github.com/jmorganca/ollama)
- [Hugging Face Models](https://huggingface.co/models)

### Troubleshooting
- Check logs: `ollama logs`
- Restart service: `ollama serve`
- Update Ollama: Download latest installer

## Quick Start Commands

```batch
# Install and start
ollama pull llama2:7b
ollama serve

# Test integration
curl -X POST http://localhost:3001/api/unstructured/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?", "context": "Artificial Intelligence is..."}'
```

This guide ensures your NeoBoi application has full offline LLM capabilities integrated with document processing, search, and analysis features.</content>
<parameter name="filePath">d:\Software\boiSoftware\neoboi\docs\installation\ollama-installation.md