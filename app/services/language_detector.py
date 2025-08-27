from langdetect import detect
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Language detection service using langdetect library."""
    
    @staticmethod
    def detect_language(text: str) -> Optional[str]:
        """Detect language of given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code or None if detection fails
        """
        if not text or not text.strip():
            return None
            
        try:
            detected = detect(text.strip())
            logger.info(f"Detected language: {detected} for text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            return detected
            
        except Exception as e:
            logger.warning(f"Language detection failed for text '{text[:30]}...': {e}")
            return None