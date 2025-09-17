@echo off
echo Starting Frontend Service...
echo.

cd /d "%~dp0"
cd ..

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Navigate to frontend directory
cd frontend

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

REM Start the frontend server
echo 🚀 Starting frontend server on port 3000...
npm start