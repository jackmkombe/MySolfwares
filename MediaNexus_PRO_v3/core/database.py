"""
MediaNexus PRO v3.0 - Core Database Module
Gestion SQLite thread-safe avec verrous explicites.
"""
import sqlite3
import threading
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

class DatabaseManager:
    """
    Gestionnaire de base de données thread-safe.
    Utilise un verrou pour éviter les accès concurrents.
    """
    _lock = threading.Lock()

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._local = threading.local()
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Retourne une connexion par thread."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row  # Accès par nom de colonne
        return self._local.conn

    def _initialize_schema(self):
        """Crée le schéma complet de la base de données."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Table des profils utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    avatar_path TEXT,
                    theme TEXT DEFAULT 'dark',
                    password_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Table des bibliothèques (liées aux profils)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS libraries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    source TEXT DEFAULT 'Automatique',
                    translate_synopsis INTEGER DEFAULT 1,
                    paths TEXT NOT NULL,  -- JSON array
                    preferred_lang TEXT DEFAULT 'fr-FR',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
                )
            ''')

            # Migrations : Ajouter les colonnes si elles n'existent pas
            try:
                cursor.execute("SELECT source FROM libraries LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE libraries ADD COLUMN source TEXT DEFAULT 'Automatique'")
                
            try:
                cursor.execute("SELECT translate_synopsis FROM libraries LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE libraries ADD COLUMN translate_synopsis INTEGER DEFAULT 1")

            # Table des items médias (schéma étendu)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS media_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lib_id INTEGER NOT NULL,
                    raw_name TEXT NOT NULL,
                    local_path TEXT NOT NULL,
                    file_hash TEXT,
                    
                    -- Métadonnées principales
                    title TEXT,
                    original_title TEXT,
                    summary TEXT,
                    poster_url TEXT,
                    backdrop_url TEXT,
                    
                    -- Détails temporels
                    release_date TEXT,
                    release_year INTEGER,
                    
                    -- Évaluation
                    score REAL,
                    vote_count INTEGER,
                    
                    -- Classification
                    genres TEXT,  -- JSON array
                    
                    -- Séries / Animés
                    seasons_count INTEGER,
                    episodes_count INTEGER,
                    episode_duration INTEGER,
                    airing_status TEXT,  -- 'En cours', 'Terminé', 'Annulé'
                    
                    -- Synchronisation
                    api_source TEXT,  -- 'tmdb', 'jikan', 'rawg'
                    api_id TEXT,
                    match_confidence REAL,
                    raw_api_response TEXT,  -- JSON brut pour recalibrage
                    last_sync_at TIMESTAMP,
                    sync_status TEXT DEFAULT 'pending',  -- 'pending', 'synced', 'error', 'manual'
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lib_id) REFERENCES libraries(id) ON DELETE CASCADE
                )
            ''')

            # Table de cache API avec expiration
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_cache (
                    cache_key TEXT PRIMARY KEY,
                    response_json TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')

            # Table d'historique des items (conservation même après suppression)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historique_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lib_id INTEGER NOT NULL,
                    raw_name TEXT NOT NULL,
                    local_path TEXT,
                    
                    -- Informations minimales si non synchronisé
                    title_only TEXT,  -- Titre extrait du nom de fichier si non sync
                    
                    -- Métadonnées complètes si synchronisé
                    full_title TEXT,
                    original_title TEXT,
                    summary TEXT,
                    poster_url TEXT,
                    backdrop_url TEXT,
                    release_date TEXT,
                    release_year INTEGER,
                    score REAL,
                    vote_count INTEGER,
                    genres TEXT,
                    seasons_count INTEGER,
                    episodes_count INTEGER,
                    episode_duration INTEGER,
                    airing_status TEXT,
                    api_source TEXT,
                    api_id TEXT,
                    match_confidence REAL,
                    raw_api_response TEXT,
                    
                    -- Statut et suivi
                    was_synced BOOLEAN DEFAULT 0,  -- 0 = titre seul, 1 = synchronisé
                    sync_status_before_delete TEXT,  -- Statut avant suppression
                    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_sync_at TIMESTAMP,
                    
                    FOREIGN KEY (lib_id) REFERENCES libraries(id) ON DELETE CASCADE
                )
            ''')

            # Index pour optimisation des requêtes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_lib ON media_items(lib_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_status ON media_items(sync_status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_expiry ON api_cache(expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_historique_lib ON historique_items(lib_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_historique_deleted ON historique_items(deleted_at)')

            conn.commit()

    # --- OPÉRATIONS PROFILS ---
    def create_profile(self, name: str, theme: str = "dark", password: str = None) -> int:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Hasher le mot de passe si fourni avec un sel
            password_hash = None
            if password:
                import hashlib
                import secrets
                import base64
                
                # Génération d'un sel unique de 16 octets
                salt = secrets.token_bytes(16)
                # Utilisation de PBKDF2 avec HMAC-SHA256 (plusieurs itérations)
                dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
                # Stockage format: salt:hash (en base64 pour le stockage texte)
                password_hash = f"{base64.b64encode(salt).decode()}:{base64.b64encode(dk).decode()}"
            
            cursor.execute(
                "INSERT INTO profiles (name, theme, password_hash) VALUES (?, ?, ?)",
                (name, theme, password_hash)
            )
            conn.commit()
            return cursor.lastrowid

    def verify_password(self, profile_id: int, password: str) -> bool:
        """Vérifie si le mot de passe correspond au profil."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM profiles WHERE id=?", (profile_id,))
            row = cursor.fetchone()
            
            if not row or not row['password_hash']:
                return True if not password else False
                
            stored_hash = row['password_hash']
            
            # Gestion de l'ancien format (simple SHA256) vs nouveau (salt:hash)
            if ":" not in stored_hash:
                import hashlib
                return stored_hash == hashlib.sha256(password.encode()).hexdigest()
            
            import hashlib
            import base64
            import secrets
            
            try:
                salt_b64, hash_b64 = stored_hash.split(":")
                salt = base64.b64decode(salt_b64)
                target_hash = base64.b64decode(hash_b64)
                
                # Re-calcul du hash avec le sel extrait
                dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
                return secrets.compare_digest(dk, target_hash)
            except Exception:
                return False

    def get_profiles(self) -> List[Dict]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def delete_profile(self, profile_id: int):
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM profiles WHERE id=?", (profile_id,))
            conn.commit()

    # --- OPÉRATIONS BIBLIOTHÈQUES ---
    def create_library(self, profile_id: int, name: str, media_type: str, paths: List[str], lang: str = "fr-FR") -> int:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO libraries (profile_id, name, type, paths, preferred_lang) VALUES (?, ?, ?, ?, ?)",
                (profile_id, name, media_type, json.dumps(paths), lang)
            )
            conn.commit()
            return cursor.lastrowid

    def get_libraries(self, profile_id: int) -> List[Dict]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM libraries WHERE profile_id=? ORDER BY name", (profile_id,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_library(self, lib_id: int):
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM libraries WHERE id=?", (lib_id,))
            conn.commit()

    def update_library(self, lib_id: int, name: str, media_type: str, source: str, lang: str, translate: bool):
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE libraries SET 
                    name=?, type=?, source=?, preferred_lang=?, translate_synopsis=?
                WHERE id=?
            ''', (name, media_type, source, lang, 1 if translate else 0, lib_id))
            conn.commit()

    # --- OPÉRATIONS ITEMS ---
    def get_items(self, lib_id: int, status: str = None) -> List[Dict]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM media_items WHERE lib_id=? AND sync_status=? ORDER BY title", (lib_id, status))
            else:
                cursor.execute("SELECT * FROM media_items WHERE lib_id=? ORDER BY title", (lib_id,))
            return [dict(row) for row in cursor.fetchall()]

    def item_exists(self, lib_id: int, raw_name: str) -> bool:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM media_items WHERE lib_id=? AND raw_name=?", (lib_id, raw_name))
            return cursor.fetchone() is not None

    def insert_item(self, lib_id: int, raw_name: str, local_path: str) -> int:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO media_items (lib_id, raw_name, local_path, sync_status) VALUES (?, ?, ?, 'pending')",
                (lib_id, raw_name, local_path)
            )
            conn.commit()
            return cursor.lastrowid

    def update_item_metadata(self, item_id: int, metadata: Dict):
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE media_items SET
                    title=?, original_title=?, summary=?, poster_url=?, backdrop_url=?,
                    release_date=?, release_year=?, score=?, vote_count=?, genres=?,
                    seasons_count=?, episodes_count=?, episode_duration=?, airing_status=?,
                    api_source=?, api_id=?, match_confidence=?, raw_api_response=?,
                    last_sync_at=CURRENT_TIMESTAMP, sync_status='synced'
                WHERE id=?
            ''', (
                metadata.get('title'), metadata.get('original_title'), metadata.get('summary'),
                metadata.get('poster_url'), metadata.get('backdrop_url'),
                metadata.get('release_date'), metadata.get('release_year'),
                metadata.get('score'), metadata.get('vote_count'),
                json.dumps(metadata.get('genres', [])),
                metadata.get('seasons_count'), metadata.get('episodes_count'),
                metadata.get('episode_duration'), metadata.get('airing_status'),
                metadata.get('api_source'), metadata.get('api_id'),
                metadata.get('match_confidence'), json.dumps(metadata.get('raw_response', {})),
                item_id
            ))
            conn.commit()

    def set_item_error(self, item_id: int):
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE media_items SET sync_status='error' WHERE id=?", (item_id,))
            conn.commit()

    def delete_item(self, item_id: int):
        """Supprime un item en le déplaçant dans l'historique."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Récupérer les données de l'item avant suppression
            cursor.execute("SELECT * FROM media_items WHERE id=?", (item_id,))
            item = cursor.fetchone()
            
            if item:
                item_dict = dict(item)
                
                # Insérer dans l'historique
                cursor.execute('''
                    INSERT INTO historique_items (
                        lib_id, raw_name, local_path, title_only, full_title, original_title,
                        summary, poster_url, backdrop_url, release_date, release_year, score,
                        vote_count, genres, seasons_count, episodes_count, episode_duration,
                        airing_status, api_source, api_id, match_confidence, raw_api_response,
                        was_synced, sync_status_before_delete, last_sync_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_dict['lib_id'], item_dict['raw_name'], item_dict['local_path'],
                    item_dict['title'] if item_dict['title'] else item_dict['raw_name'],
                    item_dict['title'], item_dict['original_title'], item_dict['summary'],
                    item_dict['poster_url'], item_dict['backdrop_url'], item_dict['release_date'],
                    item_dict['release_year'], item_dict['score'], item_dict['vote_count'],
                    item_dict['genres'], item_dict['seasons_count'], item_dict['episodes_count'],
                    item_dict['episode_duration'], item_dict['airing_status'], item_dict['api_source'],
                    item_dict['api_id'], item_dict['match_confidence'], item_dict['raw_api_response'],
                    1 if item_dict['sync_status'] == 'synced' else 0,
                    item_dict['sync_status'], item_dict['last_sync_at']
                ))
                
                # Supprimer l'item original
                cursor.execute("DELETE FROM media_items WHERE id=?", (item_id,))
            
            conn.commit()

    # --- OPÉRATIONS HISTORIQUE ---
    def add_to_historique(self, lib_id: int, raw_name: str, local_path: str = None, title_only: str = None):
        """Ajoute un élément non synchronisé à l'historique."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO historique_items (
                    lib_id, raw_name, local_path, title_only, was_synced, sync_status_before_delete
                ) VALUES (?, ?, ?, ?, 0, 'non_sync')
            ''', (lib_id, raw_name, local_path, title_only or raw_name))
            conn.commit()

    def get_historique(self, lib_id: int, limit: int = 100) -> List[Dict]:
        """Récupère l'historique d'une bibliothèque."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM historique_items 
                WHERE lib_id=? 
                ORDER BY deleted_at DESC 
                LIMIT ?
            ''', (lib_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_historique_stats(self, lib_id: int) -> Dict:
        """Retourne les statistiques de l'historique."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN was_synced = 1 THEN 1 END) as synced_count,
                    COUNT(CASE WHEN was_synced = 0 THEN 1 END) as non_synced_count,
                    COUNT(CASE WHEN sync_status_before_delete = 'error' THEN 1 END) as error_count
                FROM historique_items WHERE lib_id=?
            ''', (lib_id,))
            row = cursor.fetchone()
            return dict(row) if row else {"total": 0, "synced_count": 0, "non_synced_count": 0, "error_count": 0}

    def clear_historique(self, lib_id: int, older_than_days: int = 90):
        """Nettoie l'historique plus ancien que X jours."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM historique_items 
                WHERE lib_id=? AND deleted_at < datetime('now', '-' || ? || ' days')
            ''', (lib_id, older_than_days))
            conn.commit()
            return cursor.rowcount

    # --- OPÉRATIONS CACHE ---
    def get_cached(self, cache_key: str) -> Optional[Dict]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT response_json FROM api_cache WHERE cache_key=? AND expires_at > CURRENT_TIMESTAMP",
                (cache_key,)
            )
            row = cursor.fetchone()
            return json.loads(row['response_json']) if row else None

    def set_cache(self, cache_key: str, response: Dict, source: str, expiry_days: int = 30):
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO api_cache (cache_key, response_json, source, expires_at)
                VALUES (?, ?, ?, datetime('now', '+' || ? || ' days'))
            ''', (cache_key, json.dumps(response), source, expiry_days))
            conn.commit()

    def clear_expired_cache(self):
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM api_cache WHERE expires_at < CURRENT_TIMESTAMP")
            conn.commit()
