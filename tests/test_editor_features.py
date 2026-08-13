# -*- coding: utf-8 -*-
"""Fokustests für den TASKPLAN-Editor-Slice 2010."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication

from gui.dialogs.search_replace_dialog import SearchReplaceDialog
from modules.editor.code_editor import CodeEditor


class EditorFeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.editor = CodeEditor()
        self.addCleanup(self.editor.deleteLater)

    def test_search_navigation_and_no_match(self):
        self.editor.setPlainText("Alpha beta\nalpha ALPHA")

        self.assertEqual(len(self.editor.find_matches("alpha")), 3)
        self.assertTrue(self.editor.find_next("alpha"))
        self.assertEqual(self.editor.textCursor().selectedText(), "Alpha")
        self.assertTrue(self.editor.find_next("alpha"))
        self.assertEqual(self.editor.textCursor().selectedText(), "alpha")
        self.assertTrue(self.editor.find_previous("alpha"))
        self.assertEqual(self.editor.textCursor().selectedText(), "Alpha")
        self.assertFalse(self.editor.find_next("not-present"))

    def test_search_scope_special_characters_and_regex(self):
        self.editor.setPlainText("[x] €\n[x] (x)\nother")
        cursor = self.editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(5, cursor.MoveMode.KeepAnchor)
        self.editor.setTextCursor(cursor)

        self.assertEqual(
            len(self.editor.find_matches("[x]", scope="selection")), 1
        )
        self.assertEqual(
            len(self.editor.find_matches(r"\([a-z]\)", regex=True)), 1
        )
        self.assertEqual(
            len(self.editor.find_matches("x", whole_word=True)), 3
        )
        self.assertEqual(len(self.editor.find_matches("xy", whole_word=True)), 0)

    def test_replace_all_is_one_undo_unit_and_preserves_utf8(self):
        original = "Äpfel äpfel\nÄPFEL"
        self.editor.setPlainText(original)

        self.assertEqual(self.editor.replace_all("Birne", "äpfel"), 3)
        self.assertEqual(self.editor.toPlainText(), "Birne Birne\nBirne")
        self.editor.undo()
        self.assertEqual(self.editor.toPlainText(), original)

    def test_replace_current_and_cancel_do_not_replace_via_set_plain_text(self):
        self.editor.setPlainText("one two one")
        self.assertTrue(self.editor.find_next("one"))
        self.assertTrue(self.editor.replace_current("eins"))
        self.assertEqual(self.editor.toPlainText(), "eins two one")
        self.editor.cancel_search()
        self.assertEqual(self.editor.toPlainText(), "eins two one")

    def test_folding_state_transitions(self):
        self.editor.setPlainText("def run():\n    child()\n    return True\nnext()")

        self.assertEqual(self.editor.foldable_block_numbers(), [0])
        self.assertTrue(self.editor.fold_block(0))
        self.assertTrue(self.editor.is_folded(0))
        self.assertFalse(self.editor.document().findBlockByNumber(1).isVisible())
        self.assertTrue(self.editor.unfold_block(0))
        self.assertFalse(self.editor.is_folded(0))
        self.assertTrue(self.editor.document().findBlockByNumber(1).isVisible())

        self.editor.fold_block(0)
        self.editor.insertPlainText(" # edited")
        self.assertTrue(self.editor.document().findBlockByNumber(1).isVisible())

    def test_search_dialog_exposes_scope_and_abort_contract(self):
        dialog = SearchReplaceDialog()
        self.addCleanup(dialog.deleteLater)
        self.assertEqual(dialog.scope_combo.itemData(0), "document")
        self.assertEqual(dialog.scope_combo.itemData(1), "selection")
        self.assertEqual(dialog.find_next_button.objectName(), "findNextButton")
        self.assertEqual(dialog.replace_all_button.objectName(), "replaceAllButton")

    def test_load_file_keeps_utf8_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "utf8.py"
            path.write_text("# Grüße: €\n", encoding="utf-8")
            self.assertTrue(self.editor.load_file(str(path)))
            self.assertEqual(self.editor.toPlainText(), "# Grüße: €\n")
            self.assertFalse(self.editor.is_modified())


if __name__ == "__main__":
    unittest.main()
