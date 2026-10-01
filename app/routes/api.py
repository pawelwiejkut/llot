import logging
import socket
import threading
from collections import OrderedDict

from flask import Response, current_app, jsonify, request

from app.models.language import LanguageService
from app.routes import api_bp
from app.services.translator import TranslationService
from app.services.tts import TTSError, TTSVoiceNotFound, get_tts_address, get_tts_service

logger = logging.getLogger(__name__)
translation_service = TranslationService()

MAX_TEXT_LENGTH = 10000
MAX_CONSTRAINTS = 20


def _get_request_data():
    """Extract data from request (JSON or form)."""
    if request.is_json:
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else {}
    return request.form.to_dict()


def _str(data, key, default=""):
    value = data.get(key)
    return value.strip() if isinstance(value, str) else default


def _common_params(data):
    """Parse and validate parameters shared by translation endpoints."""
    target_lang = _str(data, "target_lang") or "de"
    if target_lang not in current_app.config["ALL_LANGUAGES"]:
        raise ValueError(f"Unsupported target language: {target_lang}")

    tone = _str(data, "tone") or "neutral"
    if tone not in LanguageService.TONE_VALUES:
        tone = "neutral"

    return {
        "target_lang": target_lang,
        "tone": tone,
        "think": data.get("think") is True,
        "model": _str(data, "model") or None,
    }


def _too_long(*texts):
    return any(len(t) > MAX_TEXT_LENGTH for t in texts)


@api_bp.route("/translate", methods=["POST"])
def translate():
    """Main translation endpoint."""
    try:
        data = _get_request_data()
        logger.debug(f"Translation request: {data}")

        source_text = _str(data, "source_text")
        if not source_text:
            return jsonify({"error": "EMPTY", "translated_text": ""})
        if _too_long(source_text):
            return jsonify(
                {"error": f"Text too long (max {MAX_TEXT_LENGTH} characters)", "translated_text": ""}
            ), 413

        source_lang = _str(data, "source_lang") or "auto"
        if source_lang != "auto" and source_lang not in current_app.config["ALL_LANGUAGES"]:
            source_lang = "auto"
        params = _common_params(data)

        translated, detected = translation_service.translate(source_text, source_lang, **params)

        return jsonify(
            {
                "translated_text": translated,
                "source_lang": detected or source_lang,
                "target_lang": params["target_lang"],
            }
        )

    except ValueError as e:
        return jsonify({"error": str(e), "translated_text": ""}), 400
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return jsonify({"error": f"Translation error: {e}"}), 502


@api_bp.route("/alternatives", methods=["POST"])
def get_alternatives():
    """Get alternative translations for a word."""
    try:
        data = _get_request_data()

        source_text = _str(data, "source_text")
        current_translation = _str(data, "current_translation")
        clicked_word = _str(data, "clicked_word")

        if not all([source_text, current_translation, clicked_word]):
            return jsonify({"alternatives": []})
        if _too_long(source_text, current_translation, clicked_word):
            return jsonify({"alternatives": []}), 413

        alternatives = translation_service.get_alternatives(
            source_text, current_translation, clicked_word, **_common_params(data)
        )
        return jsonify({"alternatives": alternatives})

    except ValueError:
        return jsonify({"alternatives": []}), 400
    except Exception as e:
        logger.error(f"Alternatives error: {e}")
        return jsonify({"alternatives": []})


@api_bp.route("/refine", methods=["POST"])
def refine_translation():
    """Refine translation with user constraints."""
    data = _get_request_data()
    current_translation = _str(data, "current_translation")
    try:
        source_text = _str(data, "source_text")
        if not source_text:
            return jsonify({"translated": ""})
        if _too_long(source_text, current_translation):
            return jsonify(
                {"translated": current_translation, "faithful": False, "error": "Text too long"}
            ), 413

        enforced_phrases = [
            p.strip() for p in (data.get("enforced_phrases") or []) if isinstance(p, str) and p.strip()
        ][:MAX_CONSTRAINTS]

        replacements = []
        for r in (data.get("replacements") or [])[:MAX_CONSTRAINTS]:
            if isinstance(r, dict):
                from_word = _str(r, "from")
                to_word = _str(r, "to")
                if from_word and to_word:
                    replacements.append({"from": from_word, "to": to_word})

        translated, faithful = translation_service.refine_translation(
            source_text,
            current_translation,
            enforced_phrases=enforced_phrases,
            replacements=replacements,
            **_common_params(data),
        )
        return jsonify({"translated": translated, "faithful": faithful})

    except Exception as e:
        logger.error(f"Refinement error: {e}")
        status = 400 if isinstance(e, (ValueError, TypeError)) else 200
        return jsonify(
            {
                "translated": current_translation,
                "faithful": False,
                "error": str(e),
            }
        ), status


class TTSCache:
    """Small thread-safe LRU cache for synthesized audio."""

    def __init__(self, max_size=50):
        self._cache = OrderedDict()
        self._lock = threading.Lock()
        self.max_size = max_size

    def get(self, key):
        with self._lock:
            value = self._cache.get(key)
            if value is not None:
                self._cache.move_to_end(key)
            return value

    def set(self, key, value):
        with self._lock:
            self._cache[key] = value
            self._cache.move_to_end(key)
            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)


tts_cache = TTSCache()


def _wav_response(wav: bytes) -> Response:
    return Response(wav, mimetype="audio/wav", headers={"Content-Disposition": "inline; filename=tts.wav"})


@api_bp.route("/tts", methods=["POST"])
def text_to_speech():
    """Convert text to speech using the configured Wyoming TTS server."""
    tts = get_tts_service()
    if tts is None:
        return jsonify({"error": "TTS service not configured. Set WYOMING_TTS_HOST."}), 503

    data = _get_request_data()
    text = _str(data, "text")
    language = _str(data, "language") or "en"
    if not text:
        return jsonify({"error": "No text provided"}), 400

    cache_key = (tts.host, tts.port, language, text)
    cached = tts_cache.get(cache_key)
    if cached:
        return _wav_response(cached)

    try:
        wav = tts.synthesize(text, language)
    except TTSVoiceNotFound as e:
        return jsonify({"error": str(e)}), 404
    except TTSError as e:
        logger.error(f"TTS error: {e}")
        return jsonify({"error": str(e)}), 502

    tts_cache.set(cache_key, wav)
    return _wav_response(wav)


@api_bp.route("/tts/languages", methods=["GET"])
def tts_languages():
    """List language codes the TTS server has voices for."""
    tts = get_tts_service()
    if tts is None:
        return jsonify({"enabled": False, "languages": []})
    try:
        return jsonify({"enabled": True, "languages": tts.get_languages()})
    except TTSError as e:
        logger.warning(f"TTS voice discovery failed: {e}")
        return jsonify({"enabled": True, "languages": [], "error": str(e)}), 502


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Check health status of all services."""
    status = {
        "ollama": {"status": "ok", "error": None},
        "tts": {"status": "ok", "error": None},
        "overall": "ok",
    }

    models = translation_service.get_available_models()
    status["ollama"]["models"] = models
    if not models:
        status["ollama"].update(status="error", error="Ollama unreachable or no models available")
        status["overall"] = "error"

    host, port = get_tts_address()
    if host:
        try:
            with socket.create_connection((host, port), timeout=2):
                pass
        except OSError as e:
            status["tts"].update(status="error", error=f"Cannot connect to {host}:{port}: {e}")
    else:
        status["tts"].update(status="disabled", error="TTS not configured")

    if status["overall"] == "ok" and status["tts"]["status"] != "ok":
        status["overall"] = "warning"

    return jsonify(status)


@api_bp.route("/models", methods=["GET"])
def get_models():
    """Get available Ollama models."""
    return jsonify({"models": translation_service.get_available_models()})
