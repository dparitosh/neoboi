@echo off
echo Starting Solr service...
echo.

REM Load environment variables from .env.local
for /f "tokens=*" %%a in (.env.local) do (
    set %%a
)

REM Navigate to Solr bin directory
cd /d %SOLR_BIN_PATH%

REM Start Solr
echo Starting Solr on port %SOLR_PORT%...
%SOLR_START_COMMAND%

echo.
echo Solr start command executed.
echo Check status with: status-solr.bat
pause