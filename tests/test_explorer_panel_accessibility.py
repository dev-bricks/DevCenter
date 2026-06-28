# -*- coding: utf-8 -*-
"""Regressionstests für die Explorer-Barrierefreiheit."""

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_new_file_without_loaded_project_does_not_use_cwd(self):
        panel = ExplorerPanel()

        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            original_cwd = Path.cwd()
            try:
                os.chdir(cwd)
                with (
                    patch.object(EXPLORER_PANEL_MODULE.QInputDialog, "getText") as get_text,
                    patch.object(EXPLORER_PANEL_MODULE.QMessageBox, "warning") as warning,
                ):
                    get_text.return_value = ("leak.txt", True)
                    panel._new_file("")
            finally:
                os.chdir(original_cwd)

            self.assertFalse((cwd / "leak.txt").exists())
            get_text.assert_not_called()
            warning.assert_called_once()

    def test_new_folder_without_loaded_project_does_not_use_cwd(self):
        panel = ExplorerPanel()

        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            original_cwd = Path.cwd()
            try:
                os.chdir(cwd)
                with (
                    patch.object(EXPLORER_PANEL_MODULE.QInputDialog, "getText") as get_text,
                    patch.object(EXPLORER_PANEL_MODULE.QMessageBox, "warning") as warning,
                ):
                    get_text.return_value = ("leak", True)
                    panel._new_folder("")
            finally:
                os.chdir(original_cwd)

            self.assertFalse((cwd / "leak").exists())
            get_text.assert_not_called()
            warning.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
