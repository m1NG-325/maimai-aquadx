@echo off
setlocal
cd /d "%~dp0"
if exist "dist\v1.0\AquaSync.exe" (
  start "" "dist\v1.0\AquaSync.exe"
  exit /b 0
)
if exist "AquaSync.exe" (
  start "" "AquaSync.exe"
  exit /b 0
)
if exist ".venv\Scripts\pythonw.exe" (
  start "" ".venv\Scripts\pythonw.exe" desktop.py
  exit /b 0
)
echo Desktop runtime missing. Install requirements-desktop.txt or use AquaSync.exe.
pause
