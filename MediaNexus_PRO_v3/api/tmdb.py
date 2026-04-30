"""
MediaNexus PRO v3.0 - TMDB API Provider
The Movie Database pour Films et Séries.
"""
from typing import Dict, Optional
from .base import APIProvider

class TMDBProvider(APIProvider):
    """
    Provider pour The Movie Database (TMDB).
    Gère Films, Séries TV et recherche multi.
    """

    @property
    def name(self) -> str:
        return "tmdb"

    @property
    def base_url(self) -> str:
        return "https://api.themoviedb.org/3"

    def search(self, query: str, lang: str = "fr-FR") -> Optional[Dict]:
        """Recherche multi (films + séries)."""
        if not self.api_key:
            return None

        params = {
            "api_key": self.api_key,
            "query": query,
            "language": lang,
            "include_adult": "false"
        }
        return self._request("search/multi", params)

    def get_details(self, item_id: str, lang: str = "fr-FR", media_type: str = "movie") -> Optional[Dict]:
        """Récupère les détails complets d'un film ou d'une série."""
        if not self.api_key:
            return None

        # S'assurer que le media_type est correct pour TMDB
        mtype = "tv" if media_type in ("tv", "tv_show", "Séries") else "movie"
        endpoint = f"{mtype}/{item_id}"
        params = {
            "api_key": self.api_key,
            "language": lang,
            "append_to_response": "credits,videos,external_ids"
        }
        return self._request(endpoint, params)

    def get_tv_details(self, tv_id: str, lang: str = "fr-FR") -> Optional[Dict]:
        """Récupère les détails étendus d'une série TV (saisons, épisodes)."""
        return self.get_details(tv_id, lang, media_type="tv")
