# Neo4j Service Management
Write-Host "Neo4j Service Management..." -ForegroundColor Green
Write-Host ""

# Change to script directory and navigate to root
Set-Location $PSScriptRoot
Set-Location ..\..

# Load environment variables
$envPath = ".env.local"
if (Test-Path $envPath) {
    $envContent = Get-Content $envPath
    $neo4jUri = ($envContent | Where-Object { $_ -match "^NEO4J_URI=" }) -replace "NEO4J_URI=", ""

    if ($neo4jUri) {
        # Remove surrounding quotes if present
        $neo4jUri = $neo4jUri -replace '^"|"$', ''
        
        # Detect deployment type
        if ($neo4jUri -match "^neo4j\+s://" -or $neo4jUri -match "databases\.neo4j\.io") {
            Write-Host "Detected Neo4j Aura (Cloud) deployment" -ForegroundColor Cyan
            Write-Host "Neo4j Aura is always available - no startup required!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Current configuration:" -ForegroundColor Yellow
            Write-Host "URI: $neo4jUri" -ForegroundColor White
        } elseif ($neo4jUri -match "^(bolt|neo4j)://") {
            Write-Host "Detected On-Premise Neo4j deployment" -ForegroundColor Cyan
            Write-Host "For on-premise Neo4j, please start your local Neo4j instance manually." -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Current configuration:" -ForegroundColor Yellow
            Write-Host "URI: $neo4jUri" -ForegroundColor White
            Write-Host ""
            Write-Host "Make sure your Neo4j instance is running and accessible." -ForegroundColor Cyan
        } else {
            Write-Host "Unknown Neo4j URI format: $neo4jUri" -ForegroundColor Red
            Write-Host "Please check your NEO4J_URI configuration in .env.local" -ForegroundColor Yellow
        }
    } else {
        Write-Host "NEO4J_URI not configured in .env.local" -ForegroundColor Red
        Write-Host "Please add NEO4J_URI to your .env.local file" -ForegroundColor Yellow
    }
} else {
    Write-Host "Configuration file .env.local not found" -ForegroundColor Red
    Write-Host "Please create .env.local with Neo4j configuration" -ForegroundColor Yellow
}