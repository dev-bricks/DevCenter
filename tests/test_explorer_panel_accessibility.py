# -*- coding: utf-8 -*-
"""Regressionstests für die Explorer-Barrierefreiheit."""

import importlib.util
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

EXPLORER_PANEL_PATH = Path(__file__).parent.parent / "src" / "gui" / "panels" / "explorer_panel.py"
EXPLORER_PANEL_SPEC = importlib.util.spec_from_file_location(
    "devcenter_explorer_panel",
    EXPLORER_PANEL_PATH,
)
EXPLORER_PANEL_MODULE = importlib.util.module_from_spec(EXPLORER_PANEL_SPEC)
assert EXPLORER_PANEL_SPEC.loader is not None
EXPLORER_PANEL_SPEC.loader.exec_module(EXPLORER_PANEL_MODULE)
ExplorerPanel = EXPLORER_PANEL_MODULE.ExplorerPanel


class ExplorerPanelAccessibilityTests(unittest.TestCase):
    """Sichert sprechende Namen für die kompakte Explorer-Toolbar."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_compact_explorer_controls_expose_accessible_context(self):
        panel = ExplorerPanel()

        self.assertEqual(panel.refresh_btn.toolTip(), "Aktualisieren")
        self.assertEqual(panel.refresh_btn.accessibleName(), "Explorer aktualisieren")
        self.assertIn("Projektstruktur", panel.refresh_btn.accessibleDescription())

        self.assertEqual(panel.collapse_btn.toolTip(), "Alle zuklappen")
        self.assertEqual(panel.collapse_btn.accessibleName(), "Explorer zuklappen")
        self.assertIn("geöffneten Ordner", panel.collapse_btn.accessibleDescription())

        self.assertEqual(panel.filter_input.toolTip(), "Dateien im Explorer filtern")
        self.assertEqual(panel.filter_input.accessibleName(), "Dateifilter")
        self.assertIn("Projektdateien", panel.filter_input.accessibleDescription())


if __name__ == "__main__":
    unittest.main(verbosity=2)
