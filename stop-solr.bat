@echo off
echo Stopping Solr service...
echo.

REM Load environment variables from .env.local
for /f "tokens=*" %%a in (.env.local) do (
    set %%a
)

REM Navigate to Solr bin directory
cd /d %SOLR_BIN_PATH%

REM Stop Solr
echo Stopping Solr...
%SOLR_STOP_COMMAND%

echo.
echo Solr stop command executed.
pause