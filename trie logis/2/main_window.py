"""
SmartSort - Main Window (PySide6)
Interface moderne Windows 11 Fluent Design avec threading
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QTextEdit, QSplitter, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPalette, QColor
from pathlib import Path
from typing import List, Optional

from normalizer import Normalizer
from merger import DirectoryMerger, MergeAction
from executor import MergeExecutor, ExecutionResult


class AnalysisThread(QThread):
    """Thread pour l'analyse en arrière-plan (60 FPS UI)"""
    
    progress = Signal(int, int, str)  # current, total, message
    finished = Signal(list)  # actions
    error = Signal(str)
    
    def __init__(self, root_path: Path):
        super().__init__()
        self.root_path = root_path
        self.normalizer = Normalizer()
        self.merger = DirectoryMerger(self.normalizer)
    
    def run(self):
        """Exécution de l'analyse"""
        try:
            self.progress.emit(0, 100, "Analyse en cours...")
            actions = self.merger.analyze_directories(self.root_path)
            self.progress.emit(100, 100, "Analyse terminée")
            self.finished.emit(actions)
        except Exception as e:
            self.error.emit(str(e))


class ExecutionThread(QThread):
    """Thread pour l'exécution des fusions"""
    
    progress = Signal(int, int, str)  # current, total, message
    finished = Signal(dict)  # summary
    error = Signal(str)
    
    def __init__(self, actions: List[MergeAction]):
        super().__init__()
        self.actions = actions
        self.executor = MergeExecutor()
    
    def run(self):
        """Exécution des fusions"""
        try:
            def progress_callback(current, total, message):
                self.progress.emit(current, total, message)
            
            self.executor.execute_actions(self.actions, progress_callback)
            summary = self.executor.get_summary()
            self.finished.emit(summary)
        except Exception as e:
            self.error.emit(str(e))


class SmartSortWindow(QMainWindow):
    """
    Fenêtre principale avec design Windows 11 Fluent
    Architecture : Header + Content (Split) + Footer
    """
    
    def __init__(self):
        super().__init__()
        self.current_actions: List[MergeAction] = []
        self.analysis_thread: Optional[AnalysisThread] = None
        self.execution_thread: Optional[ExecutionThread] = None
        
        self.init_ui()
        self.apply_fluent_style()
    
    def init_ui(self):
        """Initialisation de l'interface"""
        self.setWindowTitle("SmartSort - Intelligent Directory Organizer")
        self.setMinimumSize(1200, 800)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # === HEADER ===
        header = self._create_header()
        layout.addWidget(header)
        
        # === PATH SELECTOR ===
        path_section = self._create_path_selector()
        layout.addWidget(path_section)
        
        # === CONTENT (SPLIT VIEW) ===
        splitter = QSplitter(Qt.Horizontal)
        
        # Panneau gauche : Arbre de prévisualisation
        self.tree_widget = self._create_tree_widget()
        splitter.addWidget(self.tree_widget)
        
        # Panneau droit : Log
        self.log_widget = self._create_log_widget()
        splitter.addWidget(self.log_widget)
        
        splitter.setSizes([700, 500])
        layout.addWidget(splitter, 1)  # Stretch factor
        
        # === PROGRESS BAR ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # === FOOTER (ACTION BUTTONS) ===
        footer = self._create_footer()
        layout.addWidget(footer)
    
    def _create_header(self) -> QWidget:
        """Crée le header avec titre et description"""
        container = QFrame()
        container.setObjectName("header")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 10)
        
        # Titre
        title = QLabel("🎯 SmartSort")
        title.setObjectName("title")
        title_font = QFont("Segoe UI", 32, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Sous-titre
        subtitle = QLabel("Analyse, regroupe et fusionne intelligemment vos répertoires désordonnés")
        subtitle.setObjectName("subtitle")
        subtitle_font = QFont("Segoe UI", 11)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)
        
        return container
    
    def _create_path_selector(self) -> QWidget:
        """Crée la section de sélection de chemin"""
        container = QFrame()
        container.setObjectName("pathSelector")
        layout = QHBoxLayout(container)
        
        label = QLabel("📁 Répertoire :")
        label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(label)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Sélectionnez un répertoire à analyser...")
        self.path_input.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.path_input, 1)
        
        browse_btn = QPushButton("Parcourir")
        browse_btn.setObjectName("browseButton")
        browse_btn.clicked.connect(self.browse_directory)
        layout.addWidget(browse_btn)
        
        self.analyze_btn = QPushButton("🔍 Analyser")
        self.analyze_btn.setObjectName("analyzeButton")
        self.analyze_btn.clicked.connect(self.start_analysis)
        layout.addWidget(self.analyze_btn)
        
        return container
    
    def _create_tree_widget(self) -> QTreeWidget:
        """Crée l'arbre de prévisualisation"""
        tree = QTreeWidget()
        tree.setHeaderLabels(["Source", "→", "Destination", "Type", "Raison"])
        tree.setColumnWidth(0, 250)
        tree.setColumnWidth(1, 30)
        tree.setColumnWidth(2, 250)
        tree.setColumnWidth(3, 100)
        tree.setFont(QFont("Segoe UI", 9))
        tree.setAlternatingRowColors(True)
        return tree
    
    def _create_log_widget(self) -> QTextEdit:
        """Crée le panneau de log"""
        log = QTextEdit()
        log.setReadOnly(True)
        log.setFont(QFont("Consolas", 9))
        log.setPlaceholderText("Les logs d'exécution apparaîtront ici...")
        return log
    
    def _create_footer(self) -> QWidget:
        """Crée le footer avec boutons d'action"""
        container = QFrame()
        layout = QHBoxLayout(container)
        
        layout.addStretch()
        
        self.apply_btn = QPushButton("✅ Appliquer les Fusions")
        self.apply_btn.setObjectName("applyButton")
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.start_execution)
        self.apply_btn.setMinimumHeight(45)
        layout.addWidget(self.apply_btn)
        
        return container
    
    def apply_fluent_style(self):
        """
        Applique le style Windows 11 Fluent Design
        Dark mode avec accents modernes
        """
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            
            QWidget {
                color: #ffffff;
                background-color: #1e1e1e;
            }
            
            #header {
                background-color: #252525;
                border-radius: 8px;
                padding: 20px;
            }
            
            #title {
                color: #00d4ff;
                font-weight: bold;
            }
            
            #subtitle {
                color: #b0b0b0;
            }
            
            #pathSelector {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 15px;
            }
            
            QLineEdit {
                background-color: #3a3a3a;
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 10pt;
            }
            
            QLineEdit:focus {
                border: 2px solid #00d4ff;
            }
            
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 10pt;
            }
            
            QPushButton:hover {
                background-color: #1084d8;
            }
            
            QPushButton:pressed {
                background-color: #006cbd;
            }
            
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #6a6a6a;
            }
            
            #browseButton {
                background-color: #4a4a4a;
            }
            
            #browseButton:hover {
                background-color: #5a5a5a;
            }
            
            #analyzeButton {
                background-color: #00b294;
            }
            
            #analyzeButton:hover {
                background-color: #00c9a7;
            }
            
            #applyButton {
                background-color: #107c10;
                font-size: 11pt;
            }
            
            #applyButton:hover {
                background-color: #128c12;
            }
            
            QTreeWidget {
                background-color: #2d2d2d;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                alternate-background-color: #323232;
            }
            
            QTreeWidget::item {
                padding: 5px;
            }
            
            QTreeWidget::item:selected {
                background-color: #0078d4;
            }
            
            QHeaderView::section {
                background-color: #3a3a3a;
                color: #ffffff;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            
            QTextEdit {
                background-color: #1a1a1a;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                color: #d4d4d4;
                padding: 10px;
            }
            
            QProgressBar {
                background-color: #2d2d2d;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                text-align: center;
                color: white;
                height: 25px;
            }
            
            QProgressBar::chunk {
                background-color: #00d4ff;
                border-radius: 5px;
            }
            
            QSplitter::handle {
                background-color: #4a4a4a;
                width: 2px;
            }
        """)
    
    def browse_directory(self):
        """Ouvre le dialogue de sélection de répertoire"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner un répertoire",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if directory:
            self.path_input.setText(directory)
            self.log(f"📁 Répertoire sélectionné : {directory}")
    
    def start_analysis(self):
        """Démarre l'analyse en arrière-plan"""
        path_str = self.path_input.text().strip()
        if not path_str:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un répertoire")
            return
        
        path = Path(path_str)
        if not path.exists() or not path.is_dir():
            QMessageBox.warning(self, "Erreur", "Le chemin spécifié n'est pas valide")
            return
        
        # Réinitialise l'UI
        self.tree_widget.clear()
        self.current_actions = []
        self.apply_btn.setEnabled(False)
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.log(f"🔍 Démarrage de l'analyse de : {path}")
        
        # Lance le thread d'analyse
        self.analysis_thread = AnalysisThread(path)
        self.analysis_thread.progress.connect(self.update_progress)
        self.analysis_thread.finished.connect(self.on_analysis_finished)
        self.analysis_thread.error.connect(self.on_error)
        self.analysis_thread.start()
    
    def on_analysis_finished(self, actions: List[MergeAction]):
        """Callback quand l'analyse est terminée"""
        self.current_actions = actions
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if not actions:
            self.log("✅ Aucune fusion nécessaire - Le répertoire est déjà organisé!")
            QMessageBox.information(self, "Analyse terminée", "Aucune fusion nécessaire")
            return
        
        self.log(f"✅ Analyse terminée : {len(actions)} actions de fusion proposées")
        self.populate_tree(actions)
        self.apply_btn.setEnabled(True)
    
    def populate_tree(self, actions: List[MergeAction]):
        """Remplit l'arbre avec les actions proposées"""
        self.tree_widget.clear()
        
        for action in actions:
            # Groupe parent
            parent_item = QTreeWidgetItem(self.tree_widget)
            parent_item.setText(0, f"📦 Groupe ({len(action.source_paths)} sources)")
            parent_item.setText(2, action.destination_path.name)
            parent_item.setText(3, action.action_type.upper())
            parent_item.setText(4, action.reason)
            
            # Sous-éléments (sources)
            for source in action.source_paths:
                child = QTreeWidgetItem(parent_item)
                child.setText(0, f"  └─ {source.name}")
                child.setText(1, "→")
                child.setForeground(1, QColor("#00d4ff"))
        
        self.tree_widget.expandAll()
    
    def start_execution(self):
        """Démarre l'exécution des fusions"""
        if not self.current_actions:
            return
        
        # Confirmation
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Êtes-vous sûr de vouloir appliquer {len(self.current_actions)} fusions ?\n\n"
            "Cette opération déplacera des fichiers.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Désactive les boutons
        self.apply_btn.setEnabled(False)
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.log("🚀 Démarrage de l'exécution des fusions...")
        
        # Lance le thread d'exécution
        self.execution_thread = ExecutionThread(self.current_actions)
        self.execution_thread.progress.connect(self.update_progress)
        self.execution_thread.finished.connect(self.on_execution_finished)
        self.execution_thread.error.connect(self.on_error)
        self.execution_thread.start()
    
    def on_execution_finished(self, summary: dict):
        """Callback quand l'exécution est terminée"""
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Affiche le résumé
        self.log("\n" + "="*60)
        self.log("📊 RÉSUMÉ DE L'EXÉCUTION")
        self.log("="*60)
        self.log(f"✅ Actions réussies : {summary['successful']}/{summary['total_actions']}")
        self.log(f"❌ Actions échouées : {summary['failed']}")
        self.log(f"📁 Fichiers déplacés : {summary['total_files_moved']}")
        
        if summary['errors']:
            self.log("\n⚠️ ERREURS :")
            for error in summary['errors']:
                self.log(f"  - {error}")
        
        self.log("="*60 + "\n")
        
        # Message de succès
        QMessageBox.information(
            self,
            "Exécution terminée",
            f"Fusions terminées avec succès!\n\n"
            f"✅ {summary['successful']} actions réussies\n"
            f"📁 {summary['total_files_moved']} fichiers déplacés"
        )
        
        # Réinitialise
        self.tree_widget.clear()
        self.current_actions = []
    
    def update_progress(self, current: int, total: int, message: str):
        """Met à jour la barre de progression"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_bar.setFormat(f"{message} ({current}/{total})")
        self.log(f"⏳ {message}")
    
    def on_error(self, error: str):
        """Gestion des erreurs"""
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.log(f"❌ ERREUR : {error}")
        QMessageBox.critical(self, "Erreur", f"Une erreur est survenue :\n\n{error}")
    
    def log(self, message: str):
        """Ajoute un message au log"""
        self.log_widget.append(message)
