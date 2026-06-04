# 🚀 DevCenter

**Python Development Suite** - Eine integrierte Entwicklungsumgebung für den kompletten Python-Entwicklungszyklus

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-GPL%20v3-blue)

## 📋 Übersicht

DevCenter ist eine All-in-One Desktop-IDE für Python-Projekte, die den kompletten Entwicklungszyklus unterstützt:

**Code schreiben → Analysieren → Testen → Kompilieren → Veröffentlichen**

## Screenshot

![DevCenter Hauptfenster](README/screenshots/main.png)

### 🔧 Fusionierte Tools

DevCenter vereint 11 spezialisierte Entwicklertools zu einer kohärenten Suite:

| Ursprungstool | Modul | Funktion |
|---------------|-------|----------|
| PythonBox V8 | Editor | Code-Editor mit Syntax-Highlighting, Auto-Indent |
| MethodenAnalyser V3 | Analyzer | Statische Code-Analyse, Komplexitätsberechnung |
| EncodingFixer | Analyzer | Encoding-Erkennung und -Reparatur |
| UltimateKompilator V3.1 | Builder | Python → EXE Kompilierung via PyInstaller |
| IcoBuilder | Builder | Bild → ICO Konvertierung |
| ThirdPartyLicenses | Builder | Lizenz-Sammlung für Third-Party-Pakete |
| Entwicklerschleife V3 | AI Assistant | Claude API Integration für Code-Generierung |
| ProFiler V14 | FileManager | Datei-Indizierung und Volltext-Suche |
| ProSync V3.1 | FileManager | Intelligente Backup-Synchronisation |

## 🛠️ Installation

### Voraussetzungen
- Python 3.10 oder höher
- Windows 10/11 (primär), Linux/macOS (experimentell)

### Installation

```bash
# Repository klonen
git clone https://github.com/dev-bricks/DevCenter.git
cd DevCenter

# Abhängigkeiten installieren
pip install -r requirements.txt

# Starten
python main.py
```

### Windows-Launcher und EXE-Build

```batch
START_DevCenter.bat
build_exe.bat
```

`build_exe.bat` erstellt eine lokale One-File-EXE mit PyInstaller. Die erzeugten Artefakte in `build/`, `dist/` und `releases/` werden nicht versioniert.

### Abhängigkeiten

```
PySide6>=6.5.0        # GUI-Framework
pyinstaller>=5.0      # EXE-Erstellung
Pillow>=9.0           # Bildverarbeitung
anthropic>=0.18.0     # Claude API
chardet>=5.0          # Encoding-Erkennung
keyring>=23.0         # Sichere Schlüsselspeicherung
```

## 📦 Projektstruktur

```
DevCenter/
├── main.py                      # Haupteinstiegspunkt
├── requirements.txt             # Abhängigkeiten
├── README.md                    # Diese Datei
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/                    # Kernkomponenten
│   │   ├── project_manager.py   # Projektverwaltung
│   │   ├── settings_manager.py  # Einstellungen (Singleton)
│   │   └── event_bus.py         # Event-System (Pub/Sub)
│   │
│   ├── modules/
│   │   ├── editor/              # Code-Editor
│   │   │   └── code_editor.py   # Editor mit Syntax-Highlighting
│   │   │
│   │   ├── analyzer/            # Code-Analyse
│   │   │   ├── method_analyzer.py  # AST-basierte Analyse
│   │   │   └── encoding_fixer.py   # Encoding-Tools
│   │   │
│   │   ├── builder/             # Build-System
│   │   │   ├── kompilator.py       # PyInstaller-Wrapper
│   │   │   ├── icon_builder.py     # ICO-Konvertierung
│   │   │   └── license_generator.py # Lizenz-Sammlung
│   │   │
│   │   ├── ai_assistant/        # AI-Integration
│   │   │   └── ai_service.py    # Claude API + DevelopmentLoop
│   │   │
│   │   └── filemanager/         # Datei-Management
│   │       ├── sync_manager.py  # Backup-Synchronisation
│   │       └── profiler_bridge.py # Datei-Index
│   │
│   └── gui/
│       ├── main_window.py       # Hauptfenster
│       │
│       ├── panels/              # UI-Panels
│       │   ├── explorer_panel.py   # Datei-Navigator
│       │   ├── output_panel.py     # Terminal-Ausgabe
│       │   ├── problems_panel.py   # Fehler/Warnungen
│       │   └── ai_panel.py         # AI-Chat-Interface
│       │
│       └── dialogs/             # Dialoge
│           ├── new_project_dialog.py
│           ├── settings_dialog.py
│           └── build_dialog.py
│
├── resources/
│   ├── themes/                  # UI-Themes
│   └── icons/                   # Anwendungs-Icons
│
└── tests/
    └── test_core.py             # Unit-Tests
```

## ⚡ Features

### Editor
- ✅ Python Syntax-Highlighting (Keywords, Strings, Kommentare, Decorators)
- ✅ Zeilennummern mit aktueller Zeilen-Hervorhebung
- ✅ Auto-Indent (erhält Einrückung, fügt nach `:` hinzu)
- ✅ Smart Backspace (springt zu Tab-Stops)
- ✅ Kommentar-Toggle (Ctrl+/)
- ✅ Mehrere Editor-Tabs
- ✅ Drag & Drop Dateien

### Analyse
- ✅ Klassen- und Methoden-Erkennung
- ✅ Import-Analyse (genutzt/ungenutzt)
- ✅ Zyklomatische Komplexitäts-Berechnung
- ✅ Mutable Default Argument Warnung
- ✅ Bare Except Warnung
- ✅ TODO/FIXME Erkennung
- ✅ Encoding-Prüfung und -Reparatur

### Build
- ✅ One-Click EXE-Erstellung
- ✅ One-File und One-Directory Modi
- ✅ Icon-Konvertierung (PNG/JPG → ICO)
- ✅ Hidden Imports Verwaltung
- ✅ Zusätzliche Dateien einbinden
- ✅ UPX-Komprimierung (optional)
- ✅ Third-Party-Lizenzen sammeln

### AI-Assistent
- ✅ Claude API Integration
- ✅ Code-Generierung aus Beschreibungen
- ✅ Code-Review und Verbesserungsvorschläge
- ✅ Code-Erklärungen
- ✅ Fehler-Behebungshilfe
- ✅ Entwicklerschleife (Plan → Code → Review)

### Datei-Management
- ✅ Projekt-Explorer mit Kontextmenü
- ✅ SQLite-basierter Datei-Index
- ✅ Volltext-Suche im Code
- ✅ Duplikat-Erkennung (Hash-basiert)
- ✅ Automatische Backups mit WAL-Checkpoint
- ✅ Musterbasierte Ausschlüsse

### Einstellungen & Persistenz
- ✅ Strukturierte JSON-Einstellungen für Editor, Build, AI, Sync und Appearance
- ✅ Theme- und Fensterzustand werden beim Beenden gespeichert und beim Start wiederhergestellt
- ✅ Import/Export von Einstellungen für reproduzierbare Arbeitsumgebungen

## 🎨 Benutzeroberfläche

```
┌─────────────────────────────────────────────────────────────────┐
│  Datei  Bearbeiten  Ansicht  Ausführen  Analyse  Hilfe          │
├─────────────────────────────────────────────────────────────────┤
│  📁 Neu  📂 Öffnen  💾 Speichern  │  ▶ Ausführen  🔨 Build  │ 🤖 │
├────────────┬────────────────────────────────┬───────────────────┤
│ 📁 EXPLORER│  main.py  │  utils.py  │ ●app │   🤖 AI Assistent │
│            │─────────────────────────────────│                   │
│ 📁 src     │  1 │ # -*- coding: utf-8 -*-    │   [Chat-Verlauf]  │
│   📄 main  │  2 │ """                        │                   │
│   📄 utils │  3 │ DevCenter - Main           │   ─────────────   │
│   📁 gui   │  4 │ """                        │                   │
│            │  5 │                            │   [Input-Feld]    │
│            │  6 │ import sys                 │   [✨] [🔍] [📖]  │
│            ├────────────────────────────────┤                   │
│            │  🖥️ Terminal  │  ⚠️ Probleme   │                   │
│            │  $ python main.py              │                   │
│            │  Hello, World!                 │                   │
│            │  ✓ Prozess beendet (Code: 0)   │                   │
├────────────┴────────────────────────────────┴───────────────────┤
│  📁 DevCenter                              Ln 5, Col 1  │ UTF-8 │
└─────────────────────────────────────────────────────────────────┘
```

## ⌨️ Tastenkürzel

| Kürzel | Aktion |
|--------|--------|
| Ctrl+N | Neue Datei |
| Ctrl+O | Datei öffnen |
| Ctrl+S | Speichern |
| Ctrl+Shift+N | Neues Projekt |
| Ctrl+Shift+O | Projekt öffnen |
| Ctrl+Shift+S | Speichern unter |
| F5 | Ausführen |
| F6 | Build erstellen |
| Ctrl+/ | Kommentar umschalten |
| Ctrl+Shift+A | AI-Assistent umschalten |
| Ctrl+, | Einstellungen |

## 🔧 Konfiguration

Einstellungen werden gespeichert in:
- **Windows:** `%APPDATA%\DevCenter\settings.json`
- **Linux/macOS:** `~/.config/DevCenter/settings.json`

### Wichtige Einstellungen

```json
{
  "editor": {
    "font_family": "Consolas",
    "font_size": 11,
    "tab_size": 4,
    "line_numbers": true,
    "auto_save": false
  },
  "build": {
    "output_dir": "dist",
    "one_file": true,
    "console": true
  },
  "ai": {
    "api_key": "",
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 4096
  },
  "sync": {
    "backup_path": "D:\\Backups\\DevCenter",
    "auto_backup": true,
    "excludes": ["__pycache__", ".git", "venv"]
  }
}
```

## 🧪 Tests

```bash
# Alle Tests ausführen
python -m unittest discover -s tests -v

# Syntaxprüfung
python -m compileall -q main.py manage_translations.py translator.py src tests
```

GitHub Actions führt dieselben Smoke-Checks auf Python 3.10, 3.11 und 3.12 aus.

## Datenschutz / Privacy

DevCenter ist eine lokale Desktop-Anwendung. Projekte, Einstellungen, Datei-Indizes und Build-Artefakte bleiben standardmäßig auf dem lokalen Rechner. Netzwerkzugriffe entstehen nur durch explizit konfigurierte Integrationen, zum Beispiel die optionale Claude/Anthropic-API im AI-Assistenten oder manuell gestartete Paketinstallationen.

API-Schlüssel gehören nicht in das Repository. Verwenden Sie Umgebungsvariablen, den lokalen Schlüsselbund oder die Anwendungseinstellungen.

Details stehen in [PRIVACY_POLICY.md](PRIVACY_POLICY.md).

## 📊 Statistiken

| Metrik | Wert |
|--------|------|
| Python-Dateien | 26 |
| Code-Zeilen | ~7.500 |
| Module | 5 (Core, Editor, Analyzer, Builder, FileManager, AI) |
| GUI-Panels | 4 |
| GUI-Dialoge | 3 |
| Unit-Tests | 20+ |

## 🗺️ Roadmap

### Version 1.1
- [ ] Code-Folding
- [ ] Erweiterte Suchen-Ersetzen
- [ ] Git-Integration
- [ ] Debugger-Unterstützung

### Version 1.2
- [ ] Plugin-System
- [ ] Weitere Themes
- [ ] MSIX-Packaging
- [ ] Auto-Update

## 📝 Lizenz

GPL v3 - Siehe [LICENSE](LICENSE)

Dieses Projekt verwendet PySide6 (LGPL).

## 🤝 Mitwirkende

Basiert auf dem Fusionskonzept der Entwickler-Suite.
Erstellt mit PySide6 und Claude AI.

---

**DevCenter v1.0.0** | Januar 2026

---

## English

### DevCenter — Python Development Suite

An all-in-one Python IDE covering the full development cycle: **Write → Analyze → Test → Build → Publish**. DevCenter merges 11 specialized tools into one cohesive suite.

![DevCenter main window](README/screenshots/main.png)

### Features

- **Code Editor:** Syntax highlighting, line numbers, auto-indent, comment toggle (Ctrl+/), multi-tab
- **Static Analyzer:** AST-based method analysis, cyclomatic complexity, unused imports, bare-except detection
- **Build System:** One-click EXE via PyInstaller (one-file / one-directory), ICO converter, license collector
- **AI Assistant:** Claude API integration — code generation, review, explanation, development loop
- **File Management:** SQLite file index, full-text search, duplicate detection, automatic backups
- **Settings Persistence:** Structured JSON settings for editor, build, AI, sync, and appearance, including import/export support

### Requirements

- Python 3.10+
- Windows 10/11 (primary), Linux/macOS (experimental)

### Installation

```bash
git clone https://github.com/dev-bricks/DevCenter.git
cd DevCenter
pip install -r requirements.txt
python main.py
```

### Key Shortcuts

| Shortcut | Action |
|----------|--------|
| F5 | Run |
| F6 | Build |
| Ctrl+/ | Toggle comment |
| Ctrl+Shift+A | Toggle AI assistant |

### License

GPL v3 — See [LICENSE](LICENSE) for details.

---

## Haftung / Liability

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gelten die Haftungsausschlüsse der GPL-3.0.

Nutzung auf eigenes Risiko. Keine Wartungszusage, keine Verfügbarkeitsgarantie, keine Gewähr für Fehlerfreiheit oder Eignung für einen bestimmten Zweck.

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, no maintenance guarantee, no fitness-for-purpose assumed.

