@echo off
echo Restarting Neo4j Graph Visualization App...
echo.

REM Stop the server first
call stop.bat

REM Wait a moment for the server to fully stop
timeout /t 3 /nobreak >nul

REM Start the server
call start.bat