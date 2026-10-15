@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 goto fail
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo Ready. Double-click go-webui.bat to launch AquaSync.
pause
exit /b 0
:fail
echo Installation failed. Install Python 3.12 with Python Launcher, then try again.
pause
exit /b 1
