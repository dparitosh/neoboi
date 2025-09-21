# Service Launcher - Start Services Separately
Write-Host "Service Launcher - Start Services Separately" -ForegroundColor Green
Write-Host "Each service runs independently when triggered." -ForegroundColor Cyan
Write-Host ""

# Change to script directory and navigate to root
Set-Location $PSScriptRoot
Set-Location ..\..

Write-Host "Available Services:" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Neo4j Database:" -ForegroundColor Cyan
Write-Host "   Command: .\scripts\services\start-neo4j.ps1" -ForegroundColor White
Write-Host "   Description: Starts Neo4j database service" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Apache Solr:" -ForegroundColor Cyan
Write-Host "   Command: .\scripts\services\start-solr.ps1" -ForegroundColor White
Write-Host "   Description: Starts Apache Solr search engine" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Python FastAPI Backend:" -ForegroundColor Cyan
Write-Host "   Command: .\scripts\services\start-backend.ps1" -ForegroundColor White
Write-Host "   Description: Starts the Python FastAPI backend server" -ForegroundColor Gray
Write-Host ""

Write-Host "4. React Frontend:" -ForegroundColor Cyan
Write-Host "   Command: .\scripts\services\start-frontend.ps1" -ForegroundColor White
Write-Host "   Description: Starts the React frontend application" -ForegroundColor Gray
Write-Host ""

Write-Host "Usage Instructions:" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
Write-Host "Run each service in a separate terminal/command prompt:" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 1 - Neo4j:" -ForegroundColor Green
Write-Host "  powershell .\scripts\services\start-neo4j.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 - Solr:" -ForegroundColor Green
Write-Host "  powershell .\scripts\services\start-solr.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 3 - Backend:" -ForegroundColor Green
Write-Host "  powershell .\scripts\services\start-backend.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 4 - Frontend:" -ForegroundColor Green
Write-Host "  powershell .\scripts\services\start-frontend.ps1" -ForegroundColor White
Write-Host ""

Write-Host "Service URLs when running:" -ForegroundColor Yellow
Write-Host "Neo4j Browser: http://localhost:7474" -ForegroundColor Cyan
Write-Host "Solr Admin: http://localhost:8983" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:3001" -ForegroundColor Cyan
Write-Host "React Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

Write-Host "Management Commands:" -ForegroundColor Yellow
Write-Host "===================" -ForegroundColor Yellow
Write-Host "Check service status: .\scripts\services\status.ps1" -ForegroundColor Cyan
Write-Host "Stop all services:    .\scripts\services\stop-backend.ps1" -ForegroundColor Red
Write-Host "                      .\scripts\services\stop-frontend.ps1" -ForegroundColor Red
Write-Host ""
Write-Host "Note: Each service can be started/stopped independently." -ForegroundColor Magenta
Write-Host "Use the status script to verify all services are running correctly." -ForegroundColor Magenta