from flask import request, jsonify, current_app
from app.routes import api_bp
from app.services.translator import TranslationService
from app.models.history import history_manager
import logging

logger = logging.getLogger(__name__)
translation_service = TranslationService()


@api_bp.route("/translate", methods=["POST"])
def translate():
    """Main translation endpoint."""
    try:
        data = request.get_json(silent=True) or {}
        
        source_text = (data.get("source_text") or "").strip()
        if not source_text:
            return jsonify({"error": "EMPTY", "translated": ""})
        
        source_lang = (data.get("source_lang") or "auto").strip()
        target_lang = (data.get("target_lang") or "de").strip()
        tone = (data.get("tone") or "neutral").strip()
        
        # Perform translation
        translated, detected = translation_service.translate(
            source_text, source_lang, target_lang, tone
        )
        
        return jsonify({
            "translated": translated,
            "detected": detected
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