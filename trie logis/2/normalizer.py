"""
SmartSort - Normalizer Module
Déterministe pipeline pour l'extraction et la canonicalisation de métadonnées
"""

import re
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class NormalizedData:
    """Structure de sortie pour les données normalisées"""
    root_name: str
    season: Optional[int] = None
    episode: Optional[int] = None
    year: Optional[int] = None
    resolution: Optional[str] = None
    is_valid: bool = True
    original_name: str = ""


class Normalizer:
    """
    Moteur de normalisation déterministe pour noms de répertoires
    Implémente un pipeline en 3 étapes : Extraction -> Nettoyage -> Canonicalisation
    """
    
    # Patterns d'extraction (Étape 1)
    SEASON_PATTERN = re.compile(r'(?<![a-z0-9])[Ss](\d{1,2})(?!\d)', re.IGNORECASE)
    EPISODE_PATTERN = re.compile(r'(?<![a-z0-9])[Ee][Pp]?\s*(\d{1,3})(?!\d)', re.IGNORECASE)
    SEASON_EPISODE_PATTERN = re.compile(r'(?<![a-z0-9])[Ss]\d{1,2}[Ee]\d{1,3}(?!\d)', re.IGNORECASE)
    YEAR_PATTERN = re.compile(r'(?<![a-z0-9])(19\d{2}|20\d{2})(?!\d)', re.IGNORECASE)
    RESOLUTION_PATTERN = re.compile(r'(?<![a-z0-9])(2160p|4k|2k|1080p|720p|480p)(?!\d)', re.IGNORECASE)
    
    # Blacklist de termes à supprimer (Étape 2)
    NOISE_TERMS = [
        r'(?<![a-z0-9])x264(?![a-z0-9])', r'(?<![a-z0-9])x265(?![a-z0-9])', 
        r'(?<![a-z0-9])HEVC(?![a-z0-9])', r'(?<![a-z0-9])H\.264(?![a-z0-9])', 
        r'(?<![a-z0-9])H\.265(?![a-z0-9])', r'(?<![a-z0-9])BluRay(?![a-z0-9])', 
        r'(?<![a-z0-9])Blu-Ray(?![a-z0-9])', r'(?<![a-z0-9])WEB-DL(?![a-z0-9])', 
        r'(?<![a-z0-9])WEBDL(?![a-z0-9])', r'(?<![a-z0-9])WEB(?![a-z0-9])',
        r'(?<![a-z0-9])Remux(?![a-z0-9])', r'(?<![a-z0-9])Dual(?![a-z0-9])', 
        r'(?<![a-z0-9])Multi(?![a-z0-9])', r'(?<![a-z0-9])VOSTFR(?![a-z0-9])', 
        r'(?<![a-z0-9])VF(?![a-z0-9])', r'(?<![a-z0-9])AAC(?![a-z0-9])', 
        r'(?<![a-z0-9])DTS(?![a-z0-9])', r'(?<![a-z0-9])AC3(?![a-z0-9])', 
        r'(?<![a-z0-9])DD5\.1(?![a-z0-9])', r'(?<![a-z0-9])Atmos(?![a-z0-9])',
        r'(?<![a-z0-9])Stream(?![a-z0-9])', r'(?<![a-z0-9])HDR(?![a-z0-9])', 
        r'(?<![a-z0-9])SDR(?![a-z0-9])', r'(?<![a-z0-9])DOLBY(?![a-z0-9])',
        r'\[.*?\]', r'\(.*?\)',  # Supprime tout entre crochets/parenthèses
        r'(?<![a-z0-9])REPACK(?![a-z0-9])', r'(?<![a-z0-9])PROPER(?![a-z0-9])', 
        r'(?<![a-z0-9])REMAST\w*(?![a-z0-9])',
        r'(?<![a-z0-9])UNCUT(?![a-z0-9])', r'(?<![a-z0-9])EXTENDED(?![a-z0-9])', 
        r'(?<![a-z0-9])DIRECTOR\w*(?![a-z0-9])',
        r'(?<![a-z0-9])FRENCH(?![a-z0-9])', r'(?<![a-z0-9])ENGLISH(?![a-z0-9])', 
        r'(?<![a-z0-9])TRUEFRENCH(?![a-z0-9])',
        r'(?<![a-z0-9])DKB(?![a-z0-9])', r'(?<![a-z0-9])YGG(?![a-z0-9])', 
        r'(?<![a-z0-9])RAR\w*(?![a-z0-9])'
    ]
    
    # Patterns de nettoyage pour caractères spéciaux
    SPECIAL_CHARS_PATTERN = re.compile(r'[._\-\+]+')
    MULTIPLE_SPACES_PATTERN = re.compile(r'\s{2,}')
    
    def __init__(self):
        """Compile les patterns de blacklist pour performance"""
        self.noise_regex = re.compile('|'.join(self.NOISE_TERMS), re.IGNORECASE)
    
    def preprocess(self, name: str) -> NormalizedData:
        """
        Pipeline complet de normalisation
        
        Args:
            name: Nom du répertoire à normaliser
            
        Returns:
            NormalizedData: Objet structuré avec métadonnées extraites
        """
        if not name or not name.strip():
            return NormalizedData(root_name="", is_valid=False, original_name=name)
        
        original = name
        
        # ÉTAPE 1 : Extraction de métadonnées
        season = self._extract_season(name)
        episode = self._extract_episode(name)
        year = self._extract_year(name)
        resolution = self._extract_resolution(name)
        
        # ÉTAPE 2 : Nettoyage du bruit
        cleaned = self._remove_noise(name)
        
        # ÉTAPE 3 : Canonicalisation
        canonical = self._canonicalize(cleaned)
        
        # Validation
        is_valid = len(canonical) >= 2  # Au moins 2 caractères
        
        return NormalizedData(
            root_name=canonical,
            season=season,
            episode=episode,
            year=year,
            resolution=resolution,
            is_valid=is_valid,
            original_name=original
        )
    
    def _extract_season(self, name: str) -> Optional[int]:
        """Extrait le numéro de saison (S01, s02, etc.)"""
        match = self.SEASON_PATTERN.search(name)
        return int(match.group(1)) if match else None
    
    def _extract_episode(self, name: str) -> Optional[int]:
        """Extrait le numéro d'épisode (E01, ep12, etc.)"""
        match = self.EPISODE_PATTERN.search(name)
        return int(match.group(1)) if match else None
    
    def _extract_year(self, name: str) -> Optional[int]:
        """Extrait l'année (1900-2099)"""
        match = self.YEAR_PATTERN.search(name)
        return int(match.group(1)) if match else None
    
    def _extract_resolution(self, name: str) -> Optional[str]:
        """Extrait la résolution (4k, 1080p, etc.)"""
        match = self.RESOLUTION_PATTERN.search(name)
        return match.group(1).lower() if match else None
    
    def _remove_noise(self, name: str) -> str:
        """
        Supprime tous les termes de la blacklist
        Applique les regex de nettoyage de manière séquentielle
        """
        # Supprime les termes de bruit
        cleaned = self.noise_regex.sub(' ', name)
        
        # Supprime les patterns de saison/épisode pour éviter la duplication
        # Supprime d'abord le pattern combiné S01E01
        cleaned = self.SEASON_EPISODE_PATTERN.sub(' ', cleaned)
        # Puis les patterns individuels
        cleaned = self.SEASON_PATTERN.sub(' ', cleaned)
        cleaned = self.EPISODE_PATTERN.sub(' ', cleaned)
        cleaned = self.YEAR_PATTERN.sub(' ', cleaned)
        cleaned = self.RESOLUTION_PATTERN.sub(' ', cleaned)
        
        return cleaned
    
    def _canonicalize(self, name: str) -> str:
        """
        Canonicalisation finale :
        - Remplace caractères spéciaux par espaces
        - Lowercase
        - Trim et normalisation des espaces
        """
        # Remplace ., _, -, + par des espaces
        canonical = self.SPECIAL_CHARS_PATTERN.sub(' ', name)
        
        # Lowercase
        canonical = canonical.lower()
        
        # Normalise les espaces multiples
        canonical = self.MULTIPLE_SPACES_PATTERN.sub(' ', canonical)
        
        # Trim
        canonical = canonical.strip()
        
        return canonical


# Instance globale pour réutilisation
normalizer = Normalizer()
