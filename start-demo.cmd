@echo off
setlocal
cd /d "%~dp0"
set "RESEARCHBRIDGE_AUTH_MODE=demo"
set "PYTHON=.venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=..\..\work\.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
 echo Python environment missing. Run setup-demo.cmd first.
 pause
 exit /b 1
)
"%PYTHON%" manage.py migrate --noinput
if errorlevel 1 exit /b 1
echo Open http://127.0.0.1:8000/
"%PYTHON%" manage.py runserver 127.0.0.1:8000 --noreload
