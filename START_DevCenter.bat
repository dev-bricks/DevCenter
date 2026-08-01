@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

REM Produktivstart: kein Konsolenfenster. Fehler stehen in
REM %LOCALAPPDATA%\DevCenter\logs\app.log; debug.bat zeigt sie sichtbar.
if exist "%~dp0dist\DevCenter.exe" (
    start "" "%~dp0dist\DevCenter.exe" %*
    exit /b %ERRORLEVEL%
)
if exist "%~dp0DevCenter.exe" (
    start "" "%~dp0DevCenter.exe" %*
    exit /b %ERRORLEVEL%
)
where pythonw.exe >nul 2>&1 || exit /b 9009
start "" /B pythonw.exe "%~dp0main.py" %*
exit /b %ERRORLEVEL%
