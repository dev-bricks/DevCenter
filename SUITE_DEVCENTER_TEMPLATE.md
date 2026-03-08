# 📦 DevCenter Suite – Final Documentation

## 1. Überblick

**Kurzbeschreibung:**  
DevCenter ist eine All-in-One Desktop-IDE für den kompletten Python-Entwicklungszyklus: Code schreiben → Analysieren → Testen → Kompilieren → Veröffentlichen.

| Feld | Wert |
|------|------|
| **Version** | 1.0.0 |
| **Stand** | 2026-01-09 |
| **Status** | MVP (85% fertig) |
| **Sprache** | Python 3.10+ |
| **Framework** | PyQt6 + QScintilla |
| **Codebase** | ~7.500 Zeilen / 26 Dateien |

---

## 2. Herkunft & Fusion

### 2.1 Ursprungstools

| Tool | Version | Zeilen | Reifegrad | Kernfunktion |
|------|---------|--------|-----------|--------------|
| ProFiler | V14 | 7.575 | 85% | Datei-Management, PDF-Tools, OCR, Sync |
| PythonBox | V8 | 3.381 | 85% | Python IDE mit Debugger, Git |
| ProSync | V3.1 | 1.764 | 85% | Datei-Sync mit DB-Schutz |
| Entwicklerschleife | V3 | 1.010 | 75% | AI-gestützte Code-Generierung |
| MethodenAnalyser | V3 | 1.066 | 85% | Statische Code-Analyse |
| EncodingFixer | - | 57 | 70% | Encoding-Reparatur (ftfy) |
| UltimateKompilator | V3.1 | 443 | 85% | Python→EXE mit Auto-Icons |
| WinStorePackager | V2.3 | 1.376 | 80% | Windows Store Vorbereitung |
| IcoBuilder | - | 419 | 80% | Bild→ICO Konverter |
| pyCuttertxt | - | 91 | 75% | Code-Klassen-Extraktor |
| ThirdPartyLicenses | - | 27 | 100% | Lizenz-Generator |

**Gesamt:** 11 Tools, ~17.000 Zeilen Ursprungscode

### 2.2 Fusionsziel

> **"Eine All-in-One Desktop-IDE für den kompletten Python-Entwicklungszyklus"**

Die Suite vereint 11 spezialisierte Entwicklertools zu einer kohärenten IDE mit:
- Integriertem Code-Editor (PythonBox)
- Statischer Analyse (MethodenAnalyser)
- One-Click Build (Kompilator + IcoBuilder + Licenses)
- AI-Unterstützung (Entwicklerschleife)
- Projekt-Sync (ProSync + ProFiler)

### 2.3 Synergien

| Synergie | Beschreibung |
|----------|--------------|
| 🔄 **Editor + Analyzer** | Echtzeit-Fehleranzeige während des Tippens |
| 🤖 **Editor + AI** | Code-Generierung direkt im Editor |
| 🔍 **Analyzer + Builder** | Automatische Prüfung vor Build |
| 📁 **FileManager + Sync** | Nahtlose Backup-Integration |
| 🎨 **IcoBuilder + Kompilator** | Icon-Pipeline automatisiert |

---

## 3. Features

### 3.1 Hauptfunktionen

| Bereich | Icon | Features |
|---------|------|----------|
| **Editor** | 📝 | Syntax-Highlighting, Auto-Indent, Code Folding, Multi-Tab |
| **Analyzer** | 🔍 | AST-Analyse, Import-Check, Complexity, Encoding |
| **Builder** | 🔨 | PyInstaller, Icons, Lizenzen, MSIX |
| **AI Assistant** | 🤖 | Claude API, Code-Generierung, Review |
| **FileManager** | 📁 | Projekt-Index, Volltext-Suche, Backup |

### 3.2 Feature-Matrix

| Feature | Vor Fusion | Nach Fusion |
|---------|:----------:|:-----------:|
| IDE-Funktionen | Verteilt auf 3 Tools | ✅ Integriert |
| Code-Analyse | Separates Tool | ✅ In IDE eingebettet |
| Build-Prozess | 3 manuelle Schritte | ✅ One-Click-Build |
| AI-Unterstützung | Standalone | ✅ Context-aware |
| Projekt-Sync | Manuell | ✅ Automatisch |

### 3.3 Editor Features

- ✅ Python Syntax-Highlighting (Keywords, Strings, Kommentare, Decorators)
- ✅ Zeilennummern mit aktueller Zeilen-Hervorhebung
- ✅ Auto-Indent (erhält Einrückung, fügt nach `:` hinzu)
- ✅ Smart Backspace (springt zu Tab-Stops)
- ✅ Kommentar-Toggle (Ctrl+/)
- ✅ Mehrere Editor-Tabs
- ✅ Drag & Drop Dateien
- ✅ Code Folding

### 3.4 Analyse Features

- ✅ Klassen- und Methoden-Erkennung
- ✅ Import-Analyse (genutzt/ungenutzt)
- ✅ Zyklomatische Komplexitäts-Berechnung
- ✅ Mutable Default Argument Warnung
- ✅ Bare Except Warnung
- ✅ TODO/FIXME Erkennung
- ✅ Encoding-Prüfung und -Reparatur

### 3.5 Build Features

- ✅ One-Click EXE-Erstellung
- ✅ One-File und One-Directory Modi
- ✅ Icon-Konvertierung (PNG/JPG → ICO)
- ✅ Hidden Imports Verwaltung
- ✅ Zusätzliche Dateien einbinden
- ✅ UPX-Komprimierung (optional)
- ✅ Third-Party-Lizenzen sammeln

### 3.6 AI Features

- ✅ Claude API Integration
- ✅ Code-Generierung aus Beschreibungen
- ✅ Code-Review und Verbesserungsvorschläge
- ✅ Code-Erklärungen
- ✅ Fehler-Behebungshilfe
- ✅ Entwicklerschleife (Plan → Code → Review)

---

## 4. Architektur

### 4.1 Layer-Modell

```
┌─────────────────────────────────────────────────────────────────┐
│                         GUI Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ MainWindow  │  │   Panels    │  │        Dialogs          │  │
│  │             │  │  Explorer   │  │  NewProject, Settings   │  │
│  │             │  │  Output     │  │  Build                  │  │
│  │             │  │  Problems   │  │                         │  │
│  │             │  │  AI Panel   │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                       Module Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │
│  │  Editor  │  │ Analyzer │  │ Builder  │  │ AI Assistant  │   │
│  │          │  │          │  │          │  │               │   │
│  │ CodeEdit │  │ Methods  │  │ Kompilat │  │  AIService    │   │
│  │ Highlight│  │ Encoding │  │ Icon     │  │  DevLoop      │   │
│  │          │  │          │  │ License  │  │               │   │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘   │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     FileManager                            │  │
│  │            SyncManager      ProfilerBridge                 │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                        Core Layer                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ ProjectManager  │  │ SettingsManager │  │    EventBus     │  │
│  │                 │  │   (Singleton)   │  │   (Pub/Sub)     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Module

| Modul | Pfad | Beschreibung |
|-------|------|--------------|
| **ProjectManager** | `core/project_manager.py` | Projektverwaltung, Recent Projects |
| **SettingsManager** | `core/settings_manager.py` | Zentrale Einstellungen (Singleton) |
| **EventBus** | `core/event_bus.py` | Pub/Sub Event-System |
| **CodeEditor** | `modules/editor/code_editor.py` | QScintilla-basierter Editor |
| **MethodAnalyzer** | `modules/analyzer/method_analyzer.py` | AST-basierte Analyse |
| **EncodingFixer** | `modules/analyzer/encoding_fixer.py` | Encoding-Tools |
| **Kompilator** | `modules/builder/kompilator.py` | PyInstaller-Wrapper |
| **IconBuilder** | `modules/builder/icon_builder.py` | ICO-Konvertierung |
| **LicenseGenerator** | `modules/builder/license_generator.py` | pip-licenses |
| **AIService** | `modules/ai_assistant/ai_service.py` | Claude API |
| **SyncManager** | `modules/filemanager/sync_manager.py` | Backup-Sync |
| **ProfilerBridge** | `modules/filemanager/profiler_bridge.py` | Datei-Index |

### 4.3 Datenfluss

```
User Action → GUI Event → Module → Core/Storage
     ↓                      ↓
EventBus ← Status/Results ←─┘
     ↓
GUI Update
```

---

## 5. Projektstruktur

```
DevCenter/
├── main.py                      # Haupteinstiegspunkt
├── requirements.txt             # Abhängigkeiten
├── README.md                    # Projektbeschreibung
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

---

## 6. Datenformate & Datenbanken

### 6.1 Formate

| Format | Verwendung |
|--------|------------|
| **JSON** | Projektdatei (.devcenter/project.json), Settings |
| **SQLite** | Datei-Index (ProfilerBridge) |
| **Keyring** | Sichere API-Key-Speicherung |

### 6.2 Projekt-Konfiguration

```json
{
  "name": "MeinProjekt",
  "path": "C:/Projects/MeinProjekt",
  "main_file": "main.py",
  "python_version": "3.11",
  "build_output_dir": "dist",
  "build_icon": "icon.ico",
  "build_onefile": true,
  "build_console": true
}
```

### 6.3 Settings

Einstellungen in `%APPDATA%/DevCenter/settings.json`:
- EditorSettings (Font, Tab-Size, Auto-Save)
- BuildSettings (Output-Dir, One-File, Console)
- AISettings (API-Key, Model, Max-Tokens)
- SyncSettings (Backup-Path, Auto-Backup, Excludes)

---

## 7. Workflows

### 7.1 Entwicklungszyklus

```
1. PROJEKT ERSTELLEN
   └── FileManager: Ordnerstruktur + Git Init

2. CODE SCHREIBEN
   └── Editor: PythonBox mit Auto-Complete

3. AI-UNTERSTÜTZUNG (optional)
   └── AI Assistant: Planen → Generieren → Prüfen

4. ANALYSIEREN
   └── Analyzer: Methoden, Imports, Encoding prüfen

5. TESTEN
   └── Editor: Debugger + Output Panel

6. BUILD
   └── Builder: Kompilieren + Icons + Lizenzen

7. VERÖFFENTLICHEN
   └── Store Packager: MSIX für Windows Store

8. SYNC
   └── FileManager: Backup + DB-sichere Synchronisation
```

### 7.2 EventBus Events

| Event | Trigger | Reaktion |
|-------|---------|----------|
| `FILE_OPENED` | Datei öffnen | Tab erstellen, Recent aktualisieren |
| `FILE_SAVED` | Ctrl+S | Analyse triggern |
| `ANALYSIS_COMPLETE` | Nach Analyse | Problems Panel aktualisieren |
| `BUILD_PROGRESS` | Während Build | Progress Bar aktualisieren |
| `BUILD_COMPLETE` | Nach Build | Output Folder öffnen |

---

## 8. Installation & Setup

### 8.1 Voraussetzungen

| Anforderung | Version |
|-------------|---------|
| Python | 3.10+ |
| OS | Windows 10/11 (primär), Linux/macOS (experimentell) |
| RAM | 4 GB+ |
| Speicher | 500 MB |

### 8.2 Installation

```bash
# Repository / Ordner öffnen
cd "C:\Users\User\OneDrive\.SOFTWARE\SUITEN\DevCenter"

# Abhängigkeiten installieren
pip install -r requirements.txt

# Starten
python main.py
```

### 8.3 Abhängigkeiten

```
PyQt6>=6.4.0          # GUI-Framework
QScintilla>=2.13.0    # Code-Editor
pyinstaller>=5.0      # EXE-Erstellung
Pillow>=9.0           # Bildverarbeitung
anthropic>=0.18.0     # Claude API
chardet>=5.0          # Encoding-Erkennung
keyring>=23.0         # Sichere Schlüsselspeicherung
ftfy>=6.1.0           # Encoding-Reparatur
pip-licenses>=4.0.0   # Lizenz-Generierung
```

---

## 9. Build & Deployment

### 9.1 PyInstaller

```bash
pyinstaller --onefile --windowed --icon=resources/icons/devcenter.ico main.py
```

### 9.2 MSIX (geplant)

Store Packager für Windows Store Submission.

---

## 10. Tests

```bash
# Alle Tests ausführen
python -m pytest tests/ -v

# Oder mit unittest
python tests/test_core.py
```

---

## 11. Changelog

### 11.1 Zusammenfassung

| Datum | Version | Änderung |
|-------|---------|----------|
| 03.01.2026 | V0.1 | Fusionskonzept erstellt |
| 03.01.2026 | V0.5 | Core Framework implementiert |
| 09.01.2026 | V1.0 | MVP fertiggestellt |

### 11.2 Wichtige Meilensteine

- **Woche 1-4**: Projektfundament (Core, Editor, Projekt-Management)
- **Woche 5-6**: Code-Analyse (AST, Encoding, Problems Panel)
- **Woche 7-9**: Build-System (PyInstaller, Icons, Licenses)
- **Woche 10-11**: AI-Integration (Claude API, Code-Generierung)
- **Woche 12-13**: FileManager & Polish

---

## 12. Roadmap

### ✅ Erledigt (MVP)

- [x] Core Framework (ProjectManager, SettingsManager, EventBus)
- [x] Code-Editor mit Syntax-Highlighting
- [x] AST-basierte Code-Analyse
- [x] One-Click EXE Build
- [x] Icon-Konvertierung
- [x] AI Assistant Panel
- [x] Projekt-Suche

### ⏳ Offen

- [ ] Code-Folding verbessern
- [ ] Git-Integration
- [ ] Debugger-Unterstützung
- [ ] Plugin-System
- [ ] Auto-Update
- [ ] MSIX-Packaging

---

## 13. Lizenz

**MIT License**

---

## 14. Tastenkürzel

| Kürzel | Aktion |
|--------|--------|
| `Ctrl+N` | Neue Datei |
| `Ctrl+O` | Datei öffnen |
| `Ctrl+S` | Speichern |
| `Ctrl+Shift+N` | Neues Projekt |
| `Ctrl+Shift+O` | Projekt öffnen |
| `Ctrl+Shift+S` | Speichern unter |
| `F5` | Ausführen |
| `F6` | Build erstellen |
| `Ctrl+/` | Kommentar umschalten |
| `Ctrl+Shift+A` | AI-Assistent umschalten |
| `Ctrl+,` | Einstellungen |
| `Ctrl+F` | Suchen |
| `Ctrl+H` | Ersetzen |
| `Ctrl+Shift+F` | In Dateien suchen |
| `Ctrl+G` | Gehe zu Zeile |

---

## 15. UI-Layout

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

---

*Generiert: 2026-01-09 | DevCenter Suite MVP | ~7.500 Zeilen / 26 Dateien*
