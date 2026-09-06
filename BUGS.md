# Bekannte Defekte (BUGS.md)

Defekte, die beim Bug-Sweep identifiziert, aber nicht im laufenden Sweep behoben wurden.
Format: `[Status] Titel — Kurzbeschreibung`

---

## Offen

### SEC-AUDIT-2026-08-14-01: Store-Lizenz widerspricht dem Repository
**Status:** Offen, Release-blockierend
**Fundort:** OneDrive-Projektion `store_package.json` und `WINDOWS_STORE_PREP.md`
**Befund:** Beide Store-Flächen nennen MIT, während das kanonische Repository und
`LICENSE` GPL-3.0-only festlegen. Vor MSIX-/Store-Einreichung müssen Store-Metadaten,
Listing und Tests auf GPL-3.0 korrigiert und gegen den kanonischen Klon verifiziert werden.

### SEC-AUDIT-2026-08-14-02: Lizenzinventar fehlt im kanonischen Repository
**Status:** Offen
**Fundort:** Repository-Root
**Befund:** `THIRD_PARTY_LICENSES.txt` ist im kanonischen Checkout nicht vorhanden.
Die OneDrive-Kopie vom 2026-07-02 ist kein freigegebener Ersatz und enthält inzwischen
driftende Metadaten außerhalb der deklarierten Versionsbereiche. In einem eigenen Slice
aus dem exakt aufgelösten Build-Environment neu erzeugen, prüfen und mit Guard committen.

### SEC-AUDIT-2026-08-14-03: Dependency-Vertrag ist nicht reproduzierbar
**Status:** Offen
**Fundort:** `requirements.txt`, `pyproject.toml`, `_sources/CROSSCHECK.md`
**Befund:** Es gibt weder Lockfile noch transitive SBOM; `requirements.txt` besitzt
keine Obergrenzen, während `pyproject.toml` Major-Grenzen setzt. Der aktuelle
`pip-audit`-Resolver fand keine bekannte Schwachstelle, attestiert damit aber keinen
eingefrorenen Produktstand. Verträge angleichen und einen verifizierten Lock-/SBOM-Stand
für Releases erzeugen.

### SEC-AUDIT-2026-08-14-04: Historischer Packager installiert ungepinnte Pakete
**Status:** Offen
**Fundort:** `resources/WinStorePackager/WindowsStorePublisher_3.py`
**Befund:** Das mitgeführte Hilfsskript installiert Pillow, pygetwindow und keyring bei
Import automatisch ohne Versionsbindung. Vor erneuter Nutzung oder Distribution auf
explizite, vorab installierte und geprüfte Abhängigkeiten umstellen.

### B-005: AUFGABEN.txt Markdown-Parsing ignoriert Standard-Aufgabenlisten
**Status:** Offen
**Fundort:** `src/core/workspace_export.py` — `_parse_open_tasks()`
**Befund:** `TASK_LINE_PATTERN = re.compile(r"^\s*\[\s\]\s*(.+?)\s*$")` erwartet bare `[ ]`,
wodurch Standard-Markdown-Aufgabenlisten mit `- [ ]` oder `* [ ]` (wie in allen AUFGABEN.txt-Dateien üblich)
nicht gematcht werden und im Workspace-Export als leere Aufgaben- und Release-Checklistenlisten enden.

### B-006: requirements.txt-Parser verwirft Abhängigkeiten mit Extras
**Status:** Offen
**Fundort:** `src/core/workspace_export.py` — `_parse_requirements()`
**Befund:** `REQUIREMENT_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)\s*([<>=!~].+)?$")`
kennt keine PEP-508-Extras wie `requests[security]>=2.28` oder `pydantic[email]`.
Pakete mit eckigen Klammern schlagen im Regex fehl und werden still aus dem Export gedroppt.

### B-007: _count_project_files indexiert .venv, node_modules und .ruff_cache
**Status:** Offen
**Fundort:** `src/core/workspace_export.py` — `_count_project_files()`
**Befund:** Die Ausschlussliste `ignored_dirs` umfasst nur `.git`, `__pycache__`, `.pytest_cache`,
`build`, `dist`, `releases`. Befinden sich `.venv`, `node_modules` oder `.ruff_cache` im Projekt,
fließen tausende Artefakt-Dateien fälschlich in `files_indexed` ein.

### B-008: _infer_frameworks erzwingt PySide6 bei reinen PyQt6-Projekten
**Status:** Offen
**Fundort:** `src/core/workspace_export.py` — `_infer_frameworks()`
**Befund:** Wenn ein Projekt explizit `pyqt6` deklariert, wird `PyQt6` erkannt, aber
durch `if "PySide6" not in detected: detected.insert(0, "PySide6")` zusätzlich
`PySide6` eingefügt, obwohl beide Qt-Bindings inkompatibel sind.

---

## Behoben

### B-004: Datenverlust und Absturz in ProjectManager bei unvollständigen Metadaten und Überschreiben benutzerdefinierter Felder
**Status:** Behoben (2026-09-07)
**Dateien:** `src/core/project_manager.py`, `tests/test_bugsweep_regressions.py`
**Fix:**
1. `open_project()` sichert Pflichtfelder (`name`, `path`, `created`, `last_opened`) mit sinnvollen Fallbacks ab, statt mit `TypeError` abzustürzen, wenn eine `devcenter.json` minimal ist oder Felder fehlen.
2. `open_project()`, `save_project()` und `create_project()` aktualisieren bestehende JSON-Daten (`data.update(asdict(...))`), statt das Dateiformat durch `asdict(...)` auf Basisfelder zu reduzieren. Benutzerdefinierte Einstellungen, Erweiterungen und Plugins in `devcenter.json` bleiben erhalten.
3. `get_recent_projects()` filtert leere oder Whitespace-Pfadstrings explizit aus (in Python liefert `Path("").exists()` `True` für das aktuelle Arbeitsverzeichnis).
4. `_create_template_files()` überschreibt keine vorhandenen Projektdateien (`src/main.py`, `src/__init__.py`, `README.md`, `requirements.txt`) mehr, wenn in ein bestehendes Verzeichnis initialisiert wird.
5. Umstellung von rohen `print()`-Meldungen auf das Modul-Logging (`logger.warning` / `logger.error`).
6. 5 Regressionstests in `tests/test_bugsweep_regressions.py` hinzugefügt.

### SEC-AUDIT-2026-08-14-00: API-Key im Klartext gespeichert
**Status:** Behoben (2026-08-14)
**Dateien:** `src/core/settings_manager.py`, `src/gui/dialogs/settings_dialog.py`
**Fix:** Persistenz auf den System-Keyring begrenzt, Legacy-Klartext migriert,
JSON-/Export-/Importpfade redigiert und Keyring-Fehler fail-closed behandelt.

### B-001: Modell-Auswahl nicht funktional
**Status:** Behoben (2026-06-05)  
**Datei:** `src/gui/main_window.py` — `_apply_settings()`  
**Fix:** `_apply_settings()` liest nun `ai.model` und ruft `set_model()` mit dem korrekten `AIModel`-Enum-Wert auf. Auch `max_tokens` wird übertragen.

### B-002: Rotes Validierungs-Rahmen in NewProjectDialog wird nicht zurückgesetzt
**Status:** Behoben (2026-06-05)  
**Datei:** `src/gui/dialogs/new_project_dialog.py` — `_reset_name_style()`  
**Fix:** `name_edit.textChanged` ist nun mit `_reset_name_style()` verbunden, das `setStyleSheet("")` aufruft und so den roten Rahmen beim nächsten Tastendruck löscht.

### B-003: OutputPanel.append_output() erbt Textfarbe vom vorherigen Text
**Status:** Behoben (2026-06-05)  
**Datei:** `src/gui/panels/output_panel.py` — `append_output()`  
**Fix:** `append_output()` verwendet nun explizit `QTextCharFormat` mit Farbe `#cccccc`, sodass stdout-Ausgabe immer in der Standardtextfarbe erscheint und nicht die Farbe des vorherigen Texts (grau von info, rot von error) erbt.

---

_Zuletzt aktualisiert: 2026-09-07 (Bug-Sweep B-004 Behoben, B-005 bis B-008 erfasst)_
