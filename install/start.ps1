# Start Backend API Service Only
Write-Host "Starting Backend API Service..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot
Set-Location ..

# Start Backend Service
Write-Host "Starting Python FastAPI Backend..." -ForegroundColor Cyan
Set-Location backend
python main.py