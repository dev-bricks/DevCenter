"""Regression tests for lossless legacy-text loading in the code editor."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication  # noqa: E402

from modules.editor.code_editor import CodeEditor  # noqa: E402


def _editor() -> CodeEditor:
    QApplication.instance() or QApplication([])
    return CodeEditor()


def test_cp1252_to_utf8_roundtrip_preserves_defined_characters(tmp_path):
    path = tmp_path / "cp1252.py"
    path.write_bytes("preis = '10 €'\nname = 'Jörg'\n".encode("cp1252"))

    editor = _editor()
    assert editor.load_file(str(path))
    assert editor.file_encoding == "cp1252"
    assert editor.save_file()
    assert editor.file_encoding == "utf-8"

    assert path.read_text(encoding="utf-8") == "preis = '10 €'\nname = 'Jörg'\n"


def test_undefined_cp1252_byte_is_not_replaced_during_utf8_conversion(tmp_path):
    path = tmp_path / "legacy.txt"
    path.write_bytes(b"before\x81after\n")

    editor = _editor()
    assert editor.load_file(str(path))
    assert editor.file_encoding == "latin-1"
    assert editor.save_file()

    converted = path.read_text(encoding="utf-8")
    assert converted == "before\x81after\n"
    assert "\ufffd" not in converted
