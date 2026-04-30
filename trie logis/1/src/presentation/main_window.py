"""
Presentation Layer - Fenêtre principale
Interface utilisateur PySide6
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QCheckBox,
    QTextEdit,
    QSplitter,
    QHeaderView,
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont
from pathlib import Path
from typing import Optional

from src.domain.entities import GroupingDecision


class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application
    
    Aucune logique métier, uniquement présentation
    """
    
    # Signaux
    scan_requested = Signal(str, bool)  # path, recursive
    validation_requested = Signal(list)  # decisions
    execution_requested = Signal(list)  # validated_decisions
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Tri et Fusion Intelligente de Fichiers")
        self.setMinimumSize(1200, 800)
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Titre
        title_label = QLabel("🗂️ Tri et Fusion Intelligente de Fichiers")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Section de sélection de répertoire
        dir_layout = self._create_directory_selection()
        main_layout.addLayout(dir_layout)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Splitter pour les résultats
        splitter = QSplitter(Qt.Vertical)
        
        # Table des décisions
        self.decisions_table = self._create_decisions_table()
        splitter.addWidget(self.decisions_table)
        
        # Zone de détails
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Sélectionnez une décision pour voir les détails...")
        splitter.addWidget(self.details_text)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Boutons d'action
        action_layout = self._create_action_buttons()
        main_layout.addLayout(action_layout)
        
        # Barre de statut
        self.status_label = QLabel("Prêt")
        main_layout.addWidget(self.status_label)
    
    def _create_directory_selection(self) -> QHBoxLayout:
        """Crée la section de sélection de répertoire"""
        layout = QHBoxLayout()
        
        # Label
        label = QLabel("Répertoire:")
        layout.addWidget(label)
        
        # Champ de texte
        self.directory_input = QLineEdit()
        self.directory_input.setPlaceholderText("Sélectionnez un répertoire à analyser...")
        layout.addWidget(self.directory_input)
        
        # Bouton parcourir
        browse_button = QPushButton("📁 Parcourir")
        browse_button.clicked.connect(self._browse_directory)
        layout.addWidget(browse_button)
        
        # Checkbox récursif
        self.recursive_checkbox = QCheckBox("Récursif")
        self.recursive_checkbox.setChecked(True)
        layout.addWidget(self.recursive_checkbox)
        
        # Bouton analyser
        self.scan_button = QPushButton("🔍 Analyser")
        self.scan_button.clicked.connect(self._on_scan_clicked)
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.scan_button)
        
        return layout
    
    def _create_decisions_table(self) -> QTableWidget:
        """Crée la table des décisions"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "✓",
            "Groupe",
            "Nombre de fichiers",
            "Confiance",
            "Statut"
        ])
        
        # Configuration
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(True)
        
        # Connexion pour afficher les détails
        table.itemSelectionChanged.connect(self._on_decision_selected)
        
        return table
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Crée les boutons d'action"""
        layout = QHBoxLayout()
        
        layout.addStretch()
        
        # Bouton valider tout
        self.validate_all_button = QPushButton("✓ Valider tout")
        self.validate_all_button.setEnabled(False)
        self.validate_all_button.clicked.connect(self._on_validate_all)
        layout.addWidget(self.validate_all_button)
        
        # Bouton exécuter
        self.execute_button = QPushButton("▶ Exécuter")
        self.execute_button.setEnabled(False)
        self.execute_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.execute_button.clicked.connect(self._on_execute)
        layout.addWidget(self.execute_button)
        
        return layout
    
    def _apply_styles(self):
        """Applique les styles globaux"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QWidget {
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 14px;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #eaeeef;
                border-radius: 8px;
                background-color: #f8f9fa;
                color: #2c3e50;
                selection-background-color: #2196F3;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: #ffffff;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
                background-color: #ebeef2;
                color: #2c3e50;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #dee2e6;
            }
            QPushButton:pressed {
                background-color: #ced4da;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #eaeeef;
                border-radius: 8px;
                gridline-color: #f1f3f5;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #eaeeef;
                border-radius: 8px;
                padding: 12px;
                line-height: 1.6;
            }
            QProgressBar {
                border: none;
                background-color: #f1f3f5;
                height: 6px;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f3f5;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #ced4da;
                min-height: 20px;
                border-radius: 5px;
            }
        """)
    
    def _browse_directory(self):
        """Ouvre le dialogue de sélection de répertoire"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner un répertoire",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if directory:
            self.directory_input.setText(directory)
    
    def _on_scan_clicked(self):
        """Gère le clic sur le bouton Analyser"""
        directory = self.directory_input.text()
        
        if not directory:
            self.set_status("⚠️ Veuillez sélectionner un répertoire", error=True)
            return
        
        if not Path(directory).exists():
            self.set_status("⚠️ Le répertoire n'existe pas", error=True)
            return
        
        recursive = self.recursive_checkbox.isChecked()
        
        # Émettre le signal
        self.scan_requested.emit(directory, recursive)
    
    def _on_decision_selected(self):
        """Gère la sélection d'une décision"""
        selected_rows = self.decisions_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        
        # Récupérer la décision (stockée dans les données de la ligne)
        decision = self.decisions_table.item(row, 1).data(Qt.UserRole)
        
        if decision:
            self._display_decision_details(decision)
    
    def _on_validate_all(self):
        """Valide toutes les décisions"""
        # Cocher toutes les cases
        for row in range(self.decisions_table.rowCount()):
            checkbox_widget = self.decisions_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox_widget.setChecked(True)
        
        self.set_status("✓ Toutes les décisions ont été validées")
    
    def _on_execute(self):
        """Exécute les décisions validées"""
        validated_decisions = []
        
        for row in range(self.decisions_table.rowCount()):
            checkbox_widget = self.decisions_table.cellWidget(row, 0)
            if checkbox_widget and checkbox_widget.isChecked():
                decision = self.decisions_table.item(row, 1).data(Qt.UserRole)
                if decision:
                    validated_decisions.append(decision)
        
        if not validated_decisions:
            self.set_status("⚠️ Aucune décision validée", error=True)
            return
        
        # Émettre le signal
        self.execution_requested.emit(validated_decisions)
    
    def display_decisions(self, decisions: list[GroupingDecision]):
        """Affiche les décisions dans la table"""
        self.decisions_table.setRowCount(0)
        
        for decision in decisions:
            self._add_decision_row(decision)
        
        # Activer les boutons
        self.validate_all_button.setEnabled(True)
        self.execute_button.setEnabled(True)
        
        self.set_status(f"✓ {len(decisions)} décisions de regroupement générées")
    
    def _add_decision_row(self, decision: GroupingDecision):
        """Ajoute une ligne pour une décision"""
        row = self.decisions_table.rowCount()
        self.decisions_table.insertRow(row)
        
        # Checkbox de validation
        checkbox = QCheckBox()
        checkbox.setChecked(not decision.requires_validation)
        self.decisions_table.setCellWidget(row, 0, checkbox)
        
        # Nom du groupe
        group_item = QTableWidgetItem(decision.group_name)
        group_item.setData(Qt.UserRole, decision)  # Stocker la décision
        self.decisions_table.setItem(row, 1, group_item)
        
        # Nombre de fichiers
        count_item = QTableWidgetItem(str(len(decision.items)))
        count_item.setTextAlignment(Qt.AlignCenter)
        self.decisions_table.setItem(row, 2, count_item)
        
        # Confiance
        confidence_item = QTableWidgetItem(f"{decision.confidence:.1%}")
        confidence_item.setTextAlignment(Qt.AlignCenter)
        
        # Couleur selon la confiance
        if decision.confidence >= 0.85:
            confidence_item.setForeground(Qt.darkGreen)
        elif decision.confidence >= 0.5:
            confidence_item.setForeground(Qt.darkYellow)
        else:
            confidence_item.setForeground(Qt.red)
        
        self.decisions_table.setItem(row, 3, confidence_item)
        
        # Statut
        status = "✓ Auto" if not decision.requires_validation else "⚠ Validation requise"
        status_item = QTableWidgetItem(status)
        status_item.setTextAlignment(Qt.AlignCenter)
        self.decisions_table.setItem(row, 4, status_item)
    
    def _display_decision_details(self, decision: GroupingDecision):
        """Affiche les détails d'une décision"""
        details = []
        
        details.append(f"📁 Groupe: {decision.group_name}")
        details.append(f"📊 Confiance: {decision.confidence:.1%}")
        details.append(f"📝 Nombre de fichiers: {len(decision.items)}")
        details.append("")
        
        details.append("💡 Justification:")
        for reason in decision.reasoning:
            details.append(f"  • {reason}")
        details.append("")
        
        details.append("📄 Fichiers:")
        for item in decision.items:
            details.append(f"  • {item.name}")
        
        self.details_text.setPlainText("\n".join(details))
    
    def set_status(self, message: str, error: bool = False):
        """Définit le message de statut"""
        self.status_label.setText(message)
        
        if error:
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: #333333;")
    
    def show_progress(self, visible: bool = True):
        """Affiche/cache la barre de progression"""
        self.progress_bar.setVisible(visible)
        
        if visible:
            self.progress_bar.setRange(0, 0)  # Mode indéterminé
            self.scan_button.setEnabled(False)
        else:
            self.scan_button.setEnabled(True)
    
    def clear_results(self):
        """Efface les résultats"""
        self.decisions_table.setRowCount(0)
        self.details_text.clear()
        self.validate_all_button.setEnabled(False)
        self.execute_button.setEnabled(False)
