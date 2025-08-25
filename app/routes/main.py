from flask import render_template, current_app, request, session, redirect, url_for
from app.routes import main_bp
from app.models.language import LanguageService
import os


@main_bp.route("/", methods=["GET"])
def index():
    # Check if Wyoming Piper TTS is configured
    tts_enabled = bool(os.getenv("WYOMING_PIPER_HOST"))
    
    return render_template(
        'index.html',
        ollama_host=current_app.config['OLLAMA_HOST'],
        model=current_app.config['DEFAULT_MODEL'],
        languages=LanguageService.get_languages_for_template(),
        tones=LanguageService.get_tones_for_template(),
        tts_enabled=tts_enabled,
        last_input="",
        translated="",
        error=None
    )


@main_bp.route("/modern", methods=["GET"])
def modern():
    """Modern UI version for 2025."""
    # Check if Wyoming Piper TTS is configured
    tts_enabled = bool(os.getenv("WYOMING_PIPER_HOST"))
    
    return render_template(
        'index-modern.html',
        ollama_host=current_app.config['OLLAMA_HOST'],
        model=current_app.config['DEFAULT_MODEL'],
        languages=LanguageService.get_languages_for_template(),
        tones=LanguageService.get_tones_for_template(),
        tts_enabled=tts_enabled,
        last_input="",
        translated="",
        error=None
    )


@main_bp.route("/set_language/<language>")
def set_language(language=None):
    """Set user's preferred language (debug mode only)."""
    if not current_app.debug:
        # In production, language is detected from browser, redirect to index
        return redirect(url_for('main.index'))
    
    if language and language in current_app.config['LANGUAGES']:
        session['language'] = language
    return redirect(request.referrer or url_for('main.index'))