# NeoBoi Installation Guide

This document walks you through the recommended end-to-end setup for a fresh NeoBoi environment on Windows. The helper scripts assume you are using PowerShell (`powershell.exe`) for `.ps1` files and `cmd.exe` for `.bat` files.

> **Tip:** Every command below is meant to be run from the project root folder (`neoboi\`).

## 1. Install Prerequisites

| Tool | Minimum Version | Notes |
| ---- | --------------- | ----- |
| Python | 3.9+ | Install from [python.org](https://www.python.org/downloads/) with the "Add to PATH" option.
| Node.js | 16+ | Install the LTS release from [nodejs.org](https://nodejs.org/).
| Git | Latest | Used to clone the repository.
| Java JDK | 11+ | Required for Apache Solr and Tika. AdoptOpenJDK/OpenJDK works fine.
| Ollama *(optional)* | Latest | Provides offline LLM support. Download from [ollama.ai](https://ollama.ai/download).
| Neo4j Aura or Desktop | 5.17+ | Aura is recommended; Desktop works for local testing.

After installation, you can verify the core CLI tooling quickly:

```powershell
python --version
pip --version
node --version
npm --version
java -version
ollama --version   # optional, only if you installed Ollama
```

## 2. Clone the Repository

```powershell
git clone <REPOSITORY_URL>
cd neoboi
```

## 3. Configure Environment Variables

1. Copy the sample environment file:
   ```powershell
   Copy-Item .env.example .env.local
   ```
2. Fill in the values for Neo4j, Solr, Tika, Ollama, and any custom ports. The setup script will validate the entries later.

## 4. Run the Guided Setup Scripts

1. **Check prerequisites and external services**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\services\setup-services.ps1
   ```
   This script verifies CLI tools, confirms `.env.local` exists, and checks for Solr/Tika/Tesseract installations.

2. **Create/refresh the backend virtual environment**
   ```cmd
   scripts\services\setup-python-llm.bat
   ```
   Installs backend dependencies inside `backend\venv` and performs a lightweight import test.

3. **Install frontend dependencies and pull Ollama models**
   ```cmd
   scripts\services\setup-offline-llm.bat
   ```
   Runs `npm install` from `frontend\` and reminds you to execute model pulls such as `ollama pull llama2`.

Re-run any script at any time—they are idempotent and will only report what still needs attention.

## 5. Start the Platform

You can launch every component with a single command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\services\start-all.ps1
```

Or start services individually (each command in its own PowerShell window):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\services\start-solr.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\services\start-backend.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\services\start-frontend.ps1
```

## 6. Validate the Installation

Run these quick checks to confirm everything is online:

```powershell
# Backend health
Invoke-RestMethod http://localhost:3001/health

# Solr ping
Invoke-RestMethod "http://localhost:8983/solr/admin/ping"

# Optional: confirm Ollama models
curl http://localhost:11434/api/tags
```

Visit the UIs in your browser:

- Frontend: http://localhost:3000
- Backend docs: http://localhost:3001/docs
- Solr Admin: http://localhost:8983
- Neo4j Aura Browser or Desktop UI (depending on your deployment)

## 7. Next Steps

- Upload sample documents via the frontend to trigger the processing pipeline.
- Explore the knowledge graph and integrated chat features.
- Review the detailed guides in `docs/installation/` for service-specific configuration and production tips.

If you run into issues, re-run the setup scripts—they will highlight whatever is missing or misconfigured.
