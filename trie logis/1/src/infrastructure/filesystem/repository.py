"""
Infrastructure Layer - Repository système de fichiers
Accès au filesystem Windows
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.domain.entities import FileItem, FileType
from src.domain.interfaces import IFileSystemRepository


class WindowsFileSystemRepository(IFileSystemRepository):
    """
    Repository pour accès au système de fichiers Windows
    Aucune logique métier, uniquement accès aux données
    """
    
    # Extensions par type
    VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    AUDIO_EXTENSIONS = {'.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff'}
    DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx'}
    ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}
    
    def __init__(self, exclude_hidden: bool = True):
        """
        Initialise le repository
        
        Args:
            exclude_hidden: Exclure les fichiers/dossiers cachés
        """
        self.exclude_hidden = exclude_hidden
    
    def scan_directory(
        self,
        path: Path,
        recursive: bool = True
    ) -> list[FileItem]:
        """
        Scanne un répertoire
        
        Args:
            path: Chemin du répertoire
            recursive: Scanner récursivement
            
        Returns:
            Liste des items trouvés
        """
        if not path.exists():
            raise FileNotFoundError(f"Le répertoire n'existe pas: {path}")
        
        if not path.is_dir():
            raise ValueError(f"Le chemin n'est pas un répertoire: {path}")
        
        items = []
        
        try:
            if recursive:
                # Scan récursif
                for root, dirs, files in os.walk(path):
                    root_path = Path(root)
                    
                    # Filtrer les dossiers cachés si nécessaire
                    if self.exclude_hidden:
                        dirs[:] = [d for d in dirs if not self._is_hidden(root_path / d)]
                    
                    # Ajouter les dossiers
                    for dir_name in dirs:
                        dir_path = root_path / dir_name
                        try:
                            item = self.get_file_info(dir_path)
                            items.append(item)
                        except Exception:
                            # Ignorer les erreurs d'accès
                            pass
                    
                    # Ajouter les fichiers
                    for file_name in files:
                        file_path = root_path / file_name
                        
                        # Filtrer les fichiers cachés
                        if self.exclude_hidden and self._is_hidden(file_path):
                            continue
                        
                        try:
                            item = self.get_file_info(file_path)
                            items.append(item)
                        except Exception:
                            # Ignorer les erreurs d'accès
                            pass
            else:
                # Scan non récursif
                for entry in path.iterdir():
                    # Filtrer les fichiers cachés
                    if self.exclude_hidden and self._is_hidden(entry):
                        continue
                    
                    try:
                        item = self.get_file_info(entry)
                        items.append(item)
                    except Exception:
                        # Ignorer les erreurs d'accès
                        pass
        
        except PermissionError as e:
            raise PermissionError(f"Accès refusé au répertoire: {path}") from e
        
        return items
    
    def get_file_info(self, path: Path) -> FileItem:
        """
        Récupère les informations d'un fichier/dossier
        
        Args:
            path: Chemin du fichier
            
        Returns:
            FileItem avec métadonnées
        """
        if not path.exists():
            raise FileNotFoundError(f"Le fichier n'existe pas: {path}")
        
        # Informations de base
        is_directory = path.is_dir()
        name = path.name
        
        # Type de fichier
        file_type = self._detect_file_type(path)
        
        # Taille
        size = 0
        if not is_directory:
            try:
                size = path.stat().st_size
            except Exception:
                size = 0
        
        # Dates
        try:
            stat = path.stat()
            created_at = datetime.fromtimestamp(stat.st_ctime)
            modified_at = datetime.fromtimestamp(stat.st_mtime)
        except Exception:
            created_at = None
            modified_at = None
        
        return FileItem(
            path=str(path.absolute()),
            name=name,
            is_directory=is_directory,
            file_type=file_type,
            size=size,
            created_at=created_at,
            modified_at=modified_at,
        )
    
    def move_file(self, source: Path, destination: Path) -> bool:
        """
        Déplace un fichier
        
        Args:
            source: Chemin source
            destination: Chemin destination
            
        Returns:
            True si succès
        """
        if not source.exists():
            raise FileNotFoundError(f"Le fichier source n'existe pas: {source}")
        
        try:
            # Créer le répertoire parent si nécessaire
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Déplacer
            source.rename(destination)
            
            return True
        
        except Exception as e:
            raise RuntimeError(f"Erreur lors du déplacement: {e}") from e
    
    def create_directory(self, path: Path) -> bool:
        """
        Crée un répertoire
        
        Args:
            path: Chemin du répertoire
            
        Returns:
            True si succès
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la création du répertoire: {e}") from e
    
    def _detect_file_type(self, path: Path) -> FileType:
        """Détecte le type de fichier basé sur l'extension"""
        if path.is_dir():
            return FileType.OTHER
        
        extension = path.suffix.lower()
        
        if extension in self.VIDEO_EXTENSIONS:
            return FileType.VIDEO
        elif extension in self.AUDIO_EXTENSIONS:
            return FileType.AUDIO
        elif extension in self.IMAGE_EXTENSIONS:
            return FileType.IMAGE
        elif extension in self.DOCUMENT_EXTENSIONS:
            return FileType.DOCUMENT
        elif extension in self.ARCHIVE_EXTENSIONS:
            return FileType.ARCHIVE
        else:
            return FileType.OTHER
    
    def _is_hidden(self, path: Path) -> bool:
        """
        Vérifie si un fichier/dossier est caché (Windows)
        
        Sur Windows, vérifie l'attribut FILE_ATTRIBUTE_HIDDEN
        """
        if not path.exists():
            return False
        
        # Vérifier si commence par un point (convention Unix)
        if path.name.startswith('.'):
            return True
        
        # Vérifier l'attribut Windows
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            # FILE_ATTRIBUTE_HIDDEN = 0x2
            return bool(attrs & 0x2)
        except Exception:
            return False
