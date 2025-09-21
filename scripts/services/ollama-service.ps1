# Ollama Service Management Script
# This script helps manage the Ollama offline LLM service

param(
    [string]$Action = "status",
    [string]$Model = "llama2:7b"
)

$OLLAMA_PATH = $env:OLLAMA_PATH
if (-not $OLLAMA_PATH) {
    $OLLAMA_PATH = "$env:USERPROFILE\AppData\Local\Programs\Ollama\ollama.exe"
}

$OLLAMA_HOST = $env:OLLAMA_HOST
if (-not $OLLAMA_HOST) {
    $OLLAMA_HOST = "http://localhost:11434"
}

function Test-OllamaConnection {
    try {
        $response = Invoke-WebRequest -Uri "$OLLAMA_HOST/api/tags" -TimeoutSec 5
        return $true
    }
    catch {
        return $false
    }
}

function Get-OllamaStatus {
    Write-Host "=== Ollama Service Status ===" -ForegroundColor Cyan

    if (Test-OllamaConnection) {
        Write-Host "Ollama service is running" -ForegroundColor Green

        try {
            $models = Invoke-WebRequest -Uri "$OLLAMA_HOST/api/tags" | ConvertFrom-Json
            Write-Host "Available models:" -ForegroundColor Yellow
            foreach ($model in $models.models) {
                Write-Host "  - $($model.name)" -ForegroundColor White
            }
        }
        catch {
            Write-Host "Could not retrieve model list" -ForegroundColor Red
        }

        try {
            $running = Invoke-WebRequest -Uri "$OLLAMA_HOST/api/ps" | ConvertFrom-Json
            if ($running.models) {
                Write-Host "Running models:" -ForegroundColor Yellow
                foreach ($model in $running.models) {
                    Write-Host "  - $($model.name) (Size: $($model.size) bytes)" -ForegroundColor White
                }
            } else {
                Write-Host "No models currently running" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "Could not check running models" -ForegroundColor Red
        }
    }
    else {
        Write-Host "Ollama service is not running" -ForegroundColor Red
        Write-Host "Start it with: ollama serve" -ForegroundColor Yellow
    }
}

function Start-OllamaService {
    Write-Host "Starting Ollama service..." -ForegroundColor Cyan

    if (Test-OllamaConnection) {
        Write-Host "Ollama is already running" -ForegroundColor Green
        return
    }

    if (Test-Path $OLLAMA_PATH) {
        try {
            Write-Host "Starting Ollama service..."
            Start-Process -FilePath $OLLAMA_PATH -ArgumentList "serve" -WindowStyle Hidden
            Start-Sleep -Seconds 3

            if (Test-OllamaConnection) {
                Write-Host "Ollama service started successfully" -ForegroundColor Green
            } else {
                Write-Host "Failed to start Ollama service" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "Error starting Ollama: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "Ollama executable not found at: $OLLAMA_PATH" -ForegroundColor Red
        Write-Host "Please install Ollama from: https://ollama.ai/download" -ForegroundColor Yellow
    }
}

function Stop-OllamaService {
    Write-Host "Stopping Ollama service..." -ForegroundColor Cyan

    try {
        Invoke-WebRequest -Uri "$OLLAMA_HOST/api/stop" -Method POST | Out-Null
        $ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
        if ($ollamaProcess) {
            Stop-Process -Name "ollama" -Force
            Write-Host "Ollama service stopped" -ForegroundColor Green
        } else {
            Write-Host "Ollama process not found" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Error stopping Ollama: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Install-Model {
    param([string]$ModelName)

    Write-Host "Installing model: $ModelName" -ForegroundColor Cyan

    if (-not (Test-OllamaConnection)) {
        Write-Host "Ollama service is not running. Starting it first..." -ForegroundColor Yellow
        Start-OllamaService
        Start-Sleep -Seconds 3
    }

    try {
        $process = Start-Process -FilePath $OLLAMA_PATH -ArgumentList "pull", $ModelName -WindowStyle Hidden -PassThru
        $process.WaitForExit()

        if ($process.ExitCode -eq 0) {
            Write-Host "Model $ModelName installed successfully" -ForegroundColor Green
        } else {
            Write-Host "Failed to install model $ModelName" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "Error installing model: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function List-Models {
    Write-Host "=== Available Models ===" -ForegroundColor Cyan

    if (Test-OllamaConnection) {
        try {
            $models = Invoke-WebRequest -Uri "$OLLAMA_HOST/api/tags" | ConvertFrom-Json
            foreach ($model in $models.models) {
                Write-Host "$($model.name) - Size: $([math]::Round($model.size / 1MB, 2)) MB" -ForegroundColor White
            }
        }
        catch {
            Write-Host "Could not retrieve models" -ForegroundColor Red
        }
    } else {
        Write-Host "Ollama service is not running" -ForegroundColor Red
    }
}

function Test-Model {
    param([string]$ModelName)

    Write-Host "Testing model: $ModelName" -ForegroundColor Cyan

    if (-not (Test-OllamaConnection)) {
        Write-Host "Ollama service is not running" -ForegroundColor Red
        return
    }

    try {
        $body = @{
            model = $ModelName
            prompt = "Hello! Please respond with a brief greeting and tell me what model you are."
            stream = $false
        } | ConvertTo-Json

        $response = Invoke-WebRequest -Uri "$OLLAMA_HOST/api/generate" -Method POST -Body $body -ContentType "application/json"
        $result = $response.Content | ConvertFrom-Json

        Write-Host "Model Response:" -ForegroundColor Green
        Write-Host $result.response -ForegroundColor White
        Write-Host "Response time: $([math]::Round($result.total_duration / 1e9, 2)) seconds" -ForegroundColor Yellow
    }
    catch {
        Write-Host "Error testing model: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main script logic
switch ($Action.ToLower()) {
    "start" {
        Start-OllamaService
    }
    "stop" {
        Stop-OllamaService
    }
    "status" {
        Get-OllamaStatus
    }
    "install" {
        if ($Model) {
            Install-Model -ModelName $Model
        } else {
            Write-Host "Please specify a model name with -Model parameter" -ForegroundColor Red
        }
    }
    "list" {
        List-Models
    }
    "test" {
        if ($Model) {
            Test-Model -ModelName $Model
        } else {
            Write-Host "Please specify a model name with -Model parameter" -ForegroundColor Red
        }
    }
    default {
        Write-Host "Usage: .\ollama-service.ps1 -Action (action) [-Model (model_name)]" -ForegroundColor Yellow
        Write-Host "Actions: start, stop, status, install, list, test" -ForegroundColor Yellow
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\ollama-service.ps1 -Action status" -ForegroundColor White
        Write-Host "  .\ollama-service.ps1 -Action install -Model llama2:7b" -ForegroundColor White
        Write-Host "  .\ollama-service.ps1 -Action test -Model mistral:7b" -ForegroundColor White
    }
}