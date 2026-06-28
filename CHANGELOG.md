# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Behoben / Fixed
- `settings_dialog`: `editor_theme` und `accent_color` wurden beim Speichern verworfen (nur `appearance.theme` wurde persistiert). `_save_settings()` setzt jetzt alle drei Appearance-Felder; `_load_settings()` lädt sie vollständig. Regressionstests: `test_settings_dialog_saves_editor_theme`, `test_settings_dialog_saves_accent_color`, `test_settings_dialog_loads_appearance_fields` (142/142 grün).

### Build / Release
- EXE neu gebaut 2026-06-01 (PyInstaller `--onefile`, `DevCenter.exe`); 25/25 Tests grün, Smoke-Test bestanden. Vorherige EXE: 2026-04-29. Anlass: workspace_export.py neu hinzugefügt.

### Hinzugefügt / Added
- `web_companion/library.js`: `countChecklistProgress(checklists)` — berechnet Erledigungsfortschritt einer Release-Checkliste (`{done, total, percent}`).
- `web_companion/library.js`: `groupProblemsBySeverity(problems)` — gruppiert Analysebefunde nach Schweregrad, sortiert nach error → warning → info.
- `web_companion/app.js`: Analyse-Panel zeigt Befunde jetzt nach Schweregrad gruppiert an; Release-Panel enthält eine Fortschrittsleiste für Checklisten.
- `web_companion/manifest.webmanifest`: SVG-Icons (`app.svg` mit `purpose=any`, `app-maskable.svg` mit `purpose=maskable`) eingetragen — behebt vorherige Manifest-Regressionsfehler.
- `web_companion/styles.css`: Klassen `.problem-group-header`, `.checklist-progress`, `.progress-track`, `.progress-fill` für die neuen UI-Elemente.
- `web_companion/tests/library.test.mjs`: 12 neue Tests für `countChecklistProgress` und `groupProblemsBySeverity` (52/52 grün, alle Dateien).

### Behoben / Fixed
- GitHub Actions Smoke-Checks für Python 3.10, 3.11 und 3.12.
- Lokales `build_exe.bat` für den PyInstaller-Build mit `DevCenter.ico`.
- Datenschutzhinweise für lokale Einstellungen, Datei-Indizes, Build-Artefakte und optionale API-Nutzung.
- `llms.txt` mit maschinenlesbarer Projektpositionierung, Datenschutzgrenzen und relevanten Suchbegriffen.
- Redigierter Workspace-Export `devcenter-workspace-v1.json` als Desktop-Funktion unter `Datei -> Arbeitsstand exportieren...`.
- Statischer `web_companion/`-MVP mit lokalem JSON-Import, Demo-Fixture, read-only Dashboard, `manifest.webmanifest`, Service Worker und Node-Tests.
- `web_companion/manifest.webmanifest`: `id` und `scope` ergänzt (PWA-Installierbarkeits-Best-Practice)
- `web_companion/sw.js`: CACHE_NAME v2, `clients.claim()` in `waitUntil`-Kette verschoben
- `web_companion/tests/pwa.test.mjs`: auf 15 PWA-Tests erweitert (20/20 grün mit library-Tests)

### Geändert / Changed
- `src/gui/panels/ai_panel.py`: `model_combo.currentIndexChanged` mit `_on_model_changed()` verdrahtet; `set_ai_service()` synchronisiert das Modell sofort beim ersten Aufruf; neuer Test `tests/test_ai_panel_model_selection.py` (5 Fälle).
- Gemeinsamer Pfad-Resolver `src/core/app_paths.py` für `SettingsManager`, `ProjectManager` und `ProfilerBridge`.
- Neue Regressionstests für Settings-, Recent-Projects- und Dateiindex-Pfad plus aktualisierter Linux-Plattform-Smoke.
- README, Contribution- und Security-Dokumentation auf `dev-bricks/DevCenter` aktualisiert.
- Beispielkonfiguration für WinStorePackager anonymisiert und neutralisiert.
- README auf englischen GitHub-Einstieg, klarere DevCenter-Namensabgrenzung und bessere Discoverability-Keywords erweitert.
- Community-Workflows auf aktuelle Action-Versionen gehoben.
- `AUFGABEN.txt`, `PORTIERUNGSPLAN.md`, README und `web_companion/README.md` auf den umgesetzten Companion-Stand synchronisiert.

### Behoben / Fixed
- `closeEvent`-Crash bei laufendem AI-Worker: `AIAssistantPanel` und `OutputPanel` erhalten je eine `stop()`-Methode; `MainWindow.closeEvent` ruft beide vor `event.accept()` auf. Verhindert "QThread: Destroyed while thread is still running" und verwaiste `QProcess`-Instanzen beim Schließen während eines laufenden Vorgangs. `AIAssistantPanel.stop()` nutzt `quit() + wait(3 s) + terminate()`-Fallback (asyncio-basierter `AIWorker` hat keinen Qt-Event-Loop, daher kein reines `quit()`). `OutputPanel.stop()` nutzt `kill() + waitForFinished(3 s)`.
- `kompilator.py`-Watchdog: `Popen(PyInstaller)` läuft jetzt mit `threading.Timer`-Watchdog (600 s Limit) und einem `_cancelled`-Event. Neue `cancel()`-Methode killt den PyInstaller-Child-Prozess direkt. `BuildDialog.reject()` ruft `kompilator.cancel()` vor `worker.terminate()` auf — verhindert verwaiste PyInstaller-Prozesse und gesperrte `dist/`-Verzeichnisse beim Abbrechen. `check_pyinstaller()` und `get_pyinstaller_version()` erhalten `timeout=30` in `subprocess.run()`.
- `ProfilerBridge`: FTS5-Indexpflege für Re-Indexe auf dokumentiertes Delete-then-Insert umgestellt, SQLite-Verbindungen mit `busy_timeout`/WAL gehärtet und Lesezugriffe gegen parallele Index-Schreibpfade serialisiert.
- DevCenter legt Konfigurations- und Indexdateien auf Linux/macOS jetzt XDG-konform unter `XDG_CONFIG_HOME/DevCenter` bzw. `~/.config/DevCenter` ab, statt ungeordnet unter `~/DevCenter`.
- Persistenz unbekannter Einstellungsschlüssel abgesichert, damit UI-/Legacy-Aliase beim Speichern nicht verloren gehen.
- Fehlende `chardet`-Abhängigkeit für frische CI-/Installationsumgebungen ergänzt.
- `tests/test_ai_panel_model_selection.py`: von pytest-Fixtures auf `unittest.TestCase` umgestellt, damit `python -m unittest discover` die 5 Tests im CI erkennt (108/108 Tests grün).
- Editor-Einstellungen werden nach dem Speichern auf offene Tabs angewendet; der Dialog persistiert jetzt auch „Aktuelle Zeile hervorheben” und aktualisiert Schrift, Tab-Breite, Zeilennummern und Cursor-Markierung unmittelbar.
- Workspace-Exporte redigieren jetzt offene Aufgaben, Projektpfade und aktuelle Analyseprobleme, ohne Secrets oder lokale Vollpfade mitzuschreiben.
- `WinStorePackager`: subprocess-Deadlock behoben — `check_call` mit PIPE durch `subprocess.run(..., capture_output=True)` ersetzt; Exception-Handler liest jetzt immer `stderr or stdout`.
- `ProfilerBridge`: SQLite-Connection-Leak auf Windows geschlossen — alle 6 `conn.close()`-Stellen in `search()`, `find_duplicates()` und `get_statistics()` verwenden jetzt `try/finally`.

## [1.0.0] - 2026-02-24

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
