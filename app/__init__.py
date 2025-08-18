from flask import Flask, request, session
from flask_babel import Babel, get_locale
from app.config import Config
import logging
import os


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Set up language dictionaries
    config_instance = config_class()
    app.config['ALL_LANGUAGES'] = config_instance.ALL_LANGUAGES
    app.config['TRANSLATION_LANGUAGES'] = config_instance.get_translation_languages()
    app.config['LANGUAGES'] = config_instance.get_interface_languages()
    
    # Initialize Babel
    babel = Babel(app)
    
    def get_locale():
        # 1. In debug mode, allow manual language selection via session
        if app.debug:
            try:
                if 'language' in session:
                    return session['language']
            except Exception as e:
                pass
        
        # 2. Try to guess from Accept-Language header
        detected = request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'en'
        return detected
    
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
    
    # Configure logging
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
    
    # Register routes
    from app.routes import main_bp, api_bp, favicon_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(favicon_bp)
    
    return app