# Start Backend Service
Write-Host "Starting Python FastAPI Backend..." -ForegroundColor Cyan

# Change to script directory
Set-Location $PSScriptRoot
Set-Location ..

# Navigate to backend directory
Set-Location backend

# Start the Python backend server
python main.py