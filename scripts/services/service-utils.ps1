# Service Management Utilities
function Get-EnvFile {
    param([string]$envPath = ".env.local")
    
    if (!(Test-Path $envPath)) {
        Write-Host "Warning: Environment file $envPath not found" -ForegroundColor Yellow
        return @{}
    }
    
    $envVars = @{}
    $content = Get-Content $envPath -ErrorAction SilentlyContinue
    
    foreach ($line in $content) {
        if ($line -match '^([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim() -replace '^"|"$', ''  # Remove quotes
            $envVars[$key] = $value
            # Also set as environment variable
            Set-Item -Path "env:$key" -Value $value
        }
    }
    
    return $envVars
}

function Test-ServicePort {
    param([int]$port, [string]$serviceName)
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if ($connection) {
            Write-Host "$serviceName is running on port $port" -ForegroundColor Green
            return $true
        } else {
            Write-Host "$serviceName is not running on port $port" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "Could not check port $port for $serviceName" -ForegroundColor Red
        return $false
    }
}

function Stop-ServiceByPort {
    param([int]$port, [string]$serviceName)
    
    $processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
        Where-Object { $_.State -eq "Listen" } |
        ForEach-Object { Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue }

    if ($processes) {
        foreach ($process in $processes) {
            Write-Host "Stopping $serviceName process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Yellow
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
        Write-Host "$serviceName stopped successfully" -ForegroundColor Green
        return $true
    } else {
        Write-Host "No $serviceName process found on port $port" -ForegroundColor Cyan
        return $false
    }
}

function Get-ProjectRoot {
    param([string]$scriptPath = $PSScriptRoot)
    if ($scriptPath) {
        return Resolve-Path (Join-Path $scriptPath "..\..") 
    } else {
        return Resolve-Path "..\..\"
    }
}