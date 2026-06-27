"""
Bugsweep 2026-06-27 — Regressionstests

Bug #A: main_window.closeEvent (~Z.1181)
    AIWorker-QThread und OutputPanel-QProcess wurden beim Schließen des Fensters
    während eines laufenden Vorgangs nicht beendet.
    Symptom: "QThread: Destroyed while thread is still running"-Crash +
             verwaister PyInstaller-Child-Prozess.
    Fix: stop()-Methoden in AIAssistantPanel und OutputPanel; closeEvent ruft
         beide vor event.accept() auf.

Bug #B: kompilator.py (~Z.189)
    Popen(PyInstaller) ohne Timeout/Watchdog → hängender Build blockiert
    BuildWorker dauerhaft; reject() killt nur den QThread-Wrapper, nicht den
    PyInstaller-Child-Prozess → verwaister Prozess + gesperrte dist/build.
    Fix: threading.Timer-Watchdog + cancel() mit process.kill()+wait();
         check_pyinstaller/get_version mit timeout=30;
         build_dialog.reject() ruft kompilator.cancel() vor terminate() auf.
"""
import os
import re
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# Bug A — closeEvent-Cleanup
# ---------------------------------------------------------------------------

class TestAIPanelStopMethod(unittest.TestCase):
    """Bug #A-1: AIAssistantPanel muss stop() anbieten."""

    def _source(self) -> str:
        path = os.path.join(PROJECT_ROOT, "src", "gui", "panels", "ai_panel.py")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_stop_method_exists(self):
        self.assertIn(
            "def stop(self):",
            self._source(),
            "AIAssistantPanel benötigt eine stop()-Methode für den closeEvent-Cleanup"
        )

    def test_stop_uses_bounded_wait(self):
        """wait() ohne Argument blockiert unbegrenzt — muss wait(<ms>) sein."""
        src = self._source()
        # Extrahiere den stop()-Block (alles ab 'def stop' bis zur nächsten 'def ')
        match = re.search(r"def stop\(self\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "stop()-Methode nicht gefunden")
        stop_body = match.group(0)
        self.assertRegex(
            stop_body,
            r"\.wait\(\d+\)",
            "stop() muss wait(<timeout_ms>) mit Argument verwenden, "
            "nicht wait() — sonst blockiert das Fenster beim Schließen"
        )

    def test_stop_has_terminate_fallback(self):
        """Nach bounded wait() muss terminate() als Fallback vorhanden sein."""
        src = self._source()
        match = re.search(r"def stop\(self\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "stop()-Methode nicht gefunden")
        stop_body = match.group(0)
        self.assertIn(
            "terminate()",
            stop_body,
            "stop() benötigt terminate() als Fallback, wenn wait() abläuft"
        )


class TestOutputPanelStopMethod(unittest.TestCase):
    """Bug #A-2: OutputPanel muss stop() anbieten."""

    def _source(self) -> str:
        path = os.path.join(PROJECT_ROOT, "src", "gui", "panels", "output_panel.py")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_stop_method_exists(self):
        self.assertIn(
            "def stop(self):",
            self._source(),
            "OutputPanel benötigt eine stop()-Methode für den closeEvent-Cleanup"
        )

    def test_stop_kills_and_waits(self):
        src = self._source()
        match = re.search(r"def stop\(self\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "stop()-Methode nicht gefunden")
        stop_body = match.group(0)
        self.assertIn(
            "kill()",
            stop_body,
            "OutputPanel.stop() muss QProcess.kill() aufrufen"
        )
        self.assertIn(
            "waitForFinished(",
            stop_body,
            "OutputPanel.stop() muss waitForFinished() mit Timeout aufrufen"
        )


class TestCloseEventCallsStop(unittest.TestCase):
    """Bug #A-3: closeEvent muss stop() auf beiden Panels aufrufen."""

    def _source(self) -> str:
        path = os.path.join(PROJECT_ROOT, "src", "gui", "main_window.py")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_closeevent_calls_ai_panel_stop(self):
        src = self._source()
        # Extrahiere den closeEvent-Block
        match = re.search(r"def closeEvent\(self, event\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "closeEvent-Methode nicht gefunden")
        body = match.group(0)
        self.assertIn(
            "self.ai_panel.stop()",
            body,
            "closeEvent muss self.ai_panel.stop() aufrufen"
        )

    def test_closeevent_calls_output_panel_stop(self):
        src = self._source()
        match = re.search(r"def closeEvent\(self, event\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "closeEvent-Methode nicht gefunden")
        body = match.group(0)
        self.assertIn(
            "self.output_panel.stop()",
            body,
            "closeEvent muss self.output_panel.stop() aufrufen"
        )

    def test_stop_called_before_event_accept(self):
        """stop()-Aufruf muss im Quelltext vor event.accept() stehen."""
        src = self._source()
        match = re.search(r"def closeEvent\(self, event\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "closeEvent-Methode nicht gefunden")
        body = match.group(0)
        stop_pos = body.find("self.ai_panel.stop()")
        accept_pos = body.find("event.accept()")
        self.assertGreater(
            stop_pos, -1,
            "self.ai_panel.stop() nicht im closeEvent gefunden"
        )
        self.assertGreater(
            accept_pos, -1,
            "event.accept() nicht im closeEvent gefunden"
        )
        self.assertLess(
            stop_pos, accept_pos,
            "stop() muss VOR event.accept() stehen — sonst läuft der Worker nach dem Schließen weiter"
        )


# ---------------------------------------------------------------------------
# Bug B — Kompilator-Watchdog
# ---------------------------------------------------------------------------

class TestKompilatorTimeouts(unittest.TestCase):
    """Bug #B-1: subprocess.run()-Aufrufe ohne timeout= können dauerhaft hängen."""

    def _source(self) -> str:
        path = os.path.join(PROJECT_ROOT, "src", "modules", "builder", "kompilator.py")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_check_pyinstaller_has_timeout(self):
        src = self._source()
        # Signatur: def check_pyinstaller(self) -> bool:
        match = re.search(r"def check_pyinstaller\b.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "check_pyinstaller()-Methode nicht gefunden")
        self.assertIn(
            "timeout=30",
            match.group(0),
            "check_pyinstaller() braucht timeout=30 in subprocess.run()"
        )

    def test_get_pyinstaller_version_has_timeout(self):
        src = self._source()
        # Signatur: def get_pyinstaller_version(self) -> Optional[str]:
        match = re.search(r"def get_pyinstaller_version\b.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "get_pyinstaller_version()-Methode nicht gefunden")
        self.assertIn(
            "timeout=30",
            match.group(0),
            "get_pyinstaller_version() braucht timeout=30 in subprocess.run()"
        )


class TestKompilatorWatchdog(unittest.TestCase):
    """Bug #B-2: build() muss Watchdog-Timer und Cancel-Infrastruktur besitzen."""

    def _source(self) -> str:
        path = os.path.join(PROJECT_ROOT, "src", "modules", "builder", "kompilator.py")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_init_has_cancelled_event(self):
        src = self._source()
        match = re.search(r"def __init__\(self.*?\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "__init__-Methode nicht gefunden")
        self.assertIn(
            "_cancelled",
            match.group(0),
            "Kompilator.__init__ muss self._cancelled = threading.Event() initialisieren"
        )

    def test_init_has_active_process(self):
        src = self._source()
        match = re.search(r"def __init__\(self.*?\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "__init__-Methode nicht gefunden")
        self.assertIn(
            "_active_process",
            match.group(0),
            "Kompilator.__init__ muss self._active_process initialisieren"
        )

    def test_build_clears_cancelled_flag(self):
        src = self._source()
        match = re.search(r"def build\(self.*?\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "build()-Methode nicht gefunden")
        self.assertIn(
            "_cancelled.clear()",
            match.group(0),
            "build() muss _cancelled.clear() am Anfang aufrufen"
        )

    def test_build_uses_watchdog_timer(self):
        src = self._source()
        match = re.search(r"def build\(self.*?\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "build()-Methode nicht gefunden")
        body = match.group(0)
        self.assertIn(
            "threading.Timer(",
            body,
            "build() muss einen threading.Timer-Watchdog für den Timeout starten"
        )
        self.assertIn(
            "watchdog.cancel()",
            body,
            "build() muss watchdog.cancel() im finally-Block aufrufen"
        )

    def test_cancel_method_exists_and_sets_flag(self):
        src = self._source()
        self.assertIn(
            "def cancel(self)",
            src,
            "Kompilator benötigt eine cancel()-Methode"
        )
        # Signatur: def cancel(self) -> None:
        match = re.search(r"def cancel\b.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "cancel()-Methode nicht gefunden")
        body = match.group(0)
        self.assertIn(
            "_cancelled.set()",
            body,
            "cancel() muss self._cancelled.set() aufrufen"
        )
        self.assertIn(
            "proc.kill()",
            body,
            "cancel() muss den aktiven Prozess direkt killen"
        )


class TestBuildDialogCancelOnReject(unittest.TestCase):
    """Bug #B-3: BuildDialog.reject() muss cancel() auf dem Kompilator aufrufen."""

    def _source(self) -> str:
        path = os.path.join(PROJECT_ROOT, "src", "gui", "dialogs", "build_dialog.py")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_start_build_saves_kompilator_reference(self):
        src = self._source()
        match = re.search(r"def _start_build\(self\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "_start_build()-Methode nicht gefunden")
        self.assertIn(
            "self._kompilator",
            match.group(0),
            "_start_build() muss self._kompilator = Kompilator() setzen, "
            "damit reject() cancel() aufrufen kann"
        )

    def test_reject_calls_kompilator_cancel(self):
        src = self._source()
        match = re.search(r"def reject\(self\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "reject()-Methode nicht gefunden")
        body = match.group(0)
        self.assertIn(
            ".cancel()",
            body,
            "reject() muss kompilator.cancel() aufrufen, um den PyInstaller-Child zu beenden"
        )

    def test_reject_cancel_before_terminate(self):
        """cancel() (killt Child) muss VOR terminate() (killt QThread) stehen."""
        src = self._source()
        match = re.search(r"def reject\(self\):.*?(?=\n    def |\Z)", src, re.DOTALL)
        self.assertIsNotNone(match, "reject()-Methode nicht gefunden")
        body = match.group(0)
        cancel_pos = body.find(".cancel()")
        terminate_pos = body.find(".terminate()")
        self.assertGreater(cancel_pos, -1, ".cancel() nicht in reject() gefunden")
        self.assertGreater(terminate_pos, -1, ".terminate() nicht in reject() gefunden")
        self.assertLess(
            cancel_pos, terminate_pos,
            "cancel() muss VOR terminate() stehen: erst Child killen, dann QThread"
        )


if __name__ == "__main__":
    unittest.main()
