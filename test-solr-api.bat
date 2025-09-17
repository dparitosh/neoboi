@echo off
echo Testing Solr Search and Query REST API...
echo.

REM Load environment variables from .env.local
for /f "tokens=*" %%a in (.env.local) do (
    set %%a
)

set BACKEND_URL=http://localhost:3001

echo Backend URL: %BACKEND_URL%
echo Solr URL: %SOLR_URL%
echo.

echo 1. Testing Solr stats endpoint...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%BACKEND_URL%/api/solr/stats' -Method GET; Write-Host '✓ Solr stats: OK'; ($response.Content | ConvertFrom-Json).solr_stats } catch { Write-Host '✗ Solr stats: ERROR -' $_.Exception.Message }"

echo.
echo 2. Testing Solr index endpoint (this will index current graph data)...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%BACKEND_URL%/api/solr/index' -Method POST; Write-Host '✓ Solr index: OK'; ($response.Content | ConvertFrom-Json).message } catch { Write-Host '✗ Solr index: ERROR -' $_.Exception.Message }"

echo.
echo 3. Testing Solr search endpoint...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%BACKEND_URL%/api/solr/search?q=test' -Method GET; Write-Host '✓ Solr search: OK'; $result = ($response.Content | ConvertFrom-Json); Write-Host ('Found ' + $result.total + ' results') } catch { Write-Host '✗ Solr search: ERROR -' $_.Exception.Message }"

echo.
echo 4. Testing Solr search with filters...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%BACKEND_URL%/api/solr/search?q=node&type=node&limit=5' -Method GET; Write-Host '✓ Solr filtered search: OK'; $result = ($response.Content | ConvertFrom-Json); Write-Host ('Found ' + $result.total + ' filtered results') } catch { Write-Host '✗ Solr filtered search: ERROR -' $_.Exception.Message }"

echo.
echo 5. Testing Solr clear index endpoint...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%BACKEND_URL%/api/solr/clear' -Method POST; Write-Host '✓ Solr clear: OK'; ($response.Content | ConvertFrom-Json).message } catch { Write-Host '✗ Solr clear: ERROR -' $_.Exception.Message }"

echo.
echo Solr API testing complete.
echo.
echo Available endpoints:
echo - GET  %BACKEND_URL%/api/solr/stats     - Get index statistics
echo - POST %BACKEND_URL%/api/solr/index     - Index graph data
echo - GET  %BACKEND_URL%/api/solr/search?q=QUERY - Search indexed data
echo - POST %BACKEND_URL%/api/solr/clear     - Clear index
echo.
pause