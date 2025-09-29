# NeoBoi Platform Test Runner
# Unified testing script for all components

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "unit", "integration", "e2e", "backend", "frontend", "services")]
    [string]$TestType = "all",

    [Parameter(Mandatory=$false)]
    [string]$Pattern,

    [Parameter(Mandatory=$false)]
    [switch]$Coverage,

    [Parameter(Mandatory=$false)]
    [switch]$Verbose,

    [Parameter(Mandatory=$false)]
    [switch]$FailFast,

    [Parameter(Mandatory=$false)]
    [string]$OutputDir = "test-results"
)

# Import utilities
. "$PSScriptRoot\service-utils-enhanced.ps1"

function Write-Header {
    param([string]$Message)
    Write-Host "`n$Message" -ForegroundColor Cyan
    Write-Host ("=" * $Message.Length) -ForegroundColor Cyan
}

function Run-UnitTests {
    Write-Header "Running Unit Tests"

    Push-Location $PROJECT_ROOT
    try {
        Write-Info "Running backend unit tests..."

        $pytestArgs = @("tests/unit/", "-v")

        if ($Pattern) {
            $pytestArgs += @("-k", $Pattern)
        }

        if ($Coverage) {
            $pytestArgs += @("--cov=backend", "--cov-report=term-missing", "--cov-report=html:$OutputDir/coverage")
        }

        if ($FailFast) {
            $pytestArgs += @("-x")
        }

        if ($Verbose) {
            $pytestArgs += @("-s")
        }

        & python -m pytest $pytestArgs

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Unit tests passed"
            return $true
        } else {
            Write-Error "Unit tests failed"
            return $false
        }
    }
    finally {
        Pop-Location
    }
}

function Run-IntegrationTests {
    Write-Header "Running Integration Tests"

    # Ensure services are running for integration tests
    Write-Info "Checking service availability for integration tests..."

    $servicesReady = $true

    # Check backend
    $backendReady = Test-ServicePort -port 8000 -serviceName "Backend" -Quiet
    if (-not $backendReady) {
        Write-Warning "Backend not running. Starting it for integration tests..."
        & "$PSScriptRoot\start-backend.ps1"
        Start-Sleep -Seconds 5
        $backendReady = Test-ServicePort -port 8000 -serviceName "Backend" -Quiet
    }
    $servicesReady = $servicesReady -and $backendReady

    # Check Neo4j (simplified check)
    try {
        $neo4jResponse = Invoke-WebRequest -Uri "http://localhost:7474" -TimeoutSec 5 -ErrorAction SilentlyContinue
        $neo4jReady = $neo4jResponse.StatusCode -eq 200
    }
    catch {
        $neo4jReady = $false
    }
    $servicesReady = $servicesReady -and $neo4jReady

    if (-not $servicesReady) {
        Write-Warning "Some services not available. Integration tests may fail."
    }

    Push-Location $PROJECT_ROOT
    try {
        Write-Info "Running backend integration tests..."

        $pytestArgs = @("tests/integration/", "-v", "-m", "integration")

        if ($Pattern) {
            $pytestArgs += @("-k", $Pattern)
        }

        if ($Coverage) {
            $pytestArgs += @("--cov=backend", "--cov-report=term-missing", "--cov-append")
        }

        if ($FailFast) {
            $pytestArgs += @("-x")
        }

        if ($Verbose) {
            $pytestArgs += @("-s")
        }

        & python -m pytest $pytestArgs

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Integration tests passed"
            return $true
        } else {
            Write-Error "Integration tests failed"
            return $false
        }
    }
    finally {
        Pop-Location
    }
}

function Run-E2ETests {
    Write-Header "Running End-to-End Tests"

    # Ensure all services are running
    Write-Info "Ensuring all services are running for E2E tests..."

    $allServicesReady = $true

    # Start backend if not running
    $backendReady = Test-ServicePort -port 8000 -serviceName "Backend" -Quiet
    if (-not $backendReady) {
        Write-Info "Starting backend for E2E tests..."
        & "$PSScriptRoot\start-backend.ps1"
        Start-Sleep -Seconds 10
    }

    # Start frontend if not running
    $frontendReady = Test-ServicePort -port 3000 -serviceName "Frontend" -Quiet
    if (-not $frontendReady) {
        Write-Info "Starting frontend for E2E tests..."
        & "$PSScriptRoot\start-frontend.ps1"
        Start-Sleep -Seconds 15
    }

    # Wait for services to be fully ready
    Write-Info "Waiting for services to be ready..."
    $backendReady = Wait-ForService -Url "http://localhost:8000/health" -Timeout 30
    $frontendReady = Wait-ForService -Url "http://localhost:3000" -Timeout 30

    $allServicesReady = $backendReady -and $frontendReady

    if (-not $allServicesReady) {
        Write-Error "Not all services are ready for E2E testing. Aborting."
        return $false
    }

    Push-Location $PROJECT_ROOT
    try {
        Write-Info "Running E2E tests..."

        # For now, we'll run Python-based E2E tests
        # In a full implementation, this might include Selenium or Playwright tests
        $pytestArgs = @("tests/e2e/", "-v", "-m", "e2e")

        if ($Pattern) {
            $pytestArgs += @("-k", $Pattern)
        }

        if ($FailFast) {
            $pytestArgs += @("-x")
        }

        if ($Verbose) {
            $pytestArgs += @("-s")
        }

        & python -m pytest $pytestArgs

        if ($LASTEXITCODE -eq 0) {
            Write-Success "E2E tests passed"
            return $true
        } else {
            Write-Error "E2E tests failed"
            return $false
        }
    }
    finally {
        Pop-Location
    }
}

function Run-BackendTests {
    Write-Header "Running Backend Tests"

    Push-Location $BACKEND_DIR
    try {
        Write-Info "Running backend-specific tests..."

        $pytestArgs = @("test_*.py", "-v")

        if ($Pattern) {
            $pytestArgs += @("-k", $Pattern)
        }

        if ($Coverage) {
            $pytestArgs += @("--cov=.", "--cov-report=term-missing", "--cov-report=html:$OutputDir/backend-coverage")
        }

        if ($FailFast) {
            $pytestArgs += @("-x")
        }

        if ($Verbose) {
            $pytestArgs += @("-s")
        }

        & python -m pytest $pytestArgs

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Backend tests passed"
            return $true
        } else {
            Write-Error "Backend tests failed"
            return $false
        }
    }
    finally {
        Pop-Location
    }
}

function Run-FrontendTests {
    Write-Header "Running Frontend Tests"

    Push-Location $FRONTEND_DIR
    try {
        Write-Info "Running frontend tests..."

        if ($Coverage) {
            & npm run test:coverage
        } else {
            & npm test -- --watchAll=false
        }

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Frontend tests passed"
            return $true
        } else {
            Write-Error "Frontend tests failed"
            return $false
        }
    }
    finally {
        Pop-Location
    }
}

function Run-ServiceTests {
    Write-Header "Running Service Tests"

    Write-Info "Testing service connectivity and health..."

    $serviceTests = @(
        @{ Name = "Backend Health"; Url = "http://localhost:8000/health"; ExpectedStatus = 200 },
        @{ Name = "Frontend"; Url = "http://localhost:3000"; ExpectedStatus = 200 },
        @{ Name = "Solr Admin"; Url = "http://localhost:8983/solr/admin/info/system"; ExpectedStatus = 200 },
        @{ Name = "OLLAMA API"; Url = "http://localhost:11434/api/tags"; ExpectedStatus = 200 }
    )

    $allPassed = $true

    foreach ($test in $serviceTests) {
        try {
            $response = Invoke-WebRequest -Uri $test.Url -TimeoutSec 10 -ErrorAction Stop
            if ($response.StatusCode -eq $test.ExpectedStatus) {
                Write-Success "$($test.Name) - OK"
            } else {
                Write-Error "$($test.Name) - Status $($response.StatusCode) (expected $($test.ExpectedStatus))"
                $allPassed = $false
            }
        }
        catch {
            Write-Error "$($test.Name) - Failed: $($_.Exception.Message)"
            $allPassed = $false
        }
    }

    if ($allPassed) {
        Write-Success "All service tests passed"
        return $true
    } else {
        Write-Error "Some service tests failed"
        return $false
    }
}

function Generate-TestReport {
    Write-Header "Generating Test Report"

    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir | Out-Null
    }

    $reportPath = Join-Path $OutputDir "test-summary.txt"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    $report = @"
NeoBoi Platform Test Report
Generated: $timestamp
Test Type: $TestType
Coverage: $($Coverage.ToString())
Pattern: $($Pattern ?? "None")

Test Results Summary:
"@

    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Success "Test report generated: $reportPath"
}

# Main execution logic
Write-Header "NeoBoi Platform Test Runner"

# Create output directory if coverage is enabled
if ($Coverage -and -not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$overallSuccess = $true

switch ($TestType) {
    "all" {
        $overallSuccess = $overallSuccess -and (Run-UnitTests)
        $overallSuccess = $overallSuccess -and (Run-IntegrationTests)
        $overallSuccess = $overallSuccess -and (Run-E2ETests)
        $overallSuccess = $overallSuccess -and (Run-ServiceTests)
    }
    "unit" {
        $overallSuccess = Run-UnitTests
    }
    "integration" {
        $overallSuccess = Run-IntegrationTests
    }
    "e2e" {
        $overallSuccess = Run-E2ETests
    }
    "backend" {
        $overallSuccess = Run-BackendTests
    }
    "frontend" {
        $overallSuccess = Run-FrontendTests
    }
    "services" {
        $overallSuccess = Run-ServiceTests
    }
}

# Generate test report if coverage was enabled
if ($Coverage) {
    Generate-TestReport
}

if ($overallSuccess) {
    Write-Header "All Tests Completed Successfully"
    Write-Success "Test suite completed with no failures"
    exit 0
} else {
    Write-Header "Test Suite Completed with Failures"
    Write-Error "Some tests failed. Check output above for details."
    exit 1
}