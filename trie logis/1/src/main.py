"""
Point d'entrée principal de l'application
Configuration et injection de dépendances
"""

import sys
import os
import logging
import structlog
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Support High DPI pour Windows 10/11
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTOSCREENSCALEFACTOR"] = "1"

from src.presentation.main_window import MainWindow
from src.presentation.controller import MainController, UIValidationService
from src.application.use_cases import FileOrganizationUseCase
from src.infrastructure.filesystem.repository import WindowsFileSystemRepository
from src.infrastructure.algorithms.semantic_extractor import SemanticExtractorService
from src.infrastructure.algorithms.similarity import AdvancedSimilarityCalculator
from src.infrastructure.algorithms.grouping import HierarchicalGroupingStrategy


def setup_logging():
    """Configure le logging structuré"""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()


def create_application():
    """
    Crée et configure l'application
    Injection de dépendances manuelle (Clean Architecture)
    """
    
    # 1. Configuration du logging
    logger = setup_logging()
    logger.info("Démarrage de l'application")
    
    # 2. Infrastructure - Repositories
    filesystem_repo = WindowsFileSystemRepository(exclude_hidden=True)
    logger.info("Repository filesystem initialisé")
    
    # 3. Infrastructure - Algorithmes
    semantic_extractor = SemanticExtractorService()
    logger.info("Extracteur sémantique initialisé")
    
    similarity_calculator = AdvancedSimilarityCalculator(
        title_weight=0.5,
        structural_weight=0.3,
        temporal_weight=0.1,
        quality_weight=0.1,
    )
    logger.info("Calculateur de similarité initialisé")
    
    grouping_strategy = HierarchicalGroupingStrategy(
        high_confidence_threshold=0.85,
        ambiguous_min_threshold=0.5,
        logger=logger,
    )
    logger.info("Stratégie de regroupement initialisée")
    
    # 4. Presentation - Services
    validation_service = UIValidationService()
    logger.info("Service de validation UI initialisé")
    
    # 5. Application - Use Cases
    use_case = FileOrganizationUseCase(
        filesystem_repo=filesystem_repo,
        semantic_extractor=semantic_extractor,
        similarity_calculator=similarity_calculator,
        grouping_strategy=grouping_strategy,
        validation_service=validation_service,
        logger=logger,
    )
    logger.info("Cas d'usage initialisé")
    
    # 6. Presentation - UI
    app = QApplication(sys.argv)
    app.setApplicationName("Tri et Fusion Intelligente")
    app.setOrganizationName("FileOrganizer")
    
    main_window = MainWindow()
    logger.info("Fenêtre principale créée")
    
    # 7. Presentation - Contrôleur
    controller = MainController(
        main_window=main_window,
        use_case=use_case,
    )
    logger.info("Contrôleur initialisé")
    
    return app, main_window, controller, logger


def main():
    """Point d'entrée principal"""
    # Réglages High DPI AVANT la création de l'application
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTOSCREENSCALEFACTOR"] = "1"
    
    # Création de l'application (le logger sera configuré à l'intérieur de create_application)
    try:
        # On doit créer l'instance QApplication avant de régler les attributs de scaling dans certains cas,
        # mais AA_EnableHighDpiScaling doit être mis AVANT.
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app, main_window, controller, logger = create_application()
        
        # Politique de rendu pour éviter le flou sur les écrans à mise à l'échelle non entière (ex: 125%, 150%)
        if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
            app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        
        # Afficher la fenêtre
        main_window.show()
        logger.info("Application démarrée")
        
        # Lancer la boucle d'événements
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
