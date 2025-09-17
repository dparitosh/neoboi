# Start Neo4j Graph Visualization App (Development Mode)
Write-Host "Starting Neo4j Graph Visualization App (Development Mode)..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot
Set-Location ..

# Start the Python backend server (Development Mode)
Write-Host "Starting Python FastAPI backend (Development Mode)..." -ForegroundColor Cyan
Set-Location backend
python main.py

Write-Host ""
Write-Host "Development server stopped." -ForegroundColor Yellow