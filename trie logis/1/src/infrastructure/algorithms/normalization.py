"""
Infrastructure Layer - Normalisation avancée
Pas de comparaisons naïves, traitement intelligent
"""

import re
from typing import Pattern
from unidecode import unidecode

from src.domain.interfaces import INormalizationService


class AdvancedNormalizationService(INormalizationService):
    """
    Service de normalisation avancée
    Gère les variantes orthographiques et le bruit
    """
    
    # Patterns de tags à supprimer
    TAG_PATTERNS: list[Pattern] = [
        re.compile(r'\[.*?\]', re.IGNORECASE),  # [1080p], [BluRay]
        re.compile(r'\(.*?\)', re.IGNORECASE),  # (2001), (VOSTFR)
        re.compile(r'\{.*?\}', re.IGNORECASE),  # {HEVC}
    ]
    
    # Patterns de qualité/source
    QUALITY_PATTERNS: list[Pattern] = [
        re.compile(r'\b(1080p|720p|480p|4k|2160p)\b', re.IGNORECASE),
        re.compile(r'\b(x264|x265|hevc|h\.264|h\.265)\b', re.IGNORECASE),
        re.compile(r'\b(bluray|blu-ray|bdrip|brrip|web-?dl|webrip|hdtv|dvdrip)\b', re.IGNORECASE),
        re.compile(r'\b(aac|ac3|dts|flac|mp3)\b', re.IGNORECASE),
    ]
    
    # Patterns de groupes de release
    RELEASE_GROUP_PATTERN = re.compile(r'-[A-Z0-9]+$', re.IGNORECASE)
    
    # Séparateurs à normaliser
    SEPARATORS = ['-', '_', '.', ' ']
    
    def __init__(self):
        """Initialise le service"""
        self._cache: dict[str, str] = {}
    
    def normalize(self, text: str) -> str:
        """
        Normalisation complète
        
        Étapes:
        1. Suppression du bruit
        2. Normalisation Unicode
        3. Normalisation de la casse
        4. Normalisation des séparateurs
        5. Normalisation des espaces
        """
        if not text:
            return ""
        
        # Cache pour performance
        if text in self._cache:
            return self._cache[text]
        
        # 1. Suppression du bruit
        normalized = self.remove_noise(text)
        
        # 2. Normalisation Unicode (juu-shiro → juu-shiro)
        normalized = unidecode(normalized)
        
        # 3. Normalisation de la casse
        normalized = normalized.lower()
        
        # 4. Normalisation des séparateurs
        normalized = self._normalize_separators(normalized)
        
        # 5. Normalisation des espaces
        normalized = self._normalize_spaces(normalized)
        
        # Cache
        self._cache[text] = normalized
        
        return normalized
    
    def remove_noise(self, text: str) -> str:
        """
        Supprime le bruit du texte
        
        Supprime:
        - Tags entre crochets/parenthèses
        - Informations de qualité
        - Groupes de release
        - Extensions de fichiers
        """
        if not text:
            return ""
        
        result = text
        
        # Suppression de l'extension
        result = self._remove_extension(result)
        
        # Suppression des tags
        for pattern in self.TAG_PATTERNS:
            result = pattern.sub(' ', result)
        
        # Suppression des informations de qualité
        for pattern in self.QUALITY_PATTERNS:
            result = pattern.sub(' ', result)
        
        # Suppression des groupes de release
        result = self.RELEASE_GROUP_PATTERN.sub('', result)
        
        return result.strip()
    
    def _remove_extension(self, text: str) -> str:
        """Supprime l'extension de fichier"""
        common_extensions = [
            '.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv',
            '.mp3', '.flac', '.wav', '.aac',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp',
            '.pdf', '.doc', '.docx', '.txt',
            '.zip', '.rar', '.7z', '.tar', '.gz',
        ]
        
        text_lower = text.lower()
        for ext in common_extensions:
            if text_lower.endswith(ext):
                return text[:-len(ext)]
        
        return text
    
    def _normalize_separators(self, text: str) -> str:
        """
        Normalise les séparateurs
        Convertit tous les séparateurs en espaces
        """
        result = text
        for sep in self.SEPARATORS:
            result = result.replace(sep, ' ')
        return result
    
    def _normalize_spaces(self, text: str) -> str:
        """
        Normalise les espaces
        Supprime les espaces multiples et trim
        """
        # Suppression des espaces multiples
        result = re.sub(r'\s+', ' ', text)
        
        # Trim
        return result.strip()
    
    def extract_variants(self, text: str) -> list[str]:
        """
        Génère des variantes orthographiques
        Pour gérer juu-shiro ≈ juushiro ≈ juu shiro
        
        Returns:
            Liste de variantes possibles
        """
        variants = [text]
        
        # Variante sans séparateurs
        no_sep = re.sub(r'[-_\s]+', '', text)
        if no_sep != text:
            variants.append(no_sep)
        
        # Variante avec espaces
        with_spaces = re.sub(r'[-_]+', ' ', text)
        if with_spaces != text:
            variants.append(with_spaces)
        
        # Variante avec tirets
        with_dashes = re.sub(r'[_\s]+', '-', text)
        if with_dashes != text:
            variants.append(with_dashes)
        
        return list(set(variants))
    
    def clear_cache(self) -> None:
        """Vide le cache de normalisation"""
        self._cache.clear()
