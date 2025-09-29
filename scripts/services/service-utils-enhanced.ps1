# Service Management Utilities for NeoBoi Platform
# Shared functions used by the unified management script

# Configuration
$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$BACKEND_DIR = Join-Path $PROJECT_ROOT "backend"
$FRONTEND_DIR = Join-Path $PROJECT_ROOT "frontend"
$SCRIPTS_DIR = $PSScriptRoot

# Logging functions
function Write-Info {
    param([string]$Message)
    Write-Host "INFO: $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "SUCCESS: $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "WARNING: $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
}

function Get-EnvFile {
    param([string]$envPath = ".env.local")

    if (!(Test-Path $envPath)) {
        Write-Warning "Environment file $envPath not found"
        return @{}
    }

    $envVars = @{}
    $content = Get-Content $envPath -ErrorAction SilentlyContinue

    foreach ($line in $content) {
        if ($line -match "^([^#][^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Remove surrounding quotes if present
            if ($value -match '^"(.*)"$') {
                $value = $matches[1]
            } elseif ($value -match "^'(.*)'$") {
                $value = $matches[1]
            }
            $envVars[$key] = $value
            [Environment]::SetEnvironmentVariable($key, $value)
        }
    }

    return $envVars
}

function Test-ServicePort {
    param([int]$port, [string]$serviceName, [switch]$Quiet)

    try {
        $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if ($connection) {
            if (-not $Quiet) {
                Write-Host "$serviceName is running on port $port" -ForegroundColor Green
            }
            return $true
        } else {
            if (-not $Quiet) {
                Write-Host "$serviceName is not running on port $port" -ForegroundColor Yellow
            }
            return $false
        }
    } catch {
        if (-not $Quiet) {
            Write-Host "Could not check port $port for $serviceName" -ForegroundColor Red
        }
        return $false
    }
}

function Get-ProjectRoot {
    param([string]$scriptPath = $PSScriptRoot)
    if ($scriptPath) {
        $parent = Split-Path $scriptPath -Parent
        return Split-Path $parent -Parent
    } else {
        return Split-Path (Split-Path $PWD -Parent) -Parent
    }
}
