# NeoBoi Platform Setup Script
# Comprehensive setup and initialization for the entire platform

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "prerequisites", "dependencies", "config", "database", "services")]
    [string]$Component = "all",

    [Parameter(Mandatory=$false)]
    [switch]$Force,

    [Parameter(Mandatory=$false)]
    [switch]$SkipTests
)

# Import utilities
. "$PSScriptRoot\service-utils-enhanced.ps1"

function Write-Header {
    param([string]$Message)
    Write-Host "`n$Message" -ForegroundColor Cyan
    Write-Host ("=" * $Message.Length) -ForegroundColor Cyan
}

function Test-Prerequisites {
    Write-Info "Checking for required software..."

    $prerequisites = @(
        @{ Name = "Python"; Command = "python --version"; Pattern = "Python 3\." },
        @{ Name = "Node.js"; Command = "node --version"; Pattern = "v1[6-9]\.|v2[0-9]\." },
        @{ Name = "Java"; Command = "java -version"; Pattern = "version `"[0-9]+\.[0-9]+\." },
        @{ Name = "Neo4j"; Command = "neo4j --version"; Pattern = "." },
        @{ Name = "Solr"; Command = "solr version"; Pattern = "." }
    )

    $allPresent = $true

    foreach ($prereq in $prerequisites) {
        try {
            $result = Invoke-Expression $prereq.Command 2>$null
            if ($result -match $prereq.Pattern) {
                Write-Success "$($prereq.Name) is installed"
            } else {
                Write-Warning "$($prereq.Name) may not be properly installed"
                $allPresent = $false
            }
        } catch {
            Write-Error "$($prereq.Name) is not installed or not in PATH"
            $allPresent = $false
        }
    }

    return $allPresent
}

function Install-BackendDeps {
    Write-Info "Installing backend Python dependencies..."

    Push-Location $BACKEND_DIR
    try {
        # Check if virtual environment exists
        if (-not (Test-Path "venv")) {
            Write-Info "Creating Python virtual environment..."
            & python -m venv venv
        }

        Write-Info "Activating virtual environment and installing dependencies..."
        & ".\venv\Scripts\activate.ps1"
        & python -m pip install --upgrade pip
        & pip install -r requirements.txt

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Backend dependencies installed successfully"
            return $true
        } else {
            Write-Error "Failed to install backend dependencies"
            return $false
        }
    } catch {
        Write-Error "Error installing backend dependencies: $($_.Exception.Message)"
        return $false
    } finally {
        Pop-Location
    }
}

function Install-FrontendDeps {
    Write-Info "Installing frontend Node.js dependencies..."

    Push-Location $FRONTEND_DIR
    try {
        if (Test-Path "package.json") {
            Write-Info "Installing npm dependencies..."
            & npm install

            if ($LASTEXITCODE -eq 0) {
                Write-Success "Frontend dependencies installed successfully"
                return $true
            } else {
                Write-Error "Failed to install frontend dependencies"
                return $false
            }
        } else {
            Write-Warning "package.json not found in frontend directory"
            return $false
        }
    } catch {
        Write-Error "Error installing frontend dependencies: $($_.Exception.Message)"
        return $false
    } finally {
        Pop-Location
    }
}

function Test-Configuration {
    Write-Info "Validating configuration files..."

    $configValid = $true

    # Check .env.local
    $envLocalPath = Join-Path $PROJECT_ROOT ".env.local"
    if (Test-Path $envLocalPath) {
        $envVars = Get-EnvFile $envLocalPath
        if ($envVars.Count -eq 0) {
            Write-Warning ".env.local exists but appears to be empty"
            $configValid = $false
        } else {
            Write-Success ".env.local configuration loaded successfully"
        }
    } else {
        Write-Warning ".env.local not found"
        $configValid = $false
    }

    # Check backend .env
    $backendEnvPath = Join-Path $BACKEND_DIR ".env"
    if (Test-Path $backendEnvPath) {
        Write-Success "Backend .env file exists"
    } else {
        Write-Warning "Backend .env file not found"
        $configValid = $false
    }

    # Check frontend .env
    $frontendEnvPath = Join-Path $FRONTEND_DIR ".env"
    if (Test-Path $frontendEnvPath) {
        Write-Success "Frontend .env file exists"
    } else {
        Write-Warning "Frontend .env file not found"
        $configValid = $false
    }

    return $configValid
}

function Setup-Prerequisites {
    Write-Header "Setting up Prerequisites"

    Write-Info "Checking system prerequisites..."
    $prereqCheck = Test-Prerequisites

    if (-not $prereqCheck) {
        Write-Error "Prerequisites check failed. Please install missing components."
        Write-Host ""
        Write-Host "Required software:" -ForegroundColor Yellow
        Write-Host "- Python 3.8+ (https://python.org)"
        Write-Host "- Node.js 16+ (https://nodejs.org)"
        Write-Host "- Java 11+ (https://adoptium.net)"
        Write-Host "- Neo4j Desktop (https://neo4j.com/download)"
        Write-Host "- Apache Solr (https://solr.apache.org)"
        Write-Host "- OLLAMA (https://ollama.ai)"
        return $false
    }

    Write-Success "All prerequisites are installed"
    return $true
}

function Setup-Dependencies {
    Write-Header "Setting up Dependencies"

    $backendSuccess = Install-BackendDeps
    $frontendSuccess = Install-FrontendDeps

    if ($backendSuccess -and $frontendSuccess) {
        Write-Success "All dependencies installed successfully"
        return $true
    } else {
        Write-Error "Failed to install some dependencies"
        return $false
    }
}

function Setup-Configuration {
    Write-Header "Setting up Configuration"

    Write-Info "Creating configuration files..."

    # Create .env.local if it doesn't exist
    $envLocalPath = Join-Path $PROJECT_ROOT ".env.local"
    if (-not (Test-Path $envLocalPath) -or $Force) {
        Write-Info "Creating .env.local configuration file..."

        $envContent = @"
# NeoBoi Platform Configuration
# Copy this file and update values for your environment

# Backend Configuration
BACKEND_HOST=localhost
BACKEND_PORT=8000
DEBUG=true

# Frontend Configuration
FRONTEND_HOST=localhost
FRONTEND_PORT=3000

# Neo4j Configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=tcs#12345
NEO4J_DATABASE=neo4j

# Solr Configuration
SOLR_HOST=localhost
SOLR_PORT=8983
SOLR_CORE=neoboi

# OLLAMA Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/neoboi.log
"@

        $envContent | Out-File -FilePath $envLocalPath -Encoding UTF8
        Write-Success "Created .env.local configuration file"
    } else {
        Write-Info ".env.local already exists (use -Force to overwrite)"
    }

    # Create backend .env if it doesn't exist
    $backendEnvPath = Join-Path $BACKEND_DIR ".env"
    if (-not (Test-Path $backendEnvPath) -or $Force) {
        Write-Info "Creating backend/.env configuration file..."

        $backendEnvContent = @"
# Backend-specific configuration
PYTHONPATH=.
ENVIRONMENT=development
WORKERS=4
TIMEOUT=30
"@

        $backendEnvContent | Out-File -FilePath $backendEnvPath -Encoding UTF8
        Write-Success "Created backend/.env configuration file"
    }

    # Create frontend .env if it doesn't exist
    $frontendEnvPath = Join-Path $FRONTEND_DIR ".env"
    if (-not (Test-Path $frontendEnvPath) -or $Force) {
        Write-Info "Creating frontend/.env configuration file..."

        $frontendEnvContent = @"
# Frontend-specific configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
GENERATE_SOURCEMAP=false
"@

        $frontendEnvContent | Out-File -FilePath $frontendEnvPath -Encoding UTF8
        Write-Success "Created frontend/.env configuration file"
    }

    # Validate configuration
    $configValid = Test-Configuration
    if ($configValid) {
        Write-Success "Configuration setup completed"
        return $true
    } else {
        Write-Warning "Configuration files created but validation failed"
        return $false
    }
}

function Setup-Database {
    Write-Header "Setting up Database Services"

    Write-Info "Setting up Neo4j database..."
    # Note: Neo4j setup would typically be done manually or through Neo4j Desktop
    Write-Host "Please ensure Neo4j is running and accessible at neo4j://localhost:7687" -ForegroundColor Yellow

    Write-Info "Setting up Solr search engine..."
    # Note: Solr setup would typically be done through the solr scripts
    Write-Host "Please ensure Solr is running and accessible at http://localhost:8983" -ForegroundColor Yellow

    Write-Info "Setting up OLLAMA LLM service..."
    Write-Host "Please ensure OLLAMA is running and LLAMA3 model is available" -ForegroundColor Yellow

    Write-Success "Database services setup instructions provided"
    return $true
}

function Setup-Services {
    Write-Header "Setting up Service Integration"

    Write-Info "Testing service connectivity..."

    # Test Neo4j connection
    try {
        # This would require neo4j-driver installation
        Write-Info "Testing Neo4j connection..."
        Write-Host "Neo4j connection test requires neo4j-driver package" -ForegroundColor Yellow
    }
    catch {
        Write-Warning "Neo4j connection test failed: $($_.Exception.Message)"
    }

    # Test Solr connection
    try {
        $solrUrl = "http://localhost:8983/solr/admin/info/system"
        $response = Invoke-WebRequest -Uri $solrUrl -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "Solr connection successful"
        }
    }
    catch {
        Write-Warning "Solr connection test failed: $($_.Exception.Message)"
    }

    # Test OLLAMA connection
    try {
        $ollamaUrl = "http://localhost:11434/api/tags"
        $response = Invoke-WebRequest -Uri $ollamaUrl -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "OLLAMA connection successful"
        }
    }
    catch {
        Write-Warning "OLLAMA connection test failed: $($_.Exception.Message)"
    }

    Write-Success "Service integration setup completed"
    return $true
}

function Run-SetupTests {
    Write-Header "Running Setup Tests"

    if ($SkipTests) {
        Write-Info "Skipping setup tests as requested"
        return $true
    }

    Write-Info "Running configuration validation tests..."

    # Test configuration loading
    try {
        $envVars = Get-EnvFile
        if ($envVars.Count -gt 0) {
            Write-Success "Configuration loading test passed"
        } else {
            Write-Warning "Configuration loading test returned empty config"
        }
    }
    catch {
        Write-Error "Configuration loading test failed: $($_.Exception.Message)"
        return $false
    }

    # Test backend imports
    Write-Info "Testing backend imports..."
    Push-Location $BACKEND_DIR
    try {
        $testResult = & python -c "import sys; sys.path.append('.'); import main; print('Backend imports successful')"
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Backend import test passed"
        } else {
            Write-Error "Backend import test failed"
            return $false
        }
    }
    catch {
        Write-Error "Backend import test failed: $($_.Exception.Message)"
        return $false
    }
    finally {
        Pop-Location
    }

    Write-Success "All setup tests passed"
    return $true
}

# Main execution logic
Write-Header "NeoBoi Platform Setup"

$overallSuccess = $true

switch ($Component) {
    "all" {
        $overallSuccess = $overallSuccess -and (Setup-Prerequisites)
        $overallSuccess = $overallSuccess -and (Setup-Dependencies)
        $overallSuccess = $overallSuccess -and (Setup-Configuration)
        $overallSuccess = $overallSuccess -and (Setup-Database)
        $overallSuccess = $overallSuccess -and (Setup-Services)
        $overallSuccess = $overallSuccess -and (Run-SetupTests)
    }
    "prerequisites" {
        $overallSuccess = Setup-Prerequisites
    }
    "dependencies" {
        $overallSuccess = Setup-Dependencies
    }
    "config" {
        $overallSuccess = Setup-Configuration
    }
    "database" {
        $overallSuccess = Setup-Database
    }
    "services" {
        $overallSuccess = Setup-Services
    }
}

if ($overallSuccess) {
    Write-Header "Setup Complete"
    Write-Success "NeoBoi platform setup completed successfully!"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Green
    Write-Host "1. Review and update configuration files in .env.local"
    Write-Host "2. Start services: .\manage.ps1 -Action start"
    Write-Host "3. Verify setup: .\manage.ps1 -Action status"
    Write-Host "4. Run tests: .\manage.ps1 -Action test"
} else {
    Write-Header "Setup Failed"
    Write-Error "Setup completed with errors. Please review the output above."
    exit 1
}