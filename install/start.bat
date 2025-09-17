@echo off
echo Starting Backend API Service...
echo.

cd /d "%~dp0"
cd ..

echo Starting Python FastAPI Backend...
cd backend
python main.py

echo.
echo Backend service stopped.
pause