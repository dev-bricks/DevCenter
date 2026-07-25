# Support & Hilfestellung — DevCenter Suite

Stand: 2026-07-25

---

## Deutsch

### Support-Kanäle

Bei Fragen, Problem-Berichten oder Verbesserungsvorschlägen zu **DevCenter Suite** nutzen Sie bitte folgende Wege:

- **GitHub Issue Tracker:** [https://github.com/file-bricks/DevCenter/issues](https://github.com/file-bricks/DevCenter/issues)
- **Dokumentation:** Siehe `README.md` und `ARCHITEKTUR_DevCenter.md` im Projektverzeichnis.

### Häufig gestellte Fragen (FAQ)

1. **Werden meine Projektdaten oder API-Schlüssel übertragen?**
   Nein. DevCenter Suite speichert Einstellungen und API-Schlüssel lokal (verschlüsselt im System-Keyring, sofern verfügbar). Netzwerkverbindungen entstehen nur bei Nutzung externer APIs (z. B. Anthropic/Claude API).

2. **Wie erstelle ich ein Executable?**
   Nutzen Sie den Menüpunkt *Build -> Exe erstellen* oder rufen Sie `build_exe.bat` direkt auf. DevCenter nutzt PyInstaller unter der Haube.

3. **Welche Python-Versionen werden unterstützt?**
   DevCenter Suite benötigt Python 3.11 oder höher sowie PySide6.

---

## English

### Support Channels

For bug reports, questions, or feature requests regarding **DevCenter Suite**, please use:

- **GitHub Issue Tracker:** [https://github.com/file-bricks/DevCenter/issues](https://github.com/file-bricks/DevCenter/issues)
- **Documentation:** Refer to `README.md` and `ARCHITEKTUR_DevCenter.md` in the project root.

### Frequently Asked Questions (FAQ)

1. **Is my code or API key uploaded anywhere?**
   No. DevCenter Suite runs locally. API keys are stored in the system keyring. Network requests only occur when you explicitly invoke external services (e.g. Claude API).

2. **How do I build an executable?**
   Use the GUI menu *Build -> Build Executable* or execute `build_exe.bat` directly. DevCenter uses PyInstaller internally.

3. **What Python version is required?**
   DevCenter Suite requires Python 3.11+ and PySide6.
