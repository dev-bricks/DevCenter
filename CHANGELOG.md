# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- GitHub Actions Smoke-Checks für Python 3.10, 3.11 und 3.12.
- Lokales `build_exe.bat` für den PyInstaller-Build mit `DevCenter.ico`.
- Datenschutzhinweise für lokale Einstellungen, Datei-Indizes, Build-Artefakte und optionale API-Nutzung.
- `llms.txt` mit maschinenlesbarer Projektpositionierung, Datenschutzgrenzen und relevanten Suchbegriffen.

### Geändert / Changed
- README, Contribution- und Security-Dokumentation auf `dev-bricks/DevCenter` aktualisiert.
- Beispielkonfiguration für WinStorePackager anonymisiert und neutralisiert.
- README auf englischen GitHub-Einstieg, klarere DevCenter-Namensabgrenzung und bessere Discoverability-Keywords erweitert.
- Community-Workflows auf aktuelle Action-Versionen gehoben.

### Behoben / Fixed
- Persistenz unbekannter Einstellungsschlüssel abgesichert, damit UI-/Legacy-Aliase beim Speichern nicht verloren gehen.
- Fehlende `chardet`-Abhängigkeit für frische CI-/Installationsumgebungen ergänzt.
- Editor-Einstellungen werden nach dem Speichern auf offene Tabs angewendet; der Dialog persistiert jetzt auch „Aktuelle Zeile hervorheben“ und aktualisiert Schrift, Tab-Breite, Zeilennummern und Cursor-Markierung unmittelbar.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
