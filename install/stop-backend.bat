@echo off
echo Stopping Backend Service...

REM Find and stop Python processes running on port 3001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001 ^| findstr LISTENING') do (
    echo Stopping process with PID: %%a
    taskkill /PID %%a /F >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Backend service stopped.
    ) else (
        echo ℹ️  No backend service found running on port 3001.
    )
    goto :done
)

echo ℹ️  No backend service found running on port 3001.
:done