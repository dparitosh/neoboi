@echo off
echo Starting All Services (Backend + Frontend)...
echo.

cd /d "%~dp0"
cd ..

echo Starting Python FastAPI Backend...
start "Backend Service" cmd /c ".\install\start-backend.bat"

REM Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

echo Starting React Frontend...
start "Frontend Service" cmd /c ".\install\start-frontend.bat"

echo.
echo All services started!
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:3001
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping all services...
call .\install\stop-frontend.bat
call .\install\stop-backend.bat

echo All services stopped.
pause