# DevCenter Suite — Windows Store WACK-Testprotokoll

Stand: 2026-11-08 (Tier-2 6-Sprachen Store-Readiness nach Policy P-006)

## Artefaktstatus & Metadaten

| Prüffeld | Vorgabe | Status | Nachweis |
|---|---|---|---|
| Application Name | DevCenter Suite | Konform | `store_package.json`, `AppxManifest.xml` |
| Identity Name | Geiger.DevCenterSuite | Konform | `store_package.json`, `AppxManifest.xml` |
| Publisher | CN=52596601-BAB4-4F3F-B182-E8F3F273B202 | Konform | Microsoft Partner Center Konto |
| Publisher Display | Geiger | Konform | `store_package.json`, `AppxManifest.xml` |
| Version | 1.0.3.0 | Eingefroren | `pyproject.toml`, `store_package.json` |
| Capabilities | runFullTrust | Konform | Eingeschränkte Windows Desktop Bridge |
| Lizenz | GPL-3.0 | Konform | `LICENSE`, `store_package.json` |
| Privacy Policy | Vorhanden & erreichbar | Konform | `PRIVACY_POLICY.md` |
| Support URL | Vorhanden & erreichbar | Konform | `SUPPORT.md` |

## Tier-2 Mehrsprachigkeit (Policy P-006)

| Sprache | Code | Kurzbeschreibung (<= 100 Zeichen) | Keywords (genau 7, <= 30 Zeichen) | Staged Listing |
|---|---|---|---|---|
| Deutsch | de-DE | 94 Zeichen | 7 Keywords | `releases/windowsstore/store_listing_de.md` |
| English | en-US | 95 Zeichen | 7 Keywords | `releases/windowsstore/store_listing_en.md` |
| Español | es-ES | 98 Zeichen | 7 Keywords | `releases/windowsstore/store_listing_es.md` |
| 简体中文 | zh-CN | 43 Zeichen | 7 Keywords | `releases/windowsstore/store_listing_zh.md` |
| 日本語 | ja-JP | 50 Zeichen | 7 Keywords | `releases/windowsstore/store_listing_ja.md` |
| Русский | ru-RU | 99 Zeichen | 7 Keywords | `releases/windowsstore/store_listing_ru.md` |

## Store-Kachel- und Logo-Assets

| Asset | Dimension | Dateiname | Status |
|---|---|---|---|
| Small Tile | 44x44 px | `Square44x44Logo.png` | Vorhanden in `store_assets/` |
| Medium Tile | 150x150 px | `Square150x150Logo.png` | Vorhanden in `store_assets/` |
| Wide Tile | 310x150 px | `Wide310x150Logo.png` | Vorhanden in `store_assets/` |
| Large Tile | 310x310 px | `Square310x310Logo.png` | Vorhanden in `store_assets/` |
| Store Logo | 50x50 px | `StoreLogo.png` | Vorhanden in `store_assets/` |

## WACK-Prüfpunkte (Windows App Certification Kit)

1. **Paketvalidierung:** Manifest-Wohlgeformtheit, XML-Validität, Schemakonformität `uap` und `rescap`.
2. **Sicherheitsmerkmale:** Keine unzulässigen Binärdateien, keine gefährlichen Berechtigungen über `runFullTrust` hinaus.
3. **Plattform-Kompatibilität:** Getestet auf Windows 10 (17763+) und Windows 11 (26100+).
4. **Offline-Funktionalität:** Alle Kernfunktionen (Build, Analyse, Index, Toolchain) starten displaylos und ohne erzwungenen Netzzugriff.
