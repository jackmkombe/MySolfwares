"""
Domain Layer - Entités métier
Aucune dépendance externe, logique métier pure
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class FileType(Enum):
    """Type de fichier détecté"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


class ContentType(Enum):
    """Type de contenu média"""
    SERIES = "series"
    MOVIE = "movie"
    MUSIC = "music"
    BOOK = "book"
    GAME = "game"
    SOFTWARE = "software"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SeasonInfo:
    """Information de saison extraite"""
    number: int
    total_episodes: Optional[int] = None
    
    def __str__(self) -> str:
        return f"S{self.number:02d}"


@dataclass(frozen=True)
class EpisodeInfo:
    """Information d'épisode extraite"""
    number: int
    title: Optional[str] = None
    
    def __str__(self) -> str:
        return f"E{self.number:02d}"


@dataclass(frozen=True)
class QualityInfo:
    """Information de qualité extraite"""
    resolution: Optional[str] = None  # 1080p, 720p, 4K
    codec: Optional[str] = None  # x264, x265, HEVC
    audio: Optional[str] = None  # AAC, DTS, etc.
    source: Optional[str] = None  # BluRay, WEB-DL, HDTV
    
    def __str__(self) -> str:
        parts = [p for p in [self.resolution, self.codec, self.source] if p]
        return " ".join(parts) if parts else "Unknown"


@dataclass(frozen=True)
class SemanticStructure:
    """
    Structure sémantique extraite d'un nom de fichier
    Immuable pour garantir la traçabilité
    """
    # Titre principal normalisé
    title: str
    
    # Titre original (avant normalisation)
    original_title: str
    
    # Type de contenu détecté
    content_type: ContentType
    
    # Informations structurées
    season: Optional[SeasonInfo] = None
    episode: Optional[EpisodeInfo] = None
    year: Optional[int] = None
    quality: Optional[QualityInfo] = None
    
    # Métadonnées
    language: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    
    # Traçabilité
    extraction_confidence: float = 0.0  # 0.0 à 1.0
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validation des contraintes métier"""
        if not self.title or not self.title.strip():
            raise ValueError("Le titre ne peut pas être vide")
        
        if not 0.0 <= self.extraction_confidence <= 1.0:
            raise ValueError("La confiance doit être entre 0.0 et 1.0")
        
        if self.year and (self.year < 1800 or self.year > 2100):
            raise ValueError(f"Année invalide: {self.year}")
    
    def get_canonical_name(self) -> str:
        """
        Retourne le nom canonique pour comparaison
        Format: titre_saison_episode
        """
        parts = [self.title.lower().strip()]
        
        if self.season:
            parts.append(str(self.season).lower())
        
        if self.episode:
            parts.append(str(self.episode).lower())
        
        return "_".join(parts)
    
    def is_series(self) -> bool:
        """Vérifie si c'est une série"""
        return self.season is not None or self.episode is not None
    
    def is_same_series(self, other: 'SemanticStructure') -> bool:
        """
        Vérifie si deux structures appartiennent à la même série
        (même titre, mais saisons/épisodes peuvent différer)
        """
        return (
            self.title.lower() == other.title.lower() and
            self.content_type == other.content_type and
            self.is_series() and
            other.is_series()
        )


@dataclass(frozen=True)
class FileItem:
    """
    Représente un fichier ou dossier à traiter
    Entité métier centrale
    """
    # Identifiant unique
    path: str
    
    # Nom original
    name: str
    
    # Type
    is_directory: bool
    file_type: FileType
    
    # Taille en octets
    size: int
    
    # Structure sémantique extraite
    semantic: Optional[SemanticStructure] = None
    
    # Métadonnées système
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validation"""
        if not self.path or not self.name:
            raise ValueError("Path et name sont obligatoires")
        
        if self.size < 0:
            raise ValueError("La taille ne peut pas être négative")
    
    def has_semantic_structure(self) -> bool:
        """Vérifie si la structure sémantique a été extraite"""
        return self.semantic is not None


@dataclass
class SimilarityScore:
    """
    Score de similarité entre deux items
    Traçable et décomposable
    """
    # Score global (0.0 à 1.0)
    total: float
    
    # Scores détaillés par composant
    title_similarity: float
    structural_similarity: float  # saison, épisode
    temporal_similarity: float  # année
    quality_similarity: float
    
    # Poids utilisés
    weights: dict[str, float] = field(default_factory=dict)
    
    # Justification
    reasoning: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validation"""
        if not 0.0 <= self.total <= 1.0:
            raise ValueError("Le score total doit être entre 0.0 et 1.0")
    
    def is_high_confidence(self, threshold: float = 0.85) -> bool:
        """Vérifie si le score est de haute confiance"""
        return self.total >= threshold
    
    def is_ambiguous(self, min_threshold: float = 0.5, max_threshold: float = 0.85) -> bool:
        """Vérifie si le score est ambigu (nécessite validation utilisateur)"""
        return min_threshold <= self.total < max_threshold
    
    def add_reasoning(self, reason: str) -> None:
        """Ajoute une justification"""
        self.reasoning.append(reason)


@dataclass
class GroupingDecision:
    """
    Décision de regroupement
    Traçable et auditable
    """
    # Items à regrouper
    items: list[FileItem]
    
    # Nom du groupe proposé
    group_name: str
    
    # Score de confiance
    confidence: float
    
    # Nécessite validation utilisateur
    requires_validation: bool
    
    # Justification de la décision
    reasoning: list[str] = field(default_factory=list)
    
    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)
    
    # Statut
    validated: bool = False
    rejected: bool = False
    
    def __post_init__(self):
        """Validation"""
        if len(self.items) < 2:
            raise ValueError("Un groupe doit contenir au moins 2 items")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("La confiance doit être entre 0.0 et 1.0")
        
        if not self.group_name or not self.group_name.strip():
            raise ValueError("Le nom du groupe ne peut pas être vide")
    
    def validate(self) -> None:
        """Valide la décision"""
        self.validated = True
        self.rejected = False
    
    def reject(self) -> None:
        """Rejette la décision"""
        self.validated = False
        self.rejected = True
