# Check status of all Neo4j Graph Visualization services
Write-Host "Checking Neo4j Graph Visualization Services Status..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot
Set-Location ..

# Function to check service status
function Check-ServiceStatus {
    param([string]$name, [string]$url, [int]$port)

    Write-Host "Checking $name..." -ForegroundColor Cyan -NoNewline

    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 5
        Write-Host " RUNNING (Port: $port, Status: $($response.StatusCode))" -ForegroundColor Green
        return $true
    } catch {
        Write-Host " NOT RUNNING (Port: $port)" -ForegroundColor Red
        return $false
    }
}

# Check Frontend Service
$frontendStatus = Check-ServiceStatus "Frontend Service" "http://localhost:3000/health" 3000

# Check Backend API Service
$backendStatus = Check-ServiceStatus "Backend API Service" "http://localhost:3001/health" 3001

# Check Apache Solr
$solrStatus = Check-ServiceStatus "Apache Solr" "http://localhost:8983/solr/admin/cores" 8983

# Check Neo4j (if accessible)
Write-Host "Checking Neo4j Database..." -ForegroundColor Cyan -NoNewline
try {
    # This would require Neo4j credentials, so we'll just check if the port is open
    $neo4jConnection = Test-NetConnection -ComputerName "localhost" -Port 7687 -WarningAction SilentlyContinue
    if ($neo4jConnection.TcpTestSucceeded) {
        Write-Host " RUNNING (Port: 7687)" -ForegroundColor Green
        $neo4jStatus = $true
    } else {
        Write-Host " NOT RUNNING (Port: 7687)" -ForegroundColor Red
        $neo4jStatus = $false
    }
} catch {
    Write-Host " NOT RUNNING (Port: 7687)" -ForegroundColor Red
    $neo4jStatus = $false
}

Write-Host ""
Write-Host "Service Summary:" -ForegroundColor Yellow
Write-Host "   Frontend: $(if ($frontendStatus) { "Running" } else { "Stopped" })" -ForegroundColor $(if ($frontendStatus) { "Green" } else { "Red" })
Write-Host "   Backend:  $(if ($backendStatus) { "Running" } else { "Stopped" })" -ForegroundColor $(if ($backendStatus) { "Green" } else { "Red" })
Write-Host "   Solr:     $(if ($solrStatus) { "Running" } else { "Stopped" })" -ForegroundColor $(if ($solrStatus) { "Green" } else { "Red" })
Write-Host "   Neo4j:    $(if ($neo4jStatus) { "Running" } else { "Stopped" })" -ForegroundColor $(if ($neo4jStatus) { "Green" } else { "Red" })

$runningCount = ($frontendStatus, $backendStatus, $solrStatus, $neo4jStatus | Where-Object { $_ }).Count
Write-Host ""
Write-Host "Services: $runningCount/4 running" -ForegroundColor $(if ($runningCount -eq 4) { "Green" } else { "Yellow" })

if ($runningCount -eq 4) {
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Cyan
    Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "   Backend API: http://localhost:3001" -ForegroundColor White
    Write-Host "   Solr Admin: http://localhost:8983" -ForegroundColor White
}