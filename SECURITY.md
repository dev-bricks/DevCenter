# Security Policy / Sicherheitsrichtlinie

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## English Security Policy

### Core Security & Privacy Principles

DevCenter is designed as a **local-first desktop development suite** for Windows. It operates under strict security and data-isolation principles:

1. **100% Offline & Zero-Egress Operation by Default:**
   - All source code editing, syntax highlighting, AST static analysis, complexity calculations, encoding repair, file indexing, and PyInstaller executable compilation run completely locally on your system.
   - DevCenter contains no telemetry, analytics, background tracking, or automatic remote synchronization.

2. **System Keyring & Secret Isolation:**
   - If you opt into using the optional Claude/Anthropic AI Assistant, your API key is **never** written to unencrypted configuration files (`settings.json`), debug logs, or project files.
   - API keys are stored exclusively in the native operating system credential store (Windows Credential Manager via Python `keyring`).
   - If Keyring access fails or is unavailable, API keys are kept in volatile process memory only and are never flushed to disk in plaintext.

3. **Redacted Workspace Export Contract:**
   - Workspace exports (`devcenter-workspace-v1.json`) automatically redact sensitive credentials, API keys, and local absolute path projections to protect confidentiality during external reviews.

4. **Safe Build Execution & Subprocess Isolation:**
   - The PyInstaller packaging pipeline operates exclusively on local project scripts specified by the user.
   - Subprocesses are spawned without elevated (Administrator) privileges and with strict working directory boundaries.

### Reporting a Vulnerability

If you discover a security vulnerability in DevCenter, please report it privately:

1. **GitHub Security Advisory (Preferred):** Go to the **Security** tab of [dev-bricks/DevCenter](https://github.com/dev-bricks/DevCenter) and select **Report a vulnerability**.
2. **Direct Security Contact:** Send an encrypted email to `security@ellmos.ai` (CC: `support@lukasgeiger.com`).

**Please do not report security vulnerabilities in public issues or discussions.** We will acknowledge receipt within 48 hours and coordinate a coordinated fix.

---

## Deutsche Sicherheitsrichtlinie (German)

### Sicherheits- und Datenschutzgrundsätze

DevCenter wurde als **lokale Desktop-Entwicklungsumgebung** für Windows entwickelt und folgt strikten Sicherheits- und Isolationsgarantien:

1. **100% Offline-Betrieb & Zero-Egress-Garantie:**
   - Code-Bearbeitung, statische AST-Analyse, Encoding-Korrektur, SQLite-Dateisuche und PyInstaller-Kompilierung laufen vollständig lokal ohne externe Serverkommunikation.
   - Es existieren keinerlei Telemetrie, Analyse-Tracker oder automatische Cloud-Uploads.

2. **Sichere Schlüsselverwaltung via System-Keyring:**
   - Bei optionaler Nutzung des Claude/Anthropic AI-Assistenten wird der API-Schlüssel niemals im Klartext in Konfigurationsdateien (`settings.json`) gespeichert.
   - Die Ablage erfolgt verschlüsselt im Windows Credential Manager (System-Keyring).

3. **Redigierter Workspace-Export:**
   - Exportierte Workspace-Zustände (`devcenter-workspace-v1.json`) bereinigen sensible absolute Pfade und entfernen Authentifizierungsgeheimnisse automatisch.

4. **Keine Administratorrechte erforderlich (Non-Elevation):**
   - DevCenter und PyInstaller laufen vollständig im Standard-Benutzerkontext ohne erhöhte Rechte.

### Meldung von Sicherheitslücken

Bitte melden Sie Sicherheitslücken vertraulich über die GitHub-Schwachstellenmeldung oder per E-Mail an `security@ellmos.ai` (CC: `support@lukasgeiger.com`).
