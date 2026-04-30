"""
MediaNexus PRO v3.2 - Advanced Fetch Configuration
"""
import json
from pathlib import Path

class AdvancedAPIConfig:
    def __init__(self, config_path: Path = Path("api_keys.json")):
        self.config_path = config_path
        self.keys = self._load_keys()
        
    def _load_keys(self):
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {"tmdb": "", "rawg": "", "omdb": "", "igdb": ""}

    def get_key(self, provider: str):
        return self.keys.get(provider, "")

    def save_keys(self, new_keys):
        self.keys.update(new_keys)
        with open(self.config_path, 'w') as f:
            json.dump(self.keys, f, indent=2)
