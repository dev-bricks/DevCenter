@echo off
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

python --version >nul 2>&1
if errorlevel 1 (
  py -3 --version >nul 2>&1
  if errorlevel 1 (
    echo [FEHLER] Python 3 wurde nicht gefunden.
    pause
    exit /b 1
  )
  set PYTHON_CMD=py -3
) else (
  set PYTHON_CMD=python
)

%PYTHON_CMD% -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onefile ^
  --name DevCenter ^
  --icon "DevCenter.ico" ^
  --add-data "locales;locales" ^
  --add-data "resources;resources" ^
  main.py

if errorlevel 1 pause
