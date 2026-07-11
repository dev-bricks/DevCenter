# -*- coding: utf-8 -*-
# Regressionstest: code_editor multiline-Highlight
# Bug: PythonHighlighter behandelte triple-double und triple-single Quotes
# mit unabhaengigen Block-States, ohne zu pruefen ob der andere Delimiter
# bereits aktiv war. Fix: gegenseitige State-Pruefung in _highlight_multiline.
import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextDocument

from modules.editor.code_editor import PythonHighlighter

TDQ = '"""'
TSQ = "'''"


class MultilineHighlightTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _block_state(self, text, line_index):
        doc = QTextDocument()
        highlighter = PythonHighlighter(doc)
        doc.setPlainText(text)
        highlighter.rehighlight()
        QApplication.processEvents()
        block = doc.begin()
        for _ in range(line_index):
            block = block.next()
        return block.userState()

    def test_triple_double_opens_state_1(self):
        state = self._block_state("x = " + TDQ + "\nhello", 0)
        self.assertEqual(state, 1)

    def test_triple_single_opens_state_2(self):
        state = self._block_state("x = " + TSQ + "\nhello", 0)
        self.assertEqual(state, 2)

    def test_triple_double_closed_same_line_no_state(self):
        state = self._block_state("x = " + TDQ + "hello" + TDQ, 0)
        self.assertNotEqual(state, 1)

    def test_triple_single_closed_same_line_no_state(self):
        state = self._block_state("x = " + TSQ + "hello" + TSQ, 0)
        self.assertNotEqual(state, 2)

    def test_single_inside_double_block_ignored(self):
        text = "x = " + TDQ + "\ncontains " + TSQ + " inside\nmore"
        state_line0 = self._block_state(text, 0)
        state_line1 = self._block_state(text, 1)
        self.assertEqual(state_line0, 1)
        self.assertNotEqual(state_line1, 2)
        self.assertEqual(state_line1, 1)

    def test_double_inside_single_block_ignored(self):
        text = "x = " + TSQ + "\ncontains " + TDQ + " inside\nmore"
        state_line0 = self._block_state(text, 0)
        state_line1 = self._block_state(text, 1)
        self.assertEqual(state_line0, 2)
        self.assertNotEqual(state_line1, 1)
        self.assertEqual(state_line1, 2)

    def test_double_closes_correctly(self):
        text = "x = " + TDQ + "\nhello\n" + TDQ + "\ny = 1"
        state_line2 = self._block_state(text, 2)
        state_line3 = self._block_state(text, 3)
        self.assertNotEqual(state_line2, 1)
        self.assertNotEqual(state_line3, 1)

    def test_single_closes_correctly(self):
        text = "x = " + TSQ + "\nhello\n" + TSQ + "\ny = 1"
        state_line2 = self._block_state(text, 2)
        state_line3 = self._block_state(text, 3)
        self.assertNotEqual(state_line2, 2)
        self.assertNotEqual(state_line3, 2)

    def test_sequential_blocks_independent(self):
        text = TDQ + "\ndoc1\n" + TDQ + "\n" + TSQ + "\ndoc2\n" + TSQ
        state_line0 = self._block_state(text, 0)
        state_line2 = self._block_state(text, 2)
        state_line3 = self._block_state(text, 3)
        state_line5 = self._block_state(text, 5)
        self.assertEqual(state_line0, 1)
        self.assertNotEqual(state_line2, 1)
        self.assertEqual(state_line3, 2)
        self.assertNotEqual(state_line5, 2)

    def test_no_multiline_yields_default_state(self):
        state = self._block_state("x = 42", 0)
        self.assertIn(state, (-1, 0))


if __name__ == "__main__":
    unittest.main()
