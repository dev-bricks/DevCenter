@echo off
setlocal EnableExtensions
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
set "PROJECT_ROOT=%CD%"
set "SOFTWARE_ROOT=%USERPROFILE%\OneDrive\.TOPICS\.SOFTWARE"
set "SCANNER=%SOFTWARE_ROOT%\_tools\build_exclude_scanner.py"
set "BUILD_ROOT=C:\_Local_DEV\codex_build\DevCenter"
set "RUN_ID=%RANDOM%%RANDOM%"
set "DIST_DIR=%BUILD_ROOT%\dist\%RUN_ID%"
set "WORK_DIR=%BUILD_ROOT%\build"
set "SPEC_DIR=%BUILD_ROOT%\spec"
set "LOG_DIR=%BUILD_ROOT%\logs"
set "EXCLUDES_FILE=%BUILD_ROOT%\pyinstaller-excludes.txt"
set "METADATA=%BUILD_ROOT%\BUILD-METADATA.txt"
set "PROJECT_DIST=%PROJECT_ROOT%\dist"

if not exist "%SCANNER%" (
  echo [FEHLER] Exclude-Scanner fehlt: %SCANNER%
  pause
  exit /b 1
)
python --version >nul 2>&1 || (
  echo [FEHLER] Python wurde nicht gefunden.
  pause
  exit /b 9009
)
for %%D in ("%BUILD_ROOT%" "%BUILD_ROOT%\dist" "%DIST_DIR%" "%WORK_DIR%" "%SPEC_DIR%" "%LOG_DIR%") do if not exist %%~D mkdir %%~D

python "%SCANNER%" --project "%PROJECT_ROOT%" --emit pyinstaller > "%EXCLUDES_FILE%"
if errorlevel 1 goto failed
set /p EXCLUDES=<"%EXCLUDES_FILE%"
echo [build] Auto-Excludes: %EXCLUDES%

python -m PyInstaller --noconfirm --clean --windowed --onefile ^
  --name DevCenter --icon "%PROJECT_ROOT%\DevCenter.ico" ^
  --add-data "%PROJECT_ROOT%\locales;locales" --add-data "%PROJECT_ROOT%\resources;resources" ^
  %EXCLUDES% --distpath "%DIST_DIR%" --workpath "%WORK_DIR%" --specpath "%SPEC_DIR%" ^
  "%PROJECT_ROOT%\main.py" > "%LOG_DIR%\pyinstaller.log" 2>&1
if errorlevel 1 goto failed

powershell -NoProfile -ExecutionPolicy Bypass -Command "$exe = Join-Path $env:DIST_DIR 'DevCenter.exe'; $p = Start-Process -FilePath $exe -PassThru; Start-Sleep -Seconds 3; if ($p.HasExited) { exit $p.ExitCode }; Stop-Process -Id $p.Id -Force; exit 0"
if errorlevel 1 (
  echo [FEHLER] Start-Smoke fehlgeschlagen. Es wird nichts nach OneDrive kopiert.
  goto failed
)

if not exist "%PROJECT_DIST%" mkdir "%PROJECT_DIST%"
copy /Y "%DIST_DIR%\DevCenter.exe" "%PROJECT_DIST%\DevCenter.exe" >nul || goto failed
copy /Y "%DIST_DIR%\DevCenter.exe" "%PROJECT_ROOT%\DevCenter.exe" >nul || goto failed

for /f "delims=" %%H in ('python -c "import hashlib, pathlib, sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest().upper())" "%DIST_DIR%\DevCenter.exe"') do set "SHA256=%%H"
for /f "delims=" %%R in ('git -C "%PROJECT_ROOT%" rev-parse --short HEAD 2^>nul') do set "REVISION=%%R"
if not defined REVISION set "REVISION=unversioned-source"
> "%METADATA%" (
  echo artifact=DevCenter.exe
  echo sha256=%SHA256%
  echo revision=%REVISION%
  echo created_local=%DATE% %TIME%
  echo source=%PROJECT_ROOT%
  echo build_dist=%DIST_DIR%\DevCenter.exe
  echo one_drive_dist=%PROJECT_DIST%\DevCenter.exe
  echo one_drive_root=%PROJECT_ROOT%\DevCenter.exe
)
echo [build] OK: %DIST_DIR%\DevCenter.exe
echo [build] SHA-256: %SHA256%
echo [build] Provenienz: %METADATA%
echo [build] OneDrive-Sync: %PROJECT_DIST%\DevCenter.exe und %PROJECT_ROOT%\DevCenter.exe aktualisiert.
echo [build] Keine automatische Release-Kopie. Nach manueller Versions-/Tag-Pruefung darf das Artefakt nach releases\candidates\ kopiert werden.
exit /b 0

:failed
echo [FEHLER] Build fehlgeschlagen. Details: %LOG_DIR%\pyinstaller.log
pause
exit /b 1
