"""
Tests für Windows-Store-Artefakte (DevCenter Suite).
Prüft Vollständigkeit, Lizenzparität (GPL-3.0), Tier-2 6-Sprachen-Harmonisierung (Policy P-006),
Partner-Center-Richtlinie 10.1.3 Keyword-Compliance und Staging-Konsistenz.
"""

from __future__ import annotations

import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TIER2_LANGUAGES = ("de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU")


class TestStoreMaterials(unittest.TestCase):

    def test_store_package_json_exists_and_is_valid(self):
        path = PROJECT_ROOT / "store_package.json"
        self.assertTrue(path.exists(), "store_package.json fehlt")
        data = json.loads(path.read_text(encoding="utf-8"))
        required = [
            "app_name",
            "publisher",
            "publisher_display",
            "identity_name",
            "version",
            "description",
            "executable",
            "capabilities",
            "category",
            "age_rating",
            "privacy_url",
            "support_url",
            "license",
            "languages",
        ]
        for field in required:
            self.assertIn(field, data, f"Pflichtfeld '{field}' fehlt in store_package.json")

    def test_store_package_publisher_matches_expected(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        expected_cn = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
        self.assertEqual(
            data["publisher"],
            expected_cn,
            "publisher CN stimmt nicht mit Partner-Center-Konto überein",
        )

    def test_store_package_executable_matches_build(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            data["executable"],
            "DevCenter.exe",
            "executable in store_package.json stimmt nicht mit build_exe.bat überein",
        )

    def test_store_package_license_matches_gpl3(self):
        """SEC-AUDIT-2026-08-14-01: Store-Lizenz muss mit GPL-3.0 übereinstimmen."""
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            data.get("license"),
            "GPL-3.0",
            "license in store_package.json muss GPL-3.0 sein (SEC-AUDIT-2026-08-14-01)",
        )

    def test_store_package_tier2_languages(self):
        """Policy P-006: Alle 6 Tier-2 Sprachen müssen im languages-Array stehen."""
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        declared = data.get("languages", [])
        for lang in TIER2_LANGUAGES:
            self.assertIn(lang, declared, f"Tier-2 Sprache '{lang}' fehlt in store_package.json languages")

    def test_store_package_short_descriptions_length(self):
        """Partner Center: Kurzbeschreibung darf max. 100 Zeichen haben."""
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for lang_code in ("de", "en", "es", "zh", "ja", "ru"):
            desc_key = f"description_{lang_code}"
            self.assertIn(desc_key, data, f"Kurzbeschreibung '{desc_key}' fehlt in store_package.json")
            val = data[desc_key]
            self.assertGreater(len(val.strip()), 0, f"'{desc_key}' darf nicht leer sein")
            self.assertLessEqual(
                len(val),
                100,
                f"'{desc_key}' hat {len(val)} Zeichen (max. 100 Zeichen erlaubt)",
            )

    def test_store_package_keywords_policy_10_1_3(self):
        """Partner Center Richtlinie 10.1.3: Genau/maximal 7 Keywords, jeweils <= 30 Zeichen."""
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for lang_code in ("de", "en", "es", "zh", "ja", "ru"):
            kw_key = f"keywords_{lang_code}"
            self.assertIn(kw_key, data, f"Keywords-Liste '{kw_key}' fehlt in store_package.json")
            kw_list = data[kw_key]
            self.assertIsInstance(kw_list, list, f"'{kw_key}' muss eine Liste sein")
            self.assertLessEqual(
                len(kw_list),
                7,
                f"'{kw_key}' hat {len(kw_list)} Keywords (max. 7 erlaubt)",
            )
            self.assertGreaterEqual(
                len(kw_list),
                3,
                f"'{kw_key}' sollte mindestens 3 Keywords haben",
            )
            for kw in kw_list:
                self.assertLessEqual(
                    len(kw),
                    30,
                    f"Keyword '{kw}' in '{kw_key}' überschreitet 30 Zeichen ({len(kw)})",
                )

    def test_privacy_policy_exists_and_nonempty(self):
        path = PROJECT_ROOT / "PRIVACY_POLICY.md"
        self.assertTrue(path.exists(), "PRIVACY_POLICY.md fehlt")
        content = path.read_text(encoding="utf-8")
        self.assertGreater(len(content.strip()), 100, "PRIVACY_POLICY.md ist zu kurz / leer")

    def test_support_md_exists_and_nonempty(self):
        path = PROJECT_ROOT / "SUPPORT.md"
        self.assertTrue(path.exists(), "SUPPORT.md fehlt")
        content = path.read_text(encoding="utf-8")
        self.assertGreater(len(content.strip()), 100, "SUPPORT.md ist zu kurz / leer")
        self.assertIn("dev-bricks", content, "SUPPORT.md muss auf dev-bricks verlinken")

    def test_store_listing_exists_and_contains_de_and_en(self):
        path = PROJECT_ROOT / "STORE_LISTING.md"
        self.assertTrue(path.exists(), "STORE_LISTING.md fehlt")
        content = path.read_text(encoding="utf-8")
        self.assertIn("Deutsch", content, "STORE_LISTING.md enthält keinen deutschen Abschnitt")
        self.assertIn("English", content, "STORE_LISTING.md enthält keinen englischen Abschnitt")

    def test_store_listing_contains_all_six_languages(self):
        """Tier-2 P-006: STORE_LISTING.md muss alle 6 Sprachen abbilden."""
        path = PROJECT_ROOT / "STORE_LISTING.md"
        self.assertTrue(path.exists(), "STORE_LISTING.md fehlt")
        content = path.read_text(encoding="utf-8")
        for lang_header in ("Deutsch", "English", "Español", "简体中文", "日本語", "Русский"):
            self.assertIn(
                f"## {lang_header}",
                content,
                f"STORE_LISTING.md fehlt Abschnitt für '## {lang_header}'",
            )

    def test_windows_store_prep_exists_and_nonempty(self):
        path = PROJECT_ROOT / "WINDOWS_STORE_PREP.md"
        self.assertTrue(path.exists(), "WINDOWS_STORE_PREP.md fehlt")
        content = path.read_text(encoding="utf-8")
        self.assertGreater(len(content.strip()), 100, "WINDOWS_STORE_PREP.md ist zu kurz / leer")
        self.assertIn("GPL-3.0", content, "WINDOWS_STORE_PREP.md muss GPL-3.0 spezifizieren")

    def test_staging_directory_and_files_exist(self):
        """Prüft, dass releases/windowsstore vollständig mit allen 6 Sprach-Listings gestaged ist."""
        staging_dir = PROJECT_ROOT / "releases" / "windowsstore"
        self.assertTrue(staging_dir.exists(), "releases/windowsstore fehlt")
        required_files = [
            "BUILD.md",
            "WACK_PROTOCOL.md",
            "store_settings.json",
            "store_listing_de.md",
            "store_listing_en.md",
            "store_listing_es.md",
            "store_listing_zh.md",
            "store_listing_ja.md",
            "store_listing_ru.md",
        ]
        for f in required_files:
            file_p = staging_dir / f
            self.assertTrue(file_p.exists(), f"Staged-Datei '{f}' fehlt in releases/windowsstore")
            self.assertGreater(
                file_p.stat().st_size,
                50,
                f"Staged-Datei '{f}' ist verdächtig klein",
            )

    def test_store_settings_json_matches_store_package(self):
        """Stellt Konsistenz zwischen store_package.json und releases/windowsstore/store_settings.json sicher."""
        pkg_path = PROJECT_ROOT / "store_package.json"
        cfg_path = PROJECT_ROOT / "releases" / "windowsstore" / "store_settings.json"
        self.assertTrue(pkg_path.exists())
        self.assertTrue(cfg_path.exists())

        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

        for key in ("app_name", "publisher", "identity_name", "version", "capabilities"):
            self.assertEqual(
                pkg.get(key),
                cfg.get(key),
                f"Mismatch zwischen store_package.json und store_settings.json für Schlüssel '{key}'",
            )
        self.assertEqual(pkg.get("languages"), cfg.get("languages"))

    def test_appx_manifest_xml_resources_and_identity(self):
        """Prüft das gestagte AppxManifest.xml auf Wohlgeformtheit, Identität und alle 6 Sprachressourcen."""
        manifest_path = PROJECT_ROOT / "store_package" / "DevCenter" / "AppxManifest.xml"
        self.assertTrue(manifest_path.exists(), "AppxManifest.xml fehlt")

        tree = ET.parse(manifest_path)
        root = tree.getroot()

        ns = {"m": "http://schemas.microsoft.com/appx/manifest/foundation/windows10"}
        identity = root.find("m:Identity", ns)
        if identity is None:
            identity = root.find("{http://schemas.microsoft.com/appx/manifest/foundation/windows10}Identity")
        self.assertIsNotNone(identity, "Identity-Element in AppxManifest.xml fehlt")
        self.assertEqual(identity.attrib.get("Name"), "Geiger.DevCenterSuite")
        self.assertEqual(identity.attrib.get("Version"), "1.0.3.0")

        resources = root.find("m:Resources", ns)
        if resources is None:
            resources = root.find("{http://schemas.microsoft.com/appx/manifest/foundation/windows10}Resources")
        self.assertIsNotNone(resources, "Resources-Element in AppxManifest.xml fehlt")

        manifest_langs = []
        for child in resources:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == "Resource":
                lang = child.attrib.get("Language")
                if lang:
                    manifest_langs.append(lang.lower())

        for expected in ("de-de", "en-us", "es-es", "zh-cn", "ja-jp", "ru-ru"):
            self.assertIn(
                expected,
                manifest_langs,
                f"AppxManifest.xml Resources deklariert die Sprache '{expected}' nicht",
            )

    def test_store_readiness_linter_passes(self):
        """Führt den Preflight-Linter scripts/check_store_readiness.py aus und sichert 0 Findings zu."""
        import sys
        scripts_dir = PROJECT_ROOT / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from check_store_readiness import run_store_readiness_check

        success, findings = run_store_readiness_check(PROJECT_ROOT)
        self.assertTrue(success, f"check_store_readiness meldet {len(findings)} Findings: {findings}")
        self.assertEqual(len(findings), 0)


if __name__ == "__main__":
    unittest.main()
