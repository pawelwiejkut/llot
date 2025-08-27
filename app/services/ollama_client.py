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
        self.timeout_v1 = 60
        self.timeout_legacy = 90
    
    def chat_completion(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.0) -> Optional[str]:
        """Call Ollama chat completion API with fallback support.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text or None if failed
        """
        # Try v1 API first (preferred)
        result = self._try_v1_api(prompt, max_tokens, temperature)
        if result:
            return result
        
        # Fallback to legacy API
        return self._try_legacy_api(prompt, max_tokens, temperature)
    
    def _try_v1_api(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Try the v1/chat/completions endpoint."""
        url = f"{self.host}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        try:
            logger.info(f"Calling Ollama v1 API: {url}")
            response = requests.post(url, json=payload, timeout=self.timeout_v1)
            
            if not response.ok:
                logger.warning(f"V1 API failed with status {response.status_code}")
                return None
            
            data = response.json()
            
            # Extract content from various possible response formats
            if isinstance(data, dict) and "choices" in data:
                choices = data["choices"]
                if isinstance(choices, list) and choices:
                    choice = choices[0]
                    if isinstance(choice, dict):
                        # Try message.content first
                        if "message" in choice and isinstance(choice["message"], dict):
                            content = choice["message"].get("content")
                            if isinstance(content, str):
                                return content.strip()
                        
                        # Try other possible keys
                        for key in ["text", "content"]:
                            if key in choice and isinstance(choice[key], str):
                                return choice[key].strip()
            
            logger.warning("V1 API response format not recognized")
            return None
            
        except requests.RequestException as e:
            logger.warning(f"V1 API request failed: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"V1 API response parsing failed: {e}")
            return None
    
    def _try_legacy_api(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Try the legacy /api/generate endpoint."""
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            logger.info(f"Calling Ollama legacy API: {url}")
            response = requests.post(url, json=payload, timeout=self.timeout_legacy)
            
            if not response.ok:
                logger.error(f"Legacy API failed with status {response.status_code}: {response.text}")
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            # Try to parse as JSON
            try:
                data = response.json()
                if isinstance(data, dict):
                    # Try common response keys
                    for key in ["response", "output", "result", "generated", "text"]:
                        if key in data and isinstance(data[key], str):
                            return data[key].strip()
                    
                    # Try choices format
                    if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                        choice = data["choices"][0]
                        if isinstance(choice, dict):
                            for key in ["content", "text"]:
                                if key in choice and isinstance(choice[key], str):
                                    return choice[key].strip()
                
                logger.warning("Legacy API response format not recognized")
                return response.text.strip()
                
            except json.JSONDecodeError:
                # Handle streaming response format
                return self._handle_streaming_response(response.text)
            
        except requests.RequestException as e:
            logger.error(f"Legacy API request failed: {e}")
            raise Exception(f"Ollama connection error: {e}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama.
        
        Returns:
            List of available model names
        """
        url = f"{self.host}/api/tags"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'models' in data and isinstance(data['models'], list):
                return [model.get('name', '') for model in data['models'] 
                       if model.get('name')]
            
            return []
        except Exception as e:
            logger.error(f"Failed to get models from Ollama: {e}")
            return []
    
    def change_model(self, new_model: str) -> bool:
        """Change the active model.
        
        Args:
            new_model: Name of the new model to use
            
        Returns:
            True if model was changed successfully, False otherwise
        """
        try:
            available_models = self.get_available_models()
            if new_model not in available_models:
                logger.warning(f"Model {new_model} not found in available models: {available_models}")
                if not self._pull_model(new_model):
                    return False
            
            self.model = new_model
            return True
            
        except Exception as e:
            logger.error(f"Failed to change model to {new_model}: {e}")
            return False
    
    def _handle_streaming_response(self, text: str) -> str:
        """Handle streaming response format."""
        try:
            lines = [line for line in text.splitlines() if line.strip().startswith('{')]
            parts = [json.loads(line) for line in lines]
            if parts:
                output = ''.join(part.get('response', '') for part in parts)
                if output:
                    return output.strip()
        except Exception as e:
            logger.warning(f"Failed to parse streaming response: {e}")
        
        return text.strip()
    
    def _pull_model(self, model_name: str) -> bool:
        """Try to pull a model from Ollama."""
        try:
            pull_url = f"{self.host}/api/pull"
            pull_payload = {"name": model_name}
            pull_response = requests.post(pull_url, json=pull_payload, timeout=300)
            return pull_response.ok
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False


def get_ollama_client() -> OllamaClient:
    """Get configured Ollama client instance."""
    return OllamaClient(
        host=current_app.config['OLLAMA_HOST'],
        model=current_app.config['DEFAULT_MODEL']
    )