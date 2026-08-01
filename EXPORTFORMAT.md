# Exportformat DevCenter

Stand: 2026-07-22

## Zweck

`devcenter-workspace-v1.json` ist das Austauschformat zwischen der DevCenter-Desktop-App und einem späteren Web-/PWA-Companion. Es transportiert Projektstatus, Analyseberichte, Build-Checklisten und redigierte Konfigurationen, ohne vollständige Quelltexte, API-Schlüssel, lokale Datenbanken oder Build-Artefakte weiterzugeben.

Seit 2026-06-01 erzeugt die Desktop-App diesen Export direkt über `Datei -> Arbeitsstand exportieren...`.

## Grundregeln

- UTF-8 ohne BOM.
- JSON-Objekt als Wurzel.
- `schema` ist exakt `devcenter-workspace-v1`.
- Export ist redigiert: Secrets, Tokens, Keyring-Werte und lokale Vollpfade werden nicht übernommen.
- Projektinhalte werden nur als Metadaten, Hashes oder ausdrücklich freigegebene Snippets exportiert.
- Import in den Companion ist read-only; er verändert keine lokalen Desktop-Projekte.

## Implementierte Struktur (Schema v1)

```json
{
  "schema": "devcenter-workspace-v1",
  "schema_version": 1,
  "app": {
    "name": "DevCenter",
    "version": "1.0.0",
    "exported_at": "2026-05-27T00:00:00Z"
  },
  "project": {
    "name": "example-project",
    "path_ref": "project-1",
    "language": "python",
    "frameworks": ["PySide6"],
    "has_devcenter_json": true
  },
  "analysis": {
    "summary": {
      "files_indexed": 0,
      "problems_total": 0,
      "warnings_total": 0
    },
    "problems": []
  },
  "build": {
    "target": "windows-x64",
    "one_file": true,
    "console": true,
    "output_ref": "dist",
    "hidden_imports": []
  },
  "dependencies": {
    "requirements": [],
    "licenses": []
  },
  "release": {
    "targets": [
      "github",
      "windows_store",
      "macos_direct",
      "linux_direct",
      "web"
    ],
    "target_status": {
      "github": "supported",
      "web": "supported",
      "windows_store": "planned",
      "linux_direct": "planned",
      "macos_direct": "planned"
    },
    "checklists": []
  },
  "tasks": [],
  "redactions": {
    "paths": true,
    "secrets": true,
    "source_content": true
  }
}
```

Die Desktop-Version stammt aus `pyproject.toml`; der Companion trägt dieselbe
Version in `web_companion/package.json`. Die Schema-Version bleibt bei additiven,
rückwärtskompatiblen Feldern `1`. Ein inkompatibler Strukturwechsel erhält einen
neuen Schema-Namen und eine neue Schema-Version.

## Rollen und Readback

- Die Desktop-App erzeugt ausschließlich den lokalen, redigierten JSON-Export.
- `web_companion/` liest und validiert den Export ausschließlich im Browser. Es
  gibt keinen Upload, Serverzugriff oder Rückschreiben in Desktop-Projekte.
- `web_companion/fixtures/demo-workspace.json` ist der reproduzierbare Readback
  für die Tests. `npm test` prüft Schema, Pflichtfelder und Redaktionsgrenzen.

Release-Kanäle sind nur dann aktiv, wenn `release.target_status` den Wert
`supported` enthält. Windows Store, Linux und macOS stehen hier bewusst als
`planned`; aus dem Export folgt keine Veröffentlichung oder Plattformzusage.

## Redaktionsregeln

| Datentyp | Exportregel |
|---|---|
| API-Schlüssel, Tokens, Keyring-Daten | Nie exportieren. |
| Absolute lokale Pfade | In stabile Referenzen wie `project-1`, `backup-dir-1` oder `dist` umwandeln. |
| Quelltextdateien | Standardmäßig nicht exportieren; nur Name, Endung, Größe, Hash, Analysebefunde. |
| Analysebefunde | Exportieren, wenn sie ohne vollständigen Quelltext verständlich sind. |
| Build-Konfiguration | Exportieren, aber lokale Pfade und Secrets redigieren. |
| Lizenzdaten | Paketname, Version, Lizenz und Quelle exportieren. |
| Aufgaben | Nur offene technische Aufgaben exportieren, keine internen Agenten-Notizen. |

## Akzeptanzkriterien für P0/P1

- Exportfunktion erzeugt valides JSON nach obigem Schema.
- Tests decken Secret- und Pfadredaktion ab.
- Companion kann eine Beispieldatei lokal importieren und anzeigen.
- Kein Export enthält `api_key`, `token`, `secret`, `%APPDATA%`, `C:\Users\` oder unredigierte Projekt-Vollpfade.

## Implementierter Desktop-Export (2026-06-01)

- Liest Projektmetadaten aus `devcenter.json` und der aktuell geöffneten Projektkonfiguration.
- Exportiert Analysezusammenfassung und die aktuelle Problem-Liste in redigierter Form.
- Wandelt Projektpfade in `project-1/...` und externe lokale Pfade in stabile Referenzen wie `output-dir-1` um.
- Übernimmt nur offene Aufgaben aus `AUFGABEN.txt`; erledigte Punkte bleiben außen vor.
- Exportiert bewusst keine AI- oder Keyring-Daten.
