# Windows Store — Vorbereitung DevCenter Suite

Stand: 2026-07-25

---

## Identität & Partner-Center-Metadaten

| Feld              | Wert                                         |
|-------------------|----------------------------------------------|
| App Name          | DevCenter Suite                              |
| Identity Name     | Geiger.DevCenterSuite                        |
| Publisher         | CN=52596601-BAB4-4F3F-B182-E8F3F273B202      |
| Publisher Display | Geiger                                       |
| Version           | 1.0.0.0                                      |
| Executable        | DevCenter.exe                                |
| Capabilities      | runFullTrust                                 |
| Category          | Developer Tools                              |
| Age Rating        | 3+                                           |
| License           | MIT                                          |
| Pricing           | Free                                         |

Publisher-Identität ist identisch mit anderen Anwendungen der Toolchain (gleiches Microsoft Partner Center Konto). Die Angaben müssen verbatim in `store_package.json` hinterlegt sein.

---

## Checkliste: Vor Store-Einreichung

### Pflichtartefakte

- [x] `store_package.json` erstellt (2026-07-25)
- [x] `STORE_LISTING.md` erstellt — DE + EN Beschreibung (2026-07-25)
- [x] `PRIVACY_POLICY.md` geprüft (DE + EN, Offline-Garantie, Keyring-Sicherheit)
- [x] `SUPPORT.md` erstellt (2026-07-25)
- [x] `THIRD_PARTY_LICENSES.txt` als direkte Runtime-Inventur aus `pyproject.toml`
- [x] `tests/test_store_materials.py` (Store-Test-Suite — 7 Tests grün)

### Packaging & WACK

- [ ] `build_exe.bat` ausführen → `C:\_Local_DEV\codex_build\DevCenter\dist\DevCenter.exe`
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
- 4 GB RAM empfohlen
- ca. 200 MB Speicherplatz

---

## Verwandte Dateien

- `store_package.json` — maschinenlesbare Paket-Metadaten
- `STORE_LISTING.md` — Store-Beschreibung DE/EN
- `PRIVACY_POLICY.md` — Datenschutzerklärung
- `SUPPORT.md` — Support-Hinweise & FAQ
- `THIRD_PARTY_LICENSES.txt` — direkte Runtime-Lizenzinventur
- `build_exe.bat` — Build-Skript Windows
