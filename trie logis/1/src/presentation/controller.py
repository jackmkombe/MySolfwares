"""
Presentation Layer - Contrôleur
Fait le lien entre l'UI et la logique métier
"""

from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, QThread, Signal

from src.application.use_cases import FileOrganizationUseCase
from src.domain.entities import GroupingDecision
from src.domain.interfaces import IValidationService


class ScanWorker(QThread):
    """
    Worker thread pour l'analyse en arrière-plan
    Évite de bloquer l'interface
    """
    
    # Signaux
    finished = Signal(list)  # decisions
    error = Signal(str)  # error_message
    progress = Signal(str)  # status_message
    
    def __init__(
        self,
        use_case: FileOrganizationUseCase,
        directory: Path,
        recursive: bool
    ):
        super().__init__()
        self.use_case = use_case
        self.directory = directory
        self.recursive = recursive
    
    def run(self):
        """Exécute l'analyse"""
        try:
            self.progress.emit("Analyse en cours...")
            
            decisions = self.use_case.execute(
                directory_path=self.directory,
                recursive=self.recursive,
                auto_execute=False,  # Pas d'exécution automatique
            )
            
            self.finished.emit(decisions)
            
        except Exception as e:
            self.error.emit(str(e))


class UIValidationService(QObject):
    """
    Service de validation via l'interface utilisateur
    Satisfait l'interface IValidationService par duck-typing
    """
    
    def __init__(self):
        super().__init__()
        self._pending_decisions: list[GroupingDecision] = []
        self._validations: dict[int, bool] = {}
    
    def request_validation(self, decision: GroupingDecision) -> bool:
        """
        Demande validation pour une seule décision
        
        Note: Dans cette implémentation, on retourne True par défaut
        car la validation se fait via l'UI de manière asynchrone
        """
        return True
    
    def request_batch_validation(
        self,
        decisions: list[GroupingDecision]
    ) -> dict[int, bool]:
        """
        Demande validation en batch
        
        Note: Dans cette implémentation, on retourne un dictionnaire vide
        car la validation se fait via l'UI de manière asynchrone
        """
        # Retourner un dictionnaire vide pour l'instant
        # La validation réelle se fait via les checkboxes de l'UI
        return {}


class MainController(QObject):
    """
    Contrôleur principal
    Orchestre l'interaction entre l'UI et la logique métier
    """
    
    def __init__(
        self,
        main_window,
        use_case: FileOrganizationUseCase,
    ):
        super().__init__()
        
        self.main_window = main_window
        self.use_case = use_case
        self.current_worker: Optional[ScanWorker] = None
        
        # Connexion des signaux
        self._connect_signals()
    
    def _connect_signals(self):
        """Connecte les signaux de l'UI aux slots du contrôleur"""
        self.main_window.scan_requested.connect(self._on_scan_requested)
        self.main_window.execution_requested.connect(self._on_execution_requested)
    
    def _on_scan_requested(self, directory: str, recursive: bool):
        """Gère la demande d'analyse"""
        # Nettoyer les résultats précédents
        self.main_window.clear_results()
        self.main_window.show_progress(True)
        self.main_window.set_status("🔍 Analyse en cours...")
        
        # Créer et démarrer le worker
        self.current_worker = ScanWorker(
            use_case=self.use_case,
            directory=Path(directory),
            recursive=recursive
        )
        
        # Connexion des signaux du worker
        self.current_worker.finished.connect(self._on_scan_finished)
        self.current_worker.error.connect(self._on_scan_error)
        self.current_worker.progress.connect(self._on_scan_progress)
        
        # Démarrer
        self.current_worker.start()
    
    def _on_scan_finished(self, decisions: list[GroupingDecision]):
        """Gère la fin de l'analyse"""
        self.main_window.show_progress(False)
        
        if not decisions:
            self.main_window.set_status("ℹ️ Aucun regroupement proposé")
            return
        
        # Afficher les décisions
        self.main_window.display_decisions(decisions)
    
    def _on_scan_error(self, error_message: str):
        """Gère les erreurs d'analyse"""
        self.main_window.show_progress(False)
        self.main_window.set_status(f"❌ Erreur: {error_message}", error=True)
    
    def _on_scan_progress(self, message: str):
        """Gère les messages de progression"""
        self.main_window.set_status(message)
    
    def _on_execution_requested(self, decisions: list[GroupingDecision]):
        """Gère la demande d'exécution"""
        self.main_window.set_status("▶ Exécution en cours...")
        
        try:
            # Valider les décisions
            for decision in decisions:
                decision.validate()
            
            # Exécuter (pour l'instant, juste simuler)
            # TODO: Implémenter l'exécution réelle
            self.use_case._execute_groupings(decisions)
            
            self.main_window.set_status(
                f"✓ {len(decisions)} regroupements exécutés avec succès"
            )
            
        except Exception as e:
            self.main_window.set_status(
                f"❌ Erreur lors de l'exécution: {e}",
                error=True
            )
