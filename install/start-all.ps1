# Start All Services (Neo4j + Solr + Backend + Frontend)
Write-Host "Starting All Services (Neo4j + Solr + Backend + Frontend)..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot
Set-Location ..

# Function to start a service in background
function Start-ServiceInBackground {
    param([string]$serviceName, [string]$scriptPath)

    Write-Host "Starting $serviceName..." -ForegroundColor Cyan
    $job = Start-Job -ScriptBlock {
        param($path, $name)
        Set-Location $path
        & $path
    } -ArgumentList $scriptPath, $serviceName

    Write-Host "$serviceName started (Job ID: $($job.Id))" -ForegroundColor Green
    return $job
}

# Function to start Neo4j
function Start-Neo4jService {
    Write-Host "Starting Neo4j Database..." -ForegroundColor Cyan

    $neo4jPath = Get-ChildItem "C:\neo4j" -Directory | Select-Object -First 1 -ExpandProperty FullName
    if (!$neo4jPath) {
        Write-Host "Neo4j not found. Please run setup-services.ps1 first." -ForegroundColor Red
        return $null
    }

    $job = Start-Job -ScriptBlock {
        param($path)
        Set-Location $path
        & ".\bin\neo4j.bat" console
    } -ArgumentList $neo4jPath

    Write-Host "Neo4j Database started (Job ID: $($job.Id))" -ForegroundColor Green
    return $job
}

# Function to start Solr
function Start-SolrService {
    Write-Host "Starting Apache Solr..." -ForegroundColor Cyan

    $solrPath = Get-ChildItem "C:\solr" -Directory | Select-Object -First 1 -ExpandProperty FullName
    if (!$solrPath) {
        Write-Host "Solr not found. Please run setup-services.ps1 first." -ForegroundColor Red
        return $null
    }

    $job = Start-Job -ScriptBlock {
        param($path)
        Set-Location $path
        & ".\bin\solr.cmd" start
    } -ArgumentList $solrPath

    Write-Host "Apache Solr started (Job ID: $($job.Id))" -ForegroundColor Green
    return $job
}

# Start Neo4j Service
$neo4jJob = Start-Neo4jService

# Wait for Neo4j to initialize
Start-Sleep 10

# Start Solr Service
$solrJob = Start-SolrService

# Wait for Solr to initialize
Start-Sleep 5

# Start Backend Service
$backendJob = Start-ServiceInBackground "Python FastAPI Backend" ".\install\start-backend.ps1"

# Wait a moment for backend to initialize
Start-Sleep 3

# Start Frontend Service
$frontendJob = Start-ServiceInBackground "React Frontend" ".\install\start-frontend.ps1"

Write-Host ""
Write-Host "All services started!" -ForegroundColor Green
Write-Host "Neo4j Browser: http://localhost:7474" -ForegroundColor Cyan
Write-Host "Solr Admin: http://localhost:8983" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services..." -ForegroundColor Yellow

# Wait for user to stop
try {
    while ($true) {
        Start-Sleep 1
    }
} finally {
    Write-Host ""
    Write-Host "Stopping all services..." -ForegroundColor Yellow

    # Stop jobs
    if ($neo4jJob) { Stop-Job $neo4jJob -ErrorAction SilentlyContinue }
    if ($solrJob) { Stop-Job $solrJob -ErrorAction SilentlyContinue }
    if ($backendJob) { Stop-Job $backendJob -ErrorAction SilentlyContinue }
    if ($frontendJob) { Stop-Job $frontendJob -ErrorAction SilentlyContinue }

    # Run stop scripts
    & ".\install\stop-frontend.ps1"
    & ".\install\stop-backend.ps1"

    Write-Host "All services stopped." -ForegroundColor Green
}