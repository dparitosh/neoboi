# Setup Solr Services (Pre-installed)
Write-Host "Setting up Apache Solr services..." -ForegroundColor Green
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
        $response = Invoke-WebRequest -Uri "http://localhost:8983/solr/admin/info/system" -TimeoutSec 5 -ErrorAction Stop
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
Write-Host "=== NeoBoi Services Setup ===" -ForegroundColor Magenta
Write-Host ""

# Verify all services
$solrPath = Test-SolrInstallation
$tikaJarPath = Test-TikaInstallation
$tesseractPath = Test-TesseractInstallation

Write-Host ""
Write-Host "=== Service Configuration ===" -ForegroundColor Magenta

# Configure Solr if found
if ($solrPath) {
    Initialize-SolrCore -solrPath $solrPath
}

# Test Tika if JAR found
if ($tikaJarPath) {
    Test-TikaServer -tikaJarPath $tikaJarPath
}

# Test Tesseract
if ($tesseractPath) {
    Write-Host "Tesseract OCR is ready for use." -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Setup Summary ===" -ForegroundColor Magenta
Write-Host "Solr Path: $($solrPath ? $solrPath : 'Not found')" -ForegroundColor $(if ($solrPath) { 'Green' } else { 'Yellow' })
Write-Host "Tika JAR: $($tikaJarPath ? $tikaJarPath : 'Not found')" -ForegroundColor $(if ($tikaJarPath) { 'Green' } else { 'Yellow' })
Write-Host "Tesseract: $($tesseractPath ? 'Found' : 'Not found')" -ForegroundColor $(if ($tesseractPath) { 'Green' } else { 'Yellow' })

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Magenta
Write-Host "1. Ensure all services are installed (see docs/installation/)" -ForegroundColor White
Write-Host "2. Start services in order:" -ForegroundColor White
Write-Host "   - Solr: solr start -c" -ForegroundColor Cyan
Write-Host "   - Tika: java -jar <tika-jar> --server --port 9998" -ForegroundColor Cyan
Write-Host "3. Update .env.local with correct paths and credentials" -ForegroundColor White
Write-Host "4. Run the application: .\scripts\services\start-all.ps1" -ForegroundColor White

Write-Host ""
Write-Host "For detailed installation guides, see:" -ForegroundColor Yellow
Write-Host "  docs/installation/solr-installation.md" -ForegroundColor White
Write-Host "  docs/installation/tika-installation.md" -ForegroundColor White
Write-Host "  docs/installation/tesseract-installation.md" -ForegroundColor White
Write-Host "  docs/installation/integration-guide.md" -ForegroundColor White