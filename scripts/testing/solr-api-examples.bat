@echo off
echo Solr API Usage Examples
echo =======================
echo.

REM Load environment variables from .env.local
for /f "tokens=*" %%a in (.env.local) do (
    set %%a
)

set BACKEND_URL=http://localhost:3001

echo Base URL: %BACKEND_URL%
echo.

echo Example 1: Index current graph data into Solr
echo Command: curl -X POST %BACKEND_URL%/api/solr/index
echo.

echo Example 2: Search for all nodes containing "test"
echo Command: curl "%BACKEND_URL%/api/solr/search?q=test"
echo.

echo Example 3: Search for suppliers only
echo Command: curl "%BACKEND_URL%/api/solr/search?q=supplier&type=node"
echo.

echo Example 4: Search with pagination (first 5 results)
echo Command: curl "%BACKEND_URL%/api/solr/search?q=*&limit=5"
echo.

echo Example 5: Get index statistics
echo Command: curl %BACKEND_URL%/api/solr/stats
echo.

echo Example 6: Clear the entire index
echo Command: curl -X POST %BACKEND_URL%/api/solr/clear
echo.

echo Interactive Examples:
echo.

set /p choice="Choose an example to run (1-6, or press Enter to exit): "

if "%choice%"=="1" (
    echo Running: Index graph data
    curl -X POST %BACKEND_URL%/api/solr/index
) else if "%choice%"=="2" (
    echo Running: Search for "test"
    curl "%BACKEND_URL%/api/solr/search?q=test"
) else if "%choice%"=="3" (
    echo Running: Search for suppliers
    curl "%BACKEND_URL%/api/solr/search?q=supplier&type=node"
) else if "%choice%"=="4" (
    echo Running: Search with pagination
    curl "%BACKEND_URL%/api/solr/search?q=*&limit=5"
) else if "%choice%"=="5" (
    echo Running: Get statistics
    curl %BACKEND_URL%/api/solr/stats
) else if "%choice%"=="6" (
    echo Running: Clear index
    curl -X POST %BACKEND_URL%/api/solr/clear
) else (
    echo Exiting...
)

echo.
pause