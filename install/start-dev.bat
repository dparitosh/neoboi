@echo off
echo Starting Neo4j Graph Visualization App (Development Mode)...
echo.

cd /d "%~dp0"
cd ..

echo Starting Python FastAPI backend (Development Mode)...
cd backend
python main.py

echo.
echo Development server stopped.
pause