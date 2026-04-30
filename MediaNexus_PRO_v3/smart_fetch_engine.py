"""
MediaNexus PRO v3.2 - Smart Fetch Engine
Moteur de recherche intelligent avec priorisation.
"""
from typing import Dict, List, Optional
from core.database import DatabaseManager
from api import APIManager

class SmartFetchEngine:
    def __init__(self, api_config):
        self.api_config = api_config
        self.manager = APIManager(api_config.keys)

    def fetch_smart(self, query: str, media_type: str) -> Optional[Dict]:
        # Logique de détection auto si media_type est inconnu (à implémenter)
        return self.manager.fetch(query, media_type)

class SmartSynchronizer:
    def __init__(self, db_manager: DatabaseManager, api_config):
        self.db = db_manager
        self.api_config = api_config
        self.engine = SmartFetchEngine(api_config)

    def sync_library(self, lib_id: int, progress_callback=None):
        items = self.db.get_items(lib_id, status="pending")
        total = len(items)
        
        for i, item in enumerate(items):
            # Simulation de fetching
            res = self.engine.fetch_smart(item['raw_name'], "Films / Séries") # Par défaut
            if res:
                self.db.update_item_metadata(item['id'], res)
            else:
                self.db.set_item_error(item['id'])
                
            if progress_callback:
                progress_callback(i + 1, total)
