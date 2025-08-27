import json
import re
import logging
from typing import Dict, List, Optional, Tuple
from app.services.ollama_client import get_ollama_client
from app.services.language_detector import LanguageDetector
from app.models.language import LanguageService

logger = logging.getLogger(__name__)


class TranslationService:
    def __init__(self):
        self.language_detector = LanguageDetector()
    
    def translate(self, source_text: str, source_lang: str, target_lang: str, tone: str = "neutral") -> Tuple[str, Optional[str]]:
        """
        Translate text from source language to target language.
        
        Args:
            source_text: Text to translate
            source_lang: Source language code or 'auto'
            target_lang: Target language code
            tone: Translation tone
            
        Returns:
            Tuple of (translated_text, detected_language)
        """
        if not source_text.strip():
            return "", None
        
        # Detect language if needed
        detected = None
        if source_lang == "auto":
            detected = self.language_detector.detect_language(source_text)
            source_lang_for_prompt = detected if detected else "auto"
        else:
            source_lang_for_prompt = source_lang
        
        # Build prompt
        prompt = self._build_translation_prompt(
            source_text, source_lang_for_prompt, target_lang, tone
        )
        
        # Call Ollama
        try:
            client = get_ollama_client()
            logger.info(f"Translation prompt: {prompt[:500]}...")
            translated = client.chat_completion(prompt, temperature=0.0)
            
            if not translated:
                raise Exception("Empty response from Ollama")
            
            logger.info(f"Translation completed: {len(source_text)} chars -> {len(translated)} chars")
            logger.info(f"Input: '{source_text}' -> Output: '{translated}'")
            return translated, detected
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise
    
    def get_alternatives(self, source_text: str, current_translation: str, clicked_word: str, 
                        target_lang: str, tone: str) -> List[str]:
        """
        Get alternative translations for a specific word/phrase.
        
        Args:
            source_text: Original source text
            current_translation: Current translation
            clicked_word: Word that was clicked
            target_lang: Target language code
            tone: Translation tone
            
        Returns:
            List of alternative translations
        """
        if not all([source_text, current_translation, clicked_word]):
            return []
        
        prompt = self._build_alternatives_prompt(
            source_text, current_translation, clicked_word, target_lang, tone
        )
        
        try:
            client = get_ollama_client()
            response = client.chat_completion(prompt, max_tokens=512, temperature=0.0)
            
            if not response:
                return []
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, flags=re.S)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = json.loads(response)
            
            alternatives = data.get("alternatives", [])
            
            # Filter and validate alternatives
            filtered = []
            for alt in alternatives:
                if isinstance(alt, str):
                    alt = alt.strip()
                    if 0 < len(alt) <= 60 and alt not in filtered:
                        filtered.append(alt)
            
            return filtered[:6]
            
        except Exception as e:
            logger.warning(f"Failed to get alternatives: {e}")
            return []
    
    def refine_translation(self, source_text: str, current_translation: str, 
                          target_lang: str, tone: str, enforced_phrases: List[str],
                          replacements: List[Dict[str, str]]) -> Tuple[str, bool]:
        """
        Refine translation with user constraints.
        
        Args:
            source_text: Original source text
            current_translation: Current translation draft
            target_lang: Target language code
            tone: Translation tone
            enforced_phrases: Phrases that must be included
            replacements: List of {from: str, to: str} replacements
            
        Returns:
            Tuple of (refined_translation, is_faithful)
        """
        if not source_text.strip():
            return "", True
        
        prompt = self._build_refinement_prompt(
            source_text, current_translation, target_lang, tone,
            enforced_phrases, replacements
        )
        
        try:
            client = get_ollama_client()
            response = client.chat_completion(prompt, max_tokens=768, temperature=0.0)
            
            if not response:
                return current_translation, False
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, flags=re.S)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = json.loads(response)
            
            translated = data.get("translated", "")
            faithful = bool(data.get("faithful", True))
            
            return translated, faithful
            
        except Exception as e:
            logger.warning(f"Failed to refine translation: {e}")
            return current_translation, False
    
    def _build_translation_prompt(self, source_text: str, source_lang: str, 
                                 target_lang: str, tone: str) -> str:
        """Build prompt for translation."""
        target_name = LanguageService.get_language_name(target_lang)
        source_name = ("auto-detected" if source_lang == "auto" 
                      else LanguageService.get_language_name(source_lang))
        
        tone_map = {
            "neutral": "neutral", "formal": "formal", "informal": "informal",
            "friendly": "friendly", "technical": "technical", "poetic": "poetic"
        }
        tone_desc = tone_map.get(tone, "neutral")
        
        instructions = [
            f"You are a professional translator. Translate the user's text to {target_name} ({target_lang}).",
            f"Source language: {source_name}."
        ]
        
        if tone_desc and tone_desc != "neutral":
            instructions.append(
                f"Use a {tone_desc} tone in the translation. "
                "Adapt phrasing and formality accordingly for the target language."
            )
        
        instructions.extend([
            "Keep formatting (line breaks). Do not add extra commentary, "
            "do not translate code tags, XML, or URLs.",
            "Return only the translated text, without explanations. "
            "Preserve punctuation and capitalization as appropriate."
        ])
        
        return " ".join(instructions) + "\n\nUser text:\n" + source_text
    
    def _build_alternatives_prompt(self, source_text: str, current_translation: str,
                                  clicked_word: str, target_lang: str, tone: str) -> str:
        """Build prompt for getting alternatives."""
        return (
            "You are assisting with post-editing of a translation.\n"
            f"Target language code: {target_lang}.\n"
            f"Tone: {tone}.\n"
            "Given the source sentence and its current translation to the target language, "
            f"provide up to 6 alternative single-word or short-phrase (1–3 words) replacements for the clicked token:\n"
            f"CLICKED_TOKEN: \"{clicked_word}\"\n\n"
            "Rules:\n"
            "- Keep alternatives concise (<= 3 words), natural in context, and appropriate for the target language.\n"
            "- Prefer synonyms or close variants that fit the specific sentence.\n"
            "- Avoid duplicates and avoid repeating the original token unless an inflected form differs significantly.\n"
            "- Return STRICT JSON as: {\"alternatives\": [\"...\", \"...\"]} with no extra text.\n\n"
            f"Source:\n{source_text}\n\n"
            f"Current translation:\n{current_translation}\n"
        )
    
    def _build_refinement_prompt(self, source_text: str, current_translation: str,
                                target_lang: str, tone: str, enforced_phrases: List[str],
                                replacements: List[Dict[str, str]]) -> str:
        """Build prompt for translation refinement."""
        target_name = LanguageService.get_language_name(target_lang)
        
        constraint_list = "\n".join(f"- {p}" for p in enforced_phrases) if enforced_phrases else "- (none)"
        repl_list = ("\n".join(f"- replace '{r['from']}' → '{r['to']}'" for r in replacements) 
                    if replacements else "- (none)")
        
        return (
            "You are a professional translator.\n"
            f"Task: Produce a corrected, fluent translation of the source text into {target_name} ({target_lang}).\n"
            f"Tone: {tone}.\n"
            "Return STRICT JSON ONLY:\n"
            '{"translated": "<final translation>", "faithful": true|false}'
            "\nNo explanations, no extra keys, no markdown.\n\n"
            "CONSTRAINTS:\n"
            "- The final translation MUST be faithful to the meaning of the source text.\n"
            "- You MUST include each of the following user-chosen phrases EXACTLY as written (verbatim):\n"
            f"{constraint_list}\n"
            "- Apply the following replacements to the current translation (they are user edits):\n"
            f"{repl_list}\n"
            "- Ensure each 'to' phrase appears and the corresponding 'from' token no longer appears.\n"
            "- If the enforced phrase changes the nuance, ADJUST the rest so the translation still matches the source meaning.\n"
            "- If you CANNOT keep it faithful while keeping the enforced phrase, set faithful=false and still output best-effort in 'translated'.\n"
            "- Do NOT introduce information absent from the source; you may paraphrase to keep it idiomatic.\n"
            "- You may inflect surrounding words and adjust word order, but DO NOT alter the chosen phrases themselves.\n\n"
            f"Source text:\n{source_text}\n"
            f"\nCurrent translation (user-edited draft):\n{current_translation}\n"
        )
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            client = get_ollama_client()
            return client.get_available_models()
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def change_model(self, new_model: str) -> bool:
        """Change the active Ollama model."""
        try:
            client = get_ollama_client()
            success = client.change_model(new_model)
            
            if success:
                # Update the Flask config so future requests use the new model
                from flask import current_app
                current_app.config['DEFAULT_MODEL'] = new_model
                logger.info(f"Model changed to: {new_model}")
                
            return success
        except Exception as e:
            logger.error(f"Failed to change model to {new_model}: {e}")
            return False