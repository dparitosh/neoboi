@echo off
echo Testing Neo4j Graph Visualization Services...
echo.

echo Checking Frontend (port 3000)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000/health' -Method GET; Write-Host '✓ Frontend is responding' } catch { Write-Host '✗ Frontend not responding' }"

echo.
echo Checking Backend (port 3001)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3001/docs' -Method GET; Write-Host '✓ Backend is responding' } catch { Write-Host '✗ Backend not responding' }"

echo.
echo Checking Neo4j Graph API...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3001/api/graph' -Method GET; Write-Host '✓ Graph API is responding' } catch { Write-Host '✗ Graph API not responding' }"

echo.
echo Checking Solr (port 8983)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8983/solr/admin/info/system' -Method GET; Write-Host '✓ Solr is responding' } catch { Write-Host '✗ Solr not responding' }"

echo.
echo Checking Solr API endpoints...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3001/api/solr/stats' -Method GET; Write-Host '✓ Solr API is responding' } catch { Write-Host '✗ Solr API not responding' }"

echo.
echo Service check complete.
pause