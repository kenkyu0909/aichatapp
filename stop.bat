@echo off
setlocal
cd /d "%~dp0"

if "%MRA_PORT%"=="" set "MRA_PORT=8765"

echo ============================================
echo  Matching Reply Assistant - stop (port %MRA_PORT%)
echo ============================================
echo.

set "FOUND="
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%MRA_PORT% " ^| findstr /C:"LISTENING"') do (
    set "FOUND=1"
    echo [stop] Killing process PID %%P ...
    taskkill /PID %%P /T /F >nul 2>nul
)

if defined FOUND (
    echo [done] The server has been stopped.
) else (
    echo [info] No server is listening on port %MRA_PORT%.
)

echo.
pause
endlocal
exit /b 0
