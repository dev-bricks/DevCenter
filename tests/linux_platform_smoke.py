#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reproduzierbarer Linux-Plattform-Smoke für DevCenter.

Der Smoke deckt die aktuell geplante Linux-Source-Linie ab:
- offscreen PySide6-Start des Hauptfensters
- Linux-Root-Pfad im Explorer mit echten Umlauten
- `xdg-open`-Pfad für "Im Explorer öffnen"
- `bash -c` als Shell-Pfad im Output-Panel
- aktueller Linux-Settings-Pfad unter `~/DevCenter/settings.json`
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_ROOT))

from PySide6.QtWidgets import QApplication

from core.settings_manager import SettingsManager
import core.settings_manager as settings_manager_module
from gui.main_window import MainWindow
from gui.panels.explorer_panel import ExplorerPanel
from gui.panels.output_panel import OutputPanel
import gui.main_window as main_window_module
import gui.panels.output_panel as output_panel_module


class _DummySignal:
    def __init__(self) -> None:
        self._callbacks = []

    def connect(self, callback) -> None:
        self._callbacks.append(callback)


class _FakeQProcess:
    class ProcessChannelMode:
        MergedChannels = "merged"

    class ProcessState:
        NotRunning = "not_running"
        Running = "running"

    class ProcessError:
        FailedToStart = "failed"
        Crashed = "crashed"
        Timedout = "timedout"
        WriteError = "write_error"
        ReadError = "read_error"
        UnknownError = "unknown"

    instances: list["_FakeQProcess"] = []

    def __init__(self, parent=None) -> None:
        self.parent = parent
        self.mode = None
        self.cwd = None
        self.start_args = None
        self._state = self.ProcessState.NotRunning
        self.readyReadStandardOutput = _DummySignal()
        self.finished = _DummySignal()
        self.errorOccurred = _DummySignal()
        self.__class__.instances.append(self)

    def setProcessChannelMode(self, mode) -> None:
        self.mode = mode

    def setWorkingDirectory(self, cwd: str) -> None:
        self.cwd = cwd

    def start(self, program: str, args: list[str]) -> None:
        self.start_args = (program, args)
        self._state = self.ProcessState.Running

    def state(self):
        return self._state

    def kill(self) -> None:
        self._state = self.ProcessState.NotRunning


def _exercise_linux_settings_path() -> None:
    print("Test 1: Linux-Settings-Pfad bleibt lokal unter HOME")
    with tempfile.TemporaryDirectory(prefix="devcenter-linux-home-") as temp_home:
        with mock.patch.dict(os.environ, {"HOME": temp_home}, clear=True), mock.patch.object(
            settings_manager_module.os.path,
            "expanduser",
            return_value=temp_home,
        ):
            settings = SettingsManager()
            settings_path = Path(settings.settings_path)
            expected = Path(temp_home) / "DevCenter" / "settings.json"
            assert settings_path == expected, settings_path
            assert settings_path.exists(), settings_path
    print("PASS: Settings landen aktuell unter ~/DevCenter/settings.json\n")


def _exercise_offscreen_window_and_explorer() -> None:
    print("Test 2: Offscreen-Hauptfenster und Linux-Explorerpfad funktionieren")
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory(prefix="devcenter-linux-smoke-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        settings = SettingsManager(str(temp_dir / "settings.json"))
        project_root = temp_dir / "Über Projekt"
        (project_root / "src").mkdir(parents=True)
        (project_root / "src" / "main.py").write_text("print('smoke')\n", encoding="utf-8")

        with mock.patch.object(main_window_module, "get_settings", return_value=settings), mock.patch.object(
            main_window_module,
            "AIService",
            return_value=MagicMock(),
        ):
            window = MainWindow()
            try:
                window.show()
                app.processEvents()
                assert window.windowTitle() == "DevCenter", window.windowTitle()

                window.explorer_panel.set_root_path(str(project_root))
                app.processEvents()
                assert "ÜBER PROJEKT" in window.explorer_panel.title_label.text(), window.explorer_panel.title_label.text()
            finally:
                window.close()
                app.processEvents()

        panel = ExplorerPanel()
        with mock.patch.object(sys, "platform", "linux"), mock.patch("subprocess.Popen") as popen_mock:
            panel._open_in_explorer(str(project_root))

        assert popen_mock.call_args.args[0] == ["xdg-open", str(project_root)]
    print("PASS: GUI startet offscreen und Explorer nutzt xdg-open\n")


def _exercise_linux_output_shell() -> None:
    print("Test 3: Output-Panel verwendet unter Linux bash -c")
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory(prefix="devcenter-output-") as temp_dir_name:
        _FakeQProcess.instances.clear()
        with mock.patch.object(output_panel_module, "QProcess", _FakeQProcess), mock.patch.object(
            output_panel_module.sys,
            "platform",
            "linux",
        ):
            panel = OutputPanel()
            panel.run_command("python -V", cwd=temp_dir_name)
            app.processEvents()

        assert _FakeQProcess.instances, "Kein Fake-QProcess erzeugt"
        process = _FakeQProcess.instances[-1]
        assert process.start_args == ("bash", ["-c", "python -V"]), process.start_args
        assert process.cwd == temp_dir_name, process.cwd
        assert panel.status_label.text().startswith("Läuft:"), panel.status_label.text()
    print("PASS: Output-Panel nimmt den Linux-Shell-Pfad\n")


def main() -> int:
    print("=== DevCenter Linux Platform Smoke ===\n")
    _exercise_linux_settings_path()
    _exercise_offscreen_window_and_explorer()
    _exercise_linux_output_shell()
    print("=== ALL TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
