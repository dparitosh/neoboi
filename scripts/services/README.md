# Services Scripts Directory

This folder contains automation for setting up and running NeoBoi on Windows. Run every command from the repository root (`neoboi\`).

## 🚀 First-Time Setup Flow

1. **Verify prerequisites and external services**  
	```powershell
	powershell -ExecutionPolicy Bypass -File .\scripts\services\setup-services.ps1
	```
	The guided check confirms Python/Node/Java/Ollama availability, highlights missing tools, and validates Solr/Tika/Tesseract paths.

2. **Prepare the backend Python environment**  
	```cmd
	scripts\services\setup-python-llm.bat
	```
	Creates or updates `backend\venv`, installs `requirements.txt`, and verifies core packages can be imported.

3. **Install Ollama models and frontend dependencies**  
	```cmd
	scripts\services\setup-offline-llm.bat
	```
	Runs `npm install` from `frontend\` and reminds you to pull the required Ollama models (for example `ollama pull llama2`).

4. **Configure environment variables**  
	Copy `.env.example` to `.env.local`, then fill in Neo4j, Solr, Tika, and Ollama values. Re-run the setup script to confirm everything is detected.

When each step reports success, use the start scripts below to launch the platform.

## 🔁 Day-to-Day Operations

- Start everything:  
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\services\start-all.ps1
  ```
- Stop services: `powershell -ExecutionPolicy Bypass -File .\scripts\services\stop.ps1`
- Check status: `powershell -ExecutionPolicy Bypass -File .\scripts\services\status.ps1`
- Restart backend/frontend: `powershell -ExecutionPolicy Bypass -File .\scripts\services\restart.ps1`

## 📜 Script Catalogue

### Startup
- `start-all.ps1` – Launches Solr, backend, and frontend in the recommended order
- `start-backend.ps1` – Runs the FastAPI backend via Uvicorn
- `start-frontend.ps1` / `start-frontend-only.ps1` – Starts the React/Express UI
- `start-solr.ps1` – Boots Solr using the configured `SOLR_HOME`
- `start-neo4j.ps1` – Helper for local Neo4j Desktop installs

### Shutdown & Monitoring
- `stop.ps1`, `stop-backend.ps1`, `stop-frontend.ps1` – Graceful shutdown helpers
- `status.ps1` – Aggregated health/status check
- `restart.ps1` – Convenience wrapper to recycle backend/frontend

### Setup Utilities
- `setup-services.ps1` – Guided prerequisite and service verification
- `setup-python-llm.bat` – Backend virtual environment bootstrap
- `setup-offline-llm.bat` – Frontend dependencies and Ollama reminders
- `ollama-service.ps1` – Optional helper to run Ollama as a Windows service
- `service-utils.ps1` – Shared helper functions consumed by other scripts

## 🔗 Helpful URLs
- Frontend UI: http://localhost:3000
- Backend API docs: http://localhost:3001/docs
- Solr Admin: http://localhost:8983
- Neo4j Browser: http://localhost:7474

## ✅ Tips
- Run PowerShell scripts with `-ExecutionPolicy Bypass` or add the folder to your trusted locations.
- Use `cmd.exe` for `.bat` helpers so that `where`, `npm`, and `python` behave consistently.
- Re-run the setup scripts whenever you install new tooling or update dependencies—they are idempotent and will simply report what still needs attention.