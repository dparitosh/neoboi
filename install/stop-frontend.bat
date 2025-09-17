@echo off
echo Stopping Frontend Service...
echo.

REM Find and stop Node.js processes running on port 3000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo Stopping process with PID: %%a
    taskkill /PID %%a /F >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Frontend service stopped.
    ) else (
        echo ℹ️  No frontend service found running on port 3000.
    )
    goto :done
)

echo ℹ️  No frontend service found running on port 3000.
:done
echo.
pause