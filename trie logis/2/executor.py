"""
SmartSort - Executor Module
Exécution sécurisée des opérations de fusion avec gestion des conflits
"""

import shutil
from pathlib import Path
from typing import List, Callable, Optional
from dataclasses import dataclass
from merger import MergeAction


@dataclass
class ExecutionResult:
    """Résultat d'une opération de fusion"""
    success: bool
    action: MergeAction
    error: Optional[str] = None
    files_moved: int = 0


class MergeExecutor:
    """
    Exécuteur sécurisé des opérations de fusion
    Gestion des conflits par renommage incrémental
    """
    
    def __init__(self):
        self.results: List[ExecutionResult] = []
    
    def execute_actions(
        self, 
        actions: List[MergeAction],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[ExecutionResult]:
        """
        Exécute toutes les actions de fusion
        
        Args:
            actions: Liste des actions à exécuter
            progress_callback: Fonction de callback pour progression (current, total, message)
            
        Returns:
            Liste des résultats d'exécution
        """
        self.results = []
        total = len(actions)
        
        for idx, action in enumerate(actions, 1):
            if progress_callback:
                progress_callback(idx, total, f"Traitement de {action.destination_path.name}")
            
            try:
                result = self._execute_single_action(action)
                self.results.append(result)
            except Exception as e:
                self.results.append(ExecutionResult(
                    success=False,
                    action=action,
                    error=str(e)
                ))
        
        return self.results
    
    def _execute_single_action(self, action: MergeAction) -> ExecutionResult:
        """
        Exécute une action de fusion unique
        
        Args:
            action: Action à exécuter
            
        Returns:
            Résultat de l'exécution
        """
        files_moved = 0
        
        try:
            if action.action_type == 'merge':
                files_moved = self._execute_merge(action)
            elif action.action_type == 'hierarchy':
                files_moved = self._execute_hierarchy(action)
            else:
                raise ValueError(f"Type d'action inconnu : {action.action_type}")
            
            return ExecutionResult(
                success=True,
                action=action,
                files_moved=files_moved
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                action=action,
                error=str(e)
            )
    
    def _execute_merge(self, action: MergeAction) -> int:
        """
        RÈGLE 01 : Fusion directe de répertoires
        Déplace tous les fichiers vers la destination
        """
        dest = action.destination_path
        dest.mkdir(parents=True, exist_ok=True)
        
        files_moved = 0
        
        for source in action.source_paths:
            if source == dest:
                continue  # Skip si déjà à la bonne place
            
            # Déplace tous les fichiers
            for item in source.rglob('*'):
                if item.is_file():
                    relative_path = item.relative_to(source)
                    target = dest / relative_path
                    
                    # Crée les sous-répertoires si nécessaire
                    target.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Gestion des conflits par renommage
                    target = self._resolve_conflict(target)
                    
                    shutil.move(str(item), str(target))
                    files_moved += 1
            
            # Supprime le répertoire source vide
            if source.exists() and source != dest:
                self._remove_empty_dirs(source)
        
        return files_moved
    
    def _execute_hierarchy(self, action: MergeAction) -> int:
        """
        RÈGLE 02 : Création de hiérarchie par saison
        Structure : RootName/Season XX/
        """
        base_dest = action.destination_path
        base_dest.mkdir(parents=True, exist_ok=True)
        
        files_moved = 0
        
        for source in action.source_paths:
            # Extrait le numéro de saison du nom original
            from normalizer import normalizer
            norm = normalizer.preprocess(source.name)
            
            if norm.season:
                season_dir = base_dest / f"Season {norm.season:02d}"
            elif norm.episode:
                # RÈGLE 05 : Épisode seul rejoint Season 01 par défaut
                season_dir = base_dest / "Season 01"
            else:
                # Pas de saison détectée, utilise le nom original
                season_dir = base_dest / source.name
            
            season_dir.mkdir(parents=True, exist_ok=True)
            
            # Déplace tous les fichiers
            for item in source.rglob('*'):
                if item.is_file():
                    relative_path = item.relative_to(source)
                    target = season_dir / relative_path
                    
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target = self._resolve_conflict(target)
                    
                    shutil.move(str(item), str(target))
                    files_moved += 1
            
            # Supprime le répertoire source vide
            if source.exists() and source != base_dest:
                self._remove_empty_dirs(source)
        
        return files_moved
    
    def _resolve_conflict(self, target: Path) -> Path:
        """
        Gestion des doublons par renommage incrémental
        file.ext -> file_1.ext -> file_2.ext
        """
        if not target.exists():
            return target
        
        stem = target.stem
        suffix = target.suffix
        parent = target.parent
        counter = 1
        
        while True:
            new_target = parent / f"{stem}_{counter}{suffix}"
            if not new_target.exists():
                return new_target
            counter += 1
    
    def _remove_empty_dirs(self, path: Path):
        """
        Supprime récursivement les répertoires vides
        """
        try:
            if path.is_dir():
                # Supprime les sous-répertoires vides d'abord
                for child in path.iterdir():
                    if child.is_dir():
                        self._remove_empty_dirs(child)
                
                # Supprime le répertoire s'il est vide
                if not any(path.iterdir()):
                    path.rmdir()
        except Exception:
            pass  # Ignore les erreurs de suppression
    
    def get_summary(self) -> dict:
        """
        Génère un résumé de l'exécution
        
        Returns:
            Dictionnaire avec statistiques
        """
        total = len(self.results)
        success = sum(1 for r in self.results if r.success)
        failed = total - success
        total_files = sum(r.files_moved for r in self.results if r.success)
        
        return {
            'total_actions': total,
            'successful': success,
            'failed': failed,
            'total_files_moved': total_files,
            'errors': [r.error for r in self.results if not r.success]
        }
