# Privacy Policy / Datenschutzerklärung

## Deutsch

DevCenter ist eine lokale Desktop-Anwendung für Python-Entwicklung. Die Anwendung speichert Einstellungen, Projektlisten, optionale Datei-Indizes und Build-Artefakte auf dem lokalen Rechner.

Es werden keine Nutzungsdaten durch DevCenter an einen eigenen Server übertragen. Netzwerkzugriffe entstehen nur, wenn sie ausdrücklich ausgelöst oder konfiguriert werden, zum Beispiel:

- Installation von Python-Abhängigkeiten über `pip`
- optionale Nutzung der Claude/Anthropic-API im AI-Assistenten
- manuell gestartete Git- oder GitHub-Aktionen

API-Schlüssel und lokale Projektdaten dürfen nicht in Git eingecheckt werden. Verwenden Sie Umgebungsvariablen, den lokalen Schlüsselbund oder lokale Konfigurationsdateien, die durch `.gitignore` ausgeschlossen sind.

## English

DevCenter is a local desktop application for Python development. It stores settings, project lists, optional file indexes, and build artifacts on the local machine.

DevCenter does not send usage data to a project-owned server. Network access only happens when explicitly triggered or configured, for example:

- installing Python dependencies via `pip`
- optional use of the Claude/Anthropic API in the AI assistant
- manually started Git or GitHub actions

API keys and local project data must not be committed to Git. Use environment variables, the local keyring, or local configuration files excluded by `.gitignore`.
