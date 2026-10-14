@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
echo.
echo ============================================
echo  Matching Reply Assistant (LOCAL PC)
echo ============================================
echo.

rem Reuse a healthy instance, but never terminate an existing process.
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $s=Invoke-RestMethod -TimeoutSec 2 http://127.0.0.1:8765/api/status; if ($s.app_id -eq 'matching-reply-assistant' -and $s.demo -is [bool] -and $s.model -is [string] -and $s.model.StartsWith('gemini-')) { exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 goto :existing_app
powershell -NoProfile -Command "$c=New-Object Net.Sockets.TcpClient; try { $c.Connect('127.0.0.1',8765); exit 0 } catch { exit 1 } finally { $c.Dispose() }"
if not errorlevel 1 goto :port_in_use

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python 3.11+ virtual environment...
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3.11 -m venv .venv
  ) else (
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
echo Starting local server...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Start-Process -FilePath (Join-Path (Get-Location) '.venv\Scripts\python.exe') -ArgumentList @('-m','uvicorn','app:app','--host','127.0.0.1','--port','8765') -WorkingDirectory (Get-Location) -WindowStyle Hidden -ErrorAction Stop; exit 0 } catch { exit 1 }"
if errorlevel 1 goto :server_start_error

set "READY=0"
for /L %%I in (1,1,30) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $s=Invoke-RestMethod -TimeoutSec 1 http://127.0.0.1:8765/api/status; if ($s.app_id -eq 'matching-reply-assistant' -and $s.demo -is [bool] -and $s.model -is [string] -and $s.model.StartsWith('gemini-')) { exit 0 } else { exit 1 } } catch { exit 1 }"
  if not errorlevel 1 set "READY=1"
  if "!READY!"=="1" goto :open_firefox
  timeout /t 1 /nobreak >nul
)
echo The local server did not become ready. Check Python dependencies and port 8765.
pause
exit /b 1

:existing_app
echo A Matching Reply Assistant server is already responding at 127.0.0.1:8765.
goto :open_firefox

:port_in_use
echo Port 8765 is occupied by a server that did not identify as this app.
echo It was left running. Close it yourself or configure the other application before retrying.
pause
exit /b 1

:open_firefox
set "FIREFOX_EXE=%ProgramFiles%\Mozilla Firefox\firefox.exe"
if not exist "%FIREFOX_EXE%" set "FIREFOX_EXE=%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"
if exist "%FIREFOX_EXE%" (
  start "" "%FIREFOX_EXE%" "http://127.0.0.1:8765/"
) else (
  echo Firefox was not found. Open http://127.0.0.1:8765/ in Firefox.
)
echo App is ready at http://127.0.0.1:8765/
exit /b 0

:python_error
echo Python 3.11 or newer is required.
pause
exit /b 1

:dependency_error
echo Required packages could not be installed.
pause
exit /b 1

:server_start_error
echo The local server process could not be started.
pause
exit /b 1
