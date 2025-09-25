@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

echo ====================================================
echo  NeoBoi Backend Python Environment Setup
echo ====================================================

for %%I in ("%~dp0\..\..") do set PROJECT_ROOT=%%~fI
set BACKEND_DIR=%PROJECT_ROOT%\backend
set VENV_DIR=%BACKEND_DIR%\venv

echo [info] Using project root: %PROJECT_ROOT%
if not exist "%BACKEND_DIR%\requirements.txt" (
	echo [error] Unable to find backend\requirements.txt. Run this script inside the cloned repository.
	exit /b 1
)

where /q python >nul 2>&1
if errorlevel 1 (
	echo [error] Python 3.9+ is required but was not found in PATH.
	echo         Install Python from https://www.python.org/downloads/ and re-run this script.
	exit /b 1
)

echo.
echo [Step 1] Create (or reuse) a virtual environment
if not exist "%VENV_DIR%" (
	echo         Creating venv at %VENV_DIR% ...
	pushd "%BACKEND_DIR%" >nul
	python -m venv venv
	if errorlevel 1 (
		echo [error] Failed to create the virtual environment. Check your Python install and rerun.
		popd >nul
		exit /b 1
	)
	popd >nul
) else (
	echo         Existing virtual environment detected. Reusing it.
)

echo.
echo [Step 2] Activate the virtual environment and install backend dependencies
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
	echo [error] Could not activate the virtual environment.
	exit /b 1
)

pushd "%BACKEND_DIR%" >nul
echo         Installing requirements from backend\requirements.txt ...
pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
	echo [error] pip install failed. Resolve the issue above and re-run this script.
	popd >nul
	exit /b 1
)
popd >nul

echo.
echo [Step 3] Verify key Python dependencies are importable
pushd "%BACKEND_DIR%" >nul
python -c "import fastapi, neo4j, requests, dotenv; print('Backend dependencies imported successfully.')"
if errorlevel 1 (
	echo [warn ] One or more core packages failed to import. Inspect the errors above.
) else (
	echo [ ok  ] Python runtime and required packages look good.
)
popd >nul

echo.
echo [Next] When finished, deactivate the virtual environment with:
echo         call %VENV_DIR%\Scripts\deactivate.bat
echo         (the shell created by this script closes automatically on exit.)

echo.
echo Setup complete. Backend Python dependencies are ready.
endlocal
pause