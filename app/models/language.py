from dataclasses import dataclass
from typing import List, Tuple
from flask_babel import lazy_gettext as _l
from flask import current_app


@dataclass
class Language:
    code: str
    name: str
    
    def __str__(self):
        return f"{self.name} ({self.code})" if self.code != 'auto' else self.name


@dataclass 
class Tone:
    value: str
    label: str


class LanguageService:
    @classmethod
    def get_languages(cls) -> List[Language]:
        """Get all languages available for translation (configurable via TRANSLATION_LANGUAGES env var)"""
        languages = [Language("auto", _l("Auto (detect)"))]
        
        # Get available translation languages from config
        translation_languages = current_app.config['TRANSLATION_LANGUAGES']
        
        # Add languages in the order they appear in ALL_LANGUAGES
        for code, name in current_app.config['ALL_LANGUAGES'].items():
            if code in translation_languages:
                languages.append(Language(code, name))
        
        return languages
    
    @classmethod
    def get_tones(cls) -> List[Tone]:
        return [
            Tone("neutral", _l("Neutral")),
            Tone("formal", _l("Formal")),
            Tone("informal", _l("Informal")),
            Tone("friendly", _l("Friendly")),
            Tone("technical", _l("Technical")),
            Tone("poetic", _l("Poetic")),
        ]
    
    @classmethod
    def get_languages_for_template(cls) -> List[Tuple[str, str]]:
        return [(lang.code, str(lang.name)) for lang in cls.get_languages()]
    
    @classmethod
    def get_tones_for_template(cls) -> List[Tuple[str, str]]:
        return [(tone.value, str(tone.label)) for tone in cls.get_tones()]
    
    @classmethod
    def get_language_name(cls, code: str) -> str:
        for lang in cls.get_languages():
            if lang.code == code:
                return str(lang.name)
        return code