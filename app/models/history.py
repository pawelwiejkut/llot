from dataclasses import dataclass
from typing import List, Optional
import json


@dataclass
class HistoryItem:
    source: str
    translated: str
    target: str
    
    @property
    def short(self) -> str:
        return self.source[:40].replace("\n", " ") + ("..." if len(self.source) > 40 else "")


class HistoryManager:
    def __init__(self, limit: int = 5):
        self.limit = limit
        self._history: List[HistoryItem] = []
    
    def add_item(self, source_text: str, translated: str, target_lang: str) -> bool:
        if not source_text or not translated:
            return False
        
        # Remove duplicate if exists
        self._remove_duplicate(source_text, target_lang)
        
        # Add new item at the beginning
        item = HistoryItem(source_text, translated, target_lang)
        self._history.insert(0, item)
        
        # Maintain limit
        while len(self._history) > self.limit:
            self._history.pop()
        
        return True
    
    def _remove_duplicate(self, source_text: str, target_lang: str):
        for i, item in enumerate(self._history):
            if item.source == source_text and item.target == target_lang:
                self._history.pop(i)
                break
    
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