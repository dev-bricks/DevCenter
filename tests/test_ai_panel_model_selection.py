# -*- coding: utf-8 -*-
"""
TDD-Test: AIAssistantPanel model_combo.currentIndexChanged Signal-Verdrahtung

Testziel: Wenn der Nutzer im Modell-Dropdown eine andere Auswahl trifft,
wird AIService.set_model() mit dem korrekten AIModel-Enum-Wert aufgerufen.

Ausführung (erfordert Display-Umgebung oder xvfb):
    pytest tests/test_ai_panel_model_selection.py -v
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, call

# Sicherstellt, dass src/ im Importpfad liegt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="module")
def qt_app():
    """Erstellt eine QApplication-Instanz (einmalig pro Testmodul)."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_ai_service():
    """Mock für AIService mit is_available() == True."""
    svc = MagicMock()
    svc.is_available.return_value = True
    return svc


def test_model_combo_signals_wired(qt_app, mock_ai_service):
    """Nach set_ai_service() führt Combo-Wechsel auf Index 1 zu set_model(CLAUDE_OPUS)."""
    from gui.panels.ai_panel import AIAssistantPanel
    from modules.ai_assistant.ai_service import AIModel

    panel = AIAssistantPanel()
    panel.set_ai_service(mock_ai_service)

    panel.model_combo.setCurrentIndex(1)  # Claude Opus

    mock_ai_service.set_model.assert_called_with(AIModel.CLAUDE_OPUS)


def test_model_combo_initial_sync(qt_app, mock_ai_service):
    """set_ai_service() synchronisiert das aktuell ausgewählte Modell (Index 0 → SONNET)."""
    from gui.panels.ai_panel import AIAssistantPanel
    from modules.ai_assistant.ai_service import AIModel

    panel = AIAssistantPanel()
    panel.set_ai_service(mock_ai_service)

    mock_ai_service.set_model.assert_called_with(AIModel.CLAUDE_SONNET)


def test_model_combo_haiku(qt_app, mock_ai_service):
    """Combo-Wechsel auf Index 2 ergibt set_model(CLAUDE_HAIKU)."""
    from gui.panels.ai_panel import AIAssistantPanel
    from modules.ai_assistant.ai_service import AIModel

    panel = AIAssistantPanel()
    panel.set_ai_service(mock_ai_service)
    mock_ai_service.reset_mock()

    panel.model_combo.setCurrentIndex(2)  # Claude Haiku

    mock_ai_service.set_model.assert_called_with(AIModel.CLAUDE_HAIKU)


def test_model_combo_no_service_no_crash(qt_app):
    """Combo-Wechsel ohne gesetzten AI-Service löst keinen Fehler aus."""
    from gui.panels.ai_panel import AIAssistantPanel

    panel = AIAssistantPanel()
    # kein set_ai_service() — _ai_service ist None
    panel.model_combo.setCurrentIndex(1)  # darf nicht crashen


def test_model_combo_all_indices(qt_app, mock_ai_service):
    """Alle drei Combo-Indizes mappen korrekt auf die AIModel-Enum-Werte."""
    from gui.panels.ai_panel import AIAssistantPanel
    from modules.ai_assistant.ai_service import AIModel

    panel = AIAssistantPanel()
    panel.set_ai_service(mock_ai_service)
    mock_ai_service.reset_mock()

    expected = [AIModel.CLAUDE_SONNET, AIModel.CLAUDE_OPUS, AIModel.CLAUDE_HAIKU]
    for idx, model in enumerate(expected):
        panel.model_combo.setCurrentIndex(idx)
        mock_ai_service.set_model.assert_called_with(model)
