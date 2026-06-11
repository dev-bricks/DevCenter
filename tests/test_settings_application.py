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

from PySide6.QtCore import QByteArray
from PySide6.QtWidgets import QApplication, QTabWidget

from core.settings_manager import SettingsManager
from core.project_manager import ProjectManager
from gui.dialogs.settings_dialog import SettingsDialog
from gui.main_window import MainWindow
from modules.editor.code_editor import CodeEditor
from modules.filemanager.profiler_bridge import ProfilerBridge


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
        settings.set("editor.show_line_numbers", False)
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

    def test_code_editor_autocomplete_initialized_without_apply_settings(self):
        editor = CodeEditor()
        self.assertTrue(hasattr(editor, 'autocomplete_enabled'),
                        "autocomplete_enabled must be set in __init__, not only in apply_settings")
        self.assertTrue(editor.autocomplete_enabled)

    def test_window_state_roundtrip_accepts_qbytearray(self):
        settings = self._temp_settings()

        geometry = QByteArray(b"geometry-state")
        state = QByteArray(b"window-state")

        settings.save_window_state(geometry, state)
        restored_geometry, restored_state = settings.restore_window_state()

        self.assertEqual(bytes(restored_geometry), b"geometry-state")
        self.assertEqual(bytes(restored_state), b"window-state")

    def test_settings_manager_uses_xdg_config_path_on_posix(self):
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as temp_xdg:
            with unittest.mock.patch("core.app_paths.sys.platform", "linux"), unittest.mock.patch.dict(
                os.environ,
                {"HOME": temp_home, "XDG_CONFIG_HOME": temp_xdg},
                clear=False,
            ):
                settings = SettingsManager()
                self.addCleanup(Path(settings.settings_path).unlink, missing_ok=True)
                expected = Path(temp_xdg) / "DevCenter" / "settings.json"
                self.assertEqual(Path(settings.settings_path), expected)
                self.assertTrue(expected.exists())

    def test_project_manager_uses_xdg_config_path_on_posix(self):
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as temp_xdg:
            with unittest.mock.patch("core.app_paths.sys.platform", "linux"), unittest.mock.patch.dict(
                os.environ,
                {"HOME": temp_home, "XDG_CONFIG_HOME": temp_xdg},
                clear=False,
            ):
                manager = ProjectManager()
                expected = Path(temp_xdg) / "DevCenter" / "settings.json"
                self.assertEqual(Path(manager.settings_path), expected)

    def test_profiler_bridge_uses_xdg_index_path_on_posix(self):
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as temp_xdg:
            with unittest.mock.patch("core.app_paths.sys.platform", "linux"), unittest.mock.patch.dict(
                os.environ,
                {"HOME": temp_home, "XDG_CONFIG_HOME": temp_xdg},
                clear=False,
            ):
                bridge = ProfilerBridge()
                expected = Path(temp_xdg) / "DevCenter" / "file_index.db"
                self.assertEqual(Path(bridge.db_path), expected)
                self.assertTrue(expected.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
