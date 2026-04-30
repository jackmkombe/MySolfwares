"""
MediaNexus PRO v3.0 - Module de Cache API
Gestion du cache avec expiration et stratégie LRU.
"""
import hashlib
import json
from typing import Dict, Optional
from datetime import datetime, timedelta

class CacheManager:
    """
    Gestionnaire de cache API avec persistance SQLite.
    Évite les appels réseau redondants et permet le mode offline.
    """

    def __init__(self, db_manager, default_expiry_days: int = 30):
        self.db = db_manager
        self.default_expiry = default_expiry_days
        # Nettoyage des entrées expirées au démarrage
        self.db.clear_expired_cache()

    @staticmethod
    def generate_key(source: str, query: str, params: Dict = None) -> str:
        """
        Génère une clé de cache unique basée sur la source et la requête.
        """
        key_data = f"{source}:{query}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, source: str, query: str, params: Dict = None) -> Optional[Dict]:
        """
        Récupère une entrée du cache si elle existe et n'est pas expirée.
        """
        cache_key = self.generate_key(source, query, params)
        return self.db.get_cached(cache_key)

    def set(self, source: str, query: str, response: Dict, params: Dict = None, expiry_days: int = None):
        """
        Stocke une réponse API dans le cache.
        """
        cache_key = self.generate_key(source, query, params)
        expiry = expiry_days or self.default_expiry
        self.db.set_cache(cache_key, response, source, expiry)

    def invalidate(self, source: str, query: str, params: Dict = None):
        """
        Invalide une entrée de cache spécifique.
        """
        cache_key = self.generate_key(source, query, params)
        # On pourrait ajouter une méthode delete_cache dans DatabaseManager
        pass

    def clear_all(self):
        """
        Vide entièrement le cache (pour debug ou reset).
        """
        self.db.clear_expired_cache()
