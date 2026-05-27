# DevCenter Web-Companion

Stand: 2026-05-27

Dieser Ordner ist für einen späteren statischen Web-/PWA-Companion vorgesehen. Der Companion soll keine vollständige IDE ersetzen, sondern redigierte DevCenter-Exporte anzeigen.

## Geplanter Umfang

- `devcenter-workspace-v1.json` lokal im Browser importieren.
- Projektstatus, Analysezusammenfassung, Build-Konfiguration und Release-Checklisten anzeigen.
- Offline-fähig als PWA laufen.
- Android und iOS über dieselbe Weboberfläche bedienen.
- Keine Projektquellen oder API-Schlüssel hochladen.

## Nicht-Ziele

- Kein Code-Editor mit lokaler Ausführung.
- Kein PyInstaller- oder Terminal-Build im Browser.
- Kein Cloud-Service ohne separate Datenschutzentscheidung.

## Nächste Schritte

1. Beispieldatei für `devcenter-workspace-v1.json` erstellen.
2. Minimalen Import-Viewer bauen.
3. Mobile-Smokes für Android und iOS ergänzen.
4. Export-/Importvertrag gegen `EXPORTFORMAT.md` testen.
