# Start Frontend Service
Write-Host "Starting Frontend Service..." -ForegroundColor Cyan

# Change to script directory
Set-Location $PSScriptRoot
Set-Location ..

# Check if Node.js is installed
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Navigate to frontend directory
Set-Location frontend

# Install dependencies if node_modules doesn't exist
if (!(Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the frontend server
Write-Host "🚀 Starting frontend server on port 3000..." -ForegroundColor Green
npm start