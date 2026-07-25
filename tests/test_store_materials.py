"""
Tests für Windows-Store-Artefakte (DevCenter Suite).
Prüft Vollständigkeit und Konsistenz der Store-Metadaten.
"""
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestStoreMaterials(unittest.TestCase):

    def test_store_package_json_exists_and_is_valid(self):
        path = PROJECT_ROOT / "store_package.json"
        self.assertTrue(path.exists(), "store_package.json fehlt")
        data = json.loads(path.read_text(encoding="utf-8"))
        required = [
            "app_name", "publisher", "publisher_display", "identity_name",
            "version", "description", "executable", "capabilities",
            "category", "age_rating", "privacy_url", "support_url", "license",
        ]
        for field in required:
            self.assertIn(field, data, f"Pflichtfeld '{field}' fehlt in store_package.json")

    def test_store_package_publisher_matches_expected(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        expected_cn = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
        self.assertEqual(
            data["publisher"], expected_cn,
            "publisher CN stimmt nicht mit Partner-Center-Konto überein",
        )

    def test_store_package_executable_matches_build(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            data["executable"], "DevCenter.exe",
            "executable in store_package.json stimmt nicht mit build_exe.bat überein",
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

    def test_store_listing_exists_and_contains_de_and_en(self):
        path = PROJECT_ROOT / "STORE_LISTING.md"
        self.assertTrue(path.exists(), "STORE_LISTING.md fehlt")
        content = path.read_text(encoding="utf-8")
        self.assertIn("Deutsch", content, "STORE_LISTING.md enthält keinen deutschen Abschnitt")
        self.assertIn("English", content, "STORE_LISTING.md enthält keinen englischen Abschnitt")

    def test_windows_store_prep_exists_and_nonempty(self):
        path = PROJECT_ROOT / "WINDOWS_STORE_PREP.md"
        self.assertTrue(path.exists(), "WINDOWS_STORE_PREP.md fehlt")
        content = path.read_text(encoding="utf-8")
        self.assertGreater(len(content.strip()), 100, "WINDOWS_STORE_PREP.md ist zu kurz / leer")


if __name__ == "__main__":
    unittest.main()
