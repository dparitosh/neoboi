@echo off
echo Starting Backend Service...
cd /d "D:\Software\boiSoftware\neoboi\backend"
set PYTHONPATH=D:\Software\boiSoftware\neoboi
echo PYTHONPATH set to: %PYTHONPATH%
echo Current directory: %CD%
python -m uvicorn main:app --host 127.0.0.1 --port 3001 --reload
pause