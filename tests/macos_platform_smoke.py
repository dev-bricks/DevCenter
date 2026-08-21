#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reproduzierbarer macOS-Plattform-Smoke für DevCenter.

Der Smoke deckt die geplante macOS-Source-Linie ab:
- XDG-/POSIX-Settings-Pfad unter macOS (`~/.config/DevCenter/settings.json`)
- Offscreen PySide6-Start des Hauptfensters mit Unicode-Projektpfaden
- macOS-System-Explorer-Pfad via `open <path>` in ExplorerPanel
- macOS-Terminal- und Shell-Pfad via `bash -c` in OutputPanel
- Plattformunabhängige Asset- und Icon-Auflösung
- Redigierter Workspace-Export (`devcenter-workspace-v1.json`) auf macOS
- SQLite ProfilerBridge Dateiindexierung auf POSIX/macOS
"""

from __future__ import annotations

import json
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

from core.app_paths import get_app_data_dir, get_app_icon_path, get_file_index_path, get_settings_path
from modules.filemanager.profiler_bridge import ProfilerBridge
from core.project_manager import ProjectConfig
from core.settings_manager import SettingsManager
from core.workspace_export import build_workspace_export, export_workspace
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


def _ensure_app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _exercise_macos_settings_path() -> None:
    print("Test 1: macOS Settings- und Index-Pfade folgen POSIX/XDG-Konventionen")
    with tempfile.TemporaryDirectory(prefix="devcenter-macos-home-") as temp_home:
        temp_xdg = str(Path(temp_home) / ".xdg-config")
        with mock.patch("core.app_paths.sys.platform", "darwin"), mock.patch.dict(
            os.environ,
            {"HOME": temp_home, "XDG_CONFIG_HOME": temp_xdg, "QT_QPA_PLATFORM": "offscreen"},
            clear=False,
        ):
            app_dir = get_app_data_dir()
            expected_dir = Path(temp_xdg) / "DevCenter"
            assert app_dir == expected_dir, f"app_dir {app_dir} != {expected_dir}"

            settings_path = get_settings_path()
            assert settings_path == expected_dir / "settings.json", settings_path

            index_path = get_file_index_path()
            assert index_path == expected_dir / "file_index.db", index_path

            settings = SettingsManager()
            settings.set("editor.font_family", "Menlo")
            settings.set("test_umlaut", "Überprüfung für macOS")

            assert Path(settings.settings_path).exists()
            content = json.loads(Path(settings.settings_path).read_text(encoding="utf-8"))
            assert content.get("editor", {}).get("font_family") == "Menlo" or content.get("editor.font_family") == "Menlo"
            assert content.get("test_umlaut") == "Überprüfung für macOS"
    print("PASS: Settings & Index-Pfade auf macOS sind POSIX/XDG-konform\n")


def _exercise_macos_offscreen_window_and_explorer() -> None:
    print("Test 2: Offscreen-Hauptfenster und macOS-Explorerpfad ('open') funktionieren")
    app = _ensure_app()
    with tempfile.TemporaryDirectory(prefix="devcenter-macos-smoke-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        settings = SettingsManager(str(temp_dir / "settings.json"))
        project_root = temp_dir / "Mac Projékte"
        (project_root / "src").mkdir(parents=True)
        (project_root / "src" / "main.py").write_text("print('macos smoke')\n", encoding="utf-8")

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
                assert "MAC PROJÉKTE" in window.explorer_panel.title_label.text(), window.explorer_panel.title_label.text()
            finally:
                window.close()
                app.processEvents()

        panel = ExplorerPanel()
        with mock.patch.object(sys, "platform", "darwin"), mock.patch("subprocess.Popen") as popen_mock:
            panel._open_in_explorer(str(project_root))

        assert popen_mock.call_args.args[0] == ["open", str(project_root)], popen_mock.call_args.args[0]
    print("PASS: GUI startet offscreen und Explorer nutzt macOS 'open'\n")


def _exercise_macos_output_shell() -> None:
    print("Test 3: Output-Panel verwendet unter macOS bash -c")
    app = _ensure_app()
    with tempfile.TemporaryDirectory(prefix="devcenter-macos-output-") as temp_dir_name:
        _FakeQProcess.instances.clear()
        with mock.patch.object(output_panel_module, "QProcess", _FakeQProcess), mock.patch.object(
            output_panel_module.sys,
            "platform",
            "darwin",
        ):
            panel = OutputPanel()
            panel.run_command("python3 -V", cwd=temp_dir_name)
            app.processEvents()

        assert _FakeQProcess.instances, "Kein Fake-QProcess erzeugt"
        process = _FakeQProcess.instances[-1]
        assert process.start_args == ("bash", ["-c", "python3 -V"]), process.start_args
        assert process.cwd == temp_dir_name, process.cwd
        assert panel.status_label.text().startswith("Läuft:"), panel.status_label.text()
    print("PASS: Output-Panel nimmt den macOS-Shell-Pfad\n")


def _exercise_macos_asset_resolution() -> None:
    print("Test 4: App-Asset und Icon-Auflösung auf macOS")
    icon_path = get_app_icon_path()
    assert icon_path.exists(), f"Icon {icon_path} existiert nicht"
    assert icon_path.stat().st_size > 0, f"Icon {icon_path} ist leer"
    assert icon_path.suffix.lower() in {".ico", ".png"}, f"Unerwarteter Icon-Typ: {icon_path.suffix}"
    print(f"PASS: Icon erfolgreich aufgelöst ({icon_path.name})\n")


def _exercise_macos_workspace_export() -> None:
    print("Test 5: Workspace-Export auf macOS ohne Secrets und ohne BOM")
    with tempfile.TemporaryDirectory(prefix="devcenter-macos-ws-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        proj_dir = temp_dir / "Test macOS Projekt"
        proj_dir.mkdir(parents=True)
        (proj_dir / "main.py").write_text("print('hello darwin')\n", encoding="utf-8")
        (proj_dir / ".env").write_text("SECRET_KEY=super_secret_12345\n", encoding="utf-8")

        settings = SettingsManager(str(temp_dir / "settings.json"))
        settings.set("ai.api_key", "sk-ant-api03-sensitive-token")

        project = ProjectConfig(
            name="Test macOS Projekt",
            path=str(proj_dir),
            created="2026-08-21T00:00:00Z",
            last_opened="2026-08-21T00:00:00Z",
            version="1.0.0",
            description="macOS Test",
        )

        export_data = build_workspace_export(
            project=project,
            settings=settings,
        )

        assert export_data["schema"] == "devcenter-workspace-v1"
        assert export_data["project"]["name"] == "Test macOS Projekt"

        out_file = temp_dir / "export.json"
        export_workspace(project, settings, str(out_file))

        raw_bytes = out_file.read_bytes()
        assert not raw_bytes.startswith(b"\xef\xbb\xbf"), "BOM gefunden!"
        text = raw_bytes.decode("utf-8")
        assert "super_secret_12345" not in text
        assert "sk-ant-api03" not in text
    print("PASS: Workspace-Export erzeugt valide, redigierte JSON ohne Secrets\n")


def _exercise_macos_profiler_bridge() -> None:
    print("Test 6: SQLite ProfilerBridge Dateiindexierung auf POSIX/macOS")
    with tempfile.TemporaryDirectory(prefix="devcenter-macos-bridge-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        db_path = str(temp_dir / "index.db")
        bridge = ProfilerBridge(db_path=db_path)

        test_file = temp_dir / "modul_äöü.py"
        test_file.write_text("def berechne_summe(): return 42\n", encoding="utf-8")

        success = bridge.index_file(str(test_file))
        assert success is True

        stats = bridge.get_statistics()
        assert stats["total_files"] == 1

        results = bridge.search("berechne")
        assert len(results) >= 1
        assert results[0].file.name == "modul_äöü.py"
    print("PASS: ProfilerBridge SQLite-Indexierung funktioniert fehlerfrei\n")


def main() -> int:
    print("=== DevCenter macOS Platform Smoke ===\n")
    _exercise_macos_settings_path()
    _exercise_macos_offscreen_window_and_explorer()
    _exercise_macos_output_shell()
    _exercise_macos_asset_resolution()
    _exercise_macos_workspace_export()
    _exercise_macos_profiler_bridge()
    print("=== ALL macOS TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
