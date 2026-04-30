"""
MediaNexus PRO v3.0 - API Base Module
Classe abstraite pour les providers API.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import requests

class APIProvider(ABC):
    """
    Classe de base pour tous les fournisseurs d'API.
    Définit l'interface commune et la gestion des erreurs.
    """

    def __init__(self, api_key: str = None, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MediaNexus/3.0',
            'Accept': 'application/json'
        })

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du provider (ex: 'tmdb', 'jikan')."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """URL de base de l'API."""
        pass

    @abstractmethod
    def search(self, query: str, lang: str = "fr-FR") -> Optional[Dict]:
        """
        Effectue une recherche et retourne les résultats.
        
        Args:
            query: Terme de recherche
            lang: Code langue (ex: fr-FR, en-US)
            
        Returns:
            Dict avec clé 'results' contenant la liste des résultats
        """
        pass

    @abstractmethod
    def get_details(self, item_id: str, lang: str = "fr-FR") -> Optional[Dict]:
        """
        Récupère les détails complets d'un item.
        
        Args:
            item_id: Identifiant unique de l'item
            lang: Code langue
            
        Returns:
            Dict avec les métadonnées complètes
        """
        pass

    def _request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Effectue une requête GET avec gestion des erreurs.
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params or {}, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"[{self.name}] Timeout pour {endpoint}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"[{self.name}] HTTP Error {e.response.status_code}: {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[{self.name}] Request Error: {e}")
            return None
        except ValueError:
            print(f"[{self.name}] Invalid JSON response")
            return None
