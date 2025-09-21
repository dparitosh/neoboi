# Stop Neo4j Graph Visualization App
Write-Host "Stopping Neo4j Graph Visualization App..." -ForegroundColor Yellow
Write-Host ""

# Find and stop Node.js processes running server.js
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue

if ($nodeProcesses) {
    foreach ($process in $nodeProcesses) {
        try {
            # Get the command line for this process
            $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine

            if ($commandLine -and $commandLine -like "*server.js*") {
                Write-Host "Found server process (PID: $($process.Id)). Stopping..." -ForegroundColor Cyan
                Stop-Process -Id $process.Id -Force -ErrorAction Stop
                Write-Host "Server stopped successfully." -ForegroundColor Green
                exit 0
            }
        } catch {
            Write-Host "Failed to stop process $($process.Id): $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    # If no specific server process found, ask user if they want to stop all Node processes
    Write-Host "No specific server process found." -ForegroundColor Yellow
    $response = Read-Host "Do you want to stop all Node.js processes? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Stopping all Node.js processes..." -ForegroundColor Cyan
        Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
        Write-Host "All Node.js processes stopped." -ForegroundColor Green
    }
} else {
    Write-Host "No Node.js processes found running." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green