"""Language preference management for Discord users."""

from typing import Dict, Optional
import json
import os
from config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

class LanguageManager:
    """Manages user language preferences."""
    
    def __init__(self):
        self.user_languages: Dict[int, str] = {}
        self.data_file = "user_languages.json"
        self.load_preferences()
    
    def load_preferences(self):
        """Load user language preferences from file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert string keys back to integers
                    self.user_languages = {int(k): v for k, v in data.items()}
                print(f"✅ تم تحميل تفضيلات {len(self.user_languages)} مستخدم")
                print(f"✅ Loaded preferences for {len(self.user_languages)} users")
        except Exception as e:
            print(f"⚠️ خطأ في تحميل التفضيلات: {e}")
            print(f"⚠️ Error loading preferences: {e}")
            self.user_languages = {}
    
    def save_preferences(self):
        """Save user language preferences to file."""
        try:
            # Convert integer keys to strings for JSON serialization
            data = {str(k): v for k, v in self.user_languages.items()}
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ خطأ في حفظ التفضيلات: {e}")
            print(f"⚠️ Error saving preferences: {e}")
    
    def set_user_language(self, user_id: int, language_code: str) -> bool:
        """Set user's preferred language."""
        if language_code.lower() not in SUPPORTED_LANGUAGES:
            return False
        
        self.user_languages[user_id] = language_code.lower()
        self.save_preferences()
        return True
    
    def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language or default."""
        return self.user_languages.get(user_id, DEFAULT_LANGUAGE)
    
    def get_language_name(self, language_code: str) -> str:
        """Get the display name for a language code."""
        return SUPPORTED_LANGUAGES.get(language_code.lower(), language_code)
    
    def get_supported_languages_list(self) -> str:
        """Get a formatted list of supported languages."""
        languages = []
        for code, name in SUPPORTED_LANGUAGES.items():
            languages.append(f"`{code}` - {name}")
        
        # Split into chunks to avoid message length limits
        return "\n".join(languages)
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported."""
        return language_code.lower() in SUPPORTED_LANGUAGES
    
    def get_user_count(self) -> int:
        """Get the number of users with language preferences set."""
        return len(self.user_languages)
