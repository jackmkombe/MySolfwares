#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application de Tri Automatique de Fichiers et Dossiers - Version Moderne
=========================================================================
Application desktop avec interface moderne permettant de regrouper automatiquement 
des fichiers ou dossiers ayant des noms similaires.

Auteur: Ingénieur Python Senior
Version: 2.0.0 (Modern UI)
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


class ModernStyle:
    """Classe pour gérer le style moderne de l'application."""
    
    # Palette de couleurs moderne
    PRIMARY = "#2563eb"      # Bleu moderne
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#3b82f6"
    SECONDARY = "#10b981"    # Vert succès
    WARNING = "#f59e0b"      # Orange avertissement
    ERROR = "#ef4444"        # Rouge erreur
    BG_MAIN = "#f8fafc"      # Fond principal
    BG_CARD = "#ffffff"      # Fond des cartes
    TEXT_PRIMARY = "#1e293b"
    TEXT_SECONDARY = "#64748b"
    BORDER = "#e2e8f0"
    
    @staticmethod
    def configure_styles():
        """Configure les styles ttk personnalisés."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style pour les LabelFrame
        style.configure(
            'Modern.TLabelframe',
            background=ModernStyle.BG_CARD,
            borderwidth=1,
            relief='solid'
        )
        style.configure(
            'Modern.TLabelframe.Label',
            background=ModernStyle.BG_CARD,
            foreground=ModernStyle.PRIMARY,
            font=('Segoe UI', 10, 'bold')
        )
        
        # Style pour les boutons principaux
        style.configure(
            'Primary.TButton',
            background=ModernStyle.PRIMARY,
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            font=('Segoe UI', 9, 'bold'),
            padding=(20, 10)
        )
        
        # Style pour les boutons secondaires
        style.configure(
            'Secondary.TButton',
            background=ModernStyle.BG_CARD,
            foreground=ModernStyle.TEXT_PRIMARY,
            borderwidth=1,
            font=('Segoe UI', 9),
            padding=(15, 8)
        )
        
        # Style pour les labels
        style.configure(
            'Modern.TLabel',
            background=ModernStyle.BG_CARD,
            foreground=ModernStyle.TEXT_PRIMARY,
            font=('Segoe UI', 9)
        )
        
        style.configure(
            'Title.TLabel',
            background=ModernStyle.BG_MAIN,
            foreground=ModernStyle.PRIMARY,
            font=('Segoe UI', 16, 'bold')
        )


class FileOrganizerApp:
    """Application principale avec interface moderne."""
    
    FILE_TYPES = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
        'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus']
    }
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Organisateur de Fichiers - Version Moderne")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # Configurer le style moderne
        ModernStyle.configure_styles()
        self.root.configure(bg=ModernStyle.BG_MAIN)
        
        # Variables
        self.source_folder = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.sort_type = tk.StringVar(value="files")
        self.file_type_filter = tk.StringVar(value="all")
        self.use_custom_destination = tk.BooleanVar(value=False)
        self.similarity_threshold = tk.DoubleVar(value=0.7)
        self.ignore_patterns = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure l'interface utilisateur moderne."""
        # Header avec titre
        header = tk.Frame(self.root, bg=ModernStyle.BG_MAIN, height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        title_label = ttk.Label(
            header,
            text="🗂️ Organisateur Intelligent de Fichiers",
            style='Title.TLabel'
        )
        title_label.pack(side=tk.LEFT, pady=20)
        
        version_label = ttk.Label(
            header,
            text="v2.0 Modern",
            style='Modern.TLabel',
            foreground=ModernStyle.TEXT_SECONDARY
        )
        version_label.pack(side=tk.LEFT, padx=10, pady=20)
        
        # Container principal avec scrollbar
        main_container = tk.Frame(self.root, bg=ModernStyle.BG_MAIN)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas pour le scroll
        canvas = tk.Canvas(main_container, bg=ModernStyle.BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernStyle.BG_MAIN)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Sections
        self._create_source_section_modern(scrollable_frame)
        self._create_sort_type_section_modern(scrollable_frame)
        self._create_file_filter_section_modern(scrollable_frame)
        self._create_ignore_patterns_section_modern(scrollable_frame)
        self._create_similarity_section_modern(scrollable_frame)
        self._create_destination_section_modern(scrollable_frame)
        self._create_log_section_modern(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Footer avec boutons d'action
        self._create_action_buttons_modern()
        
    def _create_card_frame(self, parent, title, icon=""):
        """Crée un cadre moderne avec style carte."""
        frame = tk.Frame(parent, bg=ModernStyle.BG_CARD, relief='flat', bd=0)
        frame.pack(fill=tk.X, pady=10)
        
        # Bordure subtile
        frame.configure(highlightbackground=ModernStyle.BORDER, highlightthickness=1)
        
        # Titre
        title_frame = tk.Frame(frame, bg=ModernStyle.BG_CARD)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        title_label = tk.Label(
            title_frame,
            text=f"{icon} {title}",
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.PRIMARY,
            font=('Segoe UI', 11, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Contenu
        content_frame = tk.Frame(frame, bg=ModernStyle.BG_CARD)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        return content_frame
    
    def _create_source_section_modern(self, parent):
        """Section source avec design moderne."""
        content = self._create_card_frame(parent, "Dossier Source", "📁")
        
        entry_frame = tk.Frame(content, bg=ModernStyle.BG_CARD)
        entry_frame.pack(fill=tk.X, pady=5)
        
        entry = tk.Entry(
            entry_frame,
            textvariable=self.source_folder,
            font=('Segoe UI', 10),
            relief='solid',
            bd=1,
            state='readonly'
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        btn = tk.Button(
            entry_frame,
            text="Parcourir",
            command=self._browse_source,
            bg=ModernStyle.PRIMARY,
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        )
        btn.pack(side=tk.LEFT, padx=(10, 0))
        
    def _create_sort_type_section_modern(self, parent):
        """Section type de tri moderne."""
        content = self._create_card_frame(parent, "Type de Tri", "🔧")
        
        radio_frame = tk.Frame(content, bg=ModernStyle.BG_CARD)
        radio_frame.pack(fill=tk.X, pady=5)
        
        options = [
            ("files", "Fichiers", "📄"),
            ("folders", "Dossiers", "📁"),
            ("both", "Les deux", "📦")
        ]
        
        for value, text, icon in options:
            rb = tk.Radiobutton(
                radio_frame,
                text=f"{icon} {text}",
                variable=self.sort_type,
                value=value,
                command=self._on_sort_type_change,
                bg=ModernStyle.BG_CARD,
                fg=ModernStyle.TEXT_PRIMARY,
                font=('Segoe UI', 10),
                selectcolor=ModernStyle.PRIMARY_LIGHT,
                activebackground=ModernStyle.BG_CARD,
                cursor='hand2'
            )
            rb.pack(side=tk.LEFT, padx=15)
    
    def _create_file_filter_section_modern(self, parent):
        """Section filtres moderne."""
        content = self._create_card_frame(parent, "Filtres de Fichiers", "🎯")
        self.file_filter_content = content
        
        filter_frame = tk.Frame(content, bg=ModernStyle.BG_CARD)
        filter_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            filter_frame,
            text="Type de fichiers :",
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            font=('Segoe UI', 10)
        )
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.file_type_filter,
            values=['all', 'images', 'videos', 'documents', 'audio'],
            state='readonly',
            font=('Segoe UI', 10),
            width=20
        )
        self.filter_combo.pack(side=tk.LEFT)
        self.filter_combo.current(0)
    
    def _create_ignore_patterns_section_modern(self, parent):
        """Section motifs d'ignorance moderne."""
        content = self._create_card_frame(parent, "Règles d'Ignorance (Multiples)", "🚫")
        
        # Champ d'ajout
        add_frame = tk.Frame(content, bg=ModernStyle.BG_CARD)
        add_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.pattern_entry = tk.Entry(
            add_frame,
            font=('Segoe UI', 10),
            relief='solid',
            bd=1
        )
        self.pattern_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        add_btn = tk.Button(
            add_frame,
            text="➕ Ajouter",
            command=self._add_ignore_pattern,
            bg=ModernStyle.SECONDARY,
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        )
        add_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Raccourcis
        shortcuts_label = tk.Label(
            content,
            text="⚡ Raccourcis rapides :",
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY,
            font=('Segoe UI', 9, 'italic')
        )
        shortcuts_label.pack(anchor=tk.W, pady=(10, 5))
        
        shortcuts_frame = tk.Frame(content, bg=ModernStyle.BG_CARD)
        shortcuts_frame.pack(fill=tk.X, pady=5)
        
        shortcuts = [
            (r"\[.*?\]", "Crochets [...]"),
            (r"\(.*?\)", "Parenthèses (...)"),
            (r"_\d+", "Numéros _123"),
            (r"\d{4}", "Années"),
            (r"_v\d+\.\d+", "Versions"),
            (r"_COPY|_copy", "Copies"),
        ]
        
        for idx, (pattern, desc) in enumerate(shortcuts):
            btn = tk.Button(
                shortcuts_frame,
                text=desc,
                command=lambda p=pattern: self._add_pattern_from_shortcut(p),
                bg=ModernStyle.BG_MAIN,
                fg=ModernStyle.TEXT_PRIMARY,
                font=('Segoe UI', 8),
                relief='solid',
                bd=1,
                cursor='hand2',
                padx=10,
                pady=5
            )
            btn.grid(row=idx // 3, column=idx % 3, padx=5, pady=5, sticky=tk.W)
        
        # Aide
        help_text = tk.Label(
            content,
            text="💡 Ajoutez plusieurs motifs pour les combiner (ex: crochets + numéros)",
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.PRIMARY,
            font=('Segoe UI', 9, 'italic'),
            wraplength=800,
            justify=tk.LEFT
        )
        help_text.pack(anchor=tk.W, pady=(10, 5))
        
        # Liste des motifs actifs
        list_label = tk.Label(
            content,
            text="📋 Motifs actifs :",
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            font=('Segoe UI', 10, 'bold')
        )
        list_label.pack(anchor=tk.W, pady=(10, 5))
        
        list_frame = tk.Frame(content, bg=ModernStyle.BG_CARD)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.patterns_listbox = tk.Listbox(
            list_frame,
            height=4,
            font=('Consolas', 9),
            yscrollcommand=scrollbar.set,
            relief='solid',
            bd=1
        )
        self.patterns_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.patterns_listbox.yview)
        
        # Boutons de gestion
        btn_frame = tk.Frame(content, bg=ModernStyle.BG_CARD)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        del_btn = tk.Button(
            btn_frame,
            text="🗑️ Supprimer",
            command=self._remove_ignore_pattern,
            bg=ModernStyle.ERROR,
            fg='white',
            font=('Segoe UI', 8),
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5
        )
        del_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = tk.Button(
            btn_frame,
            text="🧹 Tout effacer",
            command=self._clear_all_patterns,
            bg=ModernStyle.WARNING,
            fg='white',
            font=('Segoe UI', 8),
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5
        )
        clear_btn.pack(side=tk.LEFT)
    
    def _create_similarity_section_modern(self, parent):
        """Section similarité moderne."""
        content = self._create_card_frame(parent, "Seuil de Similarité", "📊")
        
        scale_frame = tk.Frame(content, bg=ModernStyle.BG_CARD)
        scale_frame.pack(fill=tk.X, pady=5)
        
        self.similarity_label = tk.Label(
            scale_frame,
            text=f"{self.similarity_threshold.get():.2f}",
            bg=ModernStyle.PRIMARY,
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            padx=15,
            pady=5,
            relief='flat'
        )
        self.similarity_label.pack(side=tk.RIGHT)
        
        scale = tk.Scale(
            scale_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            variable=self.similarity_threshold,
            orient=tk.HORIZONTAL,
            command=self._update_similarity_label,
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            font=('Segoe UI', 9),
            highlightthickness=0,
            troughcolor=ModernStyle.BG_MAIN,
            activebackground=ModernStyle.PRIMARY
        )
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        help_label = tk.Label(
            content,
            text="Plus la valeur est élevée, plus les noms doivent être similaires",
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_SECONDARY,
            font=('Segoe UI', 8, 'italic')
        )
        help_label.pack(anchor=tk.W, pady=(5, 0))
    
    def _create_destination_section_modern(self, parent):
        """Section destination moderne."""
        content = self._create_card_frame(parent, "Destination", "📂")
        
        check = tk.Checkbutton(
            content,
            text="Utiliser un dossier de destination personnalisé",
            variable=self.use_custom_destination,
            command=self._toggle_destination,
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            font=('Segoe UI', 10),
            selectcolor=ModernStyle.PRIMARY_LIGHT,
            activebackground=ModernStyle.BG_CARD,
            cursor='hand2'
        )
        check.pack(anchor=tk.W, pady=(5, 10))
        
        self.dest_frame = tk.Frame(content, bg=ModernStyle.BG_CARD)
        self.dest_frame.pack(fill=tk.X, pady=5)
        
        self.dest_entry = tk.Entry(
            self.dest_frame,
            textvariable=self.destination_folder,
            font=('Segoe UI', 10),
            relief='solid',
            bd=1,
            state='disabled'
        )
        self.dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        self.dest_btn = tk.Button(
            self.dest_frame,
            text="Parcourir",
            command=self._browse_destination,
            bg=ModernStyle.PRIMARY,
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.dest_btn.pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_log_section_modern(self, parent):
        """Section logs moderne."""
        content = self._create_card_frame(parent, "Journal d'Activité", "📋")
        
        self.log_text = scrolledtext.ScrolledText(
            content,
            height=10,
            state='disabled',
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#1e293b',
            fg='#e2e8f0',
            relief='flat',
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Tags pour coloration
        self.log_text.tag_config('info', foreground='#60a5fa')
        self.log_text.tag_config('success', foreground='#34d399')
        self.log_text.tag_config('warning', foreground='#fbbf24')
        self.log_text.tag_config('error', foreground='#f87171')
    
    def _create_action_buttons_modern(self):
        """Boutons d'action modernes dans le footer."""
        footer = tk.Frame(self.root, bg=ModernStyle.BG_MAIN, height=80)
        footer.pack(fill=tk.X, padx=20, pady=20)
        footer.pack_propagate(False)
        
        btn_container = tk.Frame(footer, bg=ModernStyle.BG_MAIN)
        btn_container.pack(expand=True)
        
        # Bouton prévisualiser
        preview_btn = tk.Button(
            btn_container,
            text="🔍 Prévisualiser",
            command=self._preview_organization,
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            font=('Segoe UI', 11, 'bold'),
            relief='solid',
            bd=1,
            cursor='hand2',
            padx=30,
            pady=15
        )
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton organiser (principal)
        organize_btn = tk.Button(
            btn_container,
            text="▶️ Organiser les Fichiers",
            command=self._organize_files,
            bg=ModernStyle.PRIMARY,
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=40,
            pady=15
        )
        organize_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton effacer logs
        clear_btn = tk.Button(
            btn_container,
            text="🗑️ Effacer Logs",
            command=self._clear_logs,
            bg=ModernStyle.BG_CARD,
            fg=ModernStyle.TEXT_PRIMARY,
            font=('Segoe UI', 10),
            relief='solid',
            bd=1,
            cursor='hand2',
            padx=20,
            pady=12
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton quitter
        quit_btn = tk.Button(
            btn_container,
            text="❌ Quitter",
            command=self.root.quit,
            bg=ModernStyle.ERROR,
            fg='white',
            font=('Segoe UI', 10),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=12
        )
        quit_btn.pack(side=tk.RIGHT, padx=5)
    
    # === MÉTHODES DE CALLBACK (identiques à la version originale) ===
    
    def _browse_source(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier source")
        if folder:
            self.source_folder.set(folder)
            self._log(f"Dossier source sélectionné: {folder}", 'info')
    
    def _browse_destination(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier de destination")
        if folder:
            self.destination_folder.set(folder)
            self._log(f"Dossier de destination sélectionné: {folder}", 'info')
    
    def _on_sort_type_change(self):
        """Gère le changement de type de tri (fichiers/dossiers/les deux)."""
        # Désactiver les filtres uniquement si on trie SEULEMENT des dossiers
        if self.sort_type.get() == "folders":
            self.filter_combo.configure(state='disabled')
        else:
            # Pour 'files' et 'both', les filtres restent actifs
            self.filter_combo.configure(state='readonly')
    
    def _toggle_destination(self):
        if self.use_custom_destination.get():
            self.dest_entry.configure(state='normal')
            self.dest_btn.configure(state='normal')
        else:
            self.dest_entry.configure(state='disabled')
            self.dest_btn.configure(state='disabled')
            self.destination_folder.set("")
    
    def _update_similarity_label(self, value):
        self.similarity_label.config(text=f"{float(value):.2f}")
    
    def _add_ignore_pattern(self):
        pattern = self.pattern_entry.get().strip()
        if pattern:
            if pattern not in self.ignore_patterns:
                self.ignore_patterns.append(pattern)
                self.patterns_listbox.insert(tk.END, pattern)
                self.pattern_entry.delete(0, tk.END)
                self._log(f"Motif ajouté: {pattern}", 'success')
            else:
                messagebox.showwarning("Doublon", "Ce motif existe déjà.")
        else:
            messagebox.showwarning("Entrée vide", "Veuillez entrer un motif valide.")
    
    def _add_pattern_from_shortcut(self, pattern: str):
        if pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
            self.patterns_listbox.insert(tk.END, pattern)
            self._log(f"Motif ajouté (raccourci): {pattern}", 'success')
        else:
            messagebox.showinfo("Déjà présent", f"Le motif '{pattern}' est déjà actif.")
    
    def _remove_ignore_pattern(self):
        selection = self.patterns_listbox.curselection()
        if selection:
            index = selection[0]
            pattern = self.ignore_patterns[index]
            self.ignore_patterns.pop(index)
            self.patterns_listbox.delete(index)
            self._log(f"Motif supprimé: {pattern}", 'warning')
        else:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un motif à supprimer.")
    
    def _clear_all_patterns(self):
        if self.ignore_patterns:
            if messagebox.askyesno("Confirmation", f"Supprimer tous les {len(self.ignore_patterns)} motifs ?"):
                count = len(self.ignore_patterns)
                self.ignore_patterns.clear()
                self.patterns_listbox.delete(0, tk.END)
                self._log(f"Tous les motifs effacés ({count})", 'warning')
        else:
            messagebox.showinfo("Liste vide", "Aucun motif à effacer.")
    
    def _clear_logs(self):
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
    
    def _log(self, message: str, level: str = 'info'):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()
    
    def _clean_name(self, name: str) -> str:
        cleaned = name
        for pattern in self.ignore_patterns:
            try:
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
            except re.error as e:
                self._log(f"Erreur regex '{pattern}': {e}", 'error')
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
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
        sort_type = self.sort_type.get()
        
        if sort_type in ("files", "both"):
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
        
        if sort_type in ("folders", "both"):
            # Traiter les dossiers
            for item in source.iterdir():
                if item.is_dir():
                    items.append(item)
        
        return items
    
    def _group_items(self, items: List[Path]) -> Dict[str, List[Path]]:
        groups = defaultdict(list)
        processed = set()
        threshold = self.similarity_threshold.get()
        
        for item in items:
            if item in processed:
                continue
            
            clean_name = self._clean_name(item.stem if item.is_file() else item.name)
            
            group_found = False
            for group_name in list(groups.keys()):
                if self._calculate_similarity(clean_name, group_name) >= threshold:
                    groups[group_name].append(item)
                    processed.add(item)
                    group_found = True
                    break
            
            if not group_found:
                groups[clean_name].append(item)
                processed.add(item)
        
        return {k: v for k, v in groups.items() if len(v) > 1}
    
    def _validate_configuration(self) -> bool:
        if not self.source_folder.get():
            messagebox.showerror("Erreur", "Sélectionnez un dossier source.")
            return False
        if not Path(self.source_folder.get()).exists():
            messagebox.showerror("Erreur", "Le dossier source n'existe pas.")
            return False
        if self.use_custom_destination.get():
            if not self.destination_folder.get():
                messagebox.showerror("Erreur", "Sélectionnez un dossier de destination.")
                return False
            if not Path(self.destination_folder.get()).exists():
                messagebox.showerror("Erreur", "Le dossier de destination n'existe pas.")
                return False
        return True
    
    def _preview_organization(self):
        if not self._validate_configuration():
            return
        
        try:
            self._log("=== PRÉVISUALISATION ===", 'info')
            items = self._get_items_to_process()
            self._log(f"Éléments trouvés: {len(items)}", 'info')
            
            if not items:
                self._log("Aucun élément à traiter.", 'warning')
                messagebox.showinfo("Prévisualisation", "Aucun élément trouvé.")
                return
            
            groups = self._group_items(items)
            
            if not groups:
                self._log("Aucun regroupement possible.", 'warning')
                messagebox.showinfo("Prévisualisation", "Aucun regroupement possible. Réduisez le seuil.")
                return
            
            self._log(f"\nGroupes créés: {len(groups)}", 'success')
            for group_name, group_items in groups.items():
                self._log(f"\n📁 {group_name} ({len(group_items)} éléments)", 'info')
                for item in group_items:
                    self._log(f"   • {item.name}", 'info')
            
            messagebox.showinfo("Prévisualisation", f"{len(groups)} groupes pour {sum(len(v) for v in groups.values())} éléments.")
        except Exception as e:
            self._log(f"Erreur: {str(e)}", 'error')
            messagebox.showerror("Erreur", str(e))
    
    def _organize_files(self):
        """Effectue l'organisation des fichiers/dossiers."""
        if not self._validate_configuration():
            return
        
        if not messagebox.askyesno("Confirmation", "Déplacer les fichiers/dossiers ?", icon='warning'):
            self._log("Opération annulée.", 'warning')
            return
        
        try:
            self._log("=== DÉBUT ORGANISATION ===", 'info')
            items = self._get_items_to_process()
            self._log(f"Éléments: {len(items)}", 'info')
            
            if not items:
                messagebox.showinfo("Terminé", "Aucun élément trouvé.")
                return
            
            groups = self._group_items(items)
            if not groups:
                messagebox.showinfo("Terminé", "Aucun regroupement nécessaire.")
                return
            
            base_folder = Path(self.destination_folder.get()) if self.use_custom_destination.get() else Path(self.source_folder.get())
            
            moved_count = 0
            error_count = 0
            reused_folders = 0
            
            for group_name, group_items in groups.items():
                # IMPORTANT : Appliquer les règles d'ignorance au nom du dossier
                # Cela garantit que le nom du dossier est propre et cohérent
                clean_folder_name = self._clean_name(group_name)
                
                # Nettoyer les caractères invalides pour les noms de dossiers Windows
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', clean_folder_name)
                
                # Si le nom est vide après nettoyage, utiliser un nom par défaut
                if not safe_name or safe_name.isspace():
                    safe_name = "groupe_sans_nom"
                
                group_folder = base_folder / safe_name
                
                try:
                    # Vérifier si le dossier existe déjà
                    folder_existed = group_folder.exists()
                    
                    # Créer le dossier (ne fait rien s'il existe déjà grâce à exist_ok=True)
                    group_folder.mkdir(exist_ok=True)
                    
                    if folder_existed:
                        self._log(f"\n📁 {safe_name} (dossier existant réutilisé)", 'info')
                        reused_folders += 1
                    else:
                        self._log(f"\n📁 {safe_name} (nouveau dossier créé)", 'success')
                    
                    for item in group_items:
                        try:
                            destination = group_folder / item.name
                            
                            # Gérer les conflits de noms
                            if destination.exists():
                                base = destination.stem if destination.suffix else destination.name
                                suffix = destination.suffix
                                counter = 1
                                while destination.exists():
                                    destination = group_folder / f"{base}_{counter}{suffix}"
                                    counter += 1
                            
                            shutil.move(str(item), str(destination))
                            self._log(f"   ✓ {item.name}", 'success')
                            moved_count += 1
                        except Exception as e:
                            self._log(f"   ✗ {item.name}: {e}", 'error')
                            error_count += 1
                except Exception as e:
                    self._log(f"Erreur groupe '{safe_name}': {e}", 'error')
                    error_count += len(group_items)
            
            self._log(f"\n=== TERMINÉ ===", 'success')
            self._log(f"Éléments déplacés: {moved_count}", 'success')
            if reused_folders > 0:
                self._log(f"Dossiers réutilisés: {reused_folders}", 'info')
            if error_count > 0:
                self._log(f"Erreurs: {error_count}", 'error')
            
            summary = f"Éléments déplacés: {moved_count}\n"
            if reused_folders > 0:
                summary += f"Dossiers réutilisés: {reused_folders}\n"
            summary += f"Erreurs: {error_count}"
            
            messagebox.showinfo("Terminé", summary)
        except Exception as e:
            self._log(f"Erreur critique: {e}", 'error')
            messagebox.showerror("Erreur", str(e))


def main():
    root = tk.Tk()
    app = FileOrganizerApp(root)
    
    # Centrer la fenêtre
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
