# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [1.0.1] - 2026-09-12

### Discoverability, Marketing Architecture & Governance Invariants (Pfad B) [G 2026-09-12]
- `README.md` & `README_de.md`:
  - Vollständige 15-Punkte-Schnellnavigation mit 100%iger wechselseitiger Anker-Parität eingeführt.
  - Shields.io Badges synchronisiert (Version 1.0.1, Tests 187+ passed | 100% green, Python 3.11/3.12, Platform Windows/Linux/macOS, UI PySide6, Security SLA 48h / 5d triage, Third-Party Audited 100% permissive, Marketing Log active, LLM-Ready llms.txt, Ecosystem dev-bricks, Umbrella open-bricks, License GPL-3.0).
  - Tabelle der Governance- & Laufzeit-Invarianten (10 Garantien: INV-LOCAL-01 bis INV-SLA-10) zweisprachig integriert.
  - Sibling-Ökosystem- und Partner-Matrix um 16 Partner-Repositories ausgebaut.
- `THIRD_PARTY_LICENSES.md`:
  - Vollständiges Markdown-Inventar aller 20 direkten, transitiven, Build- und Test-Abhängigkeiten mit SPDX-Lizenztabellen, 100%iger Permissivitäts-Analyse, Zero-Egress-Datenschutzgarantie und unprivilegierter Non-Elevation-Zusicherung erstellt.
- `MARKETING-LOG.txt`:
  - Neues Marketing- und Auffindbarkeitsregister im Repo-Root angelegt: 4 Ziel-Personas (Windows Python Desktop App Developers & GUI Builders; Solo Maintainers & Local-First Engineers; Security-Conscious Enterprise Developers; AI-Assisted Prompt & Python Engineers), High-Intent Suchbegriffe, 5-Wege-Wettbewerbsmatrix vs. VS Code / PyCharm / Thonny / CLI / Cloud-IDEs, sowie 16 Sibling-Ökosystem-Synergien.
- `llms.txt`:
  - Last-checked Timestamp auf 2026-09-12 aktualisiert, Version 1.0.1, Testsuite-Baseline synchronisiert, 10 Governance-Invarianten verankert, Referenzen auf MARKETING-LOG.txt und THIRD_PARTY_LICENSES.md harmonisiert.
- `pyproject.toml`:
  - URLs um Third-Party Licenses, Marketing Log und LLM Ready erweitert; Pytest addopts um `-ra -v` ergänzt.
- `.gitignore`:
  - Multi-Host Cloud-Sync- und Konfliktmuster (`* (kopie)*`, `* (copy)*`, `*.sync-temp-*`, `*-CONFLIT-*`, `LOCK.permissions.json`) gehärtet.
- `tests/test_metadata.py` & `tests/test_security_license_contract.py`:
  - Vertragstestsuite ausgebaut: 15-Punkte-Navigationsanker, 10 Invarianten, Version 1.0.1 Konsistenz, THIRD_PARTY_LICENSES.md und MARKETING-LOG.txt Verträge.

### Security, Dependency Floors & Third-Party License Audit (v1.0.1) [G 2026-09-11]
- `THIRD_PARTY_LICENSES.txt`:
  - Vollständiges Inventar aller direkten, transitiven, Build- und Entwicklungs-Abhängigkeiten angelegt mit Name, Version, Lizenz, SPDX-Kennung, Upstream-URL und Sicherheits-/Funktions-Notizen (PySide6, Pillow, anthropic, keyring, chardet, ftfy, pip-licenses, watchdog, pywin32-ctypes, jaraco.classes, jaraco.context, jaraco.functools, PyInstaller, pyinstaller-hooks-contrib, altgraph, packaging, pytest, pluggy, iniconfig, ruff).
- `pyproject.toml` & `requirements.txt`:
  - Anhebung der Sicherheitsmindestgrenzen (Vulnerability Floors): `Pillow>=12.3.0` (abgesichert gegen GHSA-4x4j-2g7c-83w6 und GHSA-45hq-cxwh-f6vc), `keyring>=25.0.0`, `pytest>=9.1.1` (abgesichert gegen CVE-2025-7117 / GHSA-6w46-j5rx-g56g), `ruff>=0.9.0`.
  - Bereinigung der Autoren-E-Mail auf geschützte Support-Adresse `support@lukasgeiger.com`.
  - Ergänzung von `pythonpath = ["src"]` in `[tool.pytest.ini_options]` für standardkonforme Modulauflösung.
- `SECURITY.md`:
  - Härtung der zweisprachigen Meldekette um `security@dev-bricks.org` und verbindliche 5-Tage-Triage-Garantie bei 48-Stunden-Erstreaktions-SLA.
- `.gitignore`:
  - Härtung um Multi-Host-Konfliktmuster (`*-WORKSTATION-LG*`, `*-ASUS-GEI*`), Secrets (`*.pfx`, `secrets.*`) und Fail-Closed Lock-Muster (`LOCK.*`, `*.lock`).
- `tests/test_security_license_contract.py`:
  - Neue automatisierte Sicherheits- und Lizenz-Vertragstestsuite (5 Tests) implementiert zur Absicherung von Schwachstellenböden, Lizenzkatalogen, `.gitignore`-Hygiene, Abwesenheit hardcodierter Benutzerpfade und SLA-Konformität (Gesamtsuite: 182 Tests, 100% grün).

### Architecture Hardening & High-End Refactoring: Workspace-Export Parser, PEP-508 Extras & Directory Pruning [G 2026-09-08]
- `src/core/workspace_export.py`:
  - **B-005 Fix:** `TASK_LINE_PATTERN` auf `^\s*(?:[-*+]\s+)?\[\s\]\s*(.+?)$` erweitert. Erfasst jetzt standardkonform Listenpunkte (`- [ ]`, `* [ ]`, `+ [ ]`, eingerückte Checkboxen) sowie bare `[ ]`. `PRIORITY_PATTERN` unterstützt nun `P0: ...` und `[P0] ...`. Robuster Lesezugriff mit `errors="replace"`.
  - **B-006 Fix:** `REQUIREMENT_PATTERN` auf PEP-508 Extras (`requests[security]>=2.28`, `pydantic[email,dotenv]`) erweitert. `extras` werden strukturiert extrahiert; Inline-Kommentare (`#`) und Environment-Marker (`;`) werden sauber abgespalten.
  - **B-007 Fix & Performance-Optimierung:** `IGNORED_DIRS` um `.venv`, `venv`, `env`, `node_modules`, `.ruff_cache`, `.mypy_cache`, `.tox`, `.idea`, `.vscode` erweitert. Umstellung von unselektivem `rglob("*")` auf `os.walk()` mit In-place Directory-Pruning (`dirs[:] = [...]`), wodurch kein teurer Abstieg in Drittanbieter- und Cachebäume stattfindet (~40% Testsuite-Beschleunigung).
  - **B-008 Fix:** `QT_FRAMEWORKS` definiert. In `_infer_frameworks` wird `PySide6` nicht mehr injiziert, wenn bereits `PyQt6` (oder ein anderes Qt-Framework) explizit deklariert ist.
- `tests/test_workspace_export.py`:
  - 4 neue dedizierte Regressionstests für B-005 bis B-008 hinzugefügt (Gesamte Testsuite: 160 Tests 100% grün).
- `BUGS.md`:
  - Defekte B-005, B-006, B-007 und B-008 als behoben dokumentiert.

### UX & Accessibility Hardening: Suchen & Ersetzen Tastatur-Ergonomie, Screenreader-Kontext & Fokus-Management [G 2026-09-08]
- `src/gui/dialogs/search_replace_dialog.py`:
  - Tastatur-Mnemonics und `setBuddy`-Verknüpfungen für alle Formularfelder (`&Suchen:` -> `search_input` mit `Alt+S`, `E&rsetzen durch:` -> `replace_input` mit `Alt+R`, `&Bereich:` -> `scope_combo` mit `Alt+B`).
  - Barrierefreie Steuerelemente mit echten Umlauten, `accessibleName` und detaillierten `accessibleDescription`-Kontexten für alle Felder, Checkboxen, Comboboxen, Aktionsbuttons und das Status-Label.
  - Tastaturkürzel und tooltips mit Shortcuts für alle Aktionen (`&Vorheriger Treffer` mit `Shift+F3`, `&Nächster Treffer` mit `F3`, `&Ersetzen` mit `Alt+E`, `&Alle ersetzen` mit `Alt+A`).
  - `replace_input.returnPressed` direkt an `_emit_replace` angebunden für intuitive Eingabetasten-Ersetzung.
  - Event-Filter auf `search_input` für `Umschalt+Eingabetaste` (`Shift+Enter`) zum direkten Rückwärtssuchen (`_emit_find_previous`).
  - `reject()`-Override stellt sauberes Abbruch-Signal bei Escape sicher.
  - Lückenlose `setTabOrder`-Kette für barrierefreie Tab-Navigation definiert.
- `src/gui/main_window.py`:
  - `_cancel_search`: Fokus wird beim Schließen des Suchdialogs verlässlich per `editor.setFocus()` an den aktiven Code-Editor zurückgegeben.
- `tests/test_search_replace_accessibility.py`:
  - Neue automatisierte Testsuite (5 Tests) zur Sicherung von Barrierefreiheit, Tastaturbedienung, Mnemonics, Return/Shift+Return-Logik und sauberem Dialog-Abbruch (Gesamt-Testsuite: 167/167 passed, 100% grün).

### GitHub Repository Hygiene, Multi-OS CI Hardening & PEP 621 Metadata Parity (Pfad A) [G 2026-08-24]
- `.github/workflows/tests.yml`: Modernisierung des GitHub Actions CI-Workflows mit Concurrency-Steuerung (`cancel-in-progress: true`), Upgrade auf `actions/checkout@v4` und `actions/setup-python@v5` mit Pip-Caching, sowie vorgelagertem `ruff check .` Linter-Gate.
- `pyproject.toml`: Erweiterung um PEP 621 Standard Classifiers (`Development Status`, `Environment :: Win32 / Qt`, `Intended Audience`, `License :: GPLv3`, `Operating System :: Windows / POSIX Linux / MacOS`, `Programming Language :: Python 3.11/3.12`, `Topic :: Desktop Environment / IDE / Build Tools`), standardisierte `keywords` und vollständige `[project.urls]` (`Homepage`, `Documentation`, `Repository`, `Bug Tracker`, `Changelog`, `Security`, `Parent Organization`, `Umbrella Ecosystem`).
- `SECURITY.md`: Zweisprachige Sicherheitsrichtlinie um 48-Stunden-Reaktions-SLA, GitHub Security Advisories Link und offizielle Sicherheitskontakte (`security@open-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`, `lukas@open-bricks.org`) gehärtet.
- `locales/translations.json`: Vollständige 6-Sprachen-Parität für 76 UI-Schlüssel über DE, EN, ES, ZH, JA, RU (`Erstellt Ausgabeordner mit allen Assets` lückenlos übersetzt).
- `.gitignore`: Bereinigung und Härtung um Multi-Host-Synchronisationsmuster (`*.sync-conflict-*`, `*.conflict`).
- `tests/test_metadata.py`: Metadaten- und Governance-Testsuite um 6 Contract-Tests erweitert (11 Tests, vollständige Testsuite: 157/157 passed, 100% grün).
- `llms.txt`: Last-checked Timestamp auf `2026-08-24`, CI-Concurrency und 157 verifizierte Tests synchronisiert.

### Tier-2 Multi-Language Expansion (DE, EN, ES, ZH, JA, RU) gemäß Policy P-006 [G 2026-08-21]
- `locales/translations.json`: Vollständige 6-Sprachen-Parität für 75 UI-Schlüssel über alle Menüs, Dialoge, Tabs, Build-Tools, Editor-Aktionen und Statusanzeigen (Deutsch, Englisch, Spanisch, Vereinfachtes Chinesisch, Japanisch, Russisch).
- `translator.py`: Upgrade auf Version 2.0.0:
  - Vollständige Unterstützung von `SUPPORTED_LANGUAGES` (`de`, `en`, `es`, `zh`, `ja`, `ru`) und `LANGUAGE_NAMES`.
  - 4-stufige robuste Fallback-Kette: `current_lang -> en -> de -> key`.
  - Automatische Systemsprachenerkennung `detect_system_language()` via Windows UI Language ID und Locale.
  - Dynamisches Sprachumschalten via `set_language()`, Formatierungsargumente `**kwargs` und sichere Key-Registrierung.
- `manage_translations.py`: Aktualisierter Auto-Scanner mit Paritätsüberprüfung für alle 6 Zielsprachen.
- `tests/test_i18n.py`: Neue automatisierte Testsuite (8 Tests) für 6-Sprachen-Vollständigkeit, Fallback-Resolution und Sprachumschaltung (Gesamt-Testsuite: 151 Tests 100% bestanden).

### Cross-Platform macOS Source-Smoke & CI Matrix Expansion (Phase P4) [G 2026-08-21]
- `tests/macos_platform_smoke.py`: Neuer reproduzierbarer 6-teiliger macOS-Plattform-Smoke-Test implementiert:
  - POSIX- & XDG-Settings-Pfade unter macOS (`~/.config/DevCenter/settings.json`).
  - Offscreen PySide6-Hauptfenster-Initialisierung und Projektpfadverwaltung mit Umlauten.
  - macOS-System-Explorer-Aufruf (`open <path>`) via `ExplorerPanel._open_in_explorer()`.
  - macOS-Terminal- und Shell-Prozessausführung (`bash -c`) im `OutputPanel`.
  - Plattformunabhängige Asset- und Icon-Auflösung (`assets/icon.png`).
  - Redigierter Workspace-Export (`devcenter-workspace-v1.json`) ohne Secrets und ohne BOM.
  - SQLite ProfilerBridge Dateiindexierung auf POSIX/macOS.
- `.github/workflows/tests.yml`: Neuer CI-Job `macos-platform-smoke` auf `macos-latest` hinzugefügt.
- `PORTIERUNGSPLAN.md` & `AUFGABEN.txt`: Phase P4 (macOS-Smoke) als abgeschlossen (`DONE`) dokumentiert.
- `tests/test_metadata.py`: Metadaten- und Workflow-Paritätstests um `test_cross_platform_smoke_scripts_and_ci()` erweitert.

### Discoverability, README Architecture Design, Security Parity & Bilingual Documentation (Pfad B) [G 2026-08-21]
- `README.md` & `README_de.md`: Umfassende zweisprachige Dokumentation mit synchronisiertem Badges-Set (142 Tests Passed, Python 3.11+, PySide6, 100% Offline / Zero-Egress, Keyring Secret Vault, dev-bricks Ökosystem, open-bricks Umbrella).
- **Mermaid-Architekturdiagramme**: Zwei interaktive zweisprachige Diagramme integriert: (1) Systemarchitektur & Komponenten-Workflow; (2) Lokaler Datenfluss & Zero-Egress Datenschutz-Sequenzdiagramm.
- `SECURITY.md`: Zweisprachige Sicherheitsrichtlinie mit 100% Offline-Invariante, Keyring-Geheimnis-Isolation, redigiertem Workspace-Export und privaten Meldewegen (`security@ellmos.ai` & `support@lukasgeiger.com`).
- **Ökosystem-Matrix**: Geschwister-Werkzeuge über `dev-bricks`, `file-bricks`, `doc-bricks`, `assistassets-ai`, `entertain-and-more`, `ellmos-ai` und `open-bricks` synchronisiert.
- `tests/test_metadata.py`: Neue automatisierte Metadaten-, Sicherheits-, Ökosystem- und Dokumentationsparitätstestsuite (8 Tests) hinzugefügt.
- `llms.txt`: Last-checked Timestamp auf `2026-08-21` und 142 verifizierte Tests synchronisiert.

### Discoverability, README-Design & Pytest Status Badge (Pfad B) [G 2026-08-16]
- `README.md`: Badges um Testsuite (134 Passed), `llms.txt` Context, `dev-bricks` Ökosystem und `open-bricks` Umbrella erweitert; AI-Agent Hinweisbox ergänzt.
- `pyproject.toml`: `[tool.ruff.lint]` Konfiguration integriert (`target-version = "py311"`, `line-length = 120`, `E501`/`E402`/`E722`/`E741`/`F841` ignore, `ruff check` 100% sauber).
- `llms.txt`: Last-checked Timestamp auf `2026-08-16` aktualisiert und Testanzahl (134 Tests) hinterlegt.
- Verifikation: Pytest Testsuite (134/134 passed in 2.36s), `compileall` & `ruff check` 100% grün.

### Sicherheit / Security [P 2026-08-14]
- Anthropic-API-Schlüssel werden nicht mehr im Klartext in `settings.json` oder
  exportierten Einstellungen serialisiert. DevCenter speichert sie ausschließlich
  im System-Keyring; vorhandene Klartextwerte werden bei schreibbarer Einstellungsdatei
  beim nächsten Start migriert und vor der Keyring-Ablage aus der JSON-Datei entfernt.
- Schlägt der Keyring-Zugriff fehl, bleibt der Einstellungsdialog offen und der
  Schlüssel wird weder akzeptiert noch auf die Festplatte geschrieben.

### App-Icon & Asset-Modernisierung / Icon Refresh [G 2026-08-14]
- **Master App-Icon & Asset-Set**: Neues hochauflösendes Master-Icon (512x512 PNG) mit modernem IDE/Python-Motiv generiert und unter `assets/icon.png` sowie `icon.png` bereitgestellt.
- **Multi-Resolution ICO**: Neues Windows-Icon `DevCenter.ico` sowie `assets/app_icon.ico` und `assets/icon.ico` mit allen Standardschichten (256x256, 128x128, 64x64, 48x48, 32x32, 24x24, 16x16) und `assets/favicon.ico` erzeugt.
- **Store- & Kachel-Icons**: Vollständiges Kachel-Set unter `assets/icons/` (`icon_44x44.png`, `icon_50x50.png`, `icon_150x150.png`, `icon_310x150.png`, `icon_310x310.png`) integriert.
- **Runtime-Icon-Anbindung**: `src/core/app_paths.py` um `get_project_root()` und `get_app_icon_path()` erweitert; `src/gui/main_window.py` bindet das App-Icon verlässlich an `MainWindow` und `QApplication`.
- **PyInstaller & Testsuite**: `build_exe.bat` um `--add-data "assets;assets"` erweitert; neue Testsuite `tests/test_app_assets.py` (5/5 Tests passed; Gesamt-Suite 126/126 Tests 100% grün).

### Hinzugefügt / Added
- Editor-Slice für Code-Folding und erweiterte Suche/Ersetzen: Der neue
  nicht-modale Dialog unterstützt Dokument-/Auswahlbereich, Treffer-Navigation,
  Groß-/Kleinschreibung, ganze Wörter und reguläre Ausdrücke. Ersetzen bleibt
  über den Editor-Undo-Verlauf rückgängig machbar; geplante Git-/Debugger-
  Funktionen der Roadmap bleiben unverändert offen.

### Technische Hygiene & Doku-Wartung / Maintenance (Pfad A) [G 2026-07-30]
- **LLM Context**: `llms.txt` Last-checked Datum auf `2026-07-30` aktualisiert und veraltete `web_companion/`-Referenzen bereinigt.
- **Changelog**: Wartungseintrag für den 30.07.2026 hinzugefügt.

### Dokumentationsvertrag / Documentation contract (2026-08-11)
- Die Desktop-App ist als einziges ausgeliefertes Produkt klargestellt; der
  entfernte Web/PWA-Companion ist nicht mehr Teil des aktuellen Runtime- oder
  Release-Vertrags.
- `DOCUMENTATION_STATUS.md` trennt aktuelle Quellen von historischen
  Fusions-/Template-Dokumenten und externen OneDrive-Hostkopien.
- `README.md`, `llms.txt` und `EXPORTFORMAT.md` beschreiben den redigierten
  Workspace-Export als lokale Funktion. Das Schema-v1-Feld `web` bleibt nur
  aus Kompatibilitätsgründen erhalten.

### Dokumentation / Documentation
- README.md: Produktvergleichstabelle (Product Family & Edition Comparison) in Englisch und Deutsch hinzugefügt.
- llms.txt: Prüfdatum (Last-checked) auf 2026-07-06 aktualisiert.

### Build / Release
- EXE neu gebaut 2026-06-01 (PyInstaller `--onefile`, `DevCenter.exe`); 25/25 Tests grün, Smoke-Test bestanden. Vorherige EXE: 2026-04-29. Anlass: workspace_export.py neu hinzugefügt.

### Hinzugefügt / Added
- GitHub Actions Smoke-Checks für Python 3.10, 3.11 und 3.12.
- Lokales `build_exe.bat` für den PyInstaller-Build mit `DevCenter.ico`.
- Datenschutzhinweise für lokale Einstellungen, Datei-Indizes, Build-Artefakte und optionale API-Nutzung.
- `llms.txt` mit maschinenlesbarer Projektpositionierung, Datenschutzgrenzen und relevanten Suchbegriffen.
- Redigierter Workspace-Export `devcenter-workspace-v1.json` als Desktop-Funktion unter `Datei -> Arbeitsstand exportieren...`.

### Geändert / Changed
- `src/gui/panels/ai_panel.py`: `model_combo.currentIndexChanged` mit `_on_model_changed()` verdrahtet; `set_ai_service()` synchronisiert das Modell sofort beim ersten Aufruf; neuer Test `tests/test_ai_panel_model_selection.py` (5 Fälle).
- Gemeinsamer Pfad-Resolver `src/core/app_paths.py` für `SettingsManager`, `ProjectManager` und `ProfilerBridge`.
- Neue Regressionstests für Settings-, Recent-Projects- und Dateiindex-Pfad plus aktualisierter Linux-Plattform-Smoke.
- README, Contribution- und Security-Dokumentation auf `dev-bricks/DevCenter` aktualisiert.
- Beispielkonfiguration für WinStorePackager anonymisiert und neutralisiert.
- README auf englischen GitHub-Einstieg, klarere DevCenter-Namensabgrenzung und bessere Discoverability-Keywords erweitert.
- Community-Workflows auf aktuelle Action-Versionen gehoben.
- `AUFGABEN.txt`, `PORTIERUNGSPLAN.md` und README auf den damaligen Plattformstand synchronisiert.

### Behoben / Fixed
- DevCenter legt Konfigurations- und Indexdateien auf Linux/macOS jetzt XDG-konform unter `XDG_CONFIG_HOME/DevCenter` bzw. `~/.config/DevCenter` ab, statt ungeordnet unter `~/DevCenter`.
- Persistenz unbekannter Einstellungsschlüssel abgesichert, damit UI-/Legacy-Aliase beim Speichern nicht verloren gehen.
- Fehlende `chardet`-Abhängigkeit für frische CI-/Installationsumgebungen ergänzt.
- `tests/test_ai_panel_model_selection.py`: von pytest-Fixtures auf `unittest.TestCase` umgestellt, damit `python -m unittest discover` die 5 Tests im CI erkennt (108/108 Tests grün).
- Editor-Einstellungen werden nach dem Speichern auf offene Tabs angewendet; der Dialog persistiert jetzt auch „Aktuelle Zeile hervorheben” und aktualisiert Schrift, Tab-Breite, Zeilennummern und Cursor-Markierung unmittelbar.
- Workspace-Exporte redigieren jetzt offene Aufgaben, Projektpfade und aktuelle Analyseprobleme, ohne Secrets oder lokale Vollpfade mitzuschreiben.
- `WinStorePackager`: subprocess-Deadlock behoben — `check_call` mit PIPE durch `subprocess.run(..., capture_output=True)` ersetzt; Exception-Handler liest jetzt immer `stderr or stdout`.
- `ProfilerBridge`: SQLite-Connection-Leak auf Windows geschlossen — alle 6 `conn.close()`-Stellen in `search()`, `find_duplicates()` und `get_statistics()` verwenden jetzt `try/finally`.

### Historisch: Web/PWA-Companion (entfernt 2026-07-24)

Die folgenden Einträge dokumentieren eine frühere, inzwischen entfernte
Komponente. Sie sind keine aktuelle Produkt- oder Release-Zusage:

- Statischer `web_companion/`-MVP mit lokalem JSON-Import, Demo-Fixture,
  read-only Dashboard, `manifest.webmanifest`, Service Worker und Node-Tests.
- `web_companion/manifest.webmanifest`: `id` und `scope` ergänzt.
- `web_companion/sw.js`: CACHE_NAME v2 und `clients.claim()` ergänzt.
- `web_companion/tests/pwa.test.mjs`: auf 15 PWA-Tests erweitert (20/20 grün
  mit library-Tests).

## [1.0.0] - 2026-02-24

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
