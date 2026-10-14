@echo off
setlocal
cd /d "%~dp0"
echo.
echo ============================================
echo  Matching Reply Assistant (LOCAL PC)
echo ============================================
echo.

if "%MRA_PORT%"=="" set "MRA_PORT=8765"

if not exist ".venv\Scripts\python.exe" (
  echo Checking for Python 3.11 or newer...
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
    if errorlevel 1 goto :python_error
    py -3 -m venv .venv
  ) else (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
    if errorlevel 1 goto :python_error
    python -m venv .venv
  )
  if errorlevel 1 goto :python_error
)

".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
if errorlevel 1 goto :python_error

".venv\Scripts\python.exe" -c "import fastapi, uvicorn, PIL, google.genai" >nul 2>nul
if errorlevel 1 (
  echo Installing required Python packages...
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto :dependency_error
)

if not exist ".env" if exist ".env.example" copy ".env.example" ".env" >nul
echo Starting the local server. Firefox opens after the server is ready.
echo Press Ctrl+C in this window to stop it.
".venv\Scripts\python.exe" scripts\start_server.py
set "SERVER_RESULT=%ERRORLEVEL%"
if not "%SERVER_RESULT%"=="0" (
  echo The app stopped with an error. Review the message above.
  pause
)
exit /b %SERVER_RESULT%

:python_error
echo Python 3.11 or newer is required. Install Python 3 and retry.
pause
exit /b 1

:dependency_error
echo Required packages could not be installed.
pause
exit /b 1
