# Setup Neo4j and Solr Services
Write-Host "Setting up Neo4j and Apache Solr services..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot
Set-Location ..

# Function to download and install Neo4j
function Install-Neo4j {
    Write-Host "Installing Neo4j..." -ForegroundColor Cyan

    $neo4jVersion = "5.20.0"
    $neo4jUrl = "https://neo4j.com/artifact.php?name=neo4j-community-$neo4jVersion-windows.zip"
    $neo4jZip = "neo4j-community-$neo4jVersion-windows.zip"
    $neo4jDir = "neo4j-community-$neo4jVersion"

    # Download Neo4j
    Write-Host "Downloading Neo4j $neo4jVersion..."
    Invoke-WebRequest -Uri $neo4jUrl -OutFile $neo4jZip

    # Extract Neo4j
    Write-Host "Extracting Neo4j..."
    Expand-Archive -Path $neo4jZip -DestinationPath "." -Force

    # Move to standard location
    if (!(Test-Path "C:\neo4j")) {
        New-Item -ItemType Directory -Path "C:\neo4j" -Force
    }
    Move-Item -Path $neo4jDir -Destination "C:\neo4j\$neo4jDir" -Force

    # Clean up
    Remove-Item $neo4jZip -Force

    Write-Host "Neo4j installed successfully!" -ForegroundColor Green
    return "C:\neo4j\$neo4jDir"
}

# Function to download and install Apache Solr
function Install-Solr {
    Write-Host "Installing Apache Solr..." -ForegroundColor Cyan

    $solrVersion = "9.4.1"
    $solrUrl = "https://downloads.apache.org/solr/solr/$solrVersion/solr-$solrVersion.zip"
    $solrZip = "solr-$solrVersion.zip"
    $solrDir = "solr-$solrVersion"

    # Download Solr
    Write-Host "Downloading Apache Solr $solrVersion..."
    Invoke-WebRequest -Uri $solrUrl -OutFile $solrZip

    # Extract Solr
    Write-Host "Extracting Solr..."
    Expand-Archive -Path $solrZip -DestinationPath "." -Force

    # Move to standard location
    if (!(Test-Path "C:\solr")) {
        New-Item -ItemType Directory -Path "C:\solr" -Force
    }
    Move-Item -Path $solrDir -Destination "C:\solr\$solrDir" -Force

    # Clean up
    Remove-Item $solrZip -Force

    Write-Host "Apache Solr installed successfully!" -ForegroundColor Green
    return "C:\solr\$solrDir"
}

# Check if services are already installed
$neo4jInstalled = Test-Path "C:\neo4j"
$solrInstalled = Test-Path "C:\solr"

if ($neo4jInstalled -and $solrInstalled) {
    Write-Host "Neo4j and Solr are already installed!" -ForegroundColor Green
} else {
    # Install Neo4j if not present
    if (!$neo4jInstalled) {
        $neo4jPath = Install-Neo4j
    } else {
        Write-Host "Neo4j is already installed." -ForegroundColor Yellow
        $neo4jPath = Get-ChildItem "C:\neo4j" | Select-Object -First 1 -ExpandProperty FullName
    }

    # Install Solr if not present
    if (!$solrInstalled) {
        $solrPath = Install-Solr
    } else {
        Write-Host "Apache Solr is already installed." -ForegroundColor Yellow
        $solrPath = Get-ChildItem "C:\solr" | Select-Object -First 1 -ExpandProperty FullName
    }
}

Write-Host ""
Write-Host "Setup complete! You can now start the services using:" -ForegroundColor Green
Write-Host "  .\start-neo4j.ps1" -ForegroundColor Cyan
Write-Host "  .\start-solr.ps1" -ForegroundColor Cyan
Write-Host "  .\start-all.ps1" -ForegroundColor Cyan