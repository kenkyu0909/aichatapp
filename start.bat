@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating Python virtual environment...
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -m venv .venv
  ) else (
    python -m venv .venv
  )
  if errorlevel 1 goto :error
)
echo [2/3] Installing Python dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error
if not exist ".env" copy ".env.example" ".env" >nul
echo.
echo [3/3] Starting local application...
echo Open http://127.0.0.1:8765 in your browser.
echo Press Ctrl+C in this window to stop.
start "" "http://127.0.0.1:8765"
".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8765
echo Application stopped.
pause
exit /b 0
:error
echo Setup failed. Confirm Python 3.11+ is installed.
pause
exit /b 1
