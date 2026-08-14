# -*- coding: utf-8 -*-
"""Regressionstests für DevCenter-Einstellungen."""

import os
import sys
import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

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

    def setUp(self):
        self.keyring_patcher = patch("core.settings_manager.keyring")
        self.keyring_mock = self.keyring_patcher.start()
        self.keyring_mock.get_password.return_value = None
        self.addCleanup(self.keyring_patcher.stop)

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

    def test_settings_dialog_browse_buttons_expose_accessible_context(self):
        settings = self._temp_settings()
        dialog = SettingsDialog(settings)

        browse_buttons = [
            (
                dialog.pyinstaller_browse_btn,
                "PyInstaller-Datei auswählen",
                "Öffnet die Dateiauswahl für den PyInstaller-Pfad.",
            ),
            (
                dialog.output_dir_browse_btn,
                "Ausgabeverzeichnis auswählen",
                "Öffnet die Ordnerauswahl für das Standard-Ausgabeverzeichnis.",
            ),
            (
                dialog.backup_browse_btn,
                "Backup-Verzeichnis auswählen",
                "Öffnet die Ordnerauswahl für den Backup-Pfad.",
            ),
        ]

        for button, accessible_name, description in browse_buttons:
            self.assertEqual(button.text(), "...")
            self.assertEqual(button.toolTip(), accessible_name)
            self.assertEqual(button.accessibleName(), accessible_name)
            self.assertEqual(button.accessibleDescription(), description)

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

    def test_api_key_is_saved_to_keyring_but_not_settings_json(self):
        with patch("core.settings_manager.keyring") as keyring_mock:
            keyring_mock.get_password.return_value = None
            settings = self._temp_settings()

            self.assertTrue(settings.set("ai.api_key", "secret-token"))

            payload = json.loads(Path(settings.settings_path).read_text(encoding="utf-8"))
            self.assertNotIn("api_key", payload["ai"])
            keyring_mock.set_password.assert_called_once_with(
                "DevCenter", "anthropic_api_key", "secret-token"
            )
            self.assertEqual(settings.get("ai.api_key"), "secret-token")

    def test_legacy_plaintext_api_key_is_migrated_and_removed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = Path(temp_dir) / "settings.json"
            settings_path.write_text(
                json.dumps({"ai": {"api_key": "legacy-secret", "model": "Claude Sonnet"}}),
                encoding="utf-8",
            )

            with patch("core.settings_manager.keyring") as keyring_mock:
                keyring_mock.get_password.return_value = None
                settings = SettingsManager(str(settings_path))

            payload = json.loads(settings_path.read_text(encoding="utf-8"))
            self.assertNotIn("api_key", payload["ai"])
            keyring_mock.set_password.assert_called_once_with(
                "DevCenter", "anthropic_api_key", "legacy-secret"
            )
            self.assertEqual(settings.get("ai.api_key"), "legacy-secret")

    def test_legacy_key_is_not_duplicated_when_json_cleanup_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = Path(temp_dir) / "settings.json"
            settings_path.write_text(
                json.dumps({"ai": {"api_key": "legacy-secret"}}),
                encoding="utf-8",
            )

            with patch("core.settings_manager.keyring") as keyring_mock, patch.object(
                SettingsManager, "_save", return_value=False
            ):
                keyring_mock.get_password.return_value = None
                settings = SettingsManager(str(settings_path))

            keyring_mock.set_password.assert_not_called()
            self.assertEqual(settings.get("ai.api_key"), "legacy-secret")
            self.assertIn("legacy-secret", settings_path.read_text(encoding="utf-8"))

    def test_settings_export_never_contains_api_key(self):
        with patch("core.settings_manager.keyring") as keyring_mock:
            keyring_mock.get_password.return_value = None
            settings = self._temp_settings()
            self.assertTrue(settings.set("ai.api_key", "secret-token"))

            export_path = Path(settings.settings_path).with_name("settings-export.json")
            self.assertTrue(settings.export_settings(str(export_path)))

            exported = export_path.read_text(encoding="utf-8")
            self.assertNotIn("secret-token", exported)
            self.assertNotIn("api_key", json.loads(exported)["ai"])

    def test_keyring_failure_does_not_persist_or_accept_api_key(self):
        with patch("core.settings_manager.keyring") as keyring_mock:
            keyring_mock.get_password.return_value = None
            keyring_mock.set_password.side_effect = RuntimeError("backend unavailable")
            settings = self._temp_settings()

            self.assertFalse(settings.set("ai.api_key", "secret-token"))

            payload = Path(settings.settings_path).read_text(encoding="utf-8")
            self.assertNotIn("secret-token", payload)
            self.assertEqual(settings.get("ai.api_key"), "")

    def test_reset_fails_closed_when_keyring_delete_fails(self):
        settings = self._temp_settings()
        settings.settings.ai.api_key = "secret-token"

        with patch("core.settings_manager.keyring.delete_password") as delete_password:
            delete_password.side_effect = RuntimeError("backend unavailable")

            self.assertFalse(settings.reset_to_defaults("ai"))

        self.assertEqual(settings.get("ai.api_key"), "secret-token")

    def test_unchanged_empty_api_key_does_not_require_keyring_write(self):
        settings = self._temp_settings()
        dialog = SettingsDialog(settings)

        with patch.object(settings, "set", wraps=settings.set) as settings_set:
            dialog._save_settings()

        api_key_calls = [
            call for call in settings_set.call_args_list if call.args[0] == "ai.api_key"
        ]
        self.assertEqual(api_key_calls, [])

    def test_settings_dialog_stays_open_when_keyring_write_fails(self):
        settings = self._temp_settings()
        dialog = SettingsDialog(settings)
        dialog.api_key.setText("secret-token")

        original_set = settings.set

        def fail_only_for_api_key(key, value, save=True):
            if key == "ai.api_key":
                return False
            return original_set(key, value, save)

        with patch.object(settings, "set", side_effect=fail_only_for_api_key), patch(
            "gui.dialogs.settings_dialog.QMessageBox.critical"
        ) as critical_mock:
            dialog._save_settings()

        critical_mock.assert_called_once()
        self.assertEqual(dialog.result(), 0)

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
