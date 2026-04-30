"""
MediaNexus PRO v3.0 - Configuration Globale
Centralise toutes les constantes et chemins de l'application.
"""
from pathlib import Path

# --- IDENTITÉ APPLICATION ---
APP_NAME = "MediaNexus PRO"
APP_VERSION = "3.0.0"

# --- CHEMINS DE DONNÉES ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
DB_PATH = DATA_DIR / "medianexus.db"

# Création automatique des répertoires
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# --- PARAMÈTRES PAR DÉFAUT ---
DEFAULT_SETTINGS = {
    "theme": "dark",
    "language": "fr-FR",
    "confidence_threshold": 0.65,
    "cache_expiry_days": 30,
    "api_keys": {
        "tmdb": "",
        "rawg": ""
    }
}

# --- TYPES DE MÉDIAS SUPPORTÉS ---
MEDIA_TYPES = ["Films / Séries", "Animés", "Jeux PC"]

# --- EXTENSIONS DE FICHIERS PAR TYPE ---
FILE_EXTENSIONS = {
    "Films / Séries": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
    "Animés": [".mp4", ".mkv", ".avi"],
    "Jeux PC": [".exe", ".lnk"]
}

# --- API ENDPOINTS ---
API_ENDPOINTS = {
    "tmdb": "https://api.themoviedb.org/3",
    "jikan": "https://api.jikan.moe/v4",
    "rawg": "https://api.rawg.io/api"
}
