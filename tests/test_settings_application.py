# -*- coding: utf-8 -*-
"""Regressionstests für DevCenter-Einstellungen."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication, QTabWidget

from core.settings_manager import SettingsManager
from gui.dialogs.settings_dialog import SettingsDialog
from gui.main_window import MainWindow
from modules.editor.code_editor import CodeEditor


class DevCenterSettingsTests(unittest.TestCase):
    """Tests für die Anwendung von Editor-Einstellungen."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _temp_settings(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        settings_path = Path(temp_dir.name) / "settings.json"
        return SettingsManager(str(settings_path))

    def test_settings_dialog_saves_highlight_current_line(self):
        settings = self._temp_settings()
        dialog = SettingsDialog(settings)

        dialog.highlight_line.setChecked(False)
        dialog._save_settings()

        self.assertFalse(settings.get("editor.highlight_current_line"))

    def test_main_window_applies_editor_settings_to_open_tabs(self):
        settings = self._temp_settings()
        settings.set("editor.font_family", "Courier New")
        settings.set("editor.font_size", 14)
        settings.set("editor.tab_size", 2)
        settings.set("editor.line_numbers", False)
        settings.set("editor.auto_complete", False)
        settings.set("editor.highlight_current_line", False)
        settings.set("ai.api_key", "secret-token")

        window = MainWindow.__new__(MainWindow)
        window.settings = settings
        window.ai_service = MagicMock()
        window.editor_tabs = QTabWidget()

        editor = CodeEditor()
        window.editor_tabs.addTab(editor, "scratch.py")

        window._apply_settings()

        window.ai_service.set_api_key.assert_called_once_with("secret-token")
        self.assertEqual(editor.font().family(), "Courier New")
        self.assertEqual(editor.font().pointSize(), 14)
        self.assertEqual(editor.tab_size, 2)
        self.assertEqual(editor.line_number_area_width(), 0)
        self.assertFalse(editor.autocomplete_enabled)
        self.assertFalse(editor.highlight_current_line_enabled)
        self.assertEqual(editor.extraSelections(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
