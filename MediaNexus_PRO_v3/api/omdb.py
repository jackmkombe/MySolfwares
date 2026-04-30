"""
MediaNexus PRO v3.0 - OMDb API Provider
"""
from typing import Dict, Optional
from .base import APIProvider

class OMDBProvider(APIProvider):
    @property
    def name(self) -> str:
        return "omdb"

    @property
    def base_url(self) -> str:
        return "http://www.omdbapi.com/"

    def search(self, query: str, lang: str = "fr-FR") -> Optional[Dict]:
        if not self.api_key:
            return None
        params = {"apikey": self.api_key, "s": query}
        res = self._request("", params)
        if res and res.get("Response") == "True":
            return res
        return None

    def get_details(self, item_id: str, lang: str = "fr-FR") -> Optional[Dict]:
        if not self.api_key:
            return None
        params = {"apikey": self.api_key, "i": item_id, "plot": "full"}
        return self._request("", params)
