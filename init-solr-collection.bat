@echo off
echo Initializing Solr collection for Neo4j Graph Visualization...
echo.

REM Load environment variables from .env.local
for /f "tokens=*" %%a in (.env.local) do (
    set %%a
)

REM Navigate to Solr bin directory
cd /d %SOLR_BIN_PATH%

echo Checking if collection '%SOLR_COLLECTION%' exists...

REM Check if collection exists
curl -s "%SOLR_URL%/solr/admin/collections?action=LIST&wt=json" | findstr /C:"%SOLR_COLLECTION%" >nul
if %errorlevel% neq 0 (
    echo Collection '%SOLR_COLLECTION%' does not exist. Creating it...
    cmd /c solr.cmd create -c %SOLR_COLLECTION%
    if %errorlevel% equ 0 (
        echo ✓ Successfully created collection '%SOLR_COLLECTION%'
    ) else (
        echo ✗ Failed to create collection '%SOLR_COLLECTION%'
        exit /b 1
    )
) else (
    echo ✓ Collection '%SOLR_COLLECTION%' already exists
)

echo.
echo Solr collection initialization complete.
echo Collection: %SOLR_COLLECTION%
echo Solr URL: %SOLR_URL%
pause