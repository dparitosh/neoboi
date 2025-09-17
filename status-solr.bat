@echo off
echo Checking Solr service status...
echo.

REM Load environment variables from .env.local
for /f "tokens=*" %%a in (.env.local) do (
    set %%a
)

REM Navigate to Solr bin directory
cd /d %SOLR_BIN_PATH%

REM Check Solr status
echo Solr Status:
%SOLR_STATUS_COMMAND%

echo.
echo Solr home: %SOLR_HOME%
echo Solr port: %SOLR_PORT%
pause