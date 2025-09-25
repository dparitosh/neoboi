@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

echo ====================================================
echo  NeoBoi Offline LLM (Ollama) Setup Helper
echo ====================================================

rem Resolve project and frontend directories
for %%I in ("%~dp0\..\..") do set PROJECT_ROOT=%%~fI
set FRONTEND_DIR=%PROJECT_ROOT%\frontend

echo [info] Using project root: %PROJECT_ROOT%
if not exist "%FRONTEND_DIR%\package.json" (
	echo [error] Unable to find frontend\package.json. Run this script from the cloned repository.
	exit /b 1
)

echo.
echo [Step 1] Check required CLI tools
where /q npm  >nul 2>&1
if errorlevel 1 (
	echo [warn ] npm was not found in PATH. Install Node.js 16+ from https://nodejs.org/ and re-run.
)
where /q ollama  >nul 2>&1
if errorlevel 1 (
	echo [warn ] Ollama CLI not detected. Download from https://ollama.ai/download and install before continuing.
) else (
	echo [ ok  ] Ollama CLI detected.
)

echo.
echo [Step 2] Install or update Ollama models (run in a separate terminal if needed)
echo         ollama pull llama2
echo         ollama pull mistral
echo.
echo         These pulls are idempotent; rerun them anytime new model versions ship.

echo.
echo [Step 3] Install frontend dependencies used by the chat UI
pushd "%FRONTEND_DIR%" >nul
if exist node_modules (
	echo [info] Existing node_modules detected. Running npm install to ensure packages are up-to-date...
) else (
	echo [info] Installing Node.js dependencies...
)
call npm install
if errorlevel 1 (
	echo [error] npm install failed. Resolve the error above and rerun the script.
	popd >nul
	exit /b 1
)
popd >nul

echo.
echo [Step 4] (Optional) Start Ollama in another terminal if it is not already running
echo         ollama serve

echo.
echo [Next] Start the NeoBoi services once Ollama is serving models:
echo         powershell -ExecutionPolicy Bypass -File .\scripts\services\start-all.ps1
echo         or start the backend/frontend individually via the scripts in scripts\services\.

echo.
echo Setup complete. Your offline LLM dependencies are ready.
endlocal
pause