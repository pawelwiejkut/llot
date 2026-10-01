from unittest.mock import MagicMock, patch

import pytest

from app import create_app
from app.services.translator import TranslationService


@pytest.fixture
def app_ctx():
    app = create_app()
    app.testing = True
    with app.app_context():
        yield app


@pytest.fixture
def ollama():
    client = MagicMock()
    with patch("app.services.translator.get_ollama_client", return_value=client) as factory:
        client.factory = factory
        yield client


def test_translate_builds_prompt_and_detects_language(app_ctx, ollama):
    ollama.chat_completion.return_value = "Guten Morgen"
    text, detected = TranslationService().translate(
        "Good morning, how are you today?", "auto", "de", tone="formal", think=True, model="m1"
    )
    assert (text, detected) == ("Guten Morgen", "en")
    prompt = ollama.chat_completion.call_args.args[0]
    assert "Deutsch (de)" in prompt
    assert "formal tone" in prompt
    assert prompt.endswith("Good morning, how are you today?")
    assert ollama.chat_completion.call_args.kwargs["think"] is True
    ollama.factory.assert_called_with(model="m1")


def test_translate_neutral_tone_has_no_tone_instruction(app_ctx, ollama):
    ollama.chat_completion.return_value = "Hallo"
    TranslationService().translate("Hello", "en", "de")
    assert "tone" not in ollama.chat_completion.call_args.args[0].lower()


def test_alternatives_parse_filter_and_dedupe(app_ctx, ollama):
    ollama.chat_completion.return_value = (
        'Sure! {"alternatives": ["Hallo", "Servus", "Hallo", "", 42, "' + "x" * 61 + '"]}'
    )
    alts = TranslationService().get_alternatives("Hi", "Hallo", "Hallo", "de", "neutral")
    assert alts == ["Hallo", "Servus"]


def test_alternatives_invalid_json_returns_empty(app_ctx, ollama):
    ollama.chat_completion.return_value = "no json here"
    assert TranslationService().get_alternatives("Hi", "Hallo", "Hallo", "de", "neutral") == []


def test_refine_parses_json(app_ctx, ollama):
    ollama.chat_completion.return_value = '```json\n{"translated": "Servus", "faithful": true}\n```'
    result = TranslationService().refine_translation(
        "Hi", "Hallo", "de", "neutral", ["Servus"], [{"from": "Hallo", "to": "Servus"}]
    )
    assert result == ("Servus", True)
    prompt = ollama.chat_completion.call_args.args[0]
    assert "- Servus" in prompt and "'Hallo' → 'Servus'" in prompt


def test_refine_failure_keeps_current_translation(app_ctx, ollama):
    ollama.chat_completion.side_effect = Exception("boom")
    result = TranslationService().refine_translation("Hi", "Hallo", "de", "neutral", [], [])
    assert result == ("Hallo", False)


def test_unsupported_detection_falls_back_to_auto(app_ctx, ollama):
    ollama.chat_completion.return_value = "Dobranoc"
    with patch.object(TranslationService, "__init__", lambda self: None):
        service = TranslationService()
        service.language_detector = MagicMock(detect_language=lambda text: "cy")
        _, detected = service.translate("Good night", "auto", "pl")
    assert detected is None
    assert "Source language: auto-detected." in ollama.chat_completion.call_args.args[0]
