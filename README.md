# DevCenter

**Local-first Python IDE and developer toolkit for Windows.** DevCenter combines a PySide6 code editor, static analyzer, PyInstaller build helper, license collector, file index and optional Claude/Anthropic assistant in one desktop suite.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-GPL%20v3-blue)

> **Not** Azure DevCenter, Microsoft Dev Box, Moderne DevCenter or Devbox. This is `dev-bricks/DevCenter` — an open-source Python desktop app.

## Start Here

| Need | Tool |
|---|---|
| Local Python IDE with editor, analyzer and build helper | `python main.py` |
| One-click EXE packaging | `build_exe.bat` / Build tab |
| Static code analysis | Analyze tab |
| Workspace export for PWA companion | File → Export workspace |
| Windows launcher | `START_DevCenter.bat` |

![DevCenter main window showing the local Python IDE dashboard](README/screenshots/main.png)

## Why DevCenter

- **Local-first workflow:** projects, indexes, settings and build artifacts stay on your machine by default.
- **Python desktop focus:** PySide6 interface, syntax highlighting, project explorer, terminal output and settings persistence.
- **Static analysis built in:** method/class detection, complexity checks, import analysis, TODO/FIXME detection and encoding repair helpers.
- **Build and release helpers:** PyInstaller wrapper, icon conversion, third-party license collection, release notes and export planning.
- **Optional AI assistant:** Claude/Anthropic integration is opt-in and uses local settings, keyring or environment variables.
- **Companion-ready export:** writes a redacted `devcenter-workspace-v1.json` for the static `web_companion/` PWA viewer.

## Quick Start

```bash
git clone https://github.com/dev-bricks/DevCenter.git
cd DevCenter
pip install -r requirements.txt
python main.py
```

Windows helpers:

```batch
START_DevCenter.bat
build_exe.bat
```

## Features

### Editor
- Python syntax highlighting, line numbers, auto-indent, multi-tab
- Comment toggle (Ctrl+/), drag-and-drop files

### Static Analysis
- AST-based method and class detection
- Cyclomatic complexity, unused import detection
- TODO/FIXME finder, encoding checker and repair

### Build System
- One-click EXE via PyInstaller (one-file / one-directory)
- ICO converter (PNG/JPG to ICO)
- Third-party license collector for distributions

### AI Assistant
- Claude/Anthropic API integration — opt-in, key stays local
- Code generation, review, explanation, and development loop

### File Management
- SQLite file index with full-text search
- Duplicate detection (hash-based)
- Backup sync with automatic WAL checkpoint

### Settings and Persistence
- Structured JSON settings for editor, build, AI, sync and appearance
- Import/export support for reproducible setups
- Theme and window state restored on restart

### Web Companion
- Static `web_companion/` PWA viewer for redacted workspace exports
- Installable, offline-capable, no backend required

## Installation

Requirements: Python 3.10+, Windows 10/11 (primary), Linux/macOS (experimental)

```bash
git clone https://github.com/dev-bricks/DevCenter.git
cd DevCenter
pip install -r requirements.txt
python main.py
```

Dependencies (see `requirements.txt`):

```
PySide6>=6.5.0        # GUI framework
pyinstaller>=5.0      # EXE packaging
Pillow>=9.0           # Image processing
anthropic>=0.18.0     # Claude API (optional)
chardet>=5.0          # Encoding detection
keyring>=23.0         # Secure key storage
```

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Shift+N | New project |
| Ctrl+Shift+O | Open project |
| F5 | Run |
| F6 | Build |
| Ctrl+/ | Toggle comment |
| Ctrl+Shift+A | Toggle AI assistant |
| Ctrl+, | Settings |

## Tests

```bash
python -m unittest discover -s tests -v
python -m compileall -q main.py manage_translations.py translator.py src tests
```

GitHub Actions runs the same smoke checks on Python 3.10, 3.11 and 3.12.

## Privacy

DevCenter is a local desktop application. Projects, settings, file indexes and build artifacts stay on your machine by default. Network access occurs only for explicitly configured integrations such as the optional Claude/Anthropic API or package installation commands started by the user.

API keys must not be committed to the repository. Use environment variables, the local keyring or the app settings.

Details: [PRIVACY_POLICY.md](PRIVACY_POLICY.md)

## Roadmap

### Version 1.1
- Code folding
- Extended search and replace
- Git integration
- Debugger support

### Version 1.2
- Plugin system
- Additional themes
- MSIX packaging
- Auto-update

## Project Structure

```
DevCenter/
├── main.py                   # Entry point
├── requirements.txt
├── src/
│   ├── core/                 # Settings, event bus, project manager
│   ├── modules/
│   │   ├── editor/           # Code editor with syntax highlighting
│   │   ├── analyzer/         # AST analysis, encoding repair
│   │   ├── builder/          # PyInstaller wrapper, icon converter, license collector
│   │   ├── ai_assistant/     # Claude API integration
│   │   └── filemanager/      # File index, backup sync
│   └── gui/                  # Main window, panels, dialogs
├── web_companion/            # Static PWA viewer for workspace exports
└── tests/                    # Unit tests
```

## License

GPL v3 — see [LICENSE](LICENSE). PySide6 is LGPL.

## Liability

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, no maintenance guarantee, no fitness-for-purpose assumed.

---

## Deutsch / German

DevCenter ist eine lokale Desktop-Entwicklungsumgebung für Python-Projekte: **Code schreiben → Analysieren → Testen → Kompilieren → Veröffentlichen**. Kombiniert 11 spezialisierte Tools in einer kohärenten Suite.

Nicht identisch mit Azure DevCenter, Microsoft Dev Box, Moderne DevCenter oder Devbox.

### Fusionierte Tools

| Ursprungstool | Modul | Funktion |
|---|---|---|
| PythonBox V8 | Editor | Code-Editor mit Syntax-Highlighting, Auto-Indent |
| MethodenAnalyser V3 | Analyzer | Statische Code-Analyse, Komplexitätsberechnung |
| EncodingFixer | Analyzer | Encoding-Erkennung und -Reparatur |
| UltimateKompilator V3.1 | Builder | Python → EXE Kompilierung via PyInstaller |
| IcoBuilder | Builder | Bild → ICO Konvertierung |
| ThirdPartyLicenses | Builder | Lizenz-Sammlung für Third-Party-Pakete |
| Entwicklerschleife V3 | AI Assistant | Claude API Integration für Code-Generierung |
| ProFiler V14 | FileManager | Datei-Indizierung und Volltext-Suche |
| ProSync V3.1 | FileManager | Intelligente Backup-Synchronisation |

### Konfiguration

Einstellungen werden gespeichert in:
- **Windows:** `%APPDATA%\DevCenter\settings.json`
- **Linux/macOS:** `~/.config/DevCenter/settings.json`

Wichtige Einstellungen:

```json
{
  "editor": { "font_family": "Consolas", "font_size": 11, "tab_size": 4 },
  "build": { "output_dir": "dist", "one_file": true },
  "ai": { "api_key": "", "model": "claude-sonnet-4-5", "max_tokens": 4096 },
  "sync": { "backup_path": "D:\\Backups\\DevCenter", "auto_backup": true }
}
```

### Datenschutz

DevCenter ist eine lokale Desktop-Anwendung. Projekte, Einstellungen, Datei-Indizes und Build-Artefakte bleiben standardmäßig auf dem lokalen Rechner. Netzwerkzugriffe entstehen nur durch explizit konfigurierte Integrationen.

API-Schlüssel gehören nicht in das Repository. Details: [PRIVACY_POLICY.md](PRIVACY_POLICY.md)

### Haftung

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gelten die Haftungsausschlüsse der GPL-3.0. Nutzung auf eigenes Risiko.
