# DevCenter Web-Companion

Stand: 2026-06-01

Dieser Ordner ist für einen späteren statischen Web-/PWA-Companion vorgesehen. Der Companion soll keine vollständige IDE ersetzen, sondern redigierte DevCenter-Exporte anzeigen. Die Desktop-App erzeugt die passende Datei seit 2026-06-01 direkt über `Datei -> Arbeitsstand exportieren...`.

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

1. Beispieldatei für `devcenter-workspace-v1.json` aus der Desktop-App erzeugen und als Fixture ablegen.
2. Minimalen Import-Viewer bauen.
3. Mobile-Smokes für Android und iOS ergänzen.
4. Export-/Importvertrag gegen `EXPORTFORMAT.md` testen.
