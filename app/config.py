import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Ollama configuration
    OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://10.0.20.123:11434")
    DEFAULT_MODEL = os.environ.get("OL_MODEL", "gemma3:27b")
    
    # App configuration
    LISTEN_HOST = os.environ.get("APP_HOST", "0.0.0.0")
    LISTEN_PORT = int(os.environ.get("APP_PORT", "8080"))
    
    # History settings
    HISTORY_LIMIT = 5
    
    # All supported languages - can be limited by SUPPORTED_LANGUAGES env var
    ALL_LANGUAGES = {
        # Top world languages by native speakers
        'en': 'English',
        'zh': '中文 (Chinese)',
        'hi': 'हिन्दी (Hindi)',
        'es': 'Español',
        'fr': 'Français', 
        'ar': 'العربية (Arabic)',
        'bn': 'বাংলা (Bengali)',
        'pt': 'Português',
        'ru': 'Русский (Russian)',
        'ur': 'اردو (Urdu)',
        'id': 'Bahasa Indonesia',
        'de': 'Deutsch',
        'ja': '日本語 (Japanese)',
        'tr': 'Türkçe (Turkish)',
        'ko': '한국어 (Korean)',
        'vi': 'Tiếng Việt (Vietnamese)',
        'ta': 'தமிழ் (Tamil)',
        'th': 'ไทย (Thai)',
        
        # European languages
        'pl': 'Polski',
        'it': 'Italiano',
        'nl': 'Nederlands',
        'sv': 'Svenska',
        'da': 'Dansk',
        'no': 'Norsk',
        'fi': 'Suomi',
        'cs': 'Čeština',
        'sk': 'Slovenčina',
        'hu': 'Magyar',
        'ro': 'Română',
        'bg': 'Български',
        'hr': 'Hrvatski',
        'sl': 'Slovenščina',
        'lv': 'Latviešu',
        'lt': 'Lietuvių',
        'et': 'Eesti',
        'el': 'Ελληνικά',
        'mt': 'Malti',
        'ga': 'Gaeilge'
    }
    
    # Languages available for translation (configurable via env var)
    def get_translation_languages(self):
        """Languages available for translation - all by default, configurable via TRANSLATION_LANGUAGES env var"""
        supported = os.environ.get('TRANSLATION_LANGUAGES', '')
        if supported:
            # Filter to only supported languages from env var
            lang_codes = [lang.strip() for lang in supported.split(',')]
            return {code: name for code, name in self.ALL_LANGUAGES.items() if code in lang_codes}
        else:
            # Return all languages by default
            return self.ALL_LANGUAGES.copy()
    
    # Languages available for interface (same as ALL_LANGUAGES)
    def get_interface_languages(self):
        """Languages available for interface - always all languages"""
        return self.ALL_LANGUAGES.copy()
    
    # Backward compatibility - these will be set during app initialization
    TRANSLATION_LANGUAGES = None
    LANGUAGES = None
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'