# -*- coding: utf-8 -*-
"""Tests für CLI, Health-Check, Launcher und Runtime-Logging in DevCenter."""

import json
from pathlib import Path

from core.app_paths import get_log_file_path, get_logs_dir
from core.cli import run_cli
from core.runtime_logging import setup_logging
from modules.analyzer.method_analyzer import MethodAnalyzer


def test_app_paths_logs():
    """Prüft, dass get_logs_dir und get_log_file_path valide Pfade liefern."""
    logs_dir = get_logs_dir()
    log_file = get_log_file_path()

    assert isinstance(logs_dir, Path)
    assert isinstance(log_file, Path)
    assert logs_dir.name == "logs"
    assert log_file.name == "app.log"
    assert log_file.parent == logs_dir


def test_runtime_logging_file_and_rotation(tmp_path):
    """Prüft Datei-Logging und Formatierung über setup_logging."""
    test_log = tmp_path / "custom.log"
    logger = setup_logging(level="DEBUG", log_to_file=True, log_to_console=False, log_file=test_log)

    logger.debug("Debug-Nachricht für Unit-Test")
    logger.info("Info-Nachricht für Unit-Test")

    for h in logger.handlers:
        h.flush()

    assert test_log.exists()
    content = test_log.read_text(encoding="utf-8")
    assert "DEBUG" in content
    assert "Debug-Nachricht für Unit-Test" in content
    assert "INFO" in content
    assert "Info-Nachricht für Unit-Test" in content


def test_cli_version(capsys):
    """Prüft --version Flag."""
    code = run_cli(["--version"])
    assert code == 0
    captured = capsys.readouterr()
    assert "DevCenter 1.0.3" in captured.out


def test_cli_check_healthy(capsys):
    """Prüft den Health-Check --check."""
    code = run_cli(["--check"])
    assert code == 0
    captured = capsys.readouterr()
    assert "DevCenter Systemdiagnose" in captured.out
    assert "[Erfolg] Alle Integritätsprüfungen bestanden." in captured.out


def test_cli_analyze_file_and_json_output(tmp_path, capsys):
    """Prüft --analyze auf einer Datei mit Terminalausgabe und JSON-Export."""
    sample_py = tmp_path / "sample.py"
    sample_py.write_text(
        "class Greeter:\n    def greet(self, name: str) -> str:\n        return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    out_json = tmp_path / "report.json"

    # 1. Terminalausgabe
    code = run_cli(["--analyze", str(sample_py)])
    assert code == 0
    captured = capsys.readouterr()
    assert "Dateien analysiert:    1" in captured.out
    assert "Klassen gefunden:      1" in captured.out
    assert "Methoden gefunden:     1" in captured.out

    # 2. JSON-Export
    code = run_cli(["--analyze", str(sample_py), "--output", str(out_json)])
    assert code == 0
    assert out_json.exists()

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["files_analyzed"] == 1
    assert data["total_classes"] == 1
    assert data["total_methods"] == 1
    assert len(data["files"]) == 1


def test_cli_export_workspace(tmp_path):
    """Prüft den kopflosen Workspace-Export über --export-workspace."""
    proj_dir = tmp_path / "test_proj"
    proj_dir.mkdir()
    (proj_dir / "main.py").write_text("print('test')\n", encoding="utf-8")
    (proj_dir / "AUFGABEN.txt").write_text("- [ ] Offene Testaufgabe\n", encoding="utf-8")
    out_file = tmp_path / "exported-workspace.json"

    code = run_cli(["--export-workspace", str(proj_dir), "--output", str(out_file)])
    assert code == 0
    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["schema"] == "devcenter-workspace-v1"
    assert data["project"]["name"] == "test_proj"
    assert len(data["tasks"]) == 1


def test_cli_headless_open(capsys):
    """Prüft --headless Modus."""
    code = run_cli(["--headless", "--open", "some_project"])
    assert code == 0
    captured = capsys.readouterr()
    assert "[Headless] Projektpfad verifiziert: some_project" in captured.out


def test_method_analyzer_analyze_code():
    """Prüft die neue analyze_code Methode auf MethodAnalyzer."""
    analyzer = MethodAnalyzer()
    code = (
        "class Calculator:\n"
        "    def add(self, a, b):\n"
        "        return a + b\n"
        "\n"
        "def helper():\n"
        "    return 42\n"
    )
    result = analyzer.analyze_code(code)
    assert len(result.classes) == 1
    assert len(result.classes[0].methods) == 1
    assert len(result.functions) == 1
    assert result.classes[0].name == "Calculator"
    assert result.functions[0].name == "helper"
    assert result.total_lines == 7
