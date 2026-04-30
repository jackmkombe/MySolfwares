"""
Configuration de l'application
Paramètres configurables pour les algorithmes
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class AlgorithmSettings(BaseSettings):
    """Paramètres des algorithmes"""
    
    # Poids de similarité
    title_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    structural_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    temporal_weight: float = Field(default=0.1, ge=0.0, le=1.0)
    quality_weight: float = Field(default=0.1, ge=0.0, le=1.0)
    
    # Seuils de regroupement
    high_confidence_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    ambiguous_min_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    
    class Config:
        env_prefix = "ALGO_"


class FilesystemSettings(BaseSettings):
    """Paramètres du système de fichiers"""
    
    # Exclure les fichiers cachés
    exclude_hidden: bool = Field(default=True)
    
    # Scan récursif par défaut
    recursive_by_default: bool = Field(default=True)
    
    class Config:
        env_prefix = "FS_"


class UISettings(BaseSettings):
    """Paramètres de l'interface utilisateur"""
    
    # Largeur minimale de la fenêtre
    min_window_width: int = Field(default=1200)
    
    # Hauteur minimale de la fenêtre
    min_window_height: int = Field(default=800)
    
    class Config:
        env_prefix = "UI_"


class AppSettings(BaseSettings):
    """Configuration globale de l'application"""
    
    # Nom de l'application
    app_name: str = Field(default="Tri et Fusion Intelligente")
    
    # Version
    version: str = Field(default="1.0.0")
    
    # Niveau de log
    log_level: str = Field(default="INFO")
    
    # Sous-configurations
    algorithm: AlgorithmSettings = Field(default_factory=AlgorithmSettings)
    filesystem: FilesystemSettings = Field(default_factory=FilesystemSettings)
    ui: UISettings = Field(default_factory=UISettings)
    
    class Config:
        env_prefix = "APP_"
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instance globale de configuration
settings = AppSettings()
