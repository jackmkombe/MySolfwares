"""
MediaNexus PRO v3.2 - Translation Service
Service de traduction simple pour les synopsis.
"""
import requests
from typing import Optional

class TranslationService:
    @staticmethod
    def translate(text: str, target_lang: str = "fr", source_lang: str = "en") -> Optional[str]:
        """Traduit un texte via l'API MyMemory (gratuite)."""
        if not text:
            return None
        
        # Si déjà en français et qu'on veut du français, on ne traduit pas
        if target_lang.startswith("fr") and source_lang == "fr":
            return text
            
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": text[:500], # Limite de l'API gratuite
                "langpair": f"{source_lang}|{target_lang}"
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                translated = data.get("responseData", {}).get("translatedText")
                if translated and "MYMEMORY WARNING" not in translated:
                    return translated
        except Exception as e:
            print(f"Translation Error: {e}")
            
        return text # Fallback sur le texte original
