@echo off
echo Stopping Neo4j Graph Visualization App...
echo.

REM Find and kill Node.js processes running server.js
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq node.exe" /FO CSV /NH') do (
    REM Check if this is our server process by looking for the server.js in the command line
    tasklist /FI "PID eq %%i" /FO LIST | findstr /C:"server.js" >nul
    if not errorlevel 1 (
        echo Found server process (PID: %%i). Stopping...
        taskkill /PID %%i /F >nul 2>&1
        if errorlevel 0 (
            echo Server stopped successfully.
        ) else (
            echo Failed to stop server process.
        )
        goto :found
    )
)

REM If no specific server process found, try to kill all node processes
echo No specific server process found. Attempting to stop all Node.js processes...
taskkill /IM node.exe /F >nul 2>&1
if errorlevel 0 (
    echo All Node.js processes stopped.
) else (
    echo No Node.js processes found running.
)

:found
echo.
echo Done.
timeout /t 2 >nul