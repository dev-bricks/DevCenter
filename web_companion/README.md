# DevCenter Web-Companion

Stand: 2026-06-06

Der Companion ist jetzt als statischer Web-/PWA-Viewer gestartet. Er ersetzt keine IDE,
sondern zeigt redigierte DevCenter-Exporte aus der Desktop-App lokal, mobil und offline
an. Die Desktop-App erzeugt die passende Datei weiter direkt über
`Datei -> Arbeitsstand exportieren...`.

## Enthalten

- Lokaler Import von `devcenter-workspace-v1.json` per Datei oder eingefügtem JSON.
- Demo-Arbeitsstand unter `fixtures/demo-workspace.json` für Smokes und UI-Checks.
- Read-only-Dashboard für Projektmetadaten, Analysebefunde, Build-Stand, Release-Checks,
  Dependencies und offene Aufgaben.
- PWA-Basis mit `manifest.webmanifest`, Service Worker und lokalem Cache des zuletzt
  geladenen Arbeitsstands.
- Kleine Node-Tests für Schema-Parsing und PWA-Shell.

## Starten

Es gibt absichtlich keinen Upload-Server. Für einen lokalen Smoke reicht ein statischer
Dateiserver, zum Beispiel:

```powershell
python -m http.server 4178
```

Dann im Browser öffnen:

- `http://127.0.0.1:4178/web_companion/index.html`
- `http://127.0.0.1:4178/web_companion/index.html?demo=1`

## Tests

```powershell
cd web_companion
npm test
node --check app.js
node --check library.js
node --check sw.js
```

## Nicht-Ziele

- Kein Code-Editor mit lokaler Ausführung.
- Kein PyInstaller- oder Terminal-Build im Browser.
- Kein Cloud-Service ohne separate Datenschutzentscheidung.

## Nächste Schritte

1. Android-/iOS-Browser-Smokes für Touch, Installierbarkeit und Offline-Restore dokumentieren.
2. Companion-Ansichten bei Bedarf um Build-/Release-Historie aus echten Exporten schärfen.
3. Erst danach über eine optionale native Hülle für iOS oder Android nachdenken.
