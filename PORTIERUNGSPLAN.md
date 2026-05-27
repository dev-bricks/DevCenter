# Portierungsplan DevCenter

Stand: 2026-05-27

## Kurzentscheidung

DevCenter bleibt zuerst eine lokale Desktop-IDE für Windows und GitHub. Eine gemeinsame Web-/Mobile-Linie ist sinnvoll, aber nicht als vollständiger IDE-Clone: Android, iOS und Web sollen später als schlanker PWA-Companion für Projektüberblick, Analyseberichte, Build-Checklisten und redigierte Arbeitsstands-Exporte entstehen. macOS und Linux werden als Source-Smoke-Ziele aus derselben PySide6-Codebasis geführt; eigene Desktop-Pakete kommen erst nach stabilen Smokes.

## Warum Portierung sinnvoll ist

DevCenter bündelt Editor, statische Analyse, Build, Lizenzsammlung, Dateiindex, Sync und optionalen AI-Assistenten. Der Nutzen ist auf dem Desktop am größten, weil lokale Projektdateien, PyInstaller-Builds, Schlüsselbund, Dateiindex und Terminalprozesse Zugriff auf das echte Dateisystem brauchen. Gleichzeitig entsteht ein mobiler Bedarf: Projektstatus prüfen, Analyseergebnisse ansehen, offene Build-/Store-Punkte nachverfolgen und einem Team oder LLM einen redigierten Projektstand weitergeben.

Die sinnvolle Plattformstrategie trennt deshalb:

- **Desktop-Vollversion:** lokale Entwicklung, Dateiindex, Build, AI-Assistent, Sync und Store-Vorbereitung.
- **Web/PWA-Companion:** lesbarer Projektstatus, Analyse- und Build-Reports, Aufgaben, Checklisten und Import eines redigierten `devcenter-workspace-v1.json`.
- **Native Mobile-Apps:** nur als PWA-Hülle oder späterer Store-Kanal, nicht als parallele IDE-Codebasis.

## Plattformbewertung

| Plattform | Bewertung | Entscheidung |
|---|---|---|
| Windows Store | Möglich, aber nicht kurzfristig. DevCenter ist groß, hat optionalen AI-Key, Build-/Dateisystemzugriffe und komplexe IDE-Workflows. | Vorerst GitHub-only; Store erst nach Secret-Härtung, Store-Listing, MSIX/WACK und klarer Datenschutzabgrenzung. |
| Android | Vollständige IDE nicht sinnvoll, weil lokaler Python-/PyInstaller-/Dateisystemzugriff fehlt. | PWA-Companion für Projektübersicht, Analyseberichte und Checklisten. |
| Webapp | Sinnvoll als Companion und Team-/LLM-Übergabeoberfläche. | Bevorzugter Mobile-/Web-Strang mit Import von `devcenter-workspace-v1.json`. |
| iOS | Native IDE wegen Sandbox, Signierung und Dateisystemzugriff nicht sinnvoll. | PWA/TestFlight-Hülle nur nach funktionierendem Web-Companion. |
| Mac App | Fachlich sinnvoll für Python-Entwicklung, aber AI-Key, PyInstaller, Pfade und Keyring müssen plattformspezifisch getestet werden. | P2 Source-Smoke auf macOS, Paketierung erst danach. |
| Linux Version | Sinnvoll für Entwickler, besonders als Source-Start. AppImage/Flatpak erst nach stabilen Smokes. | P1 Linux-Source-Smoke, P3 Paketierungsentscheidung. |

## Zielarchitektur

### Desktop bleibt autoritativ

Die PySide6-App bleibt die Vollversion. Sie verwaltet lokale Projekte, `devcenter.json`, Einstellungen, Dateiindex, Builds und optionale AI-Nutzung. Keine Mobile- oder Webversion darf API-Schlüssel, lokale Pfade oder Projektinhalte unkontrolliert übernehmen.

### Austauschformat

Der geplante Export heißt `devcenter-workspace-v1.json`. Er enthält nur redigierte, mobile-taugliche Daten:

- Projektmetadaten aus `devcenter.json`
- redigierte Plattform- und Pfadhinweise
- Analysezusammenfassungen ohne vollständige Quelltexte
- Build-Konfiguration ohne absolute Secrets oder lokale Build-Artefakte
- Lizenz-/Dependency-Zusammenfassung
- Aufgaben- und Store-/Release-Checklisten
- optional: kleine, explizit freigegebene Code-Snippets

Details stehen in `EXPORTFORMAT.md`.

### Web/PWA-Companion

Der Companion liegt perspektivisch unter `web_companion/`. Er soll offline-fähig sein, JSON-Dateien lokal im Browser importieren und keine Serverpflicht haben. Eine gehostete Version darf keine Projektdateien hochladen, solange keine explizite Datenschutz- und Sicherheitsentscheidung vorliegt.

## Phasenplan

| Phase | Ziel | Ergebnis |
|---|---|---|
| P0 | Exportvertrag festlegen | `EXPORTFORMAT.md`, TODOs, redigierte Feldliste |
| P1 | Linux-Source-Smoke | Start, Tests, Pfad-/Keyring-/PyInstaller-Abgrenzung dokumentiert |
| P2 | `devcenter-workspace-v1.json` im Desktop erzeugen | Exportfunktion mit Tests, keine Secrets, keine lokalen Vollpfade ohne Redaction |
| P3 | Web/PWA-Companion bauen | Import, Dashboard, Analyse-/Build-/Release-Ansichten, Mobile-Smokes |
| P4 | macOS-Smoke | Start auf Mac Studio oder macOS-Runner, Keyring/Terminal/Build prüfen |
| P5 | Store-Entscheidung | Windows Store nur nach MSIX/WACK, Datenschutztext, Support-URL, Screenshot-Set und API-Key-Härtung |

## Nicht-Ziele

- Kein nativer Android-/iOS-IDE-Clone.
- Kein öffentlicher Webservice, der komplette Projektquellen hochlädt.
- Keine gemeinsame Desktop-/Mobile-Codebasis erzwingen, wenn sie die lokale IDE-Funktionalität verlangsamt.
- Keine Windows-Store-Einreichung, solange AI-Key, Build-Prozesse und Dateisystemrechte nicht sauber abgegrenzt sind.

## Offene Risiken

- Der AI-Assistent darf keine Schlüssel in Exporte schreiben.
- Build- und Sync-Einstellungen enthalten lokale Pfade und müssen redigiert werden.
- PyInstaller- und Terminalfunktionen sind auf macOS/Linux nicht automatisch gleichwertig.
- Ein Web-Companion kann nur Reports und Metadaten anzeigen, nicht die vollständige lokale Entwicklungsumgebung ersetzen.

## Nächste konkrete Schritte

1. Redigierten Export `devcenter-workspace-v1.json` als reine Hilfsfunktion planen und testen.
2. Linux-Source-Smoke mit `python -m unittest discover -s tests -v` und `python -m compileall -q main.py manage_translations.py translator.py src tests` dokumentieren.
3. Web-Companion minimal als statischen Import-Viewer für Projektstatus, Analysebefunde und Release-Checklisten anlegen.
4. Windows-Store-Entscheidung erst nach Secret-/Privacy-Review und Store-Artefaktprüfung wieder aufnehmen.
