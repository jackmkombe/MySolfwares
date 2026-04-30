"""
MediaNexus PRO v3.0 - RAWG API Provider
RAWG.io pour Jeux Vidéo.
"""
from typing import Dict, Optional
from .base import APIProvider

class RAWGProvider(APIProvider):
    """
    Provider pour RAWG.io (base de données de jeux vidéo).
    Clé API requise (gratuite avec inscription).
    """

    @property
    def name(self) -> str:
        return "rawg"

    @property
    def base_url(self) -> str:
        return "https://api.rawg.io/api"

    def search(self, query: str, lang: str = "fr-FR") -> Optional[Dict]:
        """Recherche de jeux par titre."""
        if not self.api_key:
            return None

        params = {
            "key": self.api_key,
            "search": query,
            "page_size": 5
        }
        return self._request("games", params)

    def get_details(self, item_id: str, lang: str = "fr-FR") -> Optional[Dict]:
        """Récupère les détails complets d'un jeu."""
        if not self.api_key:
            return None

        params = {"key": self.api_key}
        return self._request(f"games/{item_id}", params)
