@echo off
echo Restarting Solr service...
echo.

REM Load environment variables from .env.local
for /f "tokens=*" %%a in (.env.local) do (
    set %%a
)

REM Navigate to Solr bin directory
cd /d %SOLR_BIN_PATH%

REM Stop Solr first
echo Stopping Solr...
%SOLR_STOP_COMMAND%

REM Wait a moment
timeout /t 3 /nobreak > nul

REM Start Solr
echo Starting Solr...
%SOLR_START_COMMAND%

echo.
echo Solr restart completed.
echo Check status with: status-solr.bat
pause