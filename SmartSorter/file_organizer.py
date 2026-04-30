#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application de Tri Automatique de Fichiers et Dossiers
========================================================
Application desktop permettant de regrouper automatiquement des fichiers ou dossiers
ayant des noms similaires selon des règles définies par l'utilisateur.

Auteur: Ingénieur Python Senior
Version: 1.0.0
"""

import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import List, Dict, Set, Optional
from collections import defaultdict
from difflib import SequenceMatcher


class FileOrganizerApp:
    """
    Application principale de tri de fichiers et dossiers.
    
    Cette classe gère l'interface graphique et orchestre toutes les opérations
    de tri selon les règles définies par l'utilisateur.
    """
    
    # Définition des types de fichiers supportés
    FILE_TYPES = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
        'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus']
    }
    
    def __init__(self, root: tk.Tk):
        """
        Initialise l'application avec tous ses composants GUI.
        
        Args:
            root: Fenêtre principale Tkinter
        """
        self.root = root
        self.root.title("Organisateur de Fichiers et Dossiers - v1.0")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Variables de configuration
        self.source_folder = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.sort_type = tk.StringVar(value="files")
        self.file_type_filter = tk.StringVar(value="all")
        self.use_custom_destination = tk.BooleanVar(value=False)
        self.similarity_threshold = tk.DoubleVar(value=0.7)
        self.ignore_patterns = []
        
        # Initialisation de l'interface
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure tous les éléments de l'interface utilisateur."""
        # Style général
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # === SECTION 1: Sélection du dossier source ===
        self._create_source_section(main_frame, row=0)
        
        # === SECTION 2: Type de tri ===
        self._create_sort_type_section(main_frame, row=1)
        
        # === SECTION 3: Filtres de fichiers ===
        self._create_file_filter_section(main_frame, row=2)
        
        # === SECTION 4: Règles d'ignorance ===
        self._create_ignore_patterns_section(main_frame, row=3)
        
        # === SECTION 5: Seuil de similarité ===
        self._create_similarity_section(main_frame, row=4)
        
        # === SECTION 6: Destination ===
        self._create_destination_section(main_frame, row=5)
        
        # === SECTION 7: Zone de logs ===
        self._create_log_section(main_frame, row=6)
        
        # === SECTION 8: Boutons d'action ===
        self._create_action_buttons(main_frame, row=7)
        
    def _create_source_section(self, parent: ttk.Frame, row: int):
        """Crée la section de sélection du dossier source."""
        frame = ttk.LabelFrame(parent, text="📁 Dossier Source", padding="10")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="Chemin:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(frame, textvariable=self.source_folder, state='readonly').grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(frame, text="Parcourir...", command=self._browse_source).grid(
            row=0, column=2, padx=5
        )
        
    def _create_sort_type_section(self, parent: ttk.Frame, row: int):
        """Crée la section de sélection du type de tri."""
        frame = ttk.LabelFrame(parent, text="🔧 Type de Tri", padding="10")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(
            frame, text="Trier des fichiers", variable=self.sort_type,
            value="files", command=self._on_sort_type_change
        ).grid(row=0, column=0, sticky=tk.W, padx=20)
        
        ttk.Radiobutton(
            frame, text="Trier des dossiers", variable=self.sort_type,
            value="folders", command=self._on_sort_type_change
        ).grid(row=0, column=1, sticky=tk.W, padx=20)
        
    def _create_file_filter_section(self, parent: ttk.Frame, row: int):
        """Crée la section de filtrage par type de fichier."""
        self.file_filter_frame = ttk.LabelFrame(parent, text="🎯 Filtres de Fichiers", padding="10")
        self.file_filter_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.file_filter_frame, text="Type de fichiers à inclure:").grid(
            row=0, column=0, sticky=tk.W, padx=5
        )
        
        filter_combo = ttk.Combobox(
            self.file_filter_frame, textvariable=self.file_type_filter,
            values=['all', 'images', 'videos', 'documents', 'audio'],
            state='readonly', width=20
        )
        filter_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        filter_combo.current(0)
        
    def _create_ignore_patterns_section(self, parent: ttk.Frame, row: int):
        """Crée la section de gestion des motifs à ignorer."""
        frame = ttk.LabelFrame(parent, text="🚫 Règles d'Ignorance dans les Noms (Multiples Autorisées)", padding="10")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        frame.columnconfigure(0, weight=1)
        parent.rowconfigure(row, weight=1)
        
        # Sous-frame pour l'ajout de patterns
        add_frame = ttk.Frame(frame)
        add_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        add_frame.columnconfigure(1, weight=1)
        
        ttk.Label(add_frame, text="Motif à ignorer:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.pattern_entry = ttk.Entry(add_frame)
        self.pattern_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(add_frame, text="➕ Ajouter", command=self._add_ignore_pattern).grid(
            row=0, column=2, padx=5
        )
        
        # Boutons de raccourci pour motifs courants
        shortcuts_frame = ttk.LabelFrame(frame, text="⚡ Raccourcis (Cliquez pour ajouter)", padding="5")
        shortcuts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Définition des raccourcis avec leurs descriptions
        shortcuts = [
            (r"\[.*?\]", "Crochets [...]"),
            (r"\(.*?\)", "Parenthèses (...)"),
            (r"_\d+", "Numéros _123"),
            (r"\d{4}", "Années 2024"),
            (r"_v\d+\.\d+", "Versions v1.0"),
            (r"_COPY|_copy", "Copies"),
        ]
        
        # Créer les boutons en grille
        for idx, (pattern, description) in enumerate(shortcuts):
            row_pos = idx // 3
            col_pos = idx % 3
            btn = ttk.Button(
                shortcuts_frame, 
                text=description,
                command=lambda p=pattern: self._add_pattern_from_shortcut(p),
                width=15
            )
            btn.grid(row=row_pos, column=col_pos, padx=3, pady=3, sticky=tk.W)
        
        # Aide améliorée
        help_text = (
            "💡 Vous pouvez ajouter PLUSIEURS motifs simultanément !\n"
            "Exemple: Ajoutez [.*?] ET _\\d+ pour ignorer les crochets ET les numéros\n"
            "Tous les motifs actifs seront appliqués en même temps lors du tri."
        )
        help_label = ttk.Label(frame, text=help_text, foreground="blue", justify=tk.LEFT, 
                               font=('TkDefaultFont', 9, 'italic'))
        help_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Liste des patterns actifs
        list_frame = ttk.Frame(frame)
        list_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        
        ttk.Label(list_frame, text="📋 Motifs actifs (appliqués simultanément):").grid(
            row=0, column=0, sticky=tk.W, padx=5
        )
        
        # Listbox avec scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        self.patterns_listbox = tk.Listbox(list_frame, height=4, yscrollcommand=scrollbar.set)
        self.patterns_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        scrollbar.config(command=self.patterns_listbox.yview)
        list_frame.rowconfigure(1, weight=1)
        
        # Boutons de gestion
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="🗑️ Supprimer sélectionné", 
                  command=self._remove_ignore_pattern).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🧹 Tout effacer", 
                  command=self._clear_all_patterns).pack(side=tk.LEFT, padx=5)
        
    def _create_similarity_section(self, parent: ttk.Frame, row: int):
        """Crée la section de configuration du seuil de similarité."""
        frame = ttk.LabelFrame(parent, text="📊 Seuil de Similarité", padding="10")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="Similarité minimale (0.0 - 1.0):").grid(
            row=0, column=0, sticky=tk.W, padx=5
        )
        
        scale = ttk.Scale(
            frame, from_=0.0, to=1.0, variable=self.similarity_threshold,
            orient=tk.HORIZONTAL, command=self._update_similarity_label
        )
        scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        self.similarity_label = ttk.Label(frame, text=f"{self.similarity_threshold.get():.2f}")
        self.similarity_label.grid(row=0, column=2, padx=5)
        
        help_label = ttk.Label(
            frame,
            text="Plus la valeur est élevée, plus les noms doivent être similaires pour être regroupés",
            foreground="gray", font=('TkDefaultFont', 8)
        )
        help_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
    def _create_destination_section(self, parent: ttk.Frame, row: int):
        """Crée la section de sélection de la destination."""
        frame = ttk.LabelFrame(parent, text="📂 Destination", padding="10")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(1, weight=1)
        
        ttk.Checkbutton(
            frame, text="Utiliser un dossier de destination personnalisé",
            variable=self.use_custom_destination, command=self._toggle_destination
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        self.dest_label = ttk.Label(frame, text="Chemin:", state='disabled')
        self.dest_label.grid(row=1, column=0, sticky=tk.W, padx=5)
        
        self.dest_entry = ttk.Entry(frame, textvariable=self.destination_folder, state='disabled')
        self.dest_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        self.dest_button = ttk.Button(frame, text="Parcourir...", command=self._browse_destination, state='disabled')
        self.dest_button.grid(row=1, column=2, padx=5)
        
    def _create_log_section(self, parent: ttk.Frame, row: int):
        """Crée la zone d'affichage des logs."""
        frame = ttk.LabelFrame(parent, text="📋 Journal d'Activité", padding="10")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        parent.rowconfigure(row, weight=2)
        
        self.log_text = scrolledtext.ScrolledText(frame, height=10, state='disabled', wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration des tags pour la coloration
        self.log_text.tag_config('info', foreground='blue')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('error', foreground='red')
        
    def _create_action_buttons(self, parent: ttk.Frame, row: int):
        """Crée les boutons d'action principaux."""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(
            frame, text="🔍 Prévisualiser", command=self._preview_organization
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame, text="▶️ Organiser les Fichiers", command=self._organize_files,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="🗑️ Effacer les Logs", command=self._clear_logs).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="❌ Quitter", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
    # === MÉTHODES DE CALLBACK ===
    
    def _browse_source(self):
        """Ouvre un dialogue pour sélectionner le dossier source."""
        folder = filedialog.askdirectory(title="Sélectionner le dossier source")
        if folder:
            self.source_folder.set(folder)
            self._log(f"Dossier source sélectionné: {folder}", 'info')
            
    def _browse_destination(self):
        """Ouvre un dialogue pour sélectionner le dossier de destination."""
        folder = filedialog.askdirectory(title="Sélectionner le dossier de destination")
        if folder:
            self.destination_folder.set(folder)
            self._log(f"Dossier de destination sélectionné: {folder}", 'info')
            
    def _on_sort_type_change(self):
        """Gère le changement de type de tri (fichiers/dossiers)."""
        if self.sort_type.get() == "folders":
            # Désactiver les filtres de fichiers pour le tri de dossiers
            for child in self.file_filter_frame.winfo_children():
                child.configure(state='disabled')
        else:
            # Activer les filtres de fichiers
            for child in self.file_filter_frame.winfo_children():
                if isinstance(child, (ttk.Label, ttk.Combobox)):
                    child.configure(state='normal' if isinstance(child, ttk.Label) else 'readonly')
                    
    def _toggle_destination(self):
        """Active/désactive la sélection de destination personnalisée."""
        if self.use_custom_destination.get():
            self.dest_label.configure(state='normal')
            self.dest_entry.configure(state='normal')
            self.dest_button.configure(state='normal')
        else:
            self.dest_label.configure(state='disabled')
            self.dest_entry.configure(state='disabled')
            self.dest_button.configure(state='disabled')
            self.destination_folder.set("")
            
    def _update_similarity_label(self, value):
        """Met à jour l'affichage du seuil de similarité."""
        self.similarity_label.config(text=f"{float(value):.2f}")
        
    def _add_ignore_pattern(self):
        """Ajoute un motif à la liste des patterns à ignorer."""
        pattern = self.pattern_entry.get().strip()
        if pattern:
            if pattern not in self.ignore_patterns:
                self.ignore_patterns.append(pattern)
                self.patterns_listbox.insert(tk.END, pattern)
                self.pattern_entry.delete(0, tk.END)
                self._log(f"Motif ajouté: {pattern}", 'info')
            else:
                messagebox.showwarning("Doublon", "Ce motif existe déjà dans la liste.")
        else:
            messagebox.showwarning("Entrée vide", "Veuillez entrer un motif valide.")
            
    def _remove_ignore_pattern(self):
        """Supprime le motif sélectionné de la liste."""
        selection = self.patterns_listbox.curselection()
        if selection:
            index = selection[0]
            pattern = self.ignore_patterns[index]
            self.ignore_patterns.pop(index)
            self.patterns_listbox.delete(index)
            self._log(f"Motif supprimé: {pattern}", 'info')
        else:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un motif à supprimer.")
    
    def _add_pattern_from_shortcut(self, pattern: str):
        """
        Ajoute un motif prédéfini depuis les boutons de raccourci.
        
        Args:
            pattern: Motif regex à ajouter
        """
        if pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
            self.patterns_listbox.insert(tk.END, pattern)
            self._log(f"Motif ajouté (raccourci): {pattern}", 'success')
        else:
            messagebox.showinfo("Déjà présent", f"Le motif '{pattern}' est déjà dans la liste.")
    
    def _clear_all_patterns(self):
        """Efface tous les motifs d'ignorance actifs."""
        if self.ignore_patterns:
            response = messagebox.askyesno(
                "Confirmation",
                f"Voulez-vous vraiment supprimer tous les {len(self.ignore_patterns)} motifs actifs ?"
            )
            if response:
                count = len(self.ignore_patterns)
                self.ignore_patterns.clear()
                self.patterns_listbox.delete(0, tk.END)
                self._log(f"Tous les motifs ont été effacés ({count} motifs)", 'warning')
        else:
            messagebox.showinfo("Liste vide", "Aucun motif à effacer.")
            
    def _clear_logs(self):
        """Efface le contenu de la zone de logs."""
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
    # === MÉTHODES UTILITAIRES ===
    
    def _log(self, message: str, level: str = 'info'):
        """
        Ajoute un message au journal d'activité.
        
        Args:
            message: Message à afficher
            level: Niveau de log ('info', 'success', 'warning', 'error')
        """
        self.log_text.configure(state='normal')
        timestamp = Path(__file__).stat().st_mtime  # Simulé pour l'exemple
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()
        
    def _clean_name(self, name: str) -> str:
        """
        Nettoie un nom en appliquant les règles d'ignorance.
        
        Args:
            name: Nom à nettoyer
            
        Returns:
            Nom nettoyé
        """
        cleaned = name
        for pattern in self.ignore_patterns:
            try:
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
            except re.error as e:
                self._log(f"Erreur dans le motif regex '{pattern}': {e}", 'error')
        
        # Nettoyer les espaces multiples et trim
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calcule la similarité entre deux noms.
        
        Args:
            name1: Premier nom
            name2: Deuxième nom
            
        Returns:
            Score de similarité entre 0.0 et 1.0
        """
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
    
    def _get_items_to_process(self) -> List[Path]:
        """
        Récupère la liste des éléments à traiter selon les critères.
        
        Returns:
            Liste des chemins des éléments à traiter
        """
        source = Path(self.source_folder.get())
        if not source.exists():
            raise ValueError("Le dossier source n'existe pas.")
            
        items = []
        
        if self.sort_type.get() == "files":
            # Traiter les fichiers
            file_filter = self.file_type_filter.get()
            
            for item in source.iterdir():
                if item.is_file():
                    # Appliquer le filtre de type
                    if file_filter == 'all':
                        items.append(item)
                    elif file_filter in self.FILE_TYPES:
                        if item.suffix.lower() in self.FILE_TYPES[file_filter]:
                            items.append(item)
        else:
            # Traiter les dossiers
            for item in source.iterdir():
                if item.is_dir():
                    items.append(item)
                    
        return items
    
    def _group_items(self, items: List[Path]) -> Dict[str, List[Path]]:
        """
        Regroupe les éléments par similarité de nom.
        
        Args:
            items: Liste des éléments à regrouper
            
        Returns:
            Dictionnaire {nom_groupe: [liste_éléments]}
        """
        groups = defaultdict(list)
        processed = set()
        threshold = self.similarity_threshold.get()
        
        for item in items:
            if item in processed:
                continue
                
            # Nettoyer le nom (sans extension pour les fichiers)
            if item.is_file():
                clean_name = self._clean_name(item.stem)
            else:
                clean_name = self._clean_name(item.name)
                
            # Trouver un groupe existant similaire
            group_found = False
            for group_name in list(groups.keys()):
                similarity = self._calculate_similarity(clean_name, group_name)
                if similarity >= threshold:
                    groups[group_name].append(item)
                    processed.add(item)
                    group_found = True
                    break
                    
            # Créer un nouveau groupe si aucun groupe similaire trouvé
            if not group_found:
                groups[clean_name].append(item)
                processed.add(item)
                
        # Filtrer les groupes avec un seul élément (pas besoin de regroupement)
        return {k: v for k, v in groups.items() if len(v) > 1}
    
    def _validate_configuration(self) -> bool:
        """
        Valide la configuration avant le traitement.
        
        Returns:
            True si la configuration est valide, False sinon
        """
        if not self.source_folder.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier source.")
            return False
            
        if not Path(self.source_folder.get()).exists():
            messagebox.showerror("Erreur", "Le dossier source n'existe pas.")
            return False
            
        if self.use_custom_destination.get():
            if not self.destination_folder.get():
                messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de destination.")
                return False
            if not Path(self.destination_folder.get()).exists():
                messagebox.showerror("Erreur", "Le dossier de destination n'existe pas.")
                return False
                
        return True
    
    def _preview_organization(self):
        """Affiche une prévisualisation de l'organisation sans effectuer de modifications."""
        if not self._validate_configuration():
            return
            
        try:
            self._log("=== PRÉVISUALISATION ===", 'info')
            items = self._get_items_to_process()
            self._log(f"Éléments trouvés: {len(items)}", 'info')
            
            if not items:
                self._log("Aucun élément à traiter.", 'warning')
                messagebox.showinfo("Prévisualisation", "Aucun élément trouvé à traiter.")
                return
                
            groups = self._group_items(items)
            
            if not groups:
                self._log("Aucun regroupement possible avec le seuil actuel.", 'warning')
                messagebox.showinfo(
                    "Prévisualisation",
                    "Aucun regroupement possible. Essayez de réduire le seuil de similarité."
                )
                return
                
            self._log(f"\nGroupes créés: {len(groups)}", 'success')
            
            for group_name, group_items in groups.items():
                self._log(f"\n📁 Groupe: '{group_name}' ({len(group_items)} éléments)", 'info')
                for item in group_items:
                    self._log(f"   • {item.name}", 'info')
                    
            messagebox.showinfo(
                "Prévisualisation",
                f"{len(groups)} groupes seront créés pour {sum(len(v) for v in groups.values())} éléments."
            )
            
        except Exception as e:
            self._log(f"Erreur lors de la prévisualisation: {str(e)}", 'error')
            messagebox.showerror("Erreur", f"Une erreur est survenue:\n{str(e)}")
            
    def _organize_files(self):
        """Effectue l'organisation des fichiers/dossiers."""
        if not self._validate_configuration():
            return
            
        # Confirmation de l'utilisateur
        response = messagebox.askyesno(
            "Confirmation",
            "Cette opération va déplacer des fichiers/dossiers.\nVoulez-vous continuer?",
            icon='warning'
        )
        
        if not response:
            self._log("Opération annulée par l'utilisateur.", 'warning')
            return
            
        try:
            self._log("=== DÉBUT DE L'ORGANISATION ===", 'info')
            items = self._get_items_to_process()
            self._log(f"Éléments à traiter: {len(items)}", 'info')
            
            if not items:
                self._log("Aucun élément à traiter.", 'warning')
                messagebox.showinfo("Terminé", "Aucun élément trouvé à traiter.")
                return
                
            groups = self._group_items(items)
            
            if not groups:
                self._log("Aucun regroupement possible.", 'warning')
                messagebox.showinfo("Terminé", "Aucun regroupement nécessaire.")
                return
                
            # Déterminer le dossier de base pour la création des groupes
            if self.use_custom_destination.get():
                base_folder = Path(self.destination_folder.get())
            else:
                base_folder = Path(self.source_folder.get())
                
            moved_count = 0
            error_count = 0
            
            for group_name, group_items in groups.items():
                # Créer le dossier du groupe
                # Nettoyer le nom du groupe pour éviter les caractères invalides
                safe_group_name = re.sub(r'[<>:"/\\|?*]', '_', group_name)
                if not safe_group_name:
                    safe_group_name = "groupe_sans_nom"
                    
                group_folder = base_folder / safe_group_name
                
                try:
                    group_folder.mkdir(exist_ok=True)
                    self._log(f"\n📁 Création du groupe: '{safe_group_name}'", 'success')
                    
                    for item in group_items:
                        try:
                            destination = group_folder / item.name
                            
                            # Gérer les conflits de noms
                            if destination.exists():
                                base_name = destination.stem if destination.suffix else destination.name
                                suffix = destination.suffix
                                counter = 1
                                while destination.exists():
                                    new_name = f"{base_name}_{counter}{suffix}"
                                    destination = group_folder / new_name
                                    counter += 1
                                    
                            shutil.move(str(item), str(destination))
                            self._log(f"   ✓ Déplacé: {item.name}", 'success')
                            moved_count += 1
                            
                        except Exception as e:
                            self._log(f"   ✗ Erreur avec {item.name}: {str(e)}", 'error')
                            error_count += 1
                            
                except Exception as e:
                    self._log(f"Erreur lors de la création du groupe '{safe_group_name}': {str(e)}", 'error')
                    error_count += len(group_items)
                    
            self._log(f"\n=== ORGANISATION TERMINÉE ===", 'success')
            self._log(f"Éléments déplacés: {moved_count}", 'success')
            if error_count > 0:
                self._log(f"Erreurs rencontrées: {error_count}", 'error')
                
            messagebox.showinfo(
                "Terminé",
                f"Organisation terminée!\n\n"
                f"Éléments déplacés: {moved_count}\n"
                f"Erreurs: {error_count}"
            )
            
        except Exception as e:
            self._log(f"Erreur critique: {str(e)}", 'error')
            messagebox.showerror("Erreur", f"Une erreur critique est survenue:\n{str(e)}")


def main():
    """Point d'entrée principal de l'application."""
    root = tk.Tk()
    app = FileOrganizerApp(root)
    
    # Centrer la fenêtre sur l'écran
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
