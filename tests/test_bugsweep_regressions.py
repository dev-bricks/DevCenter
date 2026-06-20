"""
Bugsweep Run #12 — Regressionstests (2026-06-20)

Bug #12-1: ai_panel.py — Zombie-Signal-Verbindung beim Neustart des Workers.
           _start_request() ersetzte self._worker ohne den alten response_received-
           Signal-Slot zu trennen. Nach Worker-Beendigung (isRunning=False) liegt
           das Signal noch in der Qt-Event-Queue; ein neuer Worker + erneutes connect()
           erzeugt zwei aktive Verbindungen → _on_response wird doppelt aufgerufen
           (doppelte Chat-Nachricht, falscher Loading-State).
           Fix Teil 1: disconnect() vor dem Ersetzen des Workers (RuntimeError abfangen
           falls kein Slot mehr verbunden) — verhindert neue doppelte Connections.
           Fix Teil 2: Identitäts-Guard in _on_response (self.sender() is not self._worker
           → return) — verwirft Events veralteter Worker, die bereits in der Qt-Event-Queue
           lagen, bevor disconnect() aufgerufen werden konnte.
"""
import os
import re
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestAIPanelZombieSignal(unittest.TestCase):
    """Bug #12-1: AIAssistantPanel – fehlender disconnect() vor Worker-Neustart."""

    def test_start_request_disconnects_old_worker_before_new_connect(self):
        src = os.path.join(PROJECT_ROOT, "src", "gui", "panels", "ai_panel.py")
        with open(src, encoding="utf-8") as f:
            source = f.read()

        disconnect_pos = source.find("response_received.disconnect")
        connect_pos = source.find("response_received.connect")

        self.assertGreater(
            disconnect_pos, -1,
            "_start_request() muss response_received.disconnect() aufrufen",
        )
        self.assertGreater(
            connect_pos, -1,
            "_start_request() muss response_received.connect() aufrufen",
        )
        self.assertLess(
            disconnect_pos, connect_pos,
            "disconnect() muss VOR connect() im Quelltext stehen (verhindert doppelte Callbacks)",
        )

    def test_start_request_wraps_disconnect_in_try_except(self):
        src = os.path.join(PROJECT_ROOT, "src", "gui", "panels", "ai_panel.py")
        with open(src, encoding="utf-8") as f:
            source = f.read()

        pattern = r'try\s*:\s*\n\s*self\._worker\.response_received\.disconnect'
        self.assertIsNotNone(
            re.search(pattern, source),
            "disconnect() muss in try/except RuntimeError eingebettet sein",
        )


class TestAIPanelIdentityGuard(unittest.TestCase):
    """Bug #12-1 Teil 2: _on_response verwirft Events veralteter Worker per sender()-Guard."""

    def test_on_response_has_sender_identity_guard(self):
        src = os.path.join(PROJECT_ROOT, "src", "gui", "panels", "ai_panel.py")
        with open(src, encoding="utf-8") as f:
            source = f.read()

        self.assertIn(
            "self.sender() is not self._worker",
            source,
            "_on_response() muss einen sender()-Identitätsguard haben, der Events "
            "veralteter Worker (noch in der Qt-Event-Queue) verwirft",
        )

    def test_identity_guard_placed_before_set_loading(self):
        src = os.path.join(PROJECT_ROOT, "src", "gui", "panels", "ai_panel.py")
        with open(src, encoding="utf-8") as f:
            source = f.read()

        guard_pos = source.find("self.sender() is not self._worker")
        loading_pos = source.find("self._set_loading(False)")

        self.assertGreater(guard_pos, -1, "Sender-Guard muss in ai_panel.py vorhanden sein")
        self.assertGreater(loading_pos, -1, "_set_loading(False) muss in ai_panel.py vorhanden sein")
        self.assertLess(
            guard_pos, loading_pos,
            "sender()-Guard muss VOR _set_loading(False) stehen (Early-return vor Zustandsänderung)",
        )


if __name__ == "__main__":
    unittest.main()
