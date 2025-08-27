from dataclasses import dataclass
from typing import List, Optional
import json


@dataclass
class HistoryItem:
    """Represents a translation history item."""
    source: str
    translated: str
    target: str
    
    @property
    def short(self) -> str:
        """Get shortened version of source text for display."""
        max_length = 40
        cleaned_source = self.source.replace("\n", " ")
        if len(cleaned_source) > max_length:
            return cleaned_source[:max_length] + "..."
        return cleaned_source


class HistoryManager:
    """Manages translation history with configurable limits."""
    
    def __init__(self, limit: int = 5):
        self.limit = limit
        self._history: List[HistoryItem] = []
    
    def add_item(self, source_text: str, translated: str, target_lang: str) -> bool:
        """Add new translation to history.
        
        Args:
            source_text: Source text
            translated: Translated text
            target_lang: Target language code
            
        Returns:
            True if item was added successfully
        """
        if not source_text or not translated:
            return False
        
        # Remove duplicate if exists
        self._remove_duplicate(source_text, target_lang)
        
        # Add new item at the beginning
        item = HistoryItem(source_text, translated, target_lang)
        self._history.insert(0, item)
        
        # Maintain limit
        self._enforce_limit()
        
        return True
    
    def _remove_duplicate(self, source_text: str, target_lang: str):
        """Remove duplicate entry if it exists."""
        for i, item in enumerate(self._history):
            if item.source == source_text and item.target == target_lang:
                self._history.pop(i)
                break
    
    def _enforce_limit(self):
        """Ensure history doesn't exceed the configured limit."""
        while len(self._history) > self.limit:
            self._history.pop()
    
    def get_history(self) -> List[HistoryItem]:
        return self._history.copy()
    
    def get_history_for_template(self) -> List[dict]:
        return [
            {
                "short": item.short,
                "source": item.source,
                "target": item.target
            }
            for item in self._history
        ]
    
    def get_history_json(self) -> str:
        return json.dumps([
            {"source": item.source, "target": item.target}
            for item in self._history
        ])
    
    def get_item(self, index: int) -> Optional[HistoryItem]:
        if 0 <= index < len(self._history):
            return self._history[index]
        return None


# Global instance
history_manager = HistoryManager()