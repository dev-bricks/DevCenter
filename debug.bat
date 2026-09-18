@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

echo DevCenter-Diagnose und Debug-Start
echo ===================================
python main.py --debug %*
set "EXIT_CODE=%ERRORLEVEL%"
echo.
echo [debug] Exit-Code: %EXIT_CODE%
echo [debug] Log: %LOCALAPPDATA%\DevCenter\logs\app.log
pause
exit /b %EXIT_CODE%
