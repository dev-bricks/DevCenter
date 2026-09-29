# Windows Store — Vorbereitung DevCenter Suite

Stand: 2026-09-29

---

## Identität & Partner-Center-Metadaten

| Feld              | Wert                                         |
|-------------------|----------------------------------------------|
| App Name          | DevCenter Suite                              |
| Identity Name     | Geiger.DevCenterSuite                        |
| Publisher         | CN=52596601-BAB4-4F3F-B182-E8F3F273B202      |
| Publisher Display | Geiger                                       |
| Version           | 1.0.3.0                                      |
| Executable        | DevCenter.exe                                |
| Capabilities      | runFullTrust                                 |
| Category          | Developer Tools                              |
| Age Rating        | 3+                                           |
| License           | GPL-3.0                                      |
| Pricing           | Free                                         |

Publisher-Identität ist identisch mit anderen Anwendungen der Toolchain (gleiches Microsoft Partner Center Konto). Die Angaben müssen verbatim in `store_package.json` hinterlegt sein.

---

## Checkliste: Vor Store-Einreichung

### Pflichtartefakte

- [x] `store_package.json` erstellt und auf GPL-3.0 harmonisiert (2026-09-29)
- [x] `STORE_LISTING.md` erstellt — DE + EN Beschreibung (2026-07-25 / 2026-09-29)
- [x] `PRIVACY_POLICY.md` geprüft (DE + EN, Offline-Garantie, Keyring-Sicherheit)
- [x] `SUPPORT.md` erstellt (2026-07-25 / 2026-09-29)
- [x] `THIRD_PARTY_LICENSES.txt` als direkte Runtime-Inventur aus `pyproject.toml`
- [x] `tests/test_store_materials.py` (Store-Test-Suite — alle Tests grün)

### Packaging & WACK

- [ ] `build_exe.bat` ausführen → `dist/DevCenter.exe`
- [ ] MSIX-Paket erzeugen (via MakeAppx / MSIX Packaging Tool)
- [ ] WACK-Test (Windows App Certification Kit) ausführen
- [ ] Paket im Microsoft Partner Center hochladen

---

## Technische Hinweise

### Capabilities

`runFullTrust` — erforderlich für Dateisystem-Zugriff, PyInstaller-Steuerung, Git-Ausführung und lokalen SQLite-Index.

### Kategorie

Developer Tools — entspricht dem Funktionsprofil (Python Build, Analyse, Sync, AI-Assistenz).

### Systemanforderungen

- Windows 10 Version 1903 (Build 18362) oder höher
- x64-Prozessor
