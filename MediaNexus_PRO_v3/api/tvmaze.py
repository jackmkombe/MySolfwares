"""
MediaNexus PRO v3.0 - TVmaze API Provider
"""
from typing import Dict, Optional
from .base import APIProvider

class TVmazeProvider(APIProvider):
    def __init__(self):
        super().__init__(api_key=None)

    @property
    def name(self) -> str:
        return "tvmaze"

    @property
    def base_url(self) -> str:
        return "https://api.tvmaze.com"

    def search(self, query: str, lang: str = "fr-FR") -> Optional[Dict]:
        return self._request("search/shows", {"q": query})

    def get_details(self, item_id: str, lang: str = "fr-FR") -> Optional[Dict]:
        return self._request(f"shows/{item_id}", {"embed": "episodes"})
