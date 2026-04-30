"""
SmartSort - Application Entry Point
Point d'entrée principal avec gestion des dépendances
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from main_window import SmartSortWindow


def main():
    """Point d'entrée principal"""
    # Configuration Qt pour Windows 11
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Création de l'application
    app = QApplication(sys.argv)
    app.setApplicationName("SmartSort")
    app.setOrganizationName("SmartSort")
    app.setApplicationVersion("1.0.0")
    
    # Style Windows 11
    app.setStyle("Fusion")
    
    # Fenêtre principale
    window = SmartSortWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
