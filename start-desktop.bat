@echo off
setlocal
cd /d "%~dp0"
if exist "dist\v2.0\AquaSync.exe" (
  start "" "dist\v2.0\AquaSync.exe"
  exit /b 0
)
if exist "dist\v1.2\AquaSync.exe" (
  start "" "dist\v1.2\AquaSync.exe"
  exit /b 0
)
if exist "dist\v1.1\AquaSync-latest.exe" (
  start "" "dist\v1.1\AquaSync-latest.exe"
  exit /b 0
)
if exist "dist\score-sorting\AquaSync.exe" (
  start "" "dist\score-sorting\AquaSync.exe"
  exit /b 0
)
if exist "dist\score-cards\AquaSync.exe" (
  start "" "dist\score-cards\AquaSync.exe"
  exit /b 0
)
if exist "dist\unified-catalog\AquaSync.exe" (
  start "" "dist\unified-catalog\AquaSync.exe"
  exit /b 0
)
if exist "dist\recommend-scopes\AquaSync.exe" (
  start "" "dist\recommend-scopes\AquaSync.exe"
  exit /b 0
)
if exist "dist\rating-table\AquaSync.exe" (
  start "" "dist\rating-table\AquaSync.exe"
  exit /b 0
)
if exist "dist\v1.1\AquaSync.exe" (
  start "" "dist\v1.1\AquaSync.exe"
  exit /b 0
)
if exist "dist\milk-true\AquaSync.exe" (
  start "" "dist\milk-true\AquaSync.exe"
  exit /b 0
)
if exist "dist\plate-scopes\AquaSync.exe" (
  start "" "dist\plate-scopes\AquaSync.exe"
  exit /b 0
)
if exist "dist\v1.0.1\AquaSync.exe" (
  start "" "dist\v1.0.1\AquaSync.exe"
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
