# Navigate to project root
Set-Location "d:\Software\boiSoftware\neoboi"

# Set Python path to include both project root and backend directory
$env:PYTHONPATH = "d:\Software\boiSoftware\neoboi;d:\Software\boiSoftware\neoboi\backend"

# Start the backend service
Write-Host "Starting Backend Service on port 3001..."
Write-Host "Backend will be available at http://localhost:3001"
Write-Host "Press Ctrl+C to stop the service"

python -m uvicorn backend.main:app --host 0.0.0.0 --port 3001