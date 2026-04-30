"""
MediaNexus PRO v3.0 - API Package Init
Gestionnaire centralisé des providers API.
"""
from typing import Dict, Optional, List
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import APIProvider
from .tmdb import TMDBProvider
from .jikan import JikanProvider
from .rawg import RAWGProvider
from .omdb import OMDBProvider
from .tvmaze import TVmazeProvider

class APIManager:
    """
    Gestionnaire centralisé des API.
    Route les requêtes vers le bon provider selon le type de média ou la source choisie.
    Supporte le fetching parallèle multi-sources.
    """

    def __init__(self, api_keys: Dict[str, str] = None):
        keys = api_keys or {}
        self.providers = {
            "Films / Séries": TMDBProvider(api_key=keys.get("tmdb")),
            "Animés": JikanProvider(),
            "Jeux PC": RAWGProvider(api_key=keys.get("rawg")),
            "tmdb": TMDBProvider(api_key=keys.get("tmdb")),
            "omdb": OMDBProvider(api_key=keys.get("omdb")),
            "tvmaze": TVmazeProvider(),
            "jikan": JikanProvider(),
            "rawg": RAWGProvider(api_key=keys.get("rawg"))
        }

    def update_keys(self, api_keys: Dict[str, str]):
        """Met à jour les clés API des providers."""
        if "tmdb" in api_keys:
            self.providers["Films / Séries"].api_key = api_keys["tmdb"]
            self.providers["tmdb"].api_key = api_keys["tmdb"]
        if "rawg" in api_keys:
            self.providers["Jeux PC"].api_key = api_keys["rawg"]
            self.providers["rawg"].api_key = api_keys["rawg"]
        if "omdb" in api_keys:
            self.providers["omdb"].api_key = api_keys["omdb"]

    def fetch(self, query: str, media_type: str, lang: str = "fr-FR", source: str = None) -> Optional[Dict]:
        """
        Effectue une recherche simple ou multi-sources.
        """
        if source == "Multi-Sources":
            # Chercher partout pour ce type de média (ou les providers compatibles)
            valid_sources = []
            if media_type == "Films / Séries":
                valid_sources = ["tmdb", "omdb", "tvmaze"]
            elif media_type == "Animés":
                valid_sources = ["jikan"]
            elif media_type == "Jeux PC":
                valid_sources = ["rawg"]
            
            return self.fetch_multi(query, valid_sources, lang)

        provider = None
        if source and source.lower() in self.providers:
            provider = self.providers.get(source.lower())
        
        if not provider:
            provider = self.providers.get(media_type)
            
        if not provider:
            return None
        return provider.search(query, lang)

    def fetch_multi(self, query: str, sources: List[str], lang: str = "fr-FR") -> Dict:
        """
        Exécute des recherches en parallèle sur plusieurs sources.
        Retourne un dictionnaire fusionné contenant tous les résultats.
        """
        all_results = []
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            future_to_source = {
                executor.submit(self.providers[s].search, query, lang): s 
                for s in sources if s.lower() in self.providers
            }
            
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    res = future.result()
                    if res:
                        # On s'assure que chaque résultat porte sa source
                        candidates = res.get('results', res.get('data', [res]))
                        if not isinstance(candidates, list): candidates = [candidates]
                        
                        for c in candidates:
                            c['_api_source'] = source_name
                        
                        all_results.extend(candidates)
                except Exception as e:
                    print(f"Error fetching from {source_name}: {e}")

        return {"results": all_results}

    def get_details(self, item_id: str, media_type: str, lang: str = "fr-FR", specific_type: str = None, source: str = None) -> Optional[Dict]:
        """ Récupère les détails complets d'un item. """
        provider = None
        # Si le candidat vient d'une source spécifique (via Multi-Sources)
        if source and source.lower() in self.providers:
            provider = self.providers.get(source.lower())
            
        if not provider:
            provider = self.providers.get(media_type)
            
        if not provider:
            return None
        
        if hasattr(provider, 'get_details'):
            if specific_type and provider.name == "tmdb":
                return provider.get_details(item_id, lang, media_type=specific_type)
            return provider.get_details(item_id, lang)
        return None

__all__ = [
    'APIProvider',
    'TMDBProvider',
    'JikanProvider',
    'RAWGProvider',
    'OMDBProvider',
    'TVmazeProvider',
    'APIManager'
]
