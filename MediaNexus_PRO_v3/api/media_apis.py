"""
MediaNexus PRO v3.2 - API de Médias
Système complet de fetching pour films, séries, animés et jeux vidéo
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class MediaType(Enum):
    """Types de médias supportés."""
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    ANIME = "anime"
    MANGA = "manga"
    VIDEO_GAME = "video_game"

@dataclass
class MediaInfo:
    """Structure unifiée pour les informations de médias."""
    title: str
    type: MediaType
    year: Optional[int] = None
    synopsis: Optional[str] = None
    poster_url: Optional[str] = None
    rating: Optional[float] = None
    genres: List[str] = None
    cast: List[str] = None
    director: Optional[str] = None
    duration: Optional[str] = None
    episodes: Optional[int] = None
    seasons: Optional[int] = None
    platform: Optional[str] = None  # Pour les jeux
    release_date: Optional[str] = None
    imdb_id: Optional[str] = None
    mal_id: Optional[int] = None  # MyAnimeList ID
    igdb_id: Optional[int] = None  # IGDB ID

class APIKeyManager:
    """Gestionnaire des clés API avec signalement."""
    
    def __init__(self):
        self.required_keys = {
            "omdb": False,
            "tmdb": False,
            "rawg": False,
            "igdb": False
        }
        self.api_keys = {}
        self.load_keys()
    
    def load_keys(self):
        """Charge les clés API depuis un fichier de configuration."""
        try:
            with open("api_keys.json", "r") as f:
                self.api_keys = json.load(f)
                # Marquer les clés requises comme disponibles
                for key in self.required_keys:
                    if key in self.api_keys and self.api_keys[key]:
                        self.required_keys[key] = True
        except FileNotFoundError:
            self.save_keys()  # Créer le fichier
    
    def save_keys(self):
        """Sauvegarde les clés API."""
        with open("api_keys.json", "w") as f:
            json.dump(self.api_keys, f, indent=2)
    
    def set_key(self, api_name: str, key: str):
        """Définit une clé API."""
        self.api_keys[api_name] = key
        self.required_keys[api_name] = True
        self.save_keys()
    
    def get_key(self, api_name: str) -> Optional[str]:
        """Récupère une clé API."""
        return self.api_keys.get(api_name)
    
    def needs_key(self, api_name: str) -> bool:
        """Vérifie si une API nécessite une clé."""
        return api_name in self.required_keys and not self.required_keys[api_name]

class MediaAPIManager:
    """Gestionnaire principal des API de médias."""
    
    def __init__(self):
        self.key_manager = APIKeyManager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MediaNexus-PRO/3.2'
        })
    
    # ==================== FILMS & SÉRIES ====================
    
    def search_omdb(self, query: str, media_type: str = "all") -> List[MediaInfo]:
        """Recherche via OMDb API."""
        if self.key_manager.needs_key("omdb"):
            return []
        
        api_key = self.key_manager.get_key("omdb")
        base_url = "http://www.omdbapi.com/"
        
        params = {
            "apikey": api_key,
            "s": query,
            "type": media_type if media_type != "all" else None
        }
        
        try:
            response = self.session.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True":
                    return self._parse_omdb_results(data.get("Search", []))
        except Exception as e:
            print(f"Erreur OMDb: {e}")
        
        return []
    
    def search_tmdb(self, query: str, media_type: str = "multi") -> List[MediaInfo]:
        """Recherche via TMDb API."""
        if self.key_manager.needs_key("tmdb"):
            return []
        
        api_key = self.key_manager.get_key("tmdb")
        base_url = "https://api.themoviedb.org/3/search/"
        
        if media_type == "movie":
            endpoint = f"{base_url}movie"
        elif media_type == "tv":
            endpoint = f"{base_url}tv"
        else:
            endpoint = f"{base_url}multi"
        
        params = {
            "api_key": api_key,
            "query": query,
            "language": "fr-FR"
        }
        
        try:
            response = self.session.get(endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_tmdb_results(data.get("results", []))
        except Exception as e:
            print(f"Erreur TMDb: {e}")
        
        return []
    
    def search_tvmaze(self, query: str) -> List[MediaInfo]:
        """Recherche via TVmaze API (gratuite, sans clé)."""
        base_url = "https://api.tvmaze.com/search/shows"
        
        params = {"q": query}
        
        try:
            response = self.session.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_tvmaze_results(data)
        except Exception as e:
            print(f"Erreur TVmaze: {e}")
        
        return []
    
    # ==================== ANIMÉS & MANGAS ====================
    
    def search_jikan(self, query: str, media_type: str = "anime") -> List[MediaInfo]:
        """Recherche via Jikan API (MyAnimeList, gratuit)."""
        base_url = "https://api.jikan.moe/v4/"
        
        if media_type == "anime":
            endpoint = f"{base_url}anime"
        elif media_type == "manga":
            endpoint = f"{base_url}manga"
        else:
            endpoint = f"{base_url}anime"
        
        params = {"q": query, "limit": 20}
        
        try:
            response = self.session.get(endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_jikan_results(data.get("data", []))
        except Exception as e:
            print(f"Erreur Jikan: {e}")
        
        return []
    
    def search_animeapi(self, query: str) -> List[MediaInfo]:
        """Recherche via AnimeAPI (animeapi.skin, gratuit)."""
        base_url = "https://animeapi.skin/api"
        
        endpoints = [
            f"{base_url}/search?q={query}",
            f"{base_url}/trending"
        ]
        
        results = []
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint)
                if response.status_code == 200:
                    data = response.json()
                    results.extend(self._parse_animeapi_results(data))
            except Exception as e:
                print(f"Erreur AnimeAPI: {e}")
        
        return results
    
    def search_animembed(self, query: str = None, page: int = 1) -> List[MediaInfo]:
        """Recherche via AnimEmbed API (gratuit)."""
        base_url = "https://animembed.com/api"
        
        if query:
            endpoint = f"{base_url}/search?q={query}"
        else:
            endpoint = f"{base_url}/animes?page={page}"
        
        try:
            response = self.session.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                return self._parse_animembed_results(data)
        except Exception as e:
            print(f"Erreur AnimEmbed: {e}")
        
        return []
    
    # ==================== JEUX VIDÉO ====================
    
    def search_rawg(self, query: str) -> List[MediaInfo]:
        """Recherche via RAWG Video Game Database API."""
        if self.key_manager.needs_key("rawg"):
            return []
        
        api_key = self.key_manager.get_key("rawg")
        base_url = "https://api.rawg.io/api/games"
        
        params = {
            "key": api_key,
            "search": query,
            "page_size": 20
        }
        
        try:
            response = self.session.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_rawg_results(data.get("results", []))
        except Exception as e:
            print(f"Erreur RAWG: {e}")
        
        return []
    
    def search_igdb(self, query: str) -> List[MediaInfo]:
        """Recherche via IGDB API (Twitch)."""
        if self.key_manager.needs_key("igdb"):
            return []
        
        api_key = self.key_manager.get_key("igdb")
        base_url = "https://api.igdb.com/v4/games"
        
        headers = {
            "Client-ID": self.key_manager.get_key("igdb_client_id", ""),
            "Authorization": f"Bearer {api_key}"
        }
        
        body = f'search "{query}"; fields name, summary, cover.url, first_release_date, platforms.name, rating, genres.name;'
        
        try:
            response = self.session.post(base_url, headers=headers, data=body)
            if response.status_code == 200:
                data = response.json()
                return self._parse_igdb_results(data)
        except Exception as e:
            print(f"Erreur IGDB: {e}")
        
        return []
    
    # ==================== MÉTHODES DE PARSING ====================
    
    def _parse_omdb_results(self, results: List[Dict]) -> List[MediaInfo]:
        """Parse les résultats OMDb."""
        media_list = []
        for item in results:
            media = MediaInfo(
                title=item.get("Title", ""),
                type=MediaType.MOVIE if item.get("Type") == "movie" else MediaType.TV_SHOW,
                year=self._extract_year(item.get("Year", "")),
                poster_url=item.get("Poster"),
                imdb_id=item.get("imdbID")
            )
            media_list.append(media)
        return media_list
    
    def _parse_tmdb_results(self, results: List[Dict]) -> List[MediaInfo]:
        """Parse les résultats TMDb."""
        media_list = []
        for item in results:
            media_type = MediaType.MOVIE if item.get("media_type") == "movie" else MediaType.TV_SHOW
            media = MediaInfo(
                title=item.get("title") or item.get("name", ""),
                type=media_type,
                year=self._extract_year(item.get("release_date") or item.get("first_air_date", "")),
                synopsis=item.get("overview"),
                poster_url=f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}" if item.get("poster_path") else None,
                rating=item.get("vote_average"),
                genres=[g["name"] for g in item.get("genres", [])],
                release_date=item.get("release_date") or item.get("first_air_date")
            )
            media_list.append(media)
        return media_list
    
    def _parse_tvmaze_results(self, results: List[Dict]) -> List[MediaInfo]:
        """Parse les résultats TVmaze."""
        media_list = []
        for item in results:
            show = item.get("show", {})
            media = MediaInfo(
                title=show.get("name", ""),
                type=MediaType.TV_SHOW,
                synopsis=show.get("summary", "").replace("<p>", "").replace("</p>", "").replace("<b>", "").replace("</b>", ""),
                poster_url=show.get("image", {}).get("medium"),
                rating=show.get("rating", {}).get("average"),
                genres=show.get("genres", []),
                release_date=show.get("premiered")
            )
            media_list.append(media)
        return media_list
    
    def _parse_jikan_results(self, results: List[Dict]) -> List[MediaInfo]:
        """Parse les résultats Jikan."""
        media_list = []
        for item in results:
            anime = item.get("anime", item)  # Pour search vs direct
            media = MediaInfo(
                title=anime.get("title", ""),
                type=MediaType.ANIME,
                year=self._extract_year(anime.get("year", "")),
                synopsis=anime.get("synopsis"),
                poster_url=anime.get("images", {}).get("jpg", {}).get("image_url"),
                rating=anime.get("score"),
                episodes=anime.get("episodes"),
                mal_id=anime.get("mal_id"),
                release_date=anime.get("aired", {}).get("from")
            )
            media_list.append(media)
        return media_list
    
    def _parse_animeapi_results(self, data: Dict) -> List[MediaInfo]:
        """Parse les résultats AnimeAPI."""
        media_list = []
        if isinstance(data, list):
            for item in data:
                media = MediaInfo(
                    title=item.get("title", ""),
                    type=MediaType.ANIME,
                    synopsis=item.get("description"),
                    poster_url=item.get("image"),
                    episodes=item.get("episodes")
                )
                media_list.append(media)
        return media_list
    
    def _parse_animembed_results(self, data: Dict) -> List[MediaInfo]:
        """Parse les résultats AnimEmbed."""
        media_list = []
        if isinstance(data, dict) and "data" in data:
            for item in data["data"]:
                media = MediaInfo(
                    title=item.get("title", ""),
                    type=MediaType.ANIME,
                    synopsis=item.get("description"),
                    poster_url=item.get("image"),
                    episodes=item.get("episodes")
                )
                media_list.append(media)
        return media_list
    
    def _parse_rawg_results(self, results: List[Dict]) -> List[MediaInfo]:
        """Parse les résultats RAWG."""
        media_list = []
        for item in results:
            media = MediaInfo(
                title=item.get("name", ""),
                type=MediaType.VIDEO_GAME,
                synopsis=item.get("description_raw"),
                poster_url=item.get("background_image"),
                rating=item.get("rating"),
                genres=[g["name"] for g in item.get("genres", [])],
                platforms=[p["platform"]["name"] for p in item.get("platforms", [])],
                release_date=item.get("released")
            )
            media_list.append(media)
        return media_list
    
    def _parse_igdb_results(self, results: List[Dict]) -> List[MediaInfo]:
        """Parse les résultats IGDB."""
        media_list = []
        for item in results:
            media = MediaInfo(
                title=item.get("name", ""),
                type=MediaType.VIDEO_GAME,
                synopsis=item.get("summary"),
                poster_url=item.get("cover", {}).get("url"),
                rating=item.get("rating"),
                genres=[g["name"] for g in item.get("genres", [])],
                platforms=[p["name"] for p in item.get("platforms", [])],
                release_date=item.get("first_release_date"),
                igdb_id=item.get("id")
            )
            media_list.append(media)
        return media_list
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extrait l'année d'une chaîne de date."""
        if not date_str:
            return None
        try:
            # Format: "2023", "2023-01-01", "2023 to 2024"
            year = date_str.split("-")[0].split(" ")[0].split("–")[0]
            return int(year) if year.isdigit() else None
        except:
            return None
    
    # ==================== MÉTHODES PRINCIPALES ====================
    
    def search_media(self, query: str, media_type: str = "all") -> List[MediaInfo]:
        """Recherche universelle sur toutes les API disponibles."""
        all_results = []
        
        # Films & Séries
        if media_type in ["all", "movie", "tv"]:
            if not self.key_manager.needs_key("omdb"):
                all_results.extend(self.search_omdb(query, media_type))
            if not self.key_manager.needs_key("tmdb"):
                all_results.extend(self.search_tmdb(query, media_type))
            # TVmaze est toujours disponible (gratuit)
            all_results.extend(self.search_tvmaze(query))
        
        # Animés
        if media_type in ["all", "anime"]:
            # Jikan est toujours disponible (gratuit)
            all_results.extend(self.search_jikan(query, "anime"))
            all_results.extend(self.search_animeapi(query))
            all_results.extend(self.search_animembed(query))
        
        # Mangas
        if media_type in ["all", "manga"]:
            all_results.extend(self.search_jikan(query, "manga"))
        
        # Jeux vidéo
        if media_type in ["all", "game"]:
            if not self.key_manager.needs_key("rawg"):
                all_results.extend(self.search_rawg(query))
            if not self.key_manager.needs_key("igdb"):
                all_results.extend(self.search_igdb(query))
        
        # Dédoublonner les résultats
        return self._deduplicate_results(all_results)
    
    def _deduplicate_results(self, results: List[MediaInfo]) -> List[MediaInfo]:
        """Élimine les doublons basés sur le titre."""
        seen_titles = set()
        unique_results = []
        
        for media in results:
            title_key = media.title.lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_results.append(media)
        
        return unique_results
    
    def get_missing_keys_info(self) -> Dict[str, str]:
        """Retourne les informations sur les clés API manquantes."""
        missing_info = {}
        
        if self.key_manager.needs_key("omdb"):
            missing_info["omdb"] = "OMDb API - Films & Séries (gratuit avec clé)\nhttps://www.omdbapi.com/"
        
        if self.key_manager.needs_key("tmdb"):
            missing_info["tmdb"] = "TMDb API - Films & Séries (gratuit avec clé)\nhttps://developers.themoviedb.org/"
        
        if self.key_manager.needs_key("rawg"):
            missing_info["rawg"] = "RAWG API - Jeux Vidéo (gratuit avec clé)\nhttps://rawg.io/apidocs"
        
        if self.key_manager.needs_key("igdb"):
            missing_info["igdb"] = "IGDB API - Jeux Vidéo (gratuit avec clé)\nhttps://api-docs.igdb.com/"
        
        return missing_info
