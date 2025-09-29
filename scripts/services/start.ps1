# Consolidated NeoBoi Start Script
# Unified service startup with options for different configurations

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "backend", "frontend", "solr", "neo4j", "ollama", "tika", "tesseract")]
    [string]$Service = "all",

    [Parameter(Mandatory=$false)]
    [switch]$NoExit,

    [Parameter(Mandatory=$false)]
    [switch]$Background
)

Write-Host "=== NeoBoi Service Launcher ===" -ForegroundColor Magenta
Write-Host "Starting NeoBoi services..." -ForegroundColor Gray
Write-Host ""

# Change to script directory and navigate to project root
Set-Location $PSScriptRoot
Set-Location ..\..
$projectRoot = Get-Location
Write-Host "Project root: $projectRoot" -ForegroundColor Cyan
Write-Host ""

# Import utilities
$utilsPath = Join-Path $PSScriptRoot "service-utils-enhanced.ps1"
if (Test-Path $utilsPath) {
    . $utilsPath
}

function Start-Neo4jHelper {
    Write-Host "Checking Neo4j configuration..." -ForegroundColor Cyan
    Write-Host "Please ensure Neo4j Desktop is running and accessible at neo4j://localhost:7687" -ForegroundColor Yellow
    Write-Host "Neo4j Browser: http://localhost:7474" -ForegroundColor Blue
}

function Start-Solr {
    Write-Host "Starting Apache Solr..." -ForegroundColor Cyan
    try {
        # Load environment variables
        Get-EnvFile | Out-Null

        $solrHome = $env:SOLR_HOME
        if (-not $solrHome) {
            Write-Error "SOLR_HOME environment variable is not set"
            return
        }

        $solrBin = Join-Path $solrHome "bin"
        $solrCmd = Join-Path $solrBin "solr.cmd"

        if (Test-Path $solrCmd) {
            Write-Info "Starting Solr from: $solrCmd"
            if ($Background) {
                Start-Process cmd.exe -ArgumentList "/c `"$solrCmd`" start" -NoNewWindow
            } else {
                & cmd.exe /c "`"$solrCmd`" start"
            }
            Write-Success "Solr start command executed"
        } else {
            Write-Error "Solr command not found at: $solrCmd"
        }
    } catch {
        Write-Error "Failed to start Solr: $($_.Exception.Message)"
    }
}

function Start-Backend {
    Write-Host "Starting FastAPI backend..." -ForegroundColor Cyan
    try {
        # Navigate to project root first, then run as module
        Push-Location $projectRoot
        Write-Info "Starting backend from: $projectRoot (running as module)"

        if ($Background) {
            Start-Process python -ArgumentList "-m backend.main" -NoNewWindow
        } else {
            & python -m backend.main
        }
    } catch {
        Write-Error "Failed to start backend: $($_.Exception.Message)"
    } finally {
        Pop-Location
    }
}

function Start-Frontend {
    Write-Host "Starting React frontend..." -ForegroundColor Cyan
    try {
        Push-Location $FRONTEND_DIR
        Write-Info "Starting frontend from: $FRONTEND_DIR"

        if ($Background) {
            Start-Process npm -ArgumentList "start" -NoNewWindow
        } else {
            & npm start
        }
    } catch {
        Write-Error "Failed to start frontend: $($_.Exception.Message)"
    } finally {
        Pop-Location
    }
}

function Start-Ollama {
    Write-Host "Starting Ollama LLM service..." -ForegroundColor Cyan
    try {
        # Load environment variables
        Get-EnvFile | Out-Null

        $ollamaPath = $env:OLLAMA_PATH
        if (-not $ollamaPath) {
            $ollamaPath = "$env:USERPROFILE\AppData\Local\Programs\Ollama\ollama.exe"
        }

        if (Test-Path $ollamaPath) {
            Write-Info "Starting Ollama from: $ollamaPath"
            if ($Background) {
                Start-Process -FilePath $ollamaPath -ArgumentList "serve" -NoNewWindow
            } else {
                & $ollamaPath serve
            }
            Write-Success "Ollama start command executed"
        } else {
            Write-Error "Ollama executable not found at: $ollamaPath"
        }
    } catch {
        Write-Error "Failed to start Ollama: $($_.Exception.Message)"
    }
}

function Start-Tika {
    Write-Host "Starting Apache Tika server..." -ForegroundColor Cyan
    try {
        # Load environment variables
        Get-EnvFile | Out-Null

        # Check if Tika server is already running
        $tikaUrl = $env:TIKA_SERVER_URL
        if (-not $tikaUrl) {
            $tikaUrl = "http://localhost:9998"
        }

        try {
            $response = Invoke-WebRequest -Uri "$tikaUrl/version" -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Success "Tika server is already running at $tikaUrl"
                return
            }
        } catch {
            Write-Info "Tika server not running, attempting to start..."
        }

        # Start Tika server using the backend TikaService
        Push-Location $BACKEND_DIR
        try {
            Write-Info "Starting Tika server via backend TikaService..."

            # Run Python script from backend directory
            $pythonCmd = @"
import sys
try:
    from config import get_settings
    from unstructured_pipeline.tika_service import TikaService
    import time

    settings = get_settings()
    tika_service = TikaService(settings=settings)
    success = tika_service.start_tika_server()

    if success:
        print('Tika server started successfully')
        # Keep the process alive to maintain the server
        while True:
            time.sleep(1)
    else:
        print('Failed to start Tika server')
        sys.exit(1)
except ImportError as e:
    print(f'Failed to import required modules: {e}')
    print('Please ensure all backend dependencies are installed')
    sys.exit(1)
except Exception as e:
    print(f'Failed to start Tika server: {e}')
    sys.exit(1)
"@

            if ($Background) {
                Start-Process python -ArgumentList "-c", $pythonCmd -NoNewWindow -WorkingDirectory $BACKEND_DIR
            } else {
                & python -c $pythonCmd
            }

            # Wait a moment and check if it started
            Start-Sleep -Seconds 5
            try {
                $response = Invoke-WebRequest -Uri "$tikaUrl/version" -TimeoutSec 5 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Success "Tika server started successfully at $tikaUrl"
                } else {
                    Write-Warning "Tika server may not have started properly"
                }
            } catch {
                Write-Warning "Could not verify Tika server startup"
            }

        } catch {
            Write-Error "Failed to start Tika server via backend: $($_.Exception.Message)"
        } finally {
            Pop-Location
        }

    } catch {
        Write-Error "Failed to start Tika service: $($_.Exception.Message)"
    }
}

function Start-Tesseract {
    Write-Host "Checking Tesseract OCR installation..." -ForegroundColor Cyan
    try {
        # Check if Tesseract is installed and accessible
        $tesseractPaths = @(
            'tesseract',
            'C:\Program Files\Tesseract-OCR\tesseract.exe',
            'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            'D:\Program Files\Tesseract-OCR\tesseract.exe'
        )

        $tesseractFound = $false
        $tesseractPath = $null

        foreach ($path in $tesseractPaths) {
            try {
                $result = & $path '--version' 2>$null
                if ($LASTEXITCODE -eq 0 -and $result -match 'tesseract') {
                    $tesseractFound = $true
                    $tesseractPath = $path
                    break
                }
            } catch {
                continue
            }
        }

        if ($tesseractFound) {
            Write-Success "Tesseract OCR is installed and accessible at: $tesseractPath"

            # Test Tesseract functionality
            try {
                $version = & $tesseractPath '--version' 2>$null | Select-Object -First 1
                Write-Info "Tesseract version: $version"
            } catch {
                Write-Warning "Could not retrieve Tesseract version"
            }

            # Check for language data
            $tessdataPaths = @(
                'C:\Program Files\Tesseract-OCR\tessdata',
                'C:\Program Files (x86)\Tesseract-OCR\tessdata',
                'D:\Program Files\Tesseract-OCR\tessdata'
            )

            $tessdataFound = $false
            foreach ($path in $tessdataPaths) {
                if (Test-Path $path) {
                    $langFiles = Get-ChildItem -Path $path -Filter "*.traineddata" -ErrorAction SilentlyContinue
                    if ($langFiles.Count -gt 0) {
                        Write-Success "Found $($langFiles.Count) language data files in $path"
                        $tessdataFound = $true
                        break
                    }
                }
            }

            if (-not $tessdataFound) {
                Write-Warning "Tesseract language data files not found. OCR may not work properly."
                Write-Host "Please ensure Tesseract language data is installed." -ForegroundColor Yellow
            }

        } else {
            Write-Error "Tesseract OCR is not installed or not accessible"
            Write-Host ""
            Write-Host "To install Tesseract OCR:" -ForegroundColor Yellow
            Write-Host "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
            Write-Host "2. Install to default location: C:\Program Files\Tesseract-OCR\" -ForegroundColor Cyan
            Write-Host "3. Ensure pytesseract and opencv-python are installed: pip install pytesseract opencv-python" -ForegroundColor Cyan
        }

    } catch {
        Write-Error "Failed to check Tesseract installation: $($_.Exception.Message)"
    }
}

# Main execution logic
switch ($Service) {
    "all" {
        Write-Host "Starting all services in individual console windows..." -ForegroundColor Green
        Start-Neo4jHelper

        # Start services in individual console windows
        Write-Host "Starting Solr in new console window..." -ForegroundColor Cyan
        Start-Process powershell.exe -ArgumentList @('-ExecutionPolicy', 'Bypass', '-Command', "& { . '$PSScriptRoot\service-utils-enhanced.ps1'; Set-Location '$PSScriptRoot\..\..'; . '$PSScriptRoot\start.ps1' -Service solr -Background }") -WindowStyle Normal

        Write-Host "Starting Tika in new console window..." -ForegroundColor Cyan
        Start-Process powershell.exe -ArgumentList @('-ExecutionPolicy', 'Bypass', '-Command', "& { . '$PSScriptRoot\service-utils-enhanced.ps1'; Set-Location '$PSScriptRoot\..\..'; . '$PSScriptRoot\start.ps1' -Service tika -Background }") -WindowStyle Normal

        Write-Host "Starting backend in new console window..." -ForegroundColor Cyan
        Start-Process powershell.exe -ArgumentList @('-ExecutionPolicy', 'Bypass', '-Command', "& { . '$PSScriptRoot\service-utils-enhanced.ps1'; Set-Location '$PSScriptRoot\..\..'; . '$PSScriptRoot\start.ps1' -Service backend -Background }") -WindowStyle Normal

        Write-Host "Starting frontend in new console window..." -ForegroundColor Cyan
        Start-Process powershell.exe -ArgumentList @('-ExecutionPolicy', 'Bypass', '-Command', "& { . '$PSScriptRoot\service-utils-enhanced.ps1'; Set-Location '$PSScriptRoot\..\..'; . '$PSScriptRoot\start.ps1' -Service frontend -Background }") -WindowStyle Normal

        Write-Host "Starting Ollama in new console window..." -ForegroundColor Cyan
        Start-Process powershell.exe -ArgumentList @('-ExecutionPolicy', 'Bypass', '-Command', "& { . '$PSScriptRoot\service-utils-enhanced.ps1'; Set-Location '$PSScriptRoot\..\..'; . '$PSScriptRoot\start.ps1' -Service ollama -Background }") -WindowStyle Normal

        Write-Host ""
        Write-Host "All services started in individual console windows!" -ForegroundColor Green
        Write-Host "Each service is running in its own console window for monitoring." -ForegroundColor Cyan
        Write-Host "Use status.ps1 to check service status." -ForegroundColor Cyan
        Write-Host "Note: Tesseract OCR is checked automatically - ensure it is installed for image processing." -ForegroundColor Yellow
    }
    "backend" {
        Start-Backend
    }
    "frontend" {
        Start-Frontend
    }
    "solr" {
        Start-Solr
    }
    "neo4j" {
        Start-Neo4jHelper
    }
    "ollama" {
        Start-Ollama
    }
    "tika" {
        Start-Tika
    }
    "tesseract" {
        Start-Tesseract
    }
}

if (-not $Background -and -not $NoExit) {
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}