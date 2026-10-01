import os

from flask import current_app, redirect, render_template, session, url_for

from app.models.language import LanguageService
from app.routes import main_bp
from app.services.tts import get_tts_address

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


def _asset_version():
    """Cache-busting token that changes whenever the main JS/CSS files change."""
    files = ("js/app-modern.js", "css/style-modern.css")
    return str(int(max(os.path.getmtime(os.path.join(_STATIC_DIR, f)) for f in files)))


def _get_common_template_context():
    """Template context for the translator page."""
    tts_host, tts_port = get_tts_address()
    return {
        "ollama_host": current_app.config["OLLAMA_HOST"],
        "model": current_app.config["DEFAULT_MODEL"],
        "languages": LanguageService.get_languages_for_template(),
        "tones": LanguageService.get_tones_for_template(),
        "tts_enabled": bool(tts_host),
        "tts_host": tts_host or "",
        "tts_port": tts_port or "",
        "asset_version": _asset_version(),
    }


@main_bp.route("/", methods=["GET"])
def index():
    """Main translator UI."""
    return render_template("index-modern.html", **_get_common_template_context())


@main_bp.route("/set_language/<language>")
def set_language(language=None):
    """Set user's preferred language (debug mode only)."""
    if not current_app.debug:
        return redirect(url_for("main.index"))

    if language and language in current_app.config["LANGUAGES"]:
        session["language"] = language
    return redirect(url_for("main.index"))
