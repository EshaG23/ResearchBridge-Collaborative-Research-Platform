@echo off
setlocal
cd /d "%~dp0"
set "DEMO_PYTHON=.venv\Scripts\python.exe"
if not exist "%DEMO_PYTHON%" set "DEMO_PYTHON=..\..\work\.venv\Scripts\python.exe"
if not exist "%DEMO_PYTHON%" (
 echo Python environment missing. Run setup-demo.cmd first.
 exit /b 1
)
"%DEMO_PYTHON%" scripts\reset_demo.py
exit /b %errorlevel%
