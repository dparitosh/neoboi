# Stop Backend Service
Write-Host "Stopping Backend Service..." -ForegroundColor Yellow

# Find and stop Python processes running on port 3001
$pythonProcesses = Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" } |
    ForEach-Object { Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue }

if ($pythonProcesses) {
    foreach ($process in $pythonProcesses) {
        Write-Host "Stopping process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Yellow
        Stop-Process -Id $process.Id -Force
    }
    Write-Host "Backend service stopped." -ForegroundColor Green
} else {
    Write-Host "No backend service found running on port 3001." -ForegroundColor Cyan
}