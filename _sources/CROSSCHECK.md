# CROSSCHECK — Externe Dependencies

> Vorlage: `_TEMPLATES/CROSSCHECK_TEMPLATE.md` | Konvention: GUIDE.md §Toolchain-Standards
> Pfad: `_sources/CROSSCHECK.md` im jeweiligen Projektordner
> Stand: 2026-06-07

## Verwendete Pakete mit Major-Version-Pinning

| Paket | Gepinnte Version | Aktuelle Version | Letzte Prüfung |
|---|---|---|---|
| PySide6 | `>=6.5.0,<7.0.0` | 6.10.1 | 2026-06-07 |
| pyinstaller | `>=5.0.0,<7.0.0` | 6.14.2 | 2026-06-07 |
| Pillow | `>=9.0.0,<12.0.0` | 12.2.0 | 2026-06-07 |
| anthropic | `>=0.18.0,<1.0.0` | 0.100.0 | 2026-06-07 |
| keyring | `>=23.0.0,<26.0.0` | 25.7.0 | 2026-06-07 |
| chardet | `>=5.0.0,<6.0.0` | 5.2.0 | 2026-06-07 |
| ftfy | `>=6.1.0,<7.0.0` | 6.3.1 | 2026-06-07 |
| pip-licenses | `>=4.0.0,<5.0.0` | 5.5.0 | 2026-06-07 |
| watchdog | `>=3.0.0,<5.0.0` | 6.0.0 | 2026-06-07 |
| pytest (dev) | `>=8.0` | 9.0.3 | 2026-06-07 |
| ruff (dev) | `>=0.5` | 0.15.15 | 2026-06-07 |

Aktuelle Version prüfen: `python -m uv pip list --outdated` oder `pip list --outdated`

> **Hinweis:** Pillow (12.2.0), pip-licenses (5.5.0) und watchdog (6.0.0) liegen außerhalb
> der in `pyproject.toml` gepinnten Obergrenzen. Pinning in `pyproject.toml` aktualisieren
> oder gezielt auf Kompatibilität prüfen.

---

## P0 — Sicherheit / CVEs (blockiert Release)

| # | Paket | Problem | Status | Behoben in |
|---|---|---|---|---|
| — | — | — | — | — |

Quellen: [PyPI Safety DB](https://pypi.org/), [CVE MITRE](https://cve.mitre.org/), `safety check`

---

## P1 — Breaking Changes bei Major-Update (dokumentieren vor Update)

| # | Paket | Von | Nach | Breaking Change | Aufwand |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

---

## P2 — Deprecation-Warnings

| # | Paket | Warnung | Deadline | Maßnahme |
|---|---|---|---|---|
| — | — | — | — | — |

---

## P3 — Nice-to-have Features / Performance

| # | Paket | Neue Funktion | Nützlich für | Priorität |
|---|---|---|---|---|
| — | — | — | — | niedrig |

---

## Workflow

1. **Vor jedem Release:** Alle P0-Einträge abarbeiten; P1 dokumentiert und im CHANGELOG vermerkt.
2. **Quartalsmäßig:** `uv pip list --outdated` laufen lassen, Tabelle aktualisieren.
3. **Neue Deps:** Direkt beim Hinzufügen einen P2/P3-Eintrag anlegen, falls relevante Breaking-Change-Noten im Changelog.

---

## Hinweise zum Ausfüllen

- **Major-Version-Pinning:** `>=1.0.0,<2.0.0` in requirements.txt oder pyproject.toml
- **PySide6:** Upgrade auf neue Minor-Versionen i.d.R. sicher; Major-Wechsel (Qt 6→7) = P1
- **PyInstaller:** GPL-2.0 mit Runtime-Exception — P1 prüfen wenn Major-Update
