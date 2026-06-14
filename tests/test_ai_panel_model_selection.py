# -*- coding: utf-8 -*-
"""
Unit-Tests: AIAssistantPanel model_combo.currentIndexChanged Signal-Verdrahtung

Testziel: Wenn der Nutzer im Modell-Dropdown eine andere Auswahl trifft,
wird AIService.set_model() mit dem korrekten AIModel-Enum-Wert aufgerufen.

Ausführung:
    python -m unittest tests.test_ai_panel_model_selection -v
"""

import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestAIPanelModelSelection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        from gui.panels.ai_panel import AIAssistantPanel
        self.mock_service = MagicMock()
        self.mock_service.is_available.return_value = True
        self.panel = AIAssistantPanel()
        self.panel.set_ai_service(self.mock_service)

    def tearDown(self):
        self.panel.deleteLater()

    def test_model_combo_signals_wired(self):
        """Combo-Wechsel auf Index 1 ruft set_model(CLAUDE_OPUS) auf."""
        from modules.ai_assistant.ai_service import AIModel
        self.panel.model_combo.setCurrentIndex(1)
        self.mock_service.set_model.assert_called_with(AIModel.CLAUDE_OPUS)

    def test_model_combo_initial_sync(self):
        """set_ai_service() synchronisiert Combo-Index 0 sofort auf CLAUDE_SONNET."""
        from modules.ai_assistant.ai_service import AIModel
        self.mock_service.set_model.assert_called_with(AIModel.CLAUDE_SONNET)

    def test_model_combo_haiku(self):
        """Combo-Wechsel auf Index 2 ruft set_model(CLAUDE_HAIKU) auf."""
        from modules.ai_assistant.ai_service import AIModel
        self.mock_service.reset_mock()
        self.panel.model_combo.setCurrentIndex(2)
        self.mock_service.set_model.assert_called_with(AIModel.CLAUDE_HAIKU)

    def test_model_combo_no_service_no_crash(self):
        """Combo-Wechsel ohne AI-Service (kein set_ai_service) löst keinen Fehler aus."""
        from gui.panels.ai_panel import AIAssistantPanel
        panel = AIAssistantPanel()
        panel.model_combo.setCurrentIndex(1)  # _ai_service ist None — darf nicht crashen
        panel.deleteLater()

    def test_model_combo_all_indices(self):
        """Alle drei Combo-Indizes mappen korrekt auf die AIModel-Enum-Werte."""
        from modules.ai_assistant.ai_service import AIModel
        self.mock_service.reset_mock()
        expected = [AIModel.CLAUDE_SONNET, AIModel.CLAUDE_OPUS, AIModel.CLAUDE_HAIKU]
        # Reihenfolge 1→2→0: stellt sicher, dass currentIndexChanged immer feuert
        for idx in [1, 2, 0]:
            self.panel.model_combo.setCurrentIndex(idx)
            self.mock_service.set_model.assert_called_with(expected[idx])


if __name__ == '__main__':
    unittest.main()
