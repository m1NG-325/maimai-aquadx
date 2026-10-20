@echo off
setlocal
cd /d "%~dp0"
if exist "dist\v2.1\AquaSync\AquaSync.exe" (
  start "" "dist\v2.1\AquaSync\AquaSync.exe"
  exit /b 0
)
if exist ".venv\Scripts\pythonw.exe" (
  start "" ".venv\Scripts\pythonw.exe" desktop_studio.py
  exit /b 0
)
echo Local Python runtime missing. Install requirements-desktop.txt first.
pause
