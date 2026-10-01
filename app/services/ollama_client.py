import json
import logging
import time

import requests
from flask import current_app

logger = logging.getLogger(__name__)

CAPABILITIES_TTL = 600.0
# (host, model) -> (fetched_at, capabilities or None if unknown)
_capabilities_cache: dict[tuple[str, str], tuple[float, list[str] | None]] = {}


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, host: str, model: str):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = 120

    def chat_completion(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.0,
        think: bool = False,
        format: dict | None = None,
    ) -> str | None:
        """Call Ollama /api/chat endpoint.

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            think: Whether to enable chain-of-thought reasoning (thinking models only)
            format: Optional JSON schema; Ollama then guarantees schema-valid JSON output

        Returns:
            Generated text or None if failed
        """
        url = f"{self.host}/api/chat"
        if think and not self.supports("thinking"):
            think = False
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "think": think,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if format is not None:
            payload["format"] = format

        try:
            logger.info(f"Calling Ollama /api/chat: model={self.model} think={think}")
            response = requests.post(url, json=payload, timeout=self.timeout)

            # Ollama rejects think=true for models without reasoning support; retry without it
            if think and response.status_code == 400 and "does not support thinking" in response.text:
                logger.info(f"Model {self.model} does not support thinking, retrying with think=false")
                payload = {**payload, "think": False}
                response = requests.post(url, json=payload, timeout=self.timeout)

            if not response.ok:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text[:300]}")

            data = response.json()
            content = data.get("message", {}).get("content", "").strip()

            if not content:
                raise Exception("Empty response from Ollama")

            return content

        except requests.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise Exception(f"Ollama connection error: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Ollama response parsing failed: {e}")
            raise Exception(f"Ollama response error: {e}")

    def get_capabilities(self, model: str | None = None) -> list[str] | None:
        """Model capabilities from /api/show (e.g. completion, thinking, embedding), cached.

        Returns None when unknown (request failed or server too old to report them).
        """
        model = model or self.model
        key = (self.host, model)
        cached = _capabilities_cache.get(key)
        if cached and time.monotonic() - cached[0] < CAPABILITIES_TTL:
            return cached[1]
        try:
            response = requests.post(f"{self.host}/api/show", json={"model": model}, timeout=10)
            response.raise_for_status()
            capabilities = response.json().get("capabilities")
        except Exception as e:
            logger.warning(f"Could not read capabilities of {model}: {e}")
            capabilities = None
        _capabilities_cache[key] = (time.monotonic(), capabilities)
        return capabilities

    def supports(self, capability: str) -> bool:
        """True unless the server positively reports the model lacks the capability."""
        capabilities = self.get_capabilities()
        return capabilities is None or capability in capabilities

    def get_available_models(self) -> list[str]:
        """Models usable for chat (embedding-only models are filtered out)."""
        url = f"{self.host}/api/tags"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            names = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
        except Exception as e:
            logger.error(f"Failed to get models from Ollama: {e}")
            return []
        return [n for n in names if (caps := self.get_capabilities(n)) is None or "completion" in caps]


def get_ollama_client(model: str = None) -> OllamaClient:
    """Get configured Ollama client instance."""
    return OllamaClient(
        host=current_app.config["OLLAMA_HOST"],
        model=model or current_app.config["DEFAULT_MODEL"],
    )
