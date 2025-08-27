from flask import request, jsonify, current_app, Response
from app.routes import api_bp
from app.services.translator import TranslationService
from app.models.history import history_manager
from app.utils.debug import debug_print
import logging
import os

logger = logging.getLogger(__name__)
translation_service = TranslationService()


@api_bp.route("/translate", methods=["POST"])
def translate():
    """Main translation endpoint."""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form.to_dict()
        
        debug_print(f"Translation request data: {data}")
        
        source_text = (data.get("source_text") or "").strip()
        if not source_text:
            return jsonify({"error": "EMPTY", "translated_text": ""})
        
        source_lang = (data.get("source_lang") or "auto").strip()
        target_lang = (data.get("target_lang") or "de").strip()
        tone = (data.get("tone") or "neutral").strip()
        
        # Perform translation
        translated, detected = translation_service.translate(
            source_text, source_lang, target_lang, tone
        )
        
        return jsonify({
            "translated_text": translated,
            "source_lang": detected or source_lang,
            "target_lang": target_lang
        })
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return jsonify({"error": f"Translation error: {str(e)}"})


@api_bp.route("/history/save", methods=["POST"])
def save_history():
    """Save translation to history."""
    try:
        data = request.get_json(silent=True) or {}
        
        source_text = (data.get("source_text") or "").strip()
        translated = (data.get("translated") or "").strip()
        target_lang = (data.get("target_lang") or "de").strip()
        
        if not source_text or not translated:
            return jsonify({"ok": False, "error": "EMPTY"})
        
        success = history_manager.add_item(source_text, translated, target_lang)
        
        return jsonify({"ok": success})
        
    except Exception as e:
        logger.error(f"History save error: {e}")
        return jsonify({"ok": False, "error": str(e)})


@api_bp.route("/alternatives", methods=["POST"])
def get_alternatives():
    """Get alternative translations for a word."""
    try:
        data = request.get_json(silent=True) or {}
        
        source_text = (data.get("source_text") or "").strip()
        current_translation = (data.get("current_translation") or "").strip()
        clicked_word = (data.get("clicked_word") or "").strip()
        target_lang = (data.get("target_lang") or "de").strip()
        tone = (data.get("tone") or "neutral").strip()
        
        if not all([source_text, current_translation, clicked_word]):
            return jsonify({"alternatives": []})
        
        alternatives = translation_service.get_alternatives(
            source_text, current_translation, clicked_word, target_lang, tone
        )
        
        return jsonify({"alternatives": alternatives})
        
    except Exception as e:
        logger.error(f"Alternatives error: {e}")
        return jsonify({"alternatives": []})


@api_bp.route("/refine", methods=["POST"])
def refine_translation():
    """Refine translation with user constraints."""
    try:
        data = request.get_json(silent=True) or {}
        
        source_text = (data.get("source_text") or "").strip()
        current_translation = (data.get("current_translation") or "").strip()
        target_lang = (data.get("target_lang") or "de").strip()
        tone = (data.get("tone") or "neutral").strip()
        
        # Process enforced phrases
        enforced_phrases = [
            p.strip() for p in (data.get("enforced_phrases") or [])
            if isinstance(p, str) and p.strip()
        ]
        
        # Process replacements
        raw_replacements = data.get("replacements") or []
        replacements = []
        for r in raw_replacements:
            if isinstance(r, dict):
                from_word = (r.get("from") or "").strip()
                to_word = (r.get("to") or "").strip()
                if from_word and to_word:
                    replacements.append({"from": from_word, "to": to_word})
        
        if not source_text:
            return jsonify({"translated": ""})
        
        translated, faithful = translation_service.refine_translation(
            source_text, current_translation, target_lang, tone,
            enforced_phrases, replacements
        )
        
        return jsonify({
            "translated": translated,
            "faithful": faithful
        })
        
    except Exception as e:
        logger.error(f"Refinement error: {e}")
        return jsonify({
            "translated": current_translation,
            "faithful": False,
            "error": str(e)
        })


# Simple in-memory cache for TTS
tts_cache = {}

@api_bp.route("/tts", methods=["POST"])
def text_to_speech():
    """Convert text to speech using Wyoming Piper TTS with streaming support."""
    from flask import request as flask_request
    debug_print("TTS endpoint called!")
    try:
        debug_print("In try block")
        data = flask_request.get_json(silent=True) or {}
        
        debug_print(f"Received TTS data: {data}")
        
        text = (data.get("text") or "").strip()
        debug_print(f"TTS request for text: {text}")
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Get language and streaming preference
        language = data.get("language", "pl")
        use_streaming = data.get("streaming", False)  # Use streaming when requested
        debug_print(f"TTS language: {language}, streaming param: {data.get('streaming')}, use_streaming: {use_streaming}")
        
        # Map languages to Wyoming Piper TTS voices (only supported languages)
        voice_map = {
            # Western European
            "en": "en_US-lessac-medium",
            "de": "de_DE-thorsten-medium", 
            "fr": "fr_FR-siwis-medium",
            "es": "es_ES-sharvard-medium",
            "pt": "pt_BR-faber-medium",
            "nl": "nl_NL-mls_5809-low",
            "da": "da_DK-talesyntese-medium",
            "fi": "fi_FI-harri-medium", 
            "no": "no_NO-talesyntese-medium",
            
            # Central/Eastern European
            "pl": "pl_PL-darkman-medium",
            "cs": "cs_CZ-jirka-medium",
            "sk": "sk_SK-lili-medium",
            "hu": "hu_HU-anna-medium",
            "ro": "ro_RO-mihai-medium",
            "ru": "ru_RU-ruslan-medium",
            
            # Other languages
            "ar": "ar_JO-kareem-low",
            "hi": "hi_IN-male-medium",
            "tr": "tr_TR-dfki-medium",
            "vi": "vi_VN-vais1000-medium",
            "zh": "zh_CN-huayan-x_low",
            "id": "id_ID-fajri-medium"
        }
        
        # Primary voice selection with fallback chain
        voice = voice_map.get(language)
        if not voice:
            # Fallback chain: requested -> English -> Polish
            voice = voice_map.get("en", voice_map.get("pl", "pl_PL-darkman-medium"))
        
        # Check cache first (only for non-streaming requests)
        cache_key = f"{text}:{voice}"
        if not use_streaming and cache_key in tts_cache:
            debug_print("Found in cache, returning cached audio")
            return Response(
                tts_cache[cache_key],
                mimetype="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=tts.wav",
                    "Content-Length": str(len(tts_cache[cache_key]))
                }
            )
        
        # Check if Wyoming Piper is configured
        wyoming_host = os.getenv("WYOMING_PIPER_HOST")
        if not wyoming_host:
            return jsonify({"error": "TTS service not configured. Set WYOMING_PIPER_HOST environment variable."}), 500
            
        logger.info(f"TTS: Using Wyoming TTS for text: '{text}', voice: '{voice}', streaming: {use_streaming}")
        
        # Use simple Wyoming TTS compatible with wyoming 1.5.4
        debug_print(f"Using simple Wyoming TTS for text: '{text}', voice: '{voice}'")
        try:
            from app.services.wyoming_tts_simple import SimpleWyomingTTSService
            
            simple_tts = SimpleWyomingTTSService()
            wav_content = simple_tts.synthesize(text, voice)
            debug_print(f"Generated WAV with {len(wav_content)} bytes using simple Wyoming")
            
            # Cache the result
            if len(tts_cache) > 50:
                tts_cache.clear()
            tts_cache[cache_key] = wav_content
            debug_print("Cached TTS result")
            
            return Response(
                wav_content,
                mimetype="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=tts.wav",
                    "Content-Length": str(len(wav_content))
                }
            )
            
        except Exception as e:
            debug_print(f"Simple TTS error: {e}")
            return jsonify({"error": f"TTS service error: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"TTS endpoint error: {e}")
        return jsonify({"error": f"TTS error: {str(e)}"}), 500


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Check health status of all services."""
    try:
        from app.services.ollama_client import get_ollama_client
        import requests
        
        status = {
            "ollama": {"status": "ok", "error": None},
            "tts": {"status": "ok", "error": None},
            "overall": "ok"
        }
        
        # Check Ollama
        try:
            client = get_ollama_client()
            # Try a simple API call to check if Ollama is responding
            response = client.chat_completion("hi", temperature=0.0, max_tokens=5)
            if not response or len(response.strip()) == 0:
                raise Exception("Empty response from Ollama")
            
            # Get available models
            try:
                models = client.get_available_models()
                status["ollama"]["models"] = models
            except Exception as model_error:
                logger.warning(f"Could not get models: {model_error}")
                status["ollama"]["models"] = []
                
        except Exception as e:
            status["ollama"]["status"] = "error"
            status["ollama"]["error"] = str(e)
            status["ollama"]["models"] = []
            status["overall"] = "error"
        
        # Check TTS service
        wyoming_host = os.getenv("WYOMING_PIPER_HOST")
        if wyoming_host:
            try:
                # Simple connection test to Wyoming Piper
                wyoming_port = os.getenv("WYOMING_PIPER_PORT", "10200")
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((wyoming_host, int(wyoming_port)))
                sock.close()
                if result != 0:
                    raise Exception(f"Cannot connect to {wyoming_host}:{wyoming_port}")
            except Exception as e:
                status["tts"]["status"] = "error" 
                status["tts"]["error"] = str(e)
                if status["overall"] == "ok":
                    status["overall"] = "warning"  # TTS error is warning, not critical
        else:
            status["tts"]["status"] = "disabled"
            status["tts"]["error"] = "TTS not configured"
            if status["overall"] == "ok":
                status["overall"] = "warning"
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "ollama": {"status": "error", "error": str(e)},
            "tts": {"status": "unknown", "error": "Health check failed"},
            "overall": "error"
        }), 500


@api_bp.route("/models", methods=["GET"])
def get_models():
    """Get available Ollama models."""
    try:
        models = translation_service.get_available_models()
        return jsonify({"models": models})
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return jsonify({"error": str(e), "models": []}), 500


@api_bp.route("/change_model", methods=["POST"])
def change_model():
    """Change the active Ollama model."""
    try:
        data = request.get_json() or {}
        new_model = data.get("model")
        
        if not new_model:
            return jsonify({"error": "Model name required"}), 400
            
        # Change model in translation service
        success = translation_service.change_model(new_model)
        
        if success:
            return jsonify({"success": True, "model": new_model})
        else:
            return jsonify({"error": "Failed to change model"}), 500
            
    except Exception as e:
        logger.error(f"Error changing model: {e}")
        return jsonify({"error": str(e)}), 500