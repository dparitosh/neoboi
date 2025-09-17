@echo off
echo 🔍 Checking Neo4j Graph Visualization Services Status...
echo.

REM Function to check service
:check_service
setlocal enabledelayedexpansion
set "service_name=%~1"
set "service_url=%~2"
set "service_port=%~3"

echo|set /p="Checking %service_name%..."
curl -s --max-time 5 "%service_url%" >nul 2>&1
if errorlevel 1 (
    echo  ❌ NOT RUNNING (Port: %service_port%)
    endlocal & set "status_%service_name%=0"
) else (
    echo  ✅ RUNNING (Port: %service_port%)
    endlocal & set "status_%service_name%=1"
)
goto :eof

REM Check all services
call :check_service "Frontend Service" "http://localhost:3000/health" "3000"
call :check_service "Backend API Service" "http://localhost:3001/health" "3001"
call :check_service "Apache Solr" "http://localhost:8983/solr/admin/cores" "8983"

REM Check Neo4j port
echo|set /p="Checking Neo4j Database..."
netstat -an | findstr ":7687" >nul 2>&1
if errorlevel 1 (
    echo  ❌ NOT RUNNING (Port: 7687)
    set "status_neo4j=0"
) else (
    echo  ✅ RUNNING (Port: 7687)
    set "status_neo4j=1"
)

echo.
echo 📊 Service Summary:
if defined status_Frontend Service (
    if !status_Frontend Service! equ 1 (
        echo    Frontend: Running
    ) else (
        echo    Frontend: Stopped
    )
) else (
    echo    Frontend: Stopped
)

if defined status_Backend API Service (
    if !status_Backend API Service! equ 1 (
        echo    Backend:  Running
    ) else (
        echo    Backend:  Stopped
    )
) else (
    echo    Backend:  Stopped
)

if defined status_Apache Solr (
    if !status_Apache Solr! equ 1 (
        echo    Solr:     Running
    ) else (
        echo    Solr:     Stopped
    )
) else (
    echo    Solr:     Stopped
)

if !status_neo4j! equ 1 (
    echo    Neo4j:    Running
) else (
    echo    Neo4j:    Stopped
)

REM Count running services
set /a "running_count=0"
if defined status_Frontend Service if !status_Frontend Service! equ 1 set /a "running_count+=1"
if defined status_Backend API Service if !status_Backend API Service! equ 1 set /a "running_count+=1"
if defined status_Apache Solr if !status_Apache Solr! equ 1 set /a "running_count+=1"
if !status_neo4j! equ 1 set /a "running_count+=1"

echo.
echo 🎯 %running_count%/4 services are running

if %running_count% equ 4 (
    echo.
    echo 🌐 Access URLs:
    echo    📊 Frontend: http://localhost:3000
    echo    🔗 Backend API: http://localhost:3001
    echo    🔍 Solr Admin: http://localhost:8983
)

echo.
pause