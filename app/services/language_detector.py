import logging

from langdetect import DetectorFactory, detect
from langdetect.detector_factory import init_factory

logger = logging.getLogger(__name__)

# langdetect is non-deterministic unless seeded; load language profiles once at
# import time so concurrent threads don't race on lazy initialization
DetectorFactory.seed = 0
init_factory()


class LanguageDetector:
    """Language detection service using langdetect library."""

    @staticmethod
    def detect_language(text: str) -> str | None:
        """Detect language of given text.

        Args:
            text: Text to analyze

        Returns:
            Language code or None if detection fails
        """
        if not text or not text.strip():
            return None

        try:
            # langdetect returns e.g. 'zh-cn' / 'zh-tw'; the app uses base codes
            detected = detect(text.strip()).split("-")[0]
            logger.debug(f"Detected language: {detected}")
            return detected

        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return None
