# Stop Frontend Service
Write-Host "Stopping Frontend Service..." -ForegroundColor Yellow

# Find and stop Node.js processes running on port 3000
$nodeProcesses = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" } |
    ForEach-Object { Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue }

if ($nodeProcesses) {
    foreach ($process in $nodeProcesses) {
        Write-Host "Stopping process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Yellow
        Stop-Process -Id $process.Id -Force
    }
    Write-Host "✅ Frontend service stopped." -ForegroundColor Green
} else {
    Write-Host "ℹ️  No frontend service found running on port 3000." -ForegroundColor Cyan
}