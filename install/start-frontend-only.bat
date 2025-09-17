@echo off
echo Starting Frontend Service (Independent Mode)...
echo Note: This will work even if backend is not running
echo.

cd /d "%~dp0"
cd ..
cd frontend

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

REM Start the frontend server
echo 🚀 Starting frontend server on port 3000...
echo 📊 Frontend: http://localhost:3000
echo 🔗 Backend API: Will proxy to http://localhost:3001 (if available)
echo.
npm start