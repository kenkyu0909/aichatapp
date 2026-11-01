@echo off
setlocal
cd /d "%~dp0"

if /i "%~1"=="--hidden" goto run_hidden

if not exist "start.bat" (
    echo [ERROR] start.bat was not found next to this file.
    pause
    exit /b 1
)

rem Relaunch through the VBS wrapper so no console window stays open.
wscript "%~dp0launch_hidden.vbs" "%~f0" --hidden
exit /b 0

:run_hidden
if not exist "logs" mkdir "logs"
call "start.bat" > "logs\server.log" 2>&1 < nul
exit /b %ERRORLEVEL%
