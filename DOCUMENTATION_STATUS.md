# Documentation status and source hierarchy

Status: current repository contract, 2026-09-20

This file separates the current DevCenter source contract from retained plans,
host copies and the OneDrive deployment projection. Documentation must not turn
an unchecked plan item or an old release note into a feature or release claim.

## Current sources of truth

| Concern | Current source | Boundary |
|---|---|---|
| Package name, version, Python floor and dependencies | `pyproject.toml`, `src/__init__.py`, `src/core/cli.py`, `src/core/workspace_export.py` | `devcenter-suite`, version `1.0.3` in the checked runtime version sources, `requires-python >=3.11`; optional dev tools are `pytest` and `ruff`. |
| Runtime architecture and modules | `src/`, `ARCHITEKTUR_DevCenter.md` | The PySide6 desktop application is the only shipped runtime. |
| User-facing installation and features | `README.md` | Windows-first desktop; Linux/macOS are source-smoke targets. |
| Agent/project orientation | `llms.txt` | Describes the local desktop and redacted export; no Web/PWA companion. |
| Tests and CI | `tests/`, `.github/workflows/tests.yml` | The local 2026-09-20 readback is 208 passed; CI runs the test matrix on Python 3.11/3.12 and platform-smoke jobs on Python 3.11 for Linux/macOS. |
| Redacted workspace export | `src/core/workspace_export.py`, `EXPORTFORMAT.md` | Schema `devcenter-workspace-v1`; local artifact only, with paths/secrets/source content redacted. |
| Project license | `LICENSE`, `README.md`, `THIRD_PARTY_LICENSES.txt` when present in the checkout | GPL-3.0 for DevCenter; dependency licenses are separate notices. |
| Change history | `CHANGELOG.md` | Historical entries remain history; they do not assert that removed components still ship. |

## Historical or external documents

`SUITE_DEVCENTER_TEMPLATE.md` (stand 2026-01-09) and
`SUITE_ENTWICKLER_Fusionskonzept.md` are retained planning/fusion documents.
Their old estimates, MIT wording, Python versions, dependency examples and
unchecked feature lists are not current contracts. They are explicitly marked
as historical at their document headers.

For path checks, the active documentation set is explicit: `README.md`,
`README_de.md`, `DOCUMENTATION_STATUS.md`, `ARCHITEKTUR_DevCenter.md`,
`EXPORTFORMAT.md` and `llms.txt`. Historical planning documents are not silently
treated as current source roots. The active check is:

```powershell
python "<OneDrive>/_scripts/doc_path_check.py" README.md README_de.md DOCUMENTATION_STATUS.md ARCHITEKTUR_DevCenter.md EXPORTFORMAT.md llms.txt --search-root exact --quiet
```

Historical files remain readable and may be checked separately after their
historical path context is understood; their retained claims do not become
current product, platform, release or license commitments.

`README-Mac Studio.md`, `AUFGABEN.txt`, `PORTIERUNGSPLAN.md`,
`THIRD_PARTY_LICENSES.txt`, `WINDOWS_STORE_PREP.md`, and `*-WORKSTATION-LG.*`
may exist in the OneDrive projection or a host-specific copy without being part
of the canonical `master` checkout. They require an owner decision before
being imported into the public repository. In particular, a store note that
says `MIT` cannot override the GPL-3.0 `LICENSE`.

## Product and platform boundary

The Web/PWA companion was removed by commit `67de564` after the 2026-07-23
use-case review. The local redacted export remains implemented and documented,
but no `web_companion/` directory or hosted importer is shipped. The `web`
value that remains in schema-v1 payloads is a legacy compatibility field, not a
current release channel.

The README's Python floor follows `pyproject.toml` (`>=3.11`). The active CI
matrix is Python 3.11/3.12, with Linux and macOS platform-smoke jobs on Python
3.11. A local test count does not establish release readiness, tagging, upload
or platform certification.

## Fresh verification

The 2026-09-20 local readback against the current checkout recorded 208 passed
tests, a successful compileall run and a clean Ruff result. The readback covers
the active source and documentation contract only; historical changelog counts,
planning estimates and external deployment copies remain historical or
owner-controlled evidence.

## Maintenance rule

When a source, feature, release channel or license changes, update the current
source above first, then add a dated `CHANGELOG.md` entry. Do not rewrite or
delete the historical planning files merely to make their old claims disappear.
