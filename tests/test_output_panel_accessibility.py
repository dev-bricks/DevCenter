# -*- coding: utf-8 -*-
"""Regressionstests für die Barrierefreiheit des Output-Panels."""

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication

from gui.panels.output_panel import OutputPanel


class OutputPanelAccessibilityTests(unittest.TestCase):
    """Sichert sprechenden Kontext für die kompakte Output-Toolbar."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_compact_output_controls_expose_accessible_context(self):
        panel = OutputPanel()

        self.assertEqual(panel.run_button.toolTip(), "Aktuelle Datei oder Befehl ausführen")
        self.assertEqual(panel.run_button.accessibleName(), "Ausführen")
        self.assertIn("Shell-Befehl", panel.run_button.accessibleDescription())

        self.assertEqual(panel.stop_button.toolTip(), "Laufenden Prozess stoppen")
        self.assertEqual(panel.stop_button.accessibleName(), "Prozess stoppen")
        self.assertIn("laufenden Prozess", panel.stop_button.accessibleDescription())

        self.assertEqual(panel.clear_button.toolTip(), "Ausgabe leeren")
        self.assertEqual(panel.clear_button.accessibleName(), "Ausgabe leeren")
        self.assertIn("Status", panel.clear_button.accessibleDescription())

        self.assertEqual(panel.auto_scroll_btn.toolTip(), "Auto-Scroll deaktivieren")
        self.assertEqual(panel.auto_scroll_btn.accessibleName(), "Auto-Scroll")
        self.assertIn("aktiviert", panel.auto_scroll_btn.accessibleDescription())

        self.assertEqual(panel.output.accessibleName(), "Konsolen-Ausgabe")
        self.assertIn("Build-Protokolle", panel.output.accessibleDescription())

        self.assertEqual(panel.status_label.accessibleName(), "Prozessstatus")
        self.assertIn("zuletzt gestartete Prozess", panel.status_label.accessibleDescription())

    def test_auto_scroll_accessibility_updates_with_state(self):
        panel = OutputPanel()

        panel.auto_scroll_btn.click()
        self.assertFalse(panel.auto_scroll_btn.isChecked())
        self.assertEqual(panel.auto_scroll_btn.toolTip(), "Auto-Scroll aktivieren")
        self.assertIn("deaktiviert", panel.auto_scroll_btn.accessibleDescription())

        panel.auto_scroll_btn.click()
        self.assertTrue(panel.auto_scroll_btn.isChecked())
        self.assertEqual(panel.auto_scroll_btn.toolTip(), "Auto-Scroll deaktivieren")
        self.assertIn("aktiviert", panel.auto_scroll_btn.accessibleDescription())


if __name__ == "__main__":
    unittest.main(verbosity=2)
