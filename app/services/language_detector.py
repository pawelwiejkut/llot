from langdetect import detect
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LanguageDetector:
    @staticmethod
    def detect_language(text: str) -> Optional[str]:
        """
        Detect language of given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code or None if detection fails
        """
        try:
            if not text or not text.strip():
                return None
                
            detected = detect(text.strip())
            logger.info(f"Detected language: {detected} for text: {text[:50]}...")
            return detected
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return None