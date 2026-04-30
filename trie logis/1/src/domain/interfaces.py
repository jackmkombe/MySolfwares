"""
Domain Layer - Interfaces (ports)
Définit les contrats sans implémentation
"""

from abc import ABC, abstractmethod
from typing import Protocol
from pathlib import Path

from .entities import (
    FileItem,
    SemanticStructure,
    SimilarityScore,
    GroupingDecision,
)


class IFileSystemRepository(ABC):
    """
    Interface pour l'accès au système de fichiers
    Aucune logique métier, uniquement accès aux données
    """
    
    @abstractmethod
    def scan_directory(self, path: Path, recursive: bool = True) -> list[FileItem]:
        """
        Scanne un répertoire et retourne les items
        
        Args:
            path: Chemin du répertoire
            recursive: Scanner récursivement
            
        Returns:
            Liste des items trouvés
        """
        pass
    
    @abstractmethod
    def get_file_info(self, path: Path) -> FileItem:
        """
        Récupère les informations d'un fichier/dossier
        
        Args:
            path: Chemin du fichier
            
        Returns:
            FileItem avec métadonnées
        """
        pass
    
    @abstractmethod
    def move_file(self, source: Path, destination: Path) -> bool:
        """
        Déplace un fichier
        
        Args:
            source: Chemin source
            destination: Chemin destination
            
        Returns:
            True si succès
        """
        pass
    
    @abstractmethod
    def create_directory(self, path: Path) -> bool:
        """
        Crée un répertoire
        
        Args:
            path: Chemin du répertoire
            
        Returns:
            True si succès
        """
        pass


class ISemanticExtractor(ABC):
    """
    Interface pour l'extraction de structure sémantique
    Transforme un nom de fichier en structure riche
    """
    
    @abstractmethod
    def extract(self, filename: str) -> SemanticStructure:
        """
        Extrait la structure sémantique d'un nom de fichier
        
        Args:
            filename: Nom du fichier
            
        Returns:
            Structure sémantique extraite
        """
        pass
    
    @abstractmethod
    def extract_batch(self, filenames: list[str]) -> list[SemanticStructure]:
        """
        Extrait en batch pour optimisation
        
        Args:
            filenames: Liste de noms
            
        Returns:
            Liste de structures sémantiques
        """
        pass


class ISimilarityCalculator(ABC):
    """
    Interface pour le calcul de similarité sémantique
    Aucune comparaison naïve de chaînes
    """
    
    @abstractmethod
    def calculate(
        self,
        item1: SemanticStructure,
        item2: SemanticStructure
    ) -> SimilarityScore:
        """
        Calcule le score de similarité entre deux structures
        
        Args:
            item1: Première structure
            item2: Deuxième structure
            
        Returns:
            Score de similarité détaillé
        """
        pass
    
    @abstractmethod
    def calculate_matrix(
        self,
        items: list[SemanticStructure]
    ) -> dict[tuple[int, int], SimilarityScore]:
        """
        Calcule la matrice de similarité pour un ensemble d'items
        
        Args:
            items: Liste de structures
            
        Returns:
            Dictionnaire (index1, index2) -> score
        """
        pass


class IGroupingStrategy(ABC):
    """
    Interface pour la stratégie de regroupement
    Décide comment regrouper les items similaires
    """
    
    @abstractmethod
    def group(
        self,
        items: list[FileItem],
        similarity_matrix: dict[tuple[int, int], SimilarityScore]
    ) -> list[GroupingDecision]:
        """
        Crée des décisions de regroupement
        
        Args:
            items: Items à regrouper
            similarity_matrix: Matrice de similarité
            
        Returns:
            Liste de décisions de regroupement
        """
        pass


class INormalizationService(ABC):
    """
    Interface pour la normalisation de noms
    Première étape avant analyse sémantique
    """
    
    @abstractmethod
    def normalize(self, text: str) -> str:
        """
        Normalise un texte
        
        Args:
            text: Texte à normaliser
            
        Returns:
            Texte normalisé
        """
        pass
    
    @abstractmethod
    def remove_noise(self, text: str) -> str:
        """
        Supprime le bruit (tags, séparateurs, etc.)
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        pass


class IConfigurationRepository(ABC):
    """
    Interface pour la gestion de la configuration
    """
    
    @abstractmethod
    def get_similarity_threshold(self, content_type: str) -> float:
        """Récupère le seuil de similarité pour un type de contenu"""
        pass
    
    @abstractmethod
    def get_ambiguity_range(self) -> tuple[float, float]:
        """Récupère la plage de scores ambigus"""
        pass
    
    @abstractmethod
    def get_weights(self) -> dict[str, float]:
        """Récupère les poids pour le calcul de similarité"""
        pass
    
    @abstractmethod
    def save_configuration(self, config: dict) -> bool:
        """Sauvegarde la configuration"""
        pass


class ILogger(Protocol):
    """
    Interface pour le logging
    Toute décision doit être tracée
    """
    
    def info(self, message: str, **context) -> None:
        """Log niveau info"""
        ...
    
    def warning(self, message: str, **context) -> None:
        """Log niveau warning"""
        ...
    
    def error(self, message: str, **context) -> None:
        """Log niveau error"""
        ...
    
    def debug(self, message: str, **context) -> None:
        """Log niveau debug"""
        ...


class IValidationService(Protocol):
    """
    Interface pour la validation utilisateur
    """
    
    def request_validation(self, decision: GroupingDecision) -> bool:
        """
        Demande validation à l'utilisateur
        
        Args:
            decision: Décision à valider
            
        Returns:
            True si validé, False si rejeté
        """
        pass
    
    def request_batch_validation(
        self,
        decisions: list[GroupingDecision]
    ) -> dict[int, bool]:
        """
        Demande validation en batch
        
        Args:
            decisions: Liste de décisions
            
        Returns:
            Dictionnaire index -> validation
        """
        ...
