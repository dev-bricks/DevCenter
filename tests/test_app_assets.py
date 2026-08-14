# -*- coding: utf-8 -*-
"""
DevCenter - App Assets & Icon Test Suite
Testet die Existenz, Formate, Auflösungen und das Laden der App-Icons.
"""

import sys
import unittest
from pathlib import Path
from PIL import Image

# Pfad für Imports
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from core.app_paths import get_project_root, get_app_icon_path  # noqa: E402


class TestAppAssetsAndIcons(unittest.TestCase):
    """Tests für App-Icon-Assets und Auflösungen."""

    def test_project_root_and_icon_path_resolution(self):
        """Testet, dass get_project_root und get_app_icon_path gültige Pfade liefern."""
        root = get_project_root()
        self.assertTrue(root.exists(), f"Projekt-Root {root} existiert nicht.")
        
        icon_path = get_app_icon_path()
        self.assertIsNotNone(icon_path)
        self.assertTrue(icon_path.exists(), f"App-Icon {icon_path} existiert nicht.")

    def test_master_png_icon(self):
        """Testet das 512x512 Master-PNG in assets/ und im Root."""
        root = get_project_root()
        for p in [root / "assets" / "icon.png", root / "icon.png"]:
            self.assertTrue(p.exists(), f"{p} existiert nicht.")
            with Image.open(p) as img:
                self.assertEqual(img.format, "PNG")
                self.assertEqual(img.size, (512, 512))
                self.assertIn(img.mode, ["RGBA", "RGB"])

    def test_multi_resolution_ico_files(self):
        """Testet die Windows-ICO-Dateien auf 256x256 Basisauflösung und ICO-Format."""
        root = get_project_root()
        for p in [
            root / "DevCenter.ico",
            root / "assets" / "app_icon.ico",
            root / "assets" / "icon.ico",
        ]:
            self.assertTrue(p.exists(), f"{p} existiert nicht.")
            with Image.open(p) as img:
                self.assertEqual(img.format, "ICO")
                self.assertEqual(img.size, (256, 256))

    def test_favicon_ico(self):
        """Testet das Favicon ICO-Format."""
        root = get_project_root()
        fav = root / "assets" / "favicon.ico"
        self.assertTrue(fav.exists(), "assets/favicon.ico existiert nicht.")
        with Image.open(fav) as img:
            self.assertEqual(img.format, "ICO")

    def test_store_and_tile_icons(self):
        """Testet die Store- und Kachel-Icons in assets/icons/."""
        root = get_project_root()
        icons_dir = root / "assets" / "icons"
        
        expected_tiles = {
            "icon_44x44.png": (44, 44),
            "icon_50x50.png": (50, 50),
            "icon_150x150.png": (150, 150),
            "icon_310x150.png": (310, 150),
            "icon_310x310.png": (310, 310),
        }
        for filename, expected_size in expected_tiles.items():
            p = icons_dir / filename
            self.assertTrue(p.exists(), f"Kachel-Icon {p} existiert nicht.")
            with Image.open(p) as img:
                self.assertEqual(img.format, "PNG")
                self.assertEqual(img.size, expected_size)


if __name__ == "__main__":
    unittest.main()
