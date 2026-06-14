# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Build / Release
- EXE neu gebaut 2026-06-01 (PyInstaller `--onefile`, `DevCenter.exe`); 25/25 Tests grün, Smoke-Test bestanden. Vorherige EXE: 2026-04-29. Anlass: workspace_export.py neu hinzugefügt.

### Hinzugefügt / Added
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
- DevCenter legt Konfigurations- und Indexdateien auf Linux/macOS jetzt XDG-konform unter `XDG_CONFIG_HOME/DevCenter` bzw. `~/.config/DevCenter` ab, statt ungeordnet unter `~/DevCenter`.
- Persistenz unbekannter Einstellungsschlüssel abgesichert, damit UI-/Legacy-Aliase beim Speichern nicht verloren gehen.
- Fehlende `chardet`-Abhängigkeit für frische CI-/Installationsumgebungen ergänzt.
- Editor-Einstellungen werden nach dem Speichern auf offene Tabs angewendet; der Dialog persistiert jetzt auch „Aktuelle Zeile hervorheben” und aktualisiert Schrift, Tab-Breite, Zeilennummern und Cursor-Markierung unmittelbar.
- Workspace-Exporte redigieren jetzt offene Aufgaben, Projektpfade und aktuelle Analyseprobleme, ohne Secrets oder lokale Vollpfade mitzuschreiben.
- `WinStorePackager`: subprocess-Deadlock behoben — `check_call` mit PIPE durch `subprocess.run(..., capture_output=True)` ersetzt; Exception-Handler liest jetzt immer `stderr or stdout`.
- `ProfilerBridge`: SQLite-Connection-Leak auf Windows geschlossen — alle 6 `conn.close()`-Stellen in `search()`, `find_duplicates()` und `get_statistics()` verwenden jetzt `try/finally`.

## [1.0.0] - 2026-02-24

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
