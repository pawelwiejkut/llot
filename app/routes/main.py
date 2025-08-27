from flask import render_template, current_app, request, session, redirect, url_for
from app.routes import main_bp
from app.models.language import LanguageService
import os


def _get_common_template_context():
    """Get common template context used by both views."""
    return {
        'ollama_host': current_app.config['OLLAMA_HOST'],
        'model': current_app.config['DEFAULT_MODEL'],
        'languages': LanguageService.get_languages_for_template(),
        'tones': LanguageService.get_tones_for_template(),
        'tts_enabled': bool(os.getenv("WYOMING_PIPER_HOST")),
        'last_input': "",
        'translated': "",
        'error': None
    }


@main_bp.route("/", methods=["GET"])
def index():
    """Modern UI version (now default)."""
    context = _get_common_template_context()
    context.update({
        'tts_host': os.getenv("WYOMING_PIPER_HOST", ""),
        'tts_port': os.getenv("WYOMING_PIPER_PORT", "10200")
    })
    return render_template('index-modern.html', **context)


@main_bp.route("/modern", methods=["GET"])
def modern():
    """Modern UI version for 2025 (same as main now)."""
    context = _get_common_template_context()
    context.update({
        'tts_host': os.getenv("WYOMING_PIPER_HOST", ""),
        'tts_port': os.getenv("WYOMING_PIPER_PORT", "10200")
    })
    return render_template('index-modern.html', **context)


@main_bp.route("/classic", methods=["GET"])
def classic():
    """Classic UI version (backup)."""
    return render_template('index.html', **_get_common_template_context())


@main_bp.route("/set_language/<language>")
def set_language(language=None):
    """Set user's preferred language (debug mode only)."""
    if not current_app.debug:
        return redirect(url_for('main.index'))
    
    if language and language in current_app.config['LANGUAGES']:
        session['language'] = language
    return redirect(request.referrer or url_for('main.index'))