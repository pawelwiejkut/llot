from flask import Flask, request, session
from flask_babel import Babel
from app.config import Config
import logging
import os


def create_app(config_class=Config):
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    _setup_language_config(app, config_class)
    _setup_babel(app)
    _setup_logging(app)
    _register_blueprints(app)
    
    return app


def _setup_language_config(app, config_class):
    """Set up language configuration for the app."""
    config_instance = config_class()
    app.config['ALL_LANGUAGES'] = config_instance.ALL_LANGUAGES
    app.config['TRANSLATION_LANGUAGES'] = config_instance.get_translation_languages()
    app.config['LANGUAGES'] = config_instance.get_interface_languages()


def _setup_babel(app):
    """Initialize Babel for internationalization."""
    babel = Babel(app)
    
    def get_locale():
        # Debug mode: allow manual language selection via session
        if app.debug:
            try:
                if 'language' in session:
                    return session['language']
            except Exception:
                pass
        
        # Detect from Accept-Language header
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'en'
    
    babel.init_app(app, locale_selector=get_locale)
    
    # Make functions available in templates
    @app.context_processor
    def inject_conf_vars():
        from flask_babel import gettext, ngettext
        return {
            'get_locale': get_locale,
            'LANGUAGES': app.config['LANGUAGES'],
            'ALL_LANGUAGES': app.config['ALL_LANGUAGES'],
            '_': gettext,
            'ngettext': ngettext
        }


def _setup_logging(app):
    """Configure application logging."""
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/llot.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('LLOT startup')


def _register_blueprints(app):
    """Register all application blueprints."""
    from app.routes import main_bp, api_bp, favicon_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(favicon_bp)