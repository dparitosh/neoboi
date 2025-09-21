# Start Apache Solr Service
Write-Host "Starting Apache Solr Service..." -ForegroundColor Green
Write-Host ""

# Change to script directory and navigate to root
Set-Location $PSScriptRoot
Set-Location ..\..

# Load environment variables
$envPath = ".env.local"
$solrPath = "D:\Software\solr-9.9.0"  # Default fallback

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath
    $configuredPath = ($envContent | Where-Object { $_ -match "^SOLR_HOME=" }) -replace "SOLR_HOME=", "" -replace '"', ""
    if ($configuredPath) {
        $solrPath = $configuredPath
    }
}

# Find Solr installation
if (!(Test-Path $solrPath)) {
    Write-Host "Apache Solr not found at $solrPath. Please check the installation or update SOLR_HOME in .env.local." -ForegroundColor Red
    exit 1
}

# Start Solr
Write-Host "Starting Solr from: $solrPath" -ForegroundColor Cyan
Set-Location $solrPath

# Start Solr in background
$solrJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    & ".\bin\solr.cmd" start
} -ArgumentList $solrPath

Write-Host "Solr started (Job ID: $($solrJob.Id))" -ForegroundColor Green
Write-Host "Solr Admin will be available at: http://localhost:8983" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop Solr..." -ForegroundColor Yellow

# Wait for user to stop
try {
    while ($true) {
        Start-Sleep 1
    }
} finally {
    Write-Host ""
    Write-Host "Stopping Solr..." -ForegroundColor Yellow
    Stop-Job $solrJob -ErrorAction SilentlyContinue
    Write-Host "Solr stopped." -ForegroundColor Green
}