"""Verify the actual SDK payload without importing a real provider client."""

import asyncio
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.ai_assistant.ai_service import AIModel, AIService


@pytest.mark.parametrize(
    ("selection", "expected"),
    [
        (None, "claude-sonnet-4-6"),
        (AIModel.CLAUDE_OPUS, "claude-opus-4-6"),
        (AIModel.CLAUDE_HAIKU, "claude-haiku-4-5-20251001"),
    ],
)
def test_complete_sends_documented_model_id(monkeypatch, selection, expected):
    """The default and selectable models must reach the SDK with valid IDs."""
    create = Mock(
        return_value=SimpleNamespace(
            content=[SimpleNamespace(text="fixture response")],
            model=expected,
            usage=SimpleNamespace(input_tokens=1, output_tokens=1),
        )
    )
    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    monkeypatch.setitem(
        sys.modules, "anthropic", SimpleNamespace(Anthropic=Mock(return_value=client))
    )
    service = AIService(api_key="fixture-not-a-real-key")
    if selection is not None:
        service.set_model(selection)

    result = asyncio.run(service.complete("fixture prompt", use_history=False))

    assert result.success
    create.assert_called_once()
    assert create.call_args.kwargs["model"] == expected
    assert create.call_args.kwargs["messages"] == [
        {"role": "user", "content": "fixture prompt"}
    ]
