@echo off
echo Starting Backend Service...
cd /d "d:\Software\boiSoftware\neoboi"
set PYTHONPATH=d:\Software\boiSoftware\neoboi;d:\Software\boiSoftware\neoboi\backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 3001
pause