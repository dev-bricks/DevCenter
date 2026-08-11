# Exportformat DevCenter

Stand: 2026-08-11
Status: implementierter Desktop-Export, Schema `devcenter-workspace-v1`

## Zweck und Produktgrenze

`devcenter-workspace-v1.json` ist ein redigierter lokaler Arbeitsstand für
Speicherung oder eine ausdrücklich freigegebene Übergabe. Die Desktop-App
erzeugt ihn über `Datei -> Arbeitsstand exportieren...`. Der frühere Web/PWA-
Companion wurde entfernt; dieses Repository enthält keinen Browser-Importer,
keinen Upload-Dienst und keine `web_companion/`-Laufzeit.

## Grundregeln

- UTF-8 ohne BOM.
- JSON-Objekt als Wurzel.
- `schema` ist exakt `devcenter-workspace-v1` und `schema_version` ist `1`.
- Secrets, Tokens, Keyring-Werte und lokale Vollpfade werden redigiert.
- Projektinhalte werden nur als Metadaten, Hashes oder ausdrücklich freigegebene
  Snippets exportiert.
- Der Export ist ein read-only Artefakt; er verändert kein Projekt.

## Schema v1

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
    "targets": ["github", "windows_store", "linux_direct", "web"],
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

The `web` value remains in schema-v1 payloads for compatibility with existing
exports. It is a legacy field, not an implemented release channel.

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

## Verifizierte Prüfungen

- `tests/test_workspace_export.py` deckt Schema, Secret- und Pfadredaktion,
  Aufgaben und Release-Felder ab.
- Der Exportcode liegt in `src/core/workspace_export.py`; die Desktop-Version
  stammt aus `pyproject.toml`.
- Kein Export darf `api_key`, `token`, `secret`, `%APPDATA%`, `C:\Users\` oder
  unredigierte Projekt-Vollpfade enthalten.

## Implementierter Desktop-Export

- Liest Projektmetadaten aus `devcenter.json` und der aktuell geöffneten
  Projektkonfiguration.
- Exportiert Analysezusammenfassung und die aktuelle Problemliste in
  redigierter Form.
- Wandelt Projektpfade in `project-1/...` und externe lokale Pfade in stabile
  Referenzen wie `output-dir-1` um.
- Übernimmt nur offene Aufgaben aus `AUFGABEN.txt`; erledigte Punkte bleiben
  außen vor.
- Exportiert bewusst keine AI- oder Keyring-Daten.
