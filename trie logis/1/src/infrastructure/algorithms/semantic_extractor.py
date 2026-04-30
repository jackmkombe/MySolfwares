"""
Infrastructure Layer - Extraction sémantique
Analyse intelligente de la structure des noms de fichiers
"""

import re
from typing import Optional
from datetime import datetime

from src.domain.entities import (
    SemanticStructure,
    ContentType,
    SeasonInfo,
    EpisodeInfo,
    QualityInfo,
)
from src.domain.interfaces import ISemanticExtractor
from src.infrastructure.algorithms.normalization import AdvancedNormalizationService


class SemanticExtractorService(ISemanticExtractor):
    """
    Extracteur sémantique avancé
    Extrait une structure riche à partir d'un nom de fichier
    """
    
    # Patterns pour saisons
    SEASON_PATTERNS = [
        re.compile(r'\bs(?:eason)?[\s._-]*(\d{1,2})\b', re.IGNORECASE),
        re.compile(r'\b(\d{1,2})(?:st|nd|rd|th)?\s*season\b', re.IGNORECASE),
        re.compile(r'\bs(\d{2})\b', re.IGNORECASE),
    ]
    
    # Patterns pour épisodes
    EPISODE_PATTERNS = [
        re.compile(r'\be(?:pisode)?[\s._-]*(\d{1,3})\b', re.IGNORECASE),
        re.compile(r'\b(\d{1,3})(?:st|nd|rd|th)?\s*episode\b', re.IGNORECASE),
        re.compile(r'\be(\d{2,3})\b', re.IGNORECASE),
        re.compile(r'\s-\s(\d{2,3})\b', re.IGNORECASE),  # " - 01"
    ]
    
    # Pattern combiné saison/épisode
    SEASON_EPISODE_PATTERN = re.compile(
        r'\bs(\d{1,2})e(\d{1,3})\b',
        re.IGNORECASE
    )
    
    # Patterns pour années
    YEAR_PATTERNS = [
        re.compile(r'\b(19\d{2}|20\d{2})\b'),
        re.compile(r'\((\d{4})\)'),
    ]
    
    # Patterns pour qualité
    RESOLUTION_PATTERN = re.compile(
        r'\b(1080p|720p|480p|4k|2160p|uhd)\b',
        re.IGNORECASE
    )
    CODEC_PATTERN = re.compile(
        r'\b(x264|x265|hevc|h\.264|h\.265|xvid|divx)\b',
        re.IGNORECASE
    )
    SOURCE_PATTERN = re.compile(
        r'\b(bluray|blu-ray|bdrip|brrip|web-?dl|webrip|hdtv|dvdrip|dvd|hddvd)\b',
        re.IGNORECASE
    )
    AUDIO_PATTERN = re.compile(
        r'\b(aac|ac3|dts|dts-hd|truehd|flac|mp3|dd5\.1|dd2\.0)\b',
        re.IGNORECASE
    )
    
    # Patterns pour langues
    LANGUAGE_PATTERN = re.compile(
        r'\b(vostfr|vf|vff|multi|french|english|spanish|german|italian|japanese)\b',
        re.IGNORECASE
    )
    
    # Mots-clés pour détecter les séries vs films
    SERIES_KEYWORDS = [
        'season', 'episode', 'saison', 'episode',
        's01', 's02', 's03', 's04', 's05',
        'e01', 'e02', 'e03',
    ]
    
    # Suffixes indiquant une suite/variante
    SEQUEL_SUFFIXES = [
        'shippuden', 'kai', 'brotherhood', 'gt', 'super',
        'origins', 'legends', 'chronicles', 'saga',
        'next generation', 'the next generation',
    ]
    
    def __init__(self):
        """Initialise l'extracteur"""
        self.normalizer = AdvancedNormalizationService()
    
    def extract(self, filename: str) -> SemanticStructure:
        """
        Extrait la structure sémantique complète
        
        Args:
            filename: Nom du fichier
            
        Returns:
            Structure sémantique riche
        """
        if not filename:
            raise ValueError("Le nom de fichier ne peut pas être vide")
        
        original_title = filename
        
        # Extraction des composants structurés
        season = self._extract_season(filename)
        episode = self._extract_episode(filename)
        year = self._extract_year(filename)
        quality = self._extract_quality(filename)
        language = self._extract_language(filename)
        tags = self._extract_tags(filename)
        
        # Détection du type de contenu
        content_type = self._detect_content_type(filename, season, episode)
        
        # Extraction du titre (après suppression de tous les composants)
        title = self._extract_title(filename, season, episode, year, quality)
        
        # Calcul de la confiance
        confidence = self._calculate_confidence(
            title, season, episode, year, quality
        )
        
        return SemanticStructure(
            title=title,
            original_title=original_title,
            content_type=content_type,
            season=season,
            episode=episode,
            year=year,
            quality=quality,
            language=language,
            tags=tags,
            extraction_confidence=confidence,
            extraction_timestamp=datetime.now(),
        )
    
    def extract_batch(self, filenames: list[str]) -> list[SemanticStructure]:
        """Extraction en batch"""
        return [self.extract(filename) for filename in filenames]
    
    def _extract_season(self, text: str) -> Optional[SeasonInfo]:
        """Extrait l'information de saison"""
        # Essayer le pattern combiné S01E01
        match = self.SEASON_EPISODE_PATTERN.search(text)
        if match:
            return SeasonInfo(number=int(match.group(1)))
        
        # Essayer les patterns de saison seuls
        for pattern in self.SEASON_PATTERNS:
            match = pattern.search(text)
            if match:
                return SeasonInfo(number=int(match.group(1)))
        
        return None
    
    def _extract_episode(self, text: str) -> Optional[EpisodeInfo]:
        """Extrait l'information d'épisode"""
        # Essayer le pattern combiné S01E01
        match = self.SEASON_EPISODE_PATTERN.search(text)
        if match:
            return EpisodeInfo(number=int(match.group(2)))
        
        # Essayer les patterns d'épisode seuls
        for pattern in self.EPISODE_PATTERNS:
            match = pattern.search(text)
            if match:
                return EpisodeInfo(number=int(match.group(1)))
        
        return None
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extrait l'année"""
        for pattern in self.YEAR_PATTERNS:
            match = pattern.search(text)
            if match:
                year = int(match.group(1))
                if 1900 <= year <= 2100:
                    return year
        return None
    
    def _extract_quality(self, text: str) -> Optional[QualityInfo]:
        """Extrait les informations de qualité"""
        resolution_match = self.RESOLUTION_PATTERN.search(text)
        codec_match = self.CODEC_PATTERN.search(text)
        source_match = self.SOURCE_PATTERN.search(text)
        audio_match = self.AUDIO_PATTERN.search(text)
        
        if any([resolution_match, codec_match, source_match, audio_match]):
            return QualityInfo(
                resolution=resolution_match.group(1) if resolution_match else None,
                codec=codec_match.group(1) if codec_match else None,
                source=source_match.group(1) if source_match else None,
                audio=audio_match.group(1) if audio_match else None,
            )
        
        return None
    
    def _extract_language(self, text: str) -> Optional[str]:
        """Extrait la langue"""
        match = self.LANGUAGE_PATTERN.search(text)
        return match.group(1).upper() if match else None
    
    def _extract_tags(self, text: str) -> list[str]:
        """Extrait les tags entre crochets/parenthèses"""
        tags = []
        
        # Tags entre crochets
        bracket_tags = re.findall(r'\[([^\]]+)\]', text)
        tags.extend(bracket_tags)
        
        # Tags entre parenthèses (sauf années)
        paren_tags = re.findall(r'\(([^\)]+)\)', text)
        for tag in paren_tags:
            if not re.match(r'^\d{4}$', tag):
                tags.append(tag)
        
        return tags
    
    def _detect_content_type(
        self,
        text: str,
        season: Optional[SeasonInfo],
        episode: Optional[EpisodeInfo]
    ) -> ContentType:
        """Détecte le type de contenu"""
        text_lower = text.lower()
        
        # Si saison ou épisode détecté → série
        if season or episode:
            return ContentType.SERIES
        
        # Vérifier les mots-clés de série
        for keyword in self.SERIES_KEYWORDS:
            if keyword in text_lower:
                return ContentType.SERIES
        
        # Extensions audio
        if any(ext in text_lower for ext in ['.mp3', '.flac', '.wav', '.aac']):
            return ContentType.MUSIC
        
        # Extensions vidéo sans indicateurs de série → film
        if any(ext in text_lower for ext in ['.mkv', '.mp4', '.avi']):
            return ContentType.MOVIE
        
        return ContentType.UNKNOWN
    
    def _extract_title(
        self,
        text: str,
        season: Optional[SeasonInfo],
        episode: Optional[EpisodeInfo],
        year: Optional[int],
        quality: Optional[QualityInfo]
    ) -> str:
        """
        Extrait le titre en supprimant tous les composants structurés
        """
        # Commencer avec le texte nettoyé
        title = self.normalizer.remove_noise(text)
        
        # Supprimer saison/épisode
        if season or episode:
            title = self.SEASON_EPISODE_PATTERN.sub(' ', title)
            for pattern in self.SEASON_PATTERNS + self.EPISODE_PATTERNS:
                title = pattern.sub(' ', title)
        
        # Supprimer année
        if year:
            title = title.replace(str(year), ' ')
        
        # Normaliser
        title = self.normalizer._normalize_spaces(title)
        
        # Capitaliser proprement
        title = self._capitalize_title(title)
        
        return title.strip()
    
    def _capitalize_title(self, text: str) -> str:
        """Capitalise le titre proprement"""
        # Articles et prépositions à ne pas capitaliser
        lowercase_words = {'a', 'an', 'the', 'and', 'or', 'but', 'of', 'in', 'on', 'at', 'to', 'for'}
        
        words = text.split()
        if not words:
            return text
        
        # Premier mot toujours capitalisé
        result = [words[0].capitalize()]
        
        # Autres mots
        for word in words[1:]:
            if word.lower() in lowercase_words:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        
        return ' '.join(result)
    
    def _calculate_confidence(
        self,
        title: str,
        season: Optional[SeasonInfo],
        episode: Optional[EpisodeInfo],
        year: Optional[int],
        quality: Optional[QualityInfo]
    ) -> float:
        """
        Calcule le score de confiance de l'extraction
        
        Basé sur:
        - Présence d'un titre valide
        - Présence de composants structurés
        - Cohérence des informations
        """
        confidence = 0.0
        
        # Titre valide (30%)
        if title and len(title) >= 2:
            confidence += 0.3
        
        # Composants structurés (40%)
        if season:
            confidence += 0.15
        if episode:
            confidence += 0.15
        if year:
            confidence += 0.05
        if quality:
            confidence += 0.05
        
        # Cohérence (30%)
        # Si série, devrait avoir saison ou épisode
        if season or episode:
            confidence += 0.15
        
        # Si année valide
        if year and 1950 <= year <= 2030:
            confidence += 0.15
        
        return min(confidence, 1.0)
    
    def is_sequel_or_variant(self, title1: str, title2: str) -> bool:
        """
        Vérifie si title2 est une suite/variante de title1
        Ex: "Naruto" vs "Naruto Shippuden"
        
        Returns:
            True si c'est une variante, False sinon
        """
        title1_lower = title1.lower()
        title2_lower = title2.lower()
        
        # Vérifier si l'un contient l'autre
        if title1_lower in title2_lower or title2_lower in title1_lower:
            # Vérifier si la différence est un suffixe connu
            for suffix in self.SEQUEL_SUFFIXES:
                if suffix in title2_lower and suffix not in title1_lower:
                    return True
        
        return False
