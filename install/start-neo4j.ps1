# Start Neo4j Database Service
Write-Host "Starting Neo4j Database Service..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot
Set-Location ..

# Find Neo4j installation
$neo4jPath = Get-ChildItem "C:\neo4j" -Directory | Select-Object -First 1 -ExpandProperty FullName

if (!$neo4jPath) {
    Write-Host "Neo4j is not installed. Please run setup-services.ps1 first." -ForegroundColor Red
    exit 1
}

# Start Neo4j
Write-Host "Starting Neo4j from: $neo4jPath" -ForegroundColor Cyan
Set-Location $neo4jPath

# Start Neo4j in background
$neo4jJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    & ".\bin\neo4j.bat" console
} -ArgumentList $neo4jPath

Write-Host "Neo4j started (Job ID: $($neo4jJob.Id))" -ForegroundColor Green
Write-Host "Neo4j will be available at: http://localhost:7474 (Browser)" -ForegroundColor Cyan
Write-Host "Bolt protocol: localhost:7687" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop Neo4j..." -ForegroundColor Yellow

# Wait for user to stop
try {
    while ($true) {
        Start-Sleep 1
    }
} finally {
    Write-Host ""
    Write-Host "Stopping Neo4j..." -ForegroundColor Yellow
    Stop-Job $neo4jJob -ErrorAction SilentlyContinue
    Write-Host "Neo4j stopped." -ForegroundColor Green
}