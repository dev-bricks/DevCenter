# -*- coding: utf-8 -*-
"""Regressionstests Bugsweep 2026-06-23 (Desktop, /bugsweep-Loop Run 10/15).

A: settings_manager nicht-atomar + silent-RMW -> Totalverlust der Config.
B: method_analyzer ast.parse faengt nur SyntaxError, nicht ValueError (NUL-Bytes) -> Crash.
C: ai_service ohne Timeout -> Hang; content[0].text ohne Typ-Guard.
D: code_editor save_file nicht-atomar (Quellcode-Verlust) + kein Encoding-Fallback.
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))


def _read(rel: str) -> str:
    return (SRC / rel).read_text(encoding="utf-8")


def test_analyzer_handles_null_byte_no_crash():
    from modules.analyzer import MethodAnalyzer
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "nul.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write("x = 1\x00\n")
        result = MethodAnalyzer().analyze_file(p)  # vor Fix: ValueError-Crash
        assert any(e.get("type") in ("ParseError", "SyntaxError") for e in result.errors)


def test_settings_save_atomic_and_corrupt_backup():
    s = _read("core/settings_manager.py")
    assert "tmp.replace(settings_file)" in s
    assert ".corrupt.bak" in s


def test_settings_corrupt_file_backed_up_not_lost(tmp_path):
    # Verhaltensbeleg: korrupte settings.json wird beim Laden nach .corrupt.bak
    # gesichert (statt still verworfen + spaeter mit Defaults ueberschrieben).
    from core.settings_manager import SettingsManager
    sf = tmp_path / "settings.json"
    sf.write_text("{ kaputt : kein valides json", encoding="utf-8")
    SettingsManager(str(sf))  # _load() im Konstruktor -> Backup-Pfad
    bak = tmp_path / "settings.corrupt.bak"
    assert bak.exists()
    assert "kaputt" in bak.read_text(encoding="utf-8")


def test_editor_atomic_save_and_encoding_fallback():
    s = _read("modules/editor/code_editor.py")
    assert "_os.replace(_tmp, path)" in s
    assert "cp1252" in s


def test_ai_service_timeout_and_content_guard():
    s = _read("modules/ai_assistant/ai_service.py")
    assert s.count("timeout=60.0") >= 2
    assert 'getattr(block, "text", "")' in s
