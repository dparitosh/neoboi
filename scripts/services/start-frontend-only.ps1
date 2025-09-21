# Start Frontend Service Independently
Write-Host "Starting Frontend Service (Independent Mode)..." -ForegroundColor Green
Write-Host "Note: This will work even if backend is not running" -ForegroundColor Yellow
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot
Set-Location ..\..

# Navigate to frontend directory
Set-Location frontend

# Check if Node.js is installed
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Install dependencies if node_modules doesn't exist
if (!(Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the frontend server
Write-Host "🚀 Starting frontend server on port 3000..." -ForegroundColor Green
Write-Host "📊 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔗 Backend API: Will proxy to http://localhost:3001 (if available)" -ForegroundColor Cyan
Write-Host ""
npm start