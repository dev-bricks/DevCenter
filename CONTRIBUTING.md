# Beitragsrichtlinie / Contributing Guide

## Deutsch

Vielen Dank für Ihr Interesse, zu diesem Projekt beizutragen!

### Wie Sie beitragen können

1. **Bug melden:** Erstellen Sie ein Issue mit dem Label `bug`
2. **Feature vorschlagen:** Erstellen Sie ein Issue mit dem Label `enhancement`
3. **Code beitragen:** Erstellen Sie einen Pull Request

### Pull Requests

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch: `git checkout -b feature/mein-feature`
3. Committen Sie Ihre Änderungen: `git commit -m "Beschreibung der Änderung"`
4. Pushen Sie den Branch: `git push origin feature/mein-feature`
5. Erstellen Sie einen Pull Request

### Developer Certificate of Origin (DCO)

Dieses Projekt verwendet den [Developer Certificate of Origin (DCO)](https://developercertificate.org/).
Bitte signieren Sie jeden Commit mit `--signoff`:

    git commit --signoff -m "Beschreibung der Änderung"

Damit bestätigen Sie, dass Sie das Recht haben, den Code unter der Projektlizenz einzureichen.

### Code-Richtlinien & Quality Gates

- Python: PEP 8 Stil mit `ruff check .`
- Tests: Vollständige Suite muss grün sein (`python -m pytest -ra -v`)
- Bytecode: Kompilierung muss fehlerfrei sein (`python -m compileall -q .`)
- Encoding: UTF-8 für alle Dateien ohne BOM
- Sprache: Code und Kommentare auf Deutsch oder Englisch
- Sicherheit & Egress: Keine hardcodierten Pfade, API-Keys oder Egress-Lecks; striktes `RunAsInvoker` (keine Admin-/UAC-Rechte)
- Invarianten: Einhaltung der 10 Governance-Invarianten `INV-LOCAL-01` bis `INV-SLA-10`

### Governance- & Laufzeit-Invarianten (INV-LOCAL-01 bis INV-SLA-10)

| Invariante | Name | Spezifikation |
|---|---|---|
| `INV-LOCAL-01` | Zero-Egress Default | 100% Offline-Betrieb standardmäßig; keine Hintergrund-Telemetrie oder Pingbacks. |
| `INV-OPTIN-02` | Opt-In AI Boundary | Anthropic/Claude-API-Anfragen werden ausschließlich auf explizite Nutzerinteraktion versendet. |
| `INV-KEYRING-03` | Keyring Secret Vault | Optionale API-Schlüssel werden verschlüsselt im Betriebssystem-Schlüsselspeicher (Keyring) gehalten; kein Klartext auf Datenträgern. |
| `INV-EXPORT-04` | Redacted Workspace Export | Bereinigter Workspace-Export (`devcenter-workspace-v1.json`) entfernt Passwörter, Secrets und private Pfade. |
| `INV-STATIC-05` | Inert AST Inspection | Statische Codeanalyse parst AST-Knoten ohne Ausführung des analysierten Nutzer-Codes. |
| `INV-SECURITY-06` | Vulnerability Floors | Durchsetzung geprüfter Sicherheitsmindestversionen (`Pillow>=12.3.0`, `keyring>=25.0.0`, `pytest>=9.1.1`). |
| `INV-PERM-07` | 100% Permissive / Separation | GPLv3-Suite mit dynamischer PySide6 LGPL-Verlinkung und PyInstaller Bootloader Special Exception. |
| `INV-USER-08` | Unprivileged RunAsInvoker | Strikt unprivilegierte Ausführung im regulären Benutzerkontext ohne Administrator-/UAC-Rechte. |
| `INV-MULTI-09` | Multi-Host Sync Discipline | Plan D Git-Hygiene; `.gitignore` blockiert Sync-Konfliktdateien, Host-Nebenstände und Locks. |
| `INV-SLA-10` | 48h / 5d Security SLA | Verbindliche Sicherheitsreaktionszeiten mit 48h Erstprüfung und 5 Tagen Triage. |

### Plan D Source of Truth & Entwicklungs-Workflow

- **Kanonischer Arbeitsort (Source of Truth):** `C:\_Local_DEV\repos\DevCenter` (lokaler Klon) und GitHub `origin`.
- **OneDrive-Rolle:** Nur gitloser Projektions- und Lesespiegel (`C:\Users\lukas\OneDrive\.TOPICS\.SOFTWARE\DEV\REL-PUB_DevCenter_SUITE`). Entwicklung und Commits erfolgen niemals direkt auf Cloud-gemounteten Datenträgern, um Locking-Konflikte zu vermeiden.

### Haftungsausschluss (§ 521 BGB Gefälligkeitsrecht)

Da dieses Softwareprojekt unentgeltlich als Open-Source-Software bereitgestellt wird, haftet der Anbieter gemäß § 521 BGB nur für Vorsatz und grobe Fahrlässigkeit. Es wird keine Gewähr für Mängelfreiheit oder ununterbrochenen Betrieb übernommen.

### Sicherheits-SLA & Kontakt

Verbindliche Sicherheits-SLA: 48 Stunden Reaktionszeit auf Meldungen, 5 Tage Triage-Frist. Sicherheitsrelevante Schwachstellen bitte vertraulich melden an:
- `security@dev-bricks.org`
- `security@open-bricks.org`
- `support@lukasgeiger.com`
- `lukas@open-bricks.org`

### Version-Freeze-Disziplin (T-20260920-167562623)

- Die Version `1.0.3` ist in allen Manifesten (`pyproject.toml`, Quelltexten) eingefroren.
- Releasewechsel und Versionserhöhungen sind separaten Veröffentlichungszyklen vorbehalten.
- Alle neuen Features, Fehlerbehebungen und Hygiene-Korrekturen werden unter `## [Unreleased]` in `CHANGELOG.md` dokumentiert.

### Erste Schritte

```bash
git clone https://github.com/dev-bricks/DevCenter.git
cd DevCenter
pip install -r requirements.txt
python -m pytest -ra -v
python main.py
```

---

## English

Thank you for your interest in contributing to this project!

### How to Contribute

1. **Report bugs:** Create an issue with the `bug` label
2. **Suggest features:** Create an issue with the `enhancement` label
3. **Contribute code:** Create a Pull Request

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Description of change"`
4. Push the branch: `git push origin feature/my-feature`
5. Create a Pull Request

### Developer Certificate of Origin (DCO)

This project uses the [Developer Certificate of Origin (DCO)](https://developercertificate.org/).
Please sign off every commit with `--signoff`:

    git commit --signoff -m "Description of change"

This certifies that you have the right to submit the code under the project license.

### Code Guidelines & Quality Gates

- Python: PEP 8 style enforced with `ruff check .`
- Tests: Test suite must pass 100% (`python -m pytest -ra -v`)
- Bytecode: Clean compilation without errors (`python -m compileall -q .`)
- Encoding: UTF-8 without BOM for all files
- Language: Code and comments in German or English
- Security & Egress: No hardcoded paths, API keys, or network leaks; strict `RunAsInvoker` (no admin/UAC elevation)
- Invariants: Strict compliance with all 10 governance invariants `INV-LOCAL-01` through `INV-SLA-10`

### Governance & Runtime Invariants (INV-LOCAL-01 through INV-SLA-10)

| Invariant | Name | Specification |
|---|---|---|
| `INV-LOCAL-01` | Zero-Egress Default | 100% offline operation by default; zero telemetry or pingbacks. |
| `INV-OPTIN-02` | Opt-In AI Boundary | Anthropic/Claude API requests dispatched strictly upon explicit user interaction. |
| `INV-KEYRING-03` | Keyring Secret Vault | Optional API keys encrypted in native OS credential manager; zero plaintext on disk. |
| `INV-EXPORT-04` | Redacted Workspace Export | Sanitized workspace export (`devcenter-workspace-v1.json`) strips secrets and private paths. |
| `INV-STATIC-05` | Inert AST Inspection | Static analysis parses AST tokens inertly without executing target user code. |
| `INV-SECURITY-06` | Vulnerability Floors | Enforced security floors (`Pillow>=12.3.0`, `keyring>=25.0.0`, `pytest>=9.1.1`). |
| `INV-PERM-07` | 100% Permissive / Separation | GPLv3 suite with dynamic PySide6 LGPL linking and PyInstaller Bootloader Special Exception. |
| `INV-USER-08` | Unprivileged RunAsInvoker | Strictly unprivileged execution in user space without administrator/UAC elevation. |
| `INV-MULTI-09` | Multi-Host Sync Discipline | Plan D Git hygiene; `.gitignore` blocks cloud-sync conflicts, host-specific tokens and locks. |
| `INV-SLA-10` | 48h / 5d Security SLA | Binding security commitments: 48h initial response, 5-day triage commitment. |

### Plan D Source of Truth & Development Workflow

- **Canonical Working Directory (Source of Truth):** `C:\_Local_DEV\repos\DevCenter` and GitHub `origin`.
- **OneDrive Role:** Derived read surface and gitless projection only (`C:\Users\lukas\OneDrive\.TOPICS\.SOFTWARE\DEV\REL-PUB_DevCenter_SUITE`). Development never occurs directly inside cloud-mounted folders to avoid lock collisions.

### Statutory Disclaimer (§ 521 BGB German Civil Code)

As this open-source software project is provided free of charge, liability under German law (§ 521 BGB Gefälligkeitsrecht) is strictly limited to intent and gross negligence. No warranty for defect-free operation is assumed.

### Security Response SLA & Contacts

Binding Security SLA: 48-hour initial response to vulnerability reports, 5-day triage deadline. Report security concerns confidentially to:
- `security@dev-bricks.org`
- `security@open-bricks.org`
- `support@lukasgeiger.com`
- `lukas@open-bricks.org`

### Version Freeze Discipline (T-20260920-167562623)

- Version `1.0.3` is frozen across manifests (`pyproject.toml`, source code).
- Production releases and version bumps are managed in separate authorized release cycles.
- All new features, bug fixes, and repository hygiene changes are documented under `## [Unreleased]` in `CHANGELOG.md`.

### Getting Started

```bash
git clone https://github.com/dev-bricks/DevCenter.git
cd DevCenter
pip install -r requirements.txt
python -m pytest -ra -v
python main.py
```
