# Comprehensive Service Status Check
. "$PSScriptRoot\service-utils.ps1"

Write-Host "Neo4j GraphRAG Application - Service Status Check" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green
Write-Host ""

# Get project root and load environment
$projectRoot = Get-ProjectRoot
Set-Location $projectRoot
$envVars = Get-EnvFile

# Define services to check
$services = @(
    @{ Name = "Frontend"; Port = 3000; Url = "http://localhost:3000" },
    @{ Name = "Backend API"; Port = 3001; Url = "http://localhost:3001/health" },
    @{ Name = "Solr Search"; Port = 8983; Url = "http://localhost:8983/solr/admin/cores" }
)

$runningServices = 0

# Check each service
foreach ($service in $services) {
    Write-Host "Checking $($service.Name)..." -ForegroundColor Cyan -NoNewline
    
    # Check if port is listening
    $portActive = Test-ServicePort -port $service.Port -serviceName $service.Name
    
    if ($portActive) {
        # Try to make HTTP request if URL provided
        if ($service.Url) {
            try {
                $response = Invoke-WebRequest -Uri $service.Url -Method GET -TimeoutSec 5 -ErrorAction Stop
                Write-Host " ✅ RUNNING (Port: $($service.Port), HTTP: $($response.StatusCode))" -ForegroundColor Green
                $runningServices++
            } catch {
                Write-Host " ⚠️  PORT ACTIVE but HTTP not responding (Port: $($service.Port))" -ForegroundColor Yellow
            }
        } else {
            Write-Host " ✅ RUNNING (Port: $($service.Port))" -ForegroundColor Green
            $runningServices++
        }
    } else {
        Write-Host " ❌ NOT RUNNING (Port: $($service.Port))" -ForegroundColor Red
    }
}

# Check Neo4j configuration
Write-Host ""
Write-Host "Checking Neo4j Configuration..." -ForegroundColor Cyan
$neo4jConfigured = $false

if ($envVars.ContainsKey('NEO4J_URI') -and $envVars.ContainsKey('NEO4J_USER') -and $envVars.ContainsKey('NEO4J_PASSWORD')) {
    $uri = $envVars['NEO4J_URI']
    if ($uri -match "^neo4j\+s://" -or $uri -match "databases\.neo4j\.io") {
        Write-Host "✅ Neo4j Aura (Cloud) - CONFIGURED" -ForegroundColor Green
        $neo4jConfigured = $true
    } elseif ($uri -match "^(bolt|neo4j)://") {
        Write-Host "✅ Neo4j On-Premise - CONFIGURED (URI: $uri)" -ForegroundColor Green
        $neo4jConfigured = $true
    } else {
        Write-Host "⚠️  Neo4j - UNKNOWN URI FORMAT: $uri" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Neo4j - NOT CONFIGURED (missing credentials in .env.local)" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "=" * 50 -ForegroundColor Yellow
Write-Host "SUMMARY" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Yellow
Write-Host "Services Running: $runningServices/3" -ForegroundColor $(if ($runningServices -eq 3) { "Green" } else { "Yellow" })
Write-Host "Neo4j Configured: $(if ($neo4jConfigured) { "Yes" } else { "No" })" -ForegroundColor $(if ($neo4jConfigured) { "Green" } else { "Red" })

if ($runningServices -eq 3 -and $neo4jConfigured) {
    Write-Host ""
    Write-Host "🎉 ALL SYSTEMS OPERATIONAL!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Cyan
    Write-Host "  • Frontend:    http://localhost:3000" -ForegroundColor White
    Write-Host "  • Backend API: http://localhost:3001" -ForegroundColor White
    Write-Host "  • API Docs:    http://localhost:3001/docs" -ForegroundColor White
    Write-Host "  • Solr Admin:  http://localhost:8983" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "⚠️  Some services need attention" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To start missing services:" -ForegroundColor Cyan
    if ($runningServices -lt 3) {
        Write-Host "  • Backend:  .\scripts\services\start-backend-fixed.ps1" -ForegroundColor White
        Write-Host "  • Frontend: .\scripts\services\start-frontend.ps1" -ForegroundColor White
        Write-Host "  • Solr:     .\scripts\services\start-solr.ps1" -ForegroundColor White
    }
    if (!$neo4jConfigured) {
        Write-Host ""
        Write-Host "Configure Neo4j in .env.local:" -ForegroundColor Yellow
        Write-Host "  NEO4J_URI=neo4j://localhost:7687" -ForegroundColor White
        Write-Host "  NEO4J_USER=neo4j" -ForegroundColor White
        Write-Host "  NEO4J_PASSWORD=your-password" -ForegroundColor White
    }
}

Write-Host ""