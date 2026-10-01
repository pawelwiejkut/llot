from unittest.mock import MagicMock, patch

import pytest

from app.services import ollama_client
from app.services.ollama_client import OllamaClient


def _response(status, body=None, text=""):
    resp = MagicMock(status_code=status, ok=200 <= status < 300, text=text)
    resp.json.return_value = body or {}
    resp.raise_for_status.side_effect = None if resp.ok else Exception(f"HTTP {status}")
    return resp


@pytest.fixture(autouse=True)
def clear_capabilities_cache():
    ollama_client._capabilities_cache.clear()


def _caps(caps):
    """Patch /api/show results: caps is a list, None (unknown) or a dict per model."""
    lookup = caps if isinstance(caps, dict) else None
    return patch.object(
        OllamaClient, "get_capabilities", lambda self, model=None: lookup[model] if lookup else caps
    )


def test_chat_returns_content_and_sends_format():
    schema = {"type": "object"}
    with _caps(["completion"]), patch("app.services.ollama_client.requests.post") as post:
        post.return_value = _response(200, {"message": {"content": " Hallo "}})
        assert OllamaClient("http://x", "m").chat_completion("hi", format=schema) == "Hallo"
        payload = post.call_args.kwargs["json"]
        assert payload["think"] is False
        assert payload["format"] == schema


def test_think_skipped_when_model_reports_no_thinking():
    with _caps(["completion"]), patch("app.services.ollama_client.requests.post") as post:
        post.return_value = _response(200, {"message": {"content": "Hallo"}})
        OllamaClient("http://x", "m").chat_completion("hi", think=True)
        assert post.call_count == 1
        assert post.call_args.kwargs["json"]["think"] is False


def test_think_sent_when_model_supports_it():
    with _caps(["completion", "thinking"]), patch("app.services.ollama_client.requests.post") as post:
        post.return_value = _response(200, {"message": {"content": "Hallo"}})
        OllamaClient("http://x", "m").chat_completion("hi", think=True)
        assert post.call_args.kwargs["json"]["think"] is True


def test_think_falls_back_when_capabilities_unknown():
    with _caps(None), patch("app.services.ollama_client.requests.post") as post:
        post.side_effect = [
            _response(400, text='{"error":"\\"m\\" does not support thinking"}'),
            _response(200, {"message": {"content": "Hallo"}}),
        ]
        assert OllamaClient("http://x", "m").chat_completion("hi", think=True) == "Hallo"
        assert [c.kwargs["json"]["think"] for c in post.call_args_list] == [True, False]


def test_api_error_raises():
    with _caps(["completion"]), patch("app.services.ollama_client.requests.post") as post:
        post.return_value = _response(404, text="model not found")
        with pytest.raises(Exception, match="404"):
            OllamaClient("http://x", "m").chat_completion("hi")


def test_models_exclude_embedding_only():
    tags = {"models": [{"name": "gemma4:26b"}, {"name": "nomic-embed-text:latest"}, {"name": "old:1b"}]}
    caps = {
        "gemma4:26b": ["completion", "thinking"],
        "nomic-embed-text:latest": ["embedding"],
        "old:1b": None,
    }
    with _caps(caps), patch("app.services.ollama_client.requests.get") as get:
        get.return_value = _response(200, tags)
        assert OllamaClient("http://x", "m").get_available_models() == ["gemma4:26b", "old:1b"]


def test_capabilities_cached_and_unknown_on_error():
    with patch("app.services.ollama_client.requests.post") as post:
        post.return_value = _response(200, {"capabilities": ["completion"]})
        client = OllamaClient("http://x", "m")
        assert client.get_capabilities() == ["completion"]
        assert client.get_capabilities() == ["completion"]
        assert post.call_count == 1

        post.return_value = _response(500)
        assert client.get_capabilities("other") is None
