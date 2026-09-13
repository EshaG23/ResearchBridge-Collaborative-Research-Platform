@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
set "RESEARCHBRIDGE_AUTH_MODE=demo"
.venv\Scripts\python.exe manage.py migrate --noinput
if errorlevel 1 exit /b 1
echo Setup complete. Use start-demo.cmd. This does not seed or reset your data.
