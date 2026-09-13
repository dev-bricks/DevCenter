---
name: "DevCenter"
type: project-docs
profile: "STANDARD"
version: 1.0.0
created: "2026-08-17"
updated: 2026-08-17
reason_last_change: "Bootstrap-Check: projektlokales CLAUDE.md aus project-docs-Template abgeleitet und für DevCenter Suite zugeschnitten."
last_verified: 2026-08-17
author: "Gemini"
anthropic_compatible: true
description: |
  Project-specific instructions for AI coding agents in DevCenter Suite.
  Fokus: lokale Python/PySide6 Desktop-IDE, Code-Analyse, PyInstaller-Builds, i18n, Web-Companion und Plan-D-Repository-Grenzen.
---

# CLAUDE.md — Instructions für AI Coding Agents

> Für LLM-Agenten in `CODING/REL-PUB_DevCenter_SUITE`.
> Diese Datei ergänzt die globalen und Root-Regeln der `.SOFTWARE`-Pipeline um projektlokale
> Leitplanken für die DevCenter Suite.

---

> **Selbstkorrektur:** Wenn du veraltete Passagen oder Verweise entdeckst oder beim Arbeiten merkst,
> dass wichtige lokale Regeln fehlen, korrigiere diese Datei gezielt.

## Projekt

**DevCenter** — Lokale Desktop-Entwicklungsumgebung und Suite für Python-Projekte (Code schreiben, analysieren, testen, kompilieren und exportieren). Integriert Code-Editor, AST-Analyzer, PyInstaller-Builder, Lizenzsammler, SQLite/FTS5-Dateiindex, optionalen Claude-KI-Assistenten und statischen Web-Companion.

- **Pfad (OneDrive-Deploykopie):** `C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\CODING\REL-PUB_DevCenter_SUITE`
- **Klon (Plan-D-Arbeitskopie):** `C:\_Local_DEV\repos\DevCenter`
- **Repository:** https://github.com/dev-bricks/DevCenter (Kanonischer Branch: `master`)
- **Sprache/Stack:** Python 3.10+, PySide6 (Qt6 GUI), PyInstaller, Pillow, SQLite (FTS5 / WAL), Anthropic API (optional), HTML5/JS (PWA Viewer in `web_companion/`)

## Rolle & Stil

Arbeite als pragmatischer Senior-Entwickler mit Fokus auf Code-Qualität, Thread-Sicherheit in PySide6, lokale Datenhaltung, saubere i18n-Übersetzungen und strikte Einhaltung der Plan-D-Repository-Grenzen.

**Kommunikation:**
- Sprache: Deutsch (Code, Identifier und Variablen bleiben englisch)
- Deutsche End-User-Texte und GUI-Elemente erhalten immer echte UTF-8-Umlaute (ä, ö, ü, ß)
- Stil: präzise, evidenzbasiert, ohne Füllwörter
- Bei Unklarheiten über Modulgrenzen oder Aufgabenstand: in `AUFGABEN.txt`, `ARCHITEKTUR_DevCenter.md` und `DevCenter.repo.md` nachsehen

## Einstieg & Quick Commands

```powershell
# Desktop-App starten
python main.py
# oder via Starter
START_DevCenter.bat

# Python-Testsuite ausführen (114+ Tests)
python -m pytest tests

# Alternativ via unittest
python -m unittest discover -s tests -v

# Syntax- & Compileall-Check
python -m compileall -q main.py manage_translations.py translator.py src tests

# Übersetzungs-Management
python manage_translations.py
```

## Hard Rules (non-negotiable)

- **NIEMALS** API-Schlüssel, Anthropic-Tokens, Passwörter oder private Pfade committen, hardcoden oder in Exporte (`devcenter-workspace-v1.json`) übernehmen.
- **Plan-D-Konvention beachten:** Die OneDrive-Kopie ist eine Daten-/Deploykopie (kein `.git`). Quellcode-Änderungen und Tests primär im Klon `C:\_Local_DEV\repos\DevCenter` ausführen und mit `robocopy /E` (niemals `/MIR`!) nach OneDrive synchronisieren.
- **Testsuite 100% grün halten:** Vor und nach jeder Modifikation `pytest` ausführen.
- **Thread-Sicherheit in PySide6:** Alle GUI-Mutationen und UI-Events müssen auf dem Qt-Hauptthread laufen; Hintergrund-Prozesse (PyInstaller, KI-Worker, FTS-Indexierung) verwenden `QThread` / `Worker` mit Signal-Slot-Verdrahtung oder thread-sichere Events.
- **SQLite/FTS5-Resilienz:** Bei Datenbankzugriffen (`profiler_bridge.py`, `sync_manager.py`) immer 30s `busy_timeout` und WAL-Journalierung nutzen sowie bei FTS5-Reindizierung das Delete-then-Insert-Muster beachten.
- **Vertriebskanal-Grenzen:** GitHub (`dev-bricks/DevCenter`) ist der kanonische Release-Kanal. Windows-Store-Listing ist gemäß Beschluss vom 2026-08-11 ausgesetzt (reines Entwickler-Tooling).

## Soft Guidelines

- **Internationalisierung (i18n):** Neue sichtbare UI-Texte zweisprachig (DE/EN) in `locales/` und `translator.py` pflegen.
- **Web Companion:** Der statische PWA-Viewer unter `web_companion/` ist ein lokaler, reiner Read-Only-Viewer für redigierte JSON-Workspaces (`devcenter-workspace-v1.json`). Keine Upload-Server oder Backend-Endpunkte hinzufügen.
- **Icon-Artefakte:** `mobile_icons/` und generierte Icon-Sätze dienen der Multi-Plattform-Bereitstellung, begründen aber keinen separaten mobilen Release-Status.

## Aktive Statusquellen & Dokumente

| Datei | Zweck |
|---|---|
| [`AUFGABEN.txt`](./AUFGABEN.txt) | Kanonischer Aufgaben- und Feature-Status |
| [`CHANGELOG.md`](./CHANGELOG.md) | Chronologische Versionshistorie |
| [`DevCenter.repo.md`](./DevCenter.repo.md) | Plan-D-Repository-Pointer und Host-Tabelle |
| [`ARCHITEKTUR_DevCenter.md`](./ARCHITEKTUR_DevCenter.md) | Architektur- und Modul-Dokumentation |
| [`EXPORTFORMAT.md`](./EXPORTFORMAT.md) | Schema und Redaktionsregeln für Workspace-Export |
| [`THIRD_PARTY_LICENSES.txt`](./THIRD_PARTY_LICENSES.txt) | Drittanbieter-Lizenzen |
| [`PRIVACY_POLICY.md`](./PRIVACY_POLICY.md) | Lokale Datenhaltung und Datenschutz |
| [`README.md`](./README.md) | Zweisprachige Projektübersicht |

## Projekt-Struktur

```text
REL-PUB_DevCenter_SUITE/
├── main.py                   # App-Einstiegspunkt
├── translator.py             # Lokalisierungs- & Übersetzungs-Engine
├── manage_translations.py    # i18n-Prüfwerkzeug
├── src/
│   ├── core/                 # App-Pfade, Settings, Event-Bus, Project-Manager
│   ├── gui/                  # MainWindow, Panels (Editor, Analyze, Build, AI, Files), Dialoge
│   └── modules/
│       ├── editor/           # CodeEditor mit Highlighting und Auto-Indent
│       ├── analyzer/         # AST-Methoden-/Klassenanalyse, EncodingFixer
│       ├── builder/          # PyInstaller-Kompilator, Icon-Builder, Lizenzsammler
│       ├── ai_assistant/     # Claude/Anthropic-Service & Worker
│       └── filemanager/      # ProfilerBridge (SQLite/FTS5), BackupSync
├── tests/                    # Pytest- & Unittest-Suite (114+ Tests)
├── web_companion/            # Lokale statische PWA für Workspace-Viewer
├── assets/ / resources/      # Icons, Banner, Bilder
├── locales/                  # Übersetzungsdateien (DE / EN)
└── releases/                 # Lokale Build-Artefakte
```

## Umgebungs- & Konfigurations-Hinweise

- **Konfigurationspfade:**
  - Windows: `%APPDATA%\DevCenter\settings.json`
  - Linux / macOS: `~/.config/DevCenter/settings.json` (XDG-konform)
- **Umgebungsvariablen:**
  - `ANTHROPIC_API_KEY`: Optionaler API-Key für den Claude-Assistenten (alternativ Windows-Keyring oder GUI-Settings).
  - `PYTHONIOENCODING=utf-8`: Standard für alle CLI- und Python-Ausführungen.

## Meta

- Diese Datei wurde am 2026-08-17 im Rahmen des `SOFTWARE PROJECT BOOTSTRAP CHECK` aus dem kanonischen `project-docs`-Template erstellt und auf DevCenter zugeschnitten.
- Bei Modul-, Schema- oder Strukturänderungen `updated` und `last_verified` nachziehen.

<!-- REMEMBER: ENDUSERTEXTE BEKOMMEN ECHTE UMLAUTE Ü Ö Ä -->
