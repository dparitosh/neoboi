# Fixed Backend Service Startup
Write-Host "Starting Python FastAPI Backend..." -ForegroundColor Cyan

# Get script directory and navigate to project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..\..") 
Set-Location $projectRoot

# Set PYTHONPATH to include the project root
$env:PYTHONPATH = $projectRoot.Path

# Navigate to backend directory
$backendDir = Join-Path $projectRoot "backend"
Set-Location $backendDir

# Verify main.py exists
if (!(Test-Path "main.py")) {
    Write-Host "Error: main.py not found in backend directory" -ForegroundColor Red
    exit 1
}

Write-Host "Starting uvicorn server..." -ForegroundColor Green
Write-Host "Project Root: $($projectRoot.Path)" -ForegroundColor Gray
Write-Host "Backend Dir: $backendDir" -ForegroundColor Gray
Write-Host "PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host ""

# Start the server and keep it running
try {
    & python -m uvicorn main:app --host 127.0.0.1 --port 3001 --log-level info --reload
} catch {
    Write-Host "Error starting backend: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Write-Host "Backend service stopped." -ForegroundColor Yellow
}