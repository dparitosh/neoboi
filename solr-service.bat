@echo off
if "%1"=="" (
    echo Usage: solr-service.bat [start^|stop^|status^|restart]
    echo.
    echo Examples:
    echo   solr-service.bat start   - Start Solr service
    echo   solr-service.bat stop    - Stop Solr service
    echo   solr-service.bat status  - Check Solr status
    echo   solr-service.bat restart - Restart Solr service
    echo.
    pause
    exit /b 1
)

REM Load environment variables from .env.local
for /f "tokens=*" %%a in (.env.local) do (
    set %%a
)

REM Navigate to Solr bin directory
cd /d %SOLR_BIN_PATH%

echo Solr Service Management
echo =======================
echo Solr Home: %SOLR_HOME%
echo Solr Port: %SOLR_PORT%
echo.

if "%1"=="start" (
    echo Starting Solr service...
    %SOLR_START_COMMAND%
    echo.
    echo Solr start command executed.
) else if "%1"=="stop" (
    echo Stopping Solr service...
    %SOLR_STOP_COMMAND%
    echo.
    echo Solr stop command executed.
) else if "%1"=="status" (
    echo Checking Solr status...
    %SOLR_STATUS_COMMAND%
) else if "%1"=="restart" (
    echo Restarting Solr service...
    echo Stopping Solr...
    %SOLR_STOP_COMMAND%
    echo.
    timeout /t 3 /nobreak > nul
    echo Starting Solr...
    %SOLR_START_COMMAND%
    echo.
    echo Solr restart completed.
) else (
    echo Error: Invalid command '%1'
    echo Valid commands: start, stop, status, restart
    exit /b 1
)

echo.
pause