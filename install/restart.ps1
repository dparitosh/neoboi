# Restart Neo4j Graph Visualization App
Write-Host "Restarting Neo4j Graph Visualization App..." -ForegroundColor Green
Write-Host ""

# Stop the server first
& "$PSScriptRoot\stop.ps1"

# Wait a moment for the server to fully stop
Start-Sleep -Seconds 3

# Start the server
& "$PSScriptRoot\start.ps1"