"""
MediaNexus PRO v3.2 - Synchroniseur avec API
Intégration des API externes pour le fetching automatique des informations
"""

import os
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Import absolu pour éviter les erreurs de packages
sys.path.insert(0, str(Path(__file__).parent.parent))
from api.media_apis import MediaAPIManager, MediaInfo, MediaType
from core.database import DatabaseManager

class MediaSynchronizer:
    """Synchroniseur principal avec intégration API."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.api_manager = MediaAPIManager()
        self.sync_stats = {
            "total": 0,
            "updated": 0,
            "errors": 0,
            "missing_info": 0
        }
    
    def synchronize_library(self, library_id: int, progress_callback=None) -> Dict:
        """Synchronise une bibliothèque complète avec les API."""
        library = self.db.get_library(library_id)
        if not library:
            return {"error": "Bibliothèque non trouvée"}
        
        # Réinitialiser les statistiques
        self.sync_stats = {"total": 0, "updated": 0, "errors": 0, "missing_info": 0}
        
        # Récupérer tous les éléments de la bibliothèque
        items = self.db.get_library_items(library_id)
        total_items = len(items)
        
        if progress_callback:
            progress_callback(0, total_items, "Initialisation de la synchronisation...")
        
        # Vérifier les clés API manquantes
        missing_keys = self.api_manager.get_missing_keys_info()
        if missing_keys:
            print("⚠️  Clés API manquantes pour une synchronisation optimale:")
            for api_name, info in missing_keys.items():
                print(f"  • {api_name.upper()}: {info.split(chr(10))[0]}")
            print("\n🔄 Synchronisation avec les API gratuites disponibles...")
        
        # Traiter chaque élément
        for i, item in enumerate(items):
            try:
                if progress_callback:
                    progress_callback(i, total_items, f"Synchronisation: {item.get('title', 'Sans titre')}")
                
                # Synchroniser l'élément
                result = self._sync_item(item)
                
                if result["updated"]:
                    self.sync_stats["updated"] += 1
                elif result["error"]:
                    self.sync_stats["errors"] += 1
                elif result["missing_info"]:
                    self.sync_stats["missing_info"] += 1
                
                self.sync_stats["total"] += 1
                
                # Petite pause pour éviter les rate limits
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Erreur lors de la synchronisation de {item.get('title', 'Sans titre')}: {e}")
                self.sync_stats["errors"] += 1
                self.sync_stats["total"] += 1
        
        # Mettre à jour la date de dernière synchronisation
        self.db.update_library_sync_date(library_id)
        
        return {
            "success": True,
            "stats": self.sync_stats,
            "library": library,
            "missing_keys": missing_keys
        }
    
    def _sync_item(self, item: Dict) -> Dict:
        """Synchronise un élément individuel."""
        title = item.get('title', '').strip()
        if not title:
            return {"error": True, "message": "Titre manquant"}
        
        # Déterminer le type de média
        media_type = self._detect_media_type(item)
        
        # Rechercher via les API
        api_results = self.api_manager.search_media(title, media_type)
        
        if not api_results:
            return {"missing_info": True, "message": "Aucune information trouvée"}
        
        # Trouver le meilleur résultat
        best_match = self._find_best_match(title, api_results)
        
        if not best_match:
            return {"missing_info": True, "message": "Aucune correspondance trouvée"}
        
        # Mettre à jour l'élément avec les informations API
        updated_data = {
            "title": best_match.title,
            "synopsis": best_match.synopsis or item.get('synopsis', ''),
            "poster_url": best_match.poster_url or item.get('poster_url', ''),
            "rating": best_match.rating or item.get('rating', 0),
            "year": best_match.year or item.get('year'),
            "genres": best_match.genres or item.get('genres', []),
            "director": best_match.director or item.get('director', ''),
            "duration": best_match.duration or item.get('duration', ''),
            "episodes": best_match.episodes or item.get('episodes'),
            "seasons": best_match.seasons or item.get('seasons'),
            "platform": best_match.platform or item.get('platform', ''),
            "release_date": best_match.release_date or item.get('release_date', ''),
            "imdb_id": best_match.imdb_id or item.get('imdb_id', ''),
            "mal_id": best_match.mal_id or item.get('mal_id', ''),
            "igdb_id": best_match.igdb_id or item.get('igdb_id', ''),
            "last_sync": datetime.now().isoformat(),
            "api_sources": self._get_api_sources(best_match)
        }
        
        # Mettre à jour dans la base de données
        success = self.db.update_item(item['id'], updated_data)
        
        return {
            "updated": success,
            "data": updated_data,
            "api_match": best_match.title
        }
    
    def _detect_media_type(self, item: Dict) -> str:
        """Détecte le type de média d'un élément."""
        # Basé sur les métadonnées existantes
        if item.get('mal_id') or 'anime' in item.get('genres', []):
            return "anime"
        elif item.get('igdb_id') or 'game' in item.get('genres', []):
            return "game"
        elif item.get('seasons') or item.get('episodes'):
            return "tv"  # Série TV
        else:
            return "movie"  # Film par défaut
    
    def _find_best_match(self, title: str, results: List[MediaInfo]) -> Optional[MediaInfo]:
        """Trouve la meilleure correspondance pour un titre."""
        if not results:
            return None
        
        # Score de similarité simple
        best_score = 0
        best_match = None
        
        title_lower = title.lower().strip()
        
        for result in results:
            result_title = result.title.lower().strip()
            
            # Calculer le score de similarité
            score = 0
            
            # Titre exact
            if result_title == title_lower:
                score += 100
            
            # Titre contient
            elif title_lower in result_title or result_title in title_lower:
                score += 80
            
            # Mots communs
            else:
                title_words = set(title_lower.split())
                result_words = set(result_title.split())
                common_words = title_words & result_words
                
                if title_words:
                    score += (len(common_words) / len(title_words)) * 60
            
            # Bonus année si disponible
            if result.year:
                score += 10
            
            # Meilleur score
            if score > best_score:
                best_score = score
                best_match = result
        
        return best_match if best_score > 30 else None  # Seuil minimum
    
    def _get_api_sources(self, media_info: MediaInfo) -> List[str]:
        """Identifie les sources API utilisées."""
        sources = []
        
        if media_info.imdb_id:
            sources.append("OMDb")
        if media_info.mal_id:
            sources.append("Jikan/MyAnimeList")
        if media_info.igdb_id:
            sources.append("IGDB")
        
        # Détection basée sur les données disponibles
        if media_info.poster_url and "tmdb.org" in media_info.poster_url:
            sources.append("TMDb")
        elif media_info.poster_url and "animembed.com" in str(media_info.poster_url):
            sources.append("AnimEmbed")
        elif media_info.poster_url and "animeapi.skin" in str(media_info.poster_url):
            sources.append("AnimeAPI")
        
        return sources or ["Inconnu"]
    
    def get_sync_recommendations(self, library_id: int) -> Dict:
        """Retourne des recommandations pour améliorer la synchronisation."""
        library = self.db.get_library(library_id)
        if not library:
            return {}
        
        items = self.db.get_library_items(library_id)
        
        # Analyser les éléments sans informations complètes
        incomplete_items = []
        for item in items:
            missing_fields = []
            
            if not item.get('synopsis'):
                missing_fields.append('synopsis')
            if not item.get('poster_url'):
                missing_fields.append('poster')
            if not item.get('rating'):
                missing_fields.append('rating')
            if not item.get('genres'):
                missing_fields.append('genres')
            
            if missing_fields:
                incomplete_items.append({
                    'title': item.get('title', 'Sans titre'),
                    'missing': missing_fields
                })
        
        # Analyser les doublons potentiels
        titles = [item.get('title', '').lower() for item in items]
        duplicates = []
        seen = set()
        
        for i, title in enumerate(titles):
            if title in seen and title not in [d['title'] for d in duplicates]:
                duplicates.append({
                    'title': title,
                    'count': titles.count(title),
                    'indices': [i for i, t in enumerate(titles) if t == title]
                })
            seen.add(title)
        
        # Recommandations
        recommendations = {
            "incomplete_items": incomplete_items[:10],  # Limiter à 10 pour l'affichage
            "potential_duplicates": duplicates[:5],
            "total_items": len(items),
            "completion_rate": (len(items) - len(incomplete_items)) / len(items) * 100 if items else 0,
            "api_status": self.api_manager.get_missing_keys_info()
        }
        
        return recommendations
    
    def manual_search(self, query: str, media_type: str = "all") -> List[Dict]:
        """Recherche manuelle pour l'utilisateur."""
        results = self.api_manager.search_media(query, media_type)
        
        # Convertir en dictionnaires pour l'UI
        ui_results = []
        for media in results:
            ui_result = {
                'title': media.title,
                'type': media.type.value,
                'year': media.year,
                'synopsis': media.synopsis,
                'poster_url': media.poster_url,
                'rating': media.rating,
                'genres': media.genres,
                'director': media.director,
                'duration': media.duration,
                'episodes': media.episodes,
                'seasons': media.seasons,
                'platform': media.platform,
                'release_date': media.release_date,
                'imdb_id': media.imdb_id,
                'mal_id': media.mal_id,
                'igdb_id': media.igdb_id
            }
            ui_results.append(ui_result)
        
        return ui_results
    
    def configure_api_keys(self, keys: Dict[str, str]) -> bool:
        """Configure les clés API."""
        try:
            for api_name, key in keys.items():
                if key.strip():  # Ne pas configurer les clés vides
                    self.api_manager.key_manager.set_key(api_name, key.strip())
            
            print("✅ Clés API configurées avec succès!")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la configuration des clés: {e}")
            return False
    
    def get_api_status(self) -> Dict:
        """Retourne le statut de toutes les API."""
        status = {}
        missing = self.api_manager.get_missing_keys_info()
        
        # API Films & Séries
        status["omdb"] = {
            "name": "OMDb API",
            "description": "Films & Séries",
            "configured": not missing.get("omdb"),
            "free": True,
            "url": "https://www.omdbapi.com/"
        }
        
        status["tmdb"] = {
            "name": "TMDb API",
            "description": "Films & Séries (complet)",
            "configured": not missing.get("tmdb"),
            "free": True,
            "url": "https://developers.themoviedb.org/"
        }
        
        status["tvmaze"] = {
            "name": "TVmaze API",
            "description": "Séries TV (gratuit)",
            "configured": True,  # Toujours disponible
            "free": True,
            "url": "https://www.tvmaze.com/api"
        }
        
        # API Animés
        status["jikan"] = {
            "name": "Jikan API",
            "description": "Animés & Mangas (MyAnimeList)",
            "configured": True,  # Toujours disponible
            "free": True,
            "url": "https://api.jikan.moe/"
        }
        
        status["animeapi"] = {
            "name": "AnimeAPI",
            "description": "Animés (gratuit)",
            "configured": True,  # Toujours disponible
            "free": True,
            "url": "https://animeapi.skin/"
        }
        
        status["animembed"] = {
            "name": "AnimEmbed API",
            "description": "Animés (gratuit)",
            "configured": True,  # Toujours disponible
            "free": True,
            "url": "https://animembed.com/api"
        }
        
        # API Jeux
        status["rawg"] = {
            "name": "RAWG API",
            "description": "Jeux Vidéo",
            "configured": not missing.get("rawg"),
            "free": True,
            "url": "https://rawg.io/apidocs"
        }
        
        status["igdb"] = {
            "name": "IGDB API",
            "description": "Jeux Vidéo (officiel)",
            "configured": not missing.get("igdb"),
            "free": True,
            "url": "https://api-docs.igdb.com/"
        }
        
        return status
