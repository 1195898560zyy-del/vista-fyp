@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   VISTA Backend
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found. Install Python 3.11+
  pause
  exit /b 1
)

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
  echo [CLEANUP] Stopping old process PID=%%p
  taskkill /PID %%p /F >nul 2>&1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating virtual environment...
  python -m venv .venv
  call .venv\Scripts\activate.bat
  echo [2/3] Installing dependencies...
  pip install -r requirements.txt
) else (
  call .venv\Scripts\activate.bat
)

if not exist ".env" (
  echo [WARN] .env not found, copying from template...
  copy .env.example .env
  echo        Edit .env with your API keys, then run this file again.
  pause
  exit /b 1
)

echo [3/3] Starting server...
echo.
echo   Open in browser: http://localhost:3000
echo   Keep this window open. Press Ctrl+C to stop.
echo.

python run.py
pause
