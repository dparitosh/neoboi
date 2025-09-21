# Services Scripts Directory

This directory contains all the service management scripts for the Neo4j GraphRAG application.

## Core Service Scripts

### Start Services
- **`start-backend.ps1`** - Starts the Python FastAPI backend server (fixed version)
- **`start-frontend.ps1`** - Starts the React frontend application  
- **`start-neo4j.ps1`** - Neo4j database service management
- **`start-solr.ps1`** - Starts Apache Solr search engine
- **`start-all.ps1`** - Service launcher with instructions for all services

### Stop Services
- **`stop-backend.ps1`** - Stops the backend server
- **`stop-frontend.ps1`** - Stops the frontend application
- **`stop.ps1`** - General Node.js process stopper

### Service Management
- **`status.ps1`** - Comprehensive service status checker (improved version)
- **`restart.ps1`** - Service restart utilities
- **`service-utils.ps1`** - Shared utility functions for service management

### Setup Scripts
- **`setup-services.ps1`** - Service configuration and verification
- **`setup-offline-llm.bat`** - LLM setup for offline mode
- **`setup-python-llm.bat`** - Python LLM setup

### Specialized Services
- **`ollama-service.ps1`** - Ollama LLM service management
- **`start-frontend-only.ps1`** - Frontend-only startup option

## Usage

### Quick Start
1. Check service status: `.\scripts\services\status.ps1`
2. Start backend: `.\scripts\services\start-backend.ps1`
3. Start frontend: `.\scripts\services\start-frontend.ps1`

### Service URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:3001
- API Documentation: http://localhost:3001/docs
- Solr Admin: http://localhost:8983
- Neo4j Browser: http://localhost:7474

## Changes Made
- Removed broken/redundant scripts (`start.ps1`, `start-dev.ps1`, `run_backend.bat`, etc.)
- Fixed backend startup issues with proper uvicorn process management
- Added comprehensive service status checking
- Standardized utility functions for service management
- Consolidated environment variable handling

## Notes
- All scripts should be run from the project root directory
- Ensure `.env.local` is properly configured before starting services
- Use the status script to verify all services are running correctly