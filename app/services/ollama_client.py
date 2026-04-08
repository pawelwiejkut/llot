import requests
import json
import logging
from typing import Optional, List
from flask import current_app

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, host: str, model: str):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = 120

    def chat_completion(self, prompt: str, max_tokens: int = 2048,
                        temperature: float = 0.0, think: bool = False) -> Optional[str]:
        """Call Ollama /api/chat endpoint.

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            think: Whether to enable chain-of-thought reasoning (thinking models only)

        Returns:
            Generated text or None if failed
        """
        url = f"{self.host}/api/chat"
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

        try:
            logger.info(f"Calling Ollama /api/chat: {url} (think={think})")
            response = requests.post(url, json=payload, timeout=self.timeout)

            if not response.ok:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

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

    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        url = f"{self.host}/api/tags"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
        except Exception as e:
            logger.error(f"Failed to get models from Ollama: {e}")
            return []

    def change_model(self, new_model: str) -> bool:
        """Change the active model."""
        try:
            available = self.get_available_models()
            if new_model not in available:
                logger.warning(f"Model {new_model} not in available models")
                return False
            self.model = new_model
            return True
        except Exception as e:
            logger.error(f"Failed to change model to {new_model}: {e}")
            return False


def get_ollama_client() -> OllamaClient:
    """Get configured Ollama client instance."""
    return OllamaClient(
        host=current_app.config["OLLAMA_HOST"],
        model=current_app.config["DEFAULT_MODEL"],
    )
