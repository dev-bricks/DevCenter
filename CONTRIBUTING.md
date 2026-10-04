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
