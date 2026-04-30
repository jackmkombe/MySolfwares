"""
MediaNexus PRO v3.0 - Moteur de Synchronisation
Gestion avancée du scan avec progression, annulation et états.
"""
import threading
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from core.translation import TranslationService

class SyncState(Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    FETCHING = "fetching"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

@dataclass
class SyncProgress:
    state: SyncState
    current_item: str
    total_items: int
    processed_items: int
    success_count: int
    error_count: int
    current_source: str

    @property
    def percentage(self) -> float:
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100

class SyncEngine:
    """
    Moteur de synchronisation intelligent.
    Gère le scan, le fetch et la progression de manière asynchrone.
    """

    def __init__(self, db_manager, api_manager, cache_manager, matching_engine, monitor=None):
        self.db = db_manager
        self.api = api_manager
        self.cache = cache_manager
        self.matching = matching_engine
        self.monitor = monitor
        
        self._cancel_flag = threading.Event()
        self._progress = SyncProgress(
            state=SyncState.IDLE,
            current_item="",
            total_items=0,
            processed_items=0,
            success_count=0,
            error_count=0,
            current_source=""
        )
        self._progress_callback: Optional[Callable[[SyncProgress], None]] = None
        self._completion_callback: Optional[Callable[[], None]] = None

    def set_progress_callback(self, callback: Callable[[SyncProgress], None]):
        """Définit le callback de progression (appelé depuis le thread UI)."""
        self._progress_callback = callback

    def set_completion_callback(self, callback: Callable[[], None]):
        """Définit le callback de fin de synchronisation."""
        self._completion_callback = callback

    def _notify_progress(self):
        """Notifie l'UI de la progression."""
        if self._progress_callback:
            self._progress_callback(self._progress)

    def cancel(self):
        """Demande l'annulation de la synchronisation."""
        self._cancel_flag.set()

    def start_sync(self, library: Dict, confidence_threshold: float = 0.65):
        """
        Démarre la synchronisation d'une bibliothèque dans un thread séparé.
        """
        self._cancel_flag.clear()
        thread = threading.Thread(
            target=self._sync_library,
            args=(library, confidence_threshold),
            daemon=True
        )
        thread.start()

    def _sync_library(self, library: Dict, threshold: float):
        """
        Logique principale de synchronisation.
        """
        try:
            lib_id = library['id']
            lib_type = library['type']
            lib_lang = library.get('preferred_lang', 'fr-FR')
            lib_source = library.get('source', 'Automatique')
            lib_translate = bool(library.get('translate_synopsis', 1))
            paths = json.loads(library['paths'])

            # Phase 1 : Scan des fichiers locaux et détection des suppressions
            self._progress.state = SyncState.SCANNING
            self._progress.current_source = "Système de fichiers"
            self._notify_progress()

            # Récupérer les items existants en base
            existing_items = self.db.get_items(lib_id)
            existing_paths = {item['local_path'] for item in existing_items}
            
            all_entries = []
            for path_str in paths:
                path = Path(path_str)
                if path.exists():
                    for entry in path.iterdir():
                        if self._cancel_flag.is_set():
                            self._progress.state = SyncState.CANCELLED
                            self._notify_progress()
                            return

                        # Filtrer par type
                        if entry.is_dir() or self._is_valid_media(entry, lib_type):
                            if not self.db.item_exists(lib_id, entry.name):
                                all_entries.append(entry)

            # Détecter les items supprimés (présents en base mais plus dans les fichiers)
            current_paths = {str(entry) for entry in all_entries}
            deleted_items = existing_paths - current_paths
            
            # Déplacer les items supprimés vers l'historique
            for deleted_path in deleted_items:
                deleted_item = next((item for item in existing_items if item['local_path'] == deleted_path), None)
                if deleted_item:
                    self.db.delete_item(deleted_item['id'])

            self._progress.total_items = len(all_entries)
            self._progress.processed_items = 0
            self._progress.success_count = 0
            self._progress.error_count = 0

            # Phase 2 : Fetch des métadonnées
            self._progress.state = SyncState.FETCHING
            self._notify_progress()

            for entry in all_entries:
                if self._cancel_flag.is_set():
                    self._progress.state = SyncState.CANCELLED
                    self._notify_progress()
                    return

                self._progress.current_item = entry.name
                self._notify_progress()

                # Insertion de l'item en base (statut pending)
                item_id = self.db.insert_item(lib_id, entry.name, str(entry))

                # Nettoyage du nom et extraction de l'année
                clean_title, year = self.matching.clean_title(entry.name)

                # Vérification du cache
                cached = self.cache.get(lib_type, clean_title)
                if cached:
                    self._progress.current_source = "Cache local"
                    metadata = self._extract_metadata(cached, lib_type, threshold, clean_title, year, lib_lang, source=lib_source, translate=lib_translate)
                else:
                    # Appel API réel
                    self._progress.current_source = lib_source if lib_source != "Automatique" else self._get_source_name(lib_type)
                    
                    import time
                    start_time = time.time()
                    try:
                        api_response = self.api.fetch(clean_title, lib_type, lib_lang, source=lib_source)
                        duration = time.time() - start_time
                        
                        if self.monitor:
                            self.monitor.log_request(self._progress.current_source, lib_type, api_response is not None, duration)
                        
                        if api_response:
                            # Mise en cache
                            self.cache.set(lib_type, clean_title, api_response)
                            metadata = self._extract_metadata(api_response, lib_type, threshold, clean_title, year, lib_lang, source=lib_source, translate=lib_translate)
                        else:
                            metadata = None
                    except Exception as e:
                        if self.monitor:
                            self.monitor.log_request(self._progress.current_source, lib_type, False, time.time() - start_time, str(e))
                        metadata = None

                # Mise à jour de l'item
                if metadata:
                    self.db.update_item_metadata(item_id, metadata)
                    self._progress.success_count += 1
                else:
                    self.db.set_item_error(item_id)
                    self._progress.error_count += 1
                    
                    # Ajouter à l'historique même si non synchronisé (titre seul)
                    clean_title, _ = self.matching.clean_title(entry.name)
                    self.db.add_to_historique(lib_id, entry.name, str(entry), clean_title)

                self._progress.processed_items += 1
                self._notify_progress()

            # Terminé
            self._progress.state = SyncState.COMPLETED
            self._notify_progress()

            if self._completion_callback:
                self._completion_callback()

        except Exception as e:
            self._progress.state = SyncState.ERROR
            self._progress.current_item = str(e)
            self._notify_progress()

    def _is_valid_media(self, path: Path, media_type: str) -> bool:
        """Vérifie si le fichier correspond au type de média."""
        ext = path.suffix.lower()
        valid_extensions = {
            "Films / Séries": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
            "Animés": [".mp4", ".mkv", ".avi"],
            "Jeux PC": [".exe", ".lnk"]
        }
        return ext in valid_extensions.get(media_type, [])

    def _get_source_name(self, media_type: str) -> str:
        """Retourne le nom de la source API."""
        sources = {
            "Films / Séries": "TMDB",
            "Animés": "Jikan (MyAnimeList)",
            "Jeux PC": "RAWG"
        }
        return sources.get(media_type, "Unknown")

    def _extract_metadata(self, response: Dict, media_type: str, threshold: float,
                          query_title: str, query_year: Optional[int], lang: str = "fr-FR", 
                          source: str = None, translate: bool = False) -> Optional[Dict]:
        """
        Extrait et structure les métadonnées de manière exhaustive.
        Effectue un second appel API pour obtenir les détails complets (saisons, épisodes, etc).
        """
        # 1. Sélection du meilleur candidat parmi les résultats de recherche
        candidates = response.get('results', response.get('data', [response]))
        if not isinstance(candidates, list): candidates = [candidates]
        
        best, score = self.matching.select_best_match(query_title, query_year, candidates, media_type, threshold)

        if not best:
            return None

        # 2. Récupération des détails complets (Deep Fetching)
        detailed_item = best
        try:
            item_id = str(best.get('id') or best.get('mal_id'))
            
            # Identifier la source réelle du candidat (utile si Multi-Sources est actif)
            candidate_source = best.get('_api_source') or source

            if media_type == "Films / Séries":
                spec_type = best.get('media_type', 'movie') # 'movie' or 'tv'
                res = self.api.get_details(item_id, media_type, lang, specific_type=spec_type, source=candidate_source)
                if res: detailed_item = res
            elif media_type == "Animés":
                res = self.api.get_details(item_id, media_type, lang, source=candidate_source)
                if res: detailed_item = res.get('data', res)
        except Exception as e:
            print(f"Deep Fetch Error: {e}")

        # 3. Traduction si nécessaire
        if translate and lang.startswith("fr"):
            summary = detailed_item.get('overview') or detailed_item.get('synopsis') or detailed_item.get('summary')
            if summary:
                # Si le texte semble être en anglais ou autre, on tente la traduction
                translated = TranslationService.translate(summary, target_lang="fr")
                if translated:
                    if 'overview' in detailed_item: detailed_item['overview'] = translated
                    if 'synopsis' in detailed_item: detailed_item['synopsis'] = translated
                    if 'summary' in detailed_item: detailed_item['summary'] = translated

        # 4. Construction des métadonnées finales
        if media_type == "Films / Séries":
            return self._extract_tmdb_metadata(detailed_item, score, response)
        elif media_type == "Animés":
            return self._extract_jikan_metadata(detailed_item, score, response)
        elif media_type == "Jeux PC":
            return self._extract_rawg_metadata(detailed_item, score, response)

        return None

    def _extract_tmdb_metadata(self, item: Dict, score: float, raw: Dict) -> Dict:
        return {
            "title": item.get('title') or item.get('name'),
            "original_title": item.get('original_title') or item.get('original_name'),
            "summary": item.get('overview'),
            "poster_url": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
            "backdrop_url": f"https://image.tmdb.org/t/p/w1280{item.get('backdrop_path')}" if item.get('backdrop_path') else None,
            "release_date": item.get('release_date') or item.get('first_air_date'),
            "release_year": int((item.get('release_date') or item.get('first_air_date') or '0000')[:4]) or None,
            "score": item.get('vote_average'),
            "vote_count": item.get('vote_count'),
            "genres": [g.get('name') for g in item.get('genres', [])],
            "seasons_count": item.get('number_of_seasons'),
            "episodes_count": item.get('number_of_episodes'),
            "airing_status": "En cours" if item.get('status') == "Returning Series" else "Terminé",
            "api_source": "tmdb",
            "api_id": str(item.get('id')),
            "match_confidence": score,
            "raw_response": raw
        }

    def _extract_jikan_metadata(self, item: Dict, score: float, raw: Dict) -> Dict:
        return {
            "title": item.get('title_english') or item.get('title'),
            "original_title": item.get('title_japanese'),
            "summary": item.get('synopsis'),
            "poster_url": item.get('images', {}).get('jpg', {}).get('large_image_url'),
            "release_date": str(item.get('year', '')),
            "release_year": item.get('year'),
            "score": item.get('score'),
            "vote_count": item.get('scored_by'),
            "genres": [g.get('name') for g in item.get('genres', [])],
            "episodes_count": item.get('episodes'),
            "episode_duration": item.get('duration'),
            "airing_status": "En cours" if item.get('airing') else "Terminé",
            "api_source": "jikan",
            "api_id": str(item.get('mal_id')),
            "match_confidence": score,
            "raw_response": raw
        }

    def _extract_rawg_metadata(self, item: Dict, score: float, raw: Dict) -> Dict:
        return {
            "title": item.get('name'),
            "summary": item.get('description'),
            "poster_url": item.get('background_image'),
            "release_date": item.get('released'),
            "release_year": int(item.get('released', '0000')[:4]) if item.get('released') else None,
            "score": item.get('rating'),
            "vote_count": item.get('ratings_count'),
            "genres": [g.get('name') for g in item.get('genres', [])],
            "airing_status": "Disponible",
            "api_source": "rawg",
            "api_id": str(item.get('id')),
            "match_confidence": score,
            "raw_response": raw
        }
