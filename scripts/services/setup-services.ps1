# Guided setup helper for NeoBoi prerequisites and local services
Write-Host "=== NeoBoi Guided Services Setup ===" -ForegroundColor Magenta
Write-Host "This script verifies prerequisites and highlights any missing steps." -ForegroundColor Gray
Write-Host ""

# Change to script directory and navigate to project root
Set-Location $PSScriptRoot
Set-Location ..\..
$projectRoot = Get-Location
Write-Host "Project root: $projectRoot" -ForegroundColor Cyan
Write-Host ""

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

function Test-CommandExists {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string]$FriendlyName
    )

    if (Get-Command $Command -ErrorAction SilentlyContinue) {
        Write-Host "[ ok  ] $FriendlyName detected ($Command)" -ForegroundColor Green
        return $true
    }

    Write-Host "[ warn] $FriendlyName not found in PATH. Install it before continuing." -ForegroundColor Yellow
    return $false
}

# Function to verify Solr installation
function Test-SolrInstallation {
    Write-Host "Verifying Apache Solr installation..." -ForegroundColor Cyan

    if (Test-Path "$solrPath\bin\solr.cmd") {
        Write-Host "Found Apache Solr at: $solrPath" -ForegroundColor Green
        return $solrPath
    }

    Write-Host "Apache Solr not found at $solrPath." -ForegroundColor Yellow
    Write-Host "Please ensure Apache Solr is installed, or update SOLR_HOME in .env.local." -ForegroundColor Yellow
    return $null
}

# Function to verify Tika installation
function Test-TikaInstallation {
    Write-Host "Verifying Apache Tika installation..." -ForegroundColor Cyan

    # Check for Tika JAR in common locations
    $tikaPaths = @(
        "C:\tika",
        "C:\Program Files\tika",
        "$env:USERPROFILE\tika"
    )

    foreach ($path in $tikaPaths) {
        $tikaJar = Get-ChildItem -Path $path -Filter "tika-app-*.jar" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($tikaJar) {
            Write-Host "Found Apache Tika at: $($tikaJar.FullName)" -ForegroundColor Green
            return $tikaJar.FullName
        }
    }

    Write-Host "Apache Tika not found in standard locations." -ForegroundColor Yellow
    Write-Host "Please ensure Apache Tika JAR is available, or update the script with the correct path." -ForegroundColor Yellow
    return $null
}

# Function to verify Tesseract installation
function Test-TesseractInstallation {
    Write-Host "Verifying Tesseract OCR installation..." -ForegroundColor Cyan

    try {
        $tesseractVersion = & tesseract --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Tesseract OCR is installed and available in PATH" -ForegroundColor Green
            Write-Host "Version: $($tesseractVersion -split '\n')[0]" -ForegroundColor Green
            return $true
        }
    } catch {
        # Try common installation paths
        $tesseractPaths = @(
            "C:\Program Files\Tesseract-OCR",
            "C:\Program Files (x86)\Tesseract-OCR",
            "$env:ProgramFiles\Tesseract-OCR"
        )

        foreach ($path in $tesseractPaths) {
            if (Test-Path "$path\tesseract.exe") {
                Write-Host "Found Tesseract OCR at: $path" -ForegroundColor Green
                return $path
            }
        }
    }

    Write-Host "Tesseract OCR not found." -ForegroundColor Yellow
    Write-Host "Please ensure Tesseract OCR is installed and available in PATH." -ForegroundColor Yellow
    return $null
}

# Function to create Solr core
function Initialize-SolrCore {
    param([string]$solrPath)

    Write-Host "Initializing Apache Solr core..." -ForegroundColor Cyan

    # Check if Solr is running
    try {
        Invoke-WebRequest -Uri "http://localhost:8983/solr/admin/info/system" -TimeoutSec 5 -ErrorAction Stop | Out-Null
        Write-Host "Solr is running. Checking for 'neoboi' core..." -ForegroundColor Green

        # Check if neoboi core exists
        $coreResponse = Invoke-WebRequest -Uri "http://localhost:8983/solr/admin/cores?action=STATUS&core=neoboi" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($coreResponse.Content -match "neoboi") {
            Write-Host "'neoboi' core already exists." -ForegroundColor Green
        } else {
            Write-Host "Creating 'neoboi' core..." -ForegroundColor Yellow
            Write-Host "Please start Solr first with: solr start -c" -ForegroundColor Yellow
            Write-Host "Then run: solr create -c neoboi" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Solr is not running or not accessible on localhost:8983" -ForegroundColor Yellow
        Write-Host "Please start Solr with: solr start -c" -ForegroundColor Yellow
    }
}

# Function to test Tika server
function Test-TikaServer {
    param([string]$tikaJarPath)

    Write-Host "Testing Apache Tika server..." -ForegroundColor Cyan

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9998/version" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "Tika server is running. Version: $($response.Content)" -ForegroundColor Green
    } catch {
        Write-Host "Tika server is not running on localhost:9998" -ForegroundColor Yellow
        if ($tikaJarPath) {
            Write-Host "To start Tika server, run:" -ForegroundColor Cyan
            Write-Host "java -jar `"$tikaJarPath`" --server --host 0.0.0.0 --port 9998" -ForegroundColor White
        }
    }
}

# Main setup process
Write-Host "Step 1/5: Checking prerequisite CLI tools" -ForegroundColor Magenta
$cliChecks = @(
    @{ Name = "Python"; Command = "python" },
    @{ Name = "Pip"; Command = "pip" },
    @{ Name = "Node.js"; Command = "node" },
    @{ Name = "npm"; Command = "npm" },
    @{ Name = "Java"; Command = "java" },
    @{ Name = "Ollama (optional for offline LLM)"; Command = "ollama" }
)

$missingTools = @()
foreach ($cli in $cliChecks) {
    if (-not (Test-CommandExists -Command $cli.Command -FriendlyName $cli.Name)) {
        $missingTools += $cli.Name
    }
}
if ($missingTools.Count -eq 0) {
    Write-Host "All required command-line tools were detected." -ForegroundColor Green
} else {
    Write-Host ("The following tools still need attention: {0}" -f ($missingTools -join ", ")) -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Step 2/5: Environment configuration" -ForegroundColor Magenta
if (Test-Path $envPath) {
    Write-Host "[ ok  ] .env.local found." -ForegroundColor Green
    if (Select-String -Path $envPath -Pattern "NEO4J_URI" -Quiet) {
        Write-Host "         Core Neo4j settings detected." -ForegroundColor Gray
    } else {
        Write-Host "[warn] .env.local exists but Neo4j settings are missing. Review .env.example." -ForegroundColor Yellow
    }
} elseif (Test-Path ".env.example") {
    Write-Host "[warn] .env.local not found. Copy the sample file before continuing:" -ForegroundColor Yellow
    Write-Host "       Copy-Item .env.example .env.local" -ForegroundColor Cyan
} else {
    Write-Host "[warn] No environment file detected. Create .env.local using values from documentation." -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Step 3/5: Verifying external services" -ForegroundColor Magenta
$solrPath = Test-SolrInstallation
$tikaJarPath = Test-TikaInstallation
$tesseractPath = Test-TesseractInstallation

if ($solrPath) {
    Initialize-SolrCore -solrPath $solrPath
}

if ($tikaJarPath) {
    Test-TikaServer -tikaJarPath $tikaJarPath
}

if ($tesseractPath) {
    Write-Host "Tesseract OCR is ready for use." -ForegroundColor Green
}
Write-Host ""

Write-Host "Step 4/5: Application dependency check" -ForegroundColor Magenta
$backendVenv = Join-Path $projectRoot "backend\venv\Scripts\python.exe"
$frontendModules = Join-Path $projectRoot "frontend\node_modules"

if (Test-Path $backendVenv) {
    Write-Host "[ ok  ] Backend virtual environment detected at backend\\venv." -ForegroundColor Green
} else {
    Write-Host "[warn] Backend virtual environment not found. Run scripts\\services\\setup-python-llm.bat" -ForegroundColor Yellow
}

if (Test-Path $frontendModules) {
    Write-Host "[ ok  ] Frontend dependencies installed." -ForegroundColor Green
} else {
    Write-Host "[warn] Frontend node_modules missing. Run scripts\\services\\setup-offline-llm.bat" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Step 5/5: Summary and next actions" -ForegroundColor Magenta
if ($solrPath) {
    Write-Host ("Solr Path: {0}" -f $solrPath) -ForegroundColor Green
} else {
    Write-Host "Solr Path: Not detected" -ForegroundColor Yellow
}

if ($tikaJarPath) {
    Write-Host ("Tika JAR: {0}" -f $tikaJarPath) -ForegroundColor Green
} else {
    Write-Host "Tika JAR: Not detected" -ForegroundColor Yellow
}

if ($tesseractPath) {
    Write-Host "Tesseract: Installed" -ForegroundColor Green
} else {
    Write-Host "Tesseract: Not detected" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Magenta
Write-Host "  1. Install any missing prerequisites listed above." -ForegroundColor White
Write-Host "  2. Populate .env.local with your service credentials." -ForegroundColor White
Write-Host "  3. Start background services (Solr, Tika, Ollama) using their respective commands." -ForegroundColor White
Write-Host "  4. Launch the application: powershell -ExecutionPolicy Bypass -File .\\scripts\\services\\start-all.ps1" -ForegroundColor White

Write-Host ""
Write-Host "More documentation:" -ForegroundColor Magenta
Write-Host "  INSTALLATION.md" -ForegroundColor White
Write-Host "  docs/installation/master-installation-guide.md" -ForegroundColor White
Write-Host "  docs/installation/solr-installation.md" -ForegroundColor White
Write-Host "  docs/installation/tika-installation.md" -ForegroundColor White
Write-Host "  docs/installation/tesseract-installation.md" -ForegroundColor White