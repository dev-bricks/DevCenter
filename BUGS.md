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

---

## Behoben

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

_Zuletzt aktualisiert: 2026-08-14 (Security- und Lizenz-Audit)_
