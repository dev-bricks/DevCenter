# -*- coding: utf-8 -*-
"""Regressionstests für Barrierefreiheit und Tastaturbedienung des Suchdialogs."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from gui.dialogs.search_replace_dialog import SearchReplaceDialog


class SearchReplaceAccessibilityTests(unittest.TestCase):
    """Sichert barrierefreie Steuerelemente und Tastatur-Ergonomie."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.dialog = SearchReplaceDialog()

    def tearDown(self):
        self.dialog.close()

    def test_dialog_labels_have_buddies_and_mnemonics(self):
        """Prüft Mnemonics und Verknüpfung per setBuddy für Alt-Taste-Sprünge."""
        self.assertEqual(self.dialog.search_label.text(), "&Suchen:")
        self.assertEqual(self.dialog.search_label.buddy(), self.dialog.search_input)

        self.assertEqual(self.dialog.replace_label.text(), "E&rsetzen durch:")
        self.assertEqual(self.dialog.replace_label.buddy(), self.dialog.replace_input)

        self.assertEqual(self.dialog.scope_label.text(), "&Bereich:")
        self.assertEqual(self.dialog.scope_label.buddy(), self.dialog.scope_combo)

    def test_dialog_controls_expose_accessible_names_and_descriptions(self):
        """Stellt sicher, dass alle Steuerelemente aussagekräftige Namen und Beschreibungen haben."""
        # Eingabefelder
        self.assertEqual(self.dialog.search_input.accessibleName(), "Suchbegriff")
        self.assertIn("aktive Dokument", self.dialog.search_input.accessibleDescription())

        self.assertEqual(self.dialog.replace_input.accessibleName(), "Ersetzung")
        self.assertIn("ersetzt werden sollen", self.dialog.replace_input.accessibleDescription())

        # Checkboxen
        self.assertEqual(self.dialog.case_sensitive.accessibleName(), "Groß-/Kleinschreibung beachten")
        self.assertIn("Groß- und Kleinbuchstaben", self.dialog.case_sensitive.accessibleDescription())

        self.assertEqual(self.dialog.whole_word.accessibleName(), "Nur ganze Wörter")
        self.assertIn("Wortbestandteile ignoriert", self.dialog.whole_word.accessibleDescription())

        self.assertEqual(self.dialog.regex.accessibleName(), "Regulärer Ausdruck")
        self.assertIn("regulärer Python-Ausdruck", self.dialog.regex.accessibleDescription())

        # Combobox & Status
        self.assertEqual(self.dialog.scope_combo.accessibleName(), "Suchbereich")
        self.assertIn("gesamten Dokument", self.dialog.scope_combo.accessibleDescription())

        self.assertEqual(self.dialog.status_label.accessibleName(), "Suchstatus")
        self.assertIn("Rückmeldung", self.dialog.status_label.accessibleDescription())

        # Buttons
        self.assertEqual(self.dialog.find_previous_button.accessibleName(), "Vorherigen Treffer suchen")
        self.assertIn("vorherigen Vorkommen", self.dialog.find_previous_button.accessibleDescription())

        self.assertEqual(self.dialog.find_next_button.accessibleName(), "Nächsten Treffer suchen")
        self.assertIn("nächsten Vorkommen", self.dialog.find_next_button.accessibleDescription())

        self.assertEqual(self.dialog.replace_button.accessibleName(), "Aktuellen Treffer ersetzen")
        self.assertIn("Fundstelle durch den Ersetzungstext", self.dialog.replace_button.accessibleDescription())

        self.assertEqual(self.dialog.replace_all_button.accessibleName(), "Alle Treffer ersetzen")
        self.assertIn("alle Vorkommen", self.dialog.replace_all_button.accessibleDescription())

        self.assertEqual(self.dialog.cancel_button.accessibleName(), "Suchdialog schließen")

    def test_dialog_buttons_shortcuts_and_tooltips(self):
        """Prüft Shortcuts und Tastaturhinweise in Tooltips."""
        # Tooltips
        self.assertIn("Alt+S", self.dialog.search_input.toolTip())
        self.assertIn("Alt+R", self.dialog.replace_input.toolTip())
        self.assertIn("Alt+B", self.dialog.scope_combo.toolTip())
        self.assertIn("F3", self.dialog.find_next_button.toolTip())
        self.assertIn("Umschalt+F3", self.dialog.find_previous_button.toolTip())
        self.assertIn("Alt+E", self.dialog.replace_button.toolTip())
        self.assertIn("Alt+A", self.dialog.replace_all_button.toolTip())
        self.assertIn("Escape", self.dialog.cancel_button.toolTip())

        # Mnemonics in Buttontexten
        self.assertEqual(self.dialog.find_previous_button.text(), "&Vorheriger Treffer")
        self.assertEqual(self.dialog.find_next_button.text(), "&Nächster Treffer")
        self.assertEqual(self.dialog.replace_button.text(), "&Ersetzen")
        self.assertEqual(self.dialog.replace_all_button.text(), "&Alle ersetzen")

        # Shortcuts
        self.assertEqual(self.dialog.find_next_button.shortcut().toString(), "F3")
        self.assertEqual(self.dialog.find_previous_button.shortcut().toString(), "Shift+F3")

    def test_return_and_shift_return_handling(self):
        """Verifiziert Enter/Shift+Enter Verhalten im Such- und Ersetzenfeld."""
        next_calls = []
        prev_calls = []
        replace_calls = []

        self.dialog.find_next_requested.connect(lambda *a: next_calls.append(a))
        self.dialog.find_previous_requested.connect(lambda *a: prev_calls.append(a))
        self.dialog.replace_requested.connect(lambda *a: replace_calls.append(a))

        self.dialog.search_input.setText("test_query")
        self.dialog.replace_input.setText("replacement_text")

        # Normales Enter im Suchfeld löst find_next aus
        self.dialog.search_input.returnPressed.emit()
        self.assertEqual(len(next_calls), 1)
        self.assertEqual(next_calls[0][0], "test_query")

        # Shift+Enter im Suchfeld löst find_previous aus
        shift_enter_event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Return,
            Qt.KeyboardModifier.ShiftModifier
        )
        handled = self.dialog.eventFilter(self.dialog.search_input, shift_enter_event)
        self.assertTrue(handled)
        self.assertEqual(len(prev_calls), 1)
        self.assertEqual(prev_calls[0][0], "test_query")

        # Enter im Ersetzen-Feld löst replace aus
        self.dialog.replace_input.returnPressed.emit()
        self.assertEqual(len(replace_calls), 1)
        self.assertEqual(replace_calls[0][0], "test_query")
        self.assertEqual(replace_calls[0][1], "replacement_text")

    def test_reject_and_close_emit_cancelled(self):
        """Verifiziert, dass Escape/reject() sauber das cancelled-Signal auslöst."""
        cancelled_calls = []
        self.dialog.cancelled.connect(lambda: cancelled_calls.append(True))

        self.dialog.reject()
        self.assertEqual(len(cancelled_calls), 1)
        self.assertFalse(self.dialog.isVisible())


if __name__ == "__main__":
    unittest.main(verbosity=2)
