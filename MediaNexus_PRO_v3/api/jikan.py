"""
MediaNexus PRO v3.0 - Jikan API Provider
MyAnimeList via API Jikan (gratuite, sans clé).
"""
from typing import Dict, Optional
from .base import APIProvider

class JikanProvider(APIProvider):
    """
    Provider pour Jikan API (MyAnimeList non-officiel).
    Aucune clé API requise.
    """

    def __init__(self):
        super().__init__(api_key=None, timeout=10)

    @property
    def name(self) -> str:
        return "jikan"

    @property
    def base_url(self) -> str:
        return "https://api.jikan.moe/v4"

    def search(self, query: str, lang: str = "fr-FR") -> Optional[Dict]:
        """Recherche d'animés par titre."""
        params = {
            "q": query,
            "limit": 5,  # Top 5 candidats pour matching
            "sfw": "true"
        }
        return self._request("anime", params)

    def get_details(self, item_id: str, lang: str = "fr-FR") -> Optional[Dict]:
        """Récupère les détails complets d'un animé."""
        return self._request(f"anime/{item_id}/full")
