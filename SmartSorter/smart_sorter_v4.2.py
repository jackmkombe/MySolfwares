#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Sorter v4.2 - IA + Fusion + Consolidation
================================================
Nouvelle fonctionnalité : Consolidation des dossiers en double
"""

import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict, Counter
from difflib import SequenceMatcher

try:
    import customtkinter as ctk
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk


class IntelligentGrouper:
    """Moteur de regroupement intelligent."""
    
    # Patterns à ignorer automatiquement
    NOISE_PATTERNS = [
        r'\[.*?\]',           # Tags entre crochets
        r'\(.*?\)',           # Infos entre parenthèses
        r'\.(?:1080p|720p|480p|2160p|4K)',  # Résolutions
        r'\.(?:BluRay|WEB-DL|WEBRip|HDTV|DVDRip)',  # Sources
        r'\.(?:x264|x265|H264|H265|HEVC)',  # Codecs
        r'\.(?:AAC|AC3|DTS|MP3)',  # Audio
        r'_(?:VOSTFR|VOSTA|VF|VO|MULTI)',  # Langues
        r'\.S\d{2}E\d{2}',    # Episodes (S01E02)
        r'\.Episode\.\d+',    # Episode X
        r'\.E\d{2,3}',        # E01, E001
        r'_\d{2,3}(?:\s|$)',  # Numéros d'épisodes
        r'\d{4}',             # Années
        r'\.(?:PROPER|REPACK|INTERNAL)',  # Qualité
        r'-\w+$',             # Groupe de release à la fin
        r'\.(?:mkv|mp4|avi|mov|wmv|flv)$',  # Extensions
    ]
    
    @staticmethod
    def extract_core_name(filename: str, custom_patterns: List[str] = None) -> str:
        """Extrait le nom principal d'un fichier de manière intelligente."""
        name = Path(filename).stem
        
        # Appliquer les patterns automatiques
        for pattern in IntelligentGrouper.NOISE_PATTERNS:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
        
        # Appliquer les patterns personnalisés
        if custom_patterns:
            for pattern in custom_patterns:
                try:
                    name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
                except re.error:
                    pass  # Ignorer les patterns invalides
        
        name = re.sub(r'[._-]+', ' ', name)
        
        noise_words = [
            'watch', 'episode', 'ep', 'english', 'sub', 'vostfr', 'vf', 'vo',
            'french', 'multi', 'complete', 'season', 'saison', 'series',
            'kissasian', 'voirdrama', 'streaming', 'download', 'torrent'
        ]
        
        words = name.split()
        filtered_words = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower not in noise_words and len(word) >= 2 and not word.isdigit():
                filtered_words.append(word)
        
        core_name = ' '.join(filtered_words).strip()
        
        if not core_name and words:
            core_name = ' '.join(words[:3])
        
        return core_name or "Unknown"
    
    @staticmethod
    def calculate_smart_similarity(name1: str, name2: str) -> float:
        """Calcule la similarité de manière intelligente."""
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        
        seq_sim = SequenceMatcher(None, n1, n2).ratio()
        
        words1 = set(n1.split())
        words2 = set(n2.split())
        if words1 and words2:
            jaccard = len(words1 & words2) / len(words1 | words2)
        else:
            jaccard = 0.0
        
        def longest_common_substring(s1, s2):
            m = [[0] * (1 + len(s2)) for _ in range(1 + len(s1))]
            longest, x_longest = 0, 0
            for x in range(1, 1 + len(s1)):
                for y in range(1, 1 + len(s2)):
                    if s1[x - 1] == s2[y - 1]:
                        m[x][y] = m[x - 1][y - 1] + 1
                        if m[x][y] > longest:
                            longest = m[x][y]
                            x_longest = x
                    else:
                        m[x][y] = 0
            return longest / max(len(s1), len(s2)) if max(len(s1), len(s2)) > 0 else 0
        
        lcs_sim = longest_common_substring(n1, n2)
        
        contains_sim = 0.0
        if n1 in n2 or n2 in n1:
            contains_sim = 0.8
        
        final_score = (
            seq_sim * 0.3 +
            jaccard * 0.4 +
            lcs_sim * 0.2 +
            contains_sim * 0.1
        )
        
        return final_score
    
    @staticmethod
    def group_by_intelligence(items: List[Path], mode: str = "normal", custom_patterns: List[str] = None) -> Dict[str, List[Path]]:
        """Regroupe les éléments de manière intelligente."""
        thresholds = {
            "strict": 0.85,
            "normal": 0.65,
            "permissif": 0.45
        }
        threshold = thresholds.get(mode, 0.65)
        
        core_names = {}
        for item in items:
            core_name = IntelligentGrouper.extract_core_name(item.name, custom_patterns)
            core_names[item] = core_name
        
        groups = defaultdict(list)
        processed = set()
        
        for item in items:
            if item in processed:
                continue
            
            core_name = core_names[item]
            
            group_found = False
            for group_key in list(groups.keys()):
                similarity = IntelligentGrouper.calculate_smart_similarity(core_name, group_key)
                
                if similarity >= threshold:
                    groups[group_key].append(item)
                    processed.add(item)
                    group_found = True
                    break
            
            if not group_found:
                groups[core_name].append(item)
                processed.add(item)
        
        return {k: v for k, v in groups.items() if len(v) > 1}
    
    @staticmethod
    def consolidate_duplicate_folders(base_folder: Path, mode: str = "normal", custom_patterns: List[str] = None) -> Tuple[int, int]:
        """
        NOUVEAU : Consolide les dossiers en double.
        
        Trouve tous les dossiers similaires, crée un nouveau dossier consolidé,
        déplace tout le contenu dedans, et supprime les dossiers vides.
        
        Returns:
            (nombre de dossiers consolidés, nombre de fichiers déplacés)
        """
        thresholds = {
            "strict": 0.85,
            "normal": 0.65,
            "permissif": 0.45
        }
        threshold = thresholds.get(mode, 0.65)
        
        # Lister tous les dossiers
        folders = [item for item in base_folder.iterdir() if item.is_dir()]
        
        if not folders:
            return 0, 0
        
        # Regrouper les dossiers similaires
        folder_groups = defaultdict(list)
        processed = set()
        
        for folder in folders:
            if folder in processed:
                continue
            
            core_name = IntelligentGrouper.extract_core_name(folder.name, custom_patterns)
            
            group_found = False
            for group_key in list(folder_groups.keys()):
                similarity = IntelligentGrouper.calculate_smart_similarity(core_name, group_key)
                
                if similarity >= threshold:
                    folder_groups[group_key].append(folder)
                    processed.add(folder)
                    group_found = True
                    break
            
            if not group_found:
                folder_groups[core_name].append(folder)
                processed.add(folder)
        
        # Consolider les groupes ayant plusieurs dossiers
        consolidated_count = 0
        files_moved = 0
        
        for group_name, group_folders in folder_groups.items():
            if len(group_folders) <= 1:
                continue  # Pas de consolidation nécessaire
            
            # Créer le nom du dossier consolidé (SANS suffixe _consolidated)
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', group_name)
            consolidated_folder = base_folder / safe_name
            
            # S'assurer que le nom est unique
            counter = 1
            while consolidated_folder.exists():
                consolidated_folder = base_folder / f"{safe_name}_{counter}"
                counter += 1
            
            consolidated_folder.mkdir()
            
            # Déplacer tout le contenu de chaque dossier
            for folder in group_folders:
                for item in folder.iterdir():
                    try:
                        destination = consolidated_folder / item.name
                        
                        # Gérer les conflits de noms
                        if destination.exists():
                            base = destination.stem if destination.suffix else destination.name
                            suffix = destination.suffix if destination.is_file() else ""
                            counter = 1
                            while destination.exists():
                                if destination.is_file():
                                    destination = consolidated_folder / f"{base}_{counter}{suffix}"
                                else:
                                    destination = consolidated_folder / f"{base}_{counter}"
                                counter += 1
                        
                        shutil.move(str(item), str(destination))
                        files_moved += 1
                    except Exception:
                        pass
                
                # Supprimer le dossier vide
                try:
                    folder.rmdir()
                except Exception:
                    pass  # Le dossier n'est peut-être pas vide
            
            consolidated_count += len(group_folders)
        
        return consolidated_count, files_moved


class SmartSorterV4(ctk.CTk):
    """Smart Sorter v4.2 avec consolidation."""
    
    FILE_TYPES = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
        'Vidéos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus']
    }
    
    def __init__(self):
        super().__init__()
        
        self.title("Smart Sorter v4.2 - IA + Consolidation")
        self.geometry("850x900")
        self.minsize(750, 850)
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.source_folder = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.sort_type = tk.StringVar(value="files")
        self.use_custom_destination = tk.BooleanVar(value=False)
        self.grouping_mode = tk.StringVar(value="normal")
        self.consolidate_first = tk.BooleanVar(value=True)
        self.ignore_patterns = []  # NOUVEAU : Motifs personnalisés
        
        self.file_type_vars = {
            'Images': tk.BooleanVar(value=True),
            'Vidéos': tk.BooleanVar(value=True),
            'Documents': tk.BooleanVar(value=True),
            'Audio': tk.BooleanVar(value=True)
        }
        
        self._setup_ui()
        self.center_window()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _setup_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        self._create_header(main_container)
        
        scroll_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent",
            scrollbar_button_color="#3B82F6",
            scrollbar_button_hover_color="#2563EB"
        )
        scroll_frame.pack(fill="both", expand=True, pady=(20, 0))
        scroll_frame._parent_canvas.configure(yscrollincrement=10)
        
        def _on_mousewheel(event):
            scroll_frame._parent_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        scroll_frame._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self._create_source_section(scroll_frame)
        self._create_sort_type_section(scroll_frame)
        self._create_file_types_section(scroll_frame)
        self._create_consolidation_section(scroll_frame)
        self._create_ignore_section(scroll_frame)  # NOUVEAU : Motifs personnalisés
        self._create_intelligence_section(scroll_frame)
        self._create_destination_section(scroll_frame)
        
        self._create_action_buttons(main_container)
        
    def _create_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🧠 Smart Sorter v4.2",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1F2937"
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header,
            text="IA + Fusion + Consolidation automatique",
            font=ctk.CTkFont(size=13),
            text_color="#6B7280"
        )
        subtitle.pack(anchor="w", pady=(2, 0))
        
    def _create_card(self, parent, title):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color="#FFFFFF", border_width=1, border_color="#E5E7EB")
        card.pack(fill="x", pady=10)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1F2937"
        )
        title_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(0, 15))
        
        return content
        
    def _create_source_section(self, parent):
        content = self._create_card(parent, "📁 Dossier Source")
        
        input_frame = ctk.CTkFrame(content, fg_color="transparent")
        input_frame.pack(fill="x")
        
        self.source_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.source_folder,
            placeholder_text="Aucun dossier sélectionné",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.source_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            input_frame,
            text="Choisir",
            command=self._browse_source,
            width=100,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        browse_btn.pack(side="right")
        
    def _create_sort_type_section(self, parent):
        content = self._create_card(parent, "🔀 Type de Tri")
        
        options = [
            ("files", "📄 Trier des fichiers"),
            ("folders", "📁 Trier des dossiers"),
            ("both", "📦 Les deux")
        ]
        
        for value, text in options:
            radio = ctk.CTkRadioButton(
                content,
                text=text,
                variable=self.sort_type,
                value=value,
                command=self._on_sort_type_change,
                font=ctk.CTkFont(size=12),
                radiobutton_width=20,
                radiobutton_height=20
            )
            radio.pack(anchor="w", pady=5)
            
    def _create_file_types_section(self, parent):
        content = self._create_card(parent, "🎯 Types de Fichiers (optionnel)")
        self.file_types_card = content.master
        
        info = ctk.CTkLabel(
            content,
            text="Sélectionnez les types de fichiers à inclure :",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        )
        info.pack(anchor="w", pady=(0, 10))
        
        for file_type, var in self.file_type_vars.items():
            checkbox = ctk.CTkCheckBox(
                content,
                text=file_type,
                variable=var,
                font=ctk.CTkFont(size=12),
                checkbox_width=20,
                checkbox_height=20
            )
            checkbox.pack(anchor="w", pady=3)
    
    def _create_consolidation_section(self, parent):
        """NOUVEAU : Section de consolidation des dossiers en double."""
        content = self._create_card(parent, "🔀 Consolidation des Dossiers")
        
        info = ctk.CTkLabel(
            content,
            text="Fusionne automatiquement les dossiers ayant des noms similaires",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        )
        info.pack(anchor="w", pady=(0, 10))
        
        # Checkbox pour activer/désactiver
        consolidate_check = ctk.CTkCheckBox(
            content,
            text="Consolider les dossiers en double avant le tri",
            variable=self.consolidate_first,
            font=ctk.CTkFont(size=12, weight="bold"),
            checkbox_width=20,
            checkbox_height=20
        )
        consolidate_check.pack(anchor="w", pady=(0, 10))
        
        # Exemple
        example_frame = ctk.CTkFrame(content, fg_color="#FEF3C7", corner_radius=8)
        example_frame.pack(fill="x", pady=(10, 0))
        
        example_title = ctk.CTkLabel(
            example_frame,
            text="💡 Exemple :",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#1F2937"
        )
        example_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        examples = [
            'Avant : "Film/", "Film 2024/", "Film HD/"',
            'Après : "Film_consolidated/" (tout fusionné)',
            'Les dossiers vides sont supprimés automatiquement'
        ]
        
        for ex in examples:
            ex_label = ctk.CTkLabel(
                example_frame,
                text=f"  • {ex}",
                font=ctk.CTkFont(size=10),
                text_color="#92400E"
            )
            ex_label.pack(anchor="w", padx=15, pady=2)
        
        ctk.CTkLabel(example_frame, text="").pack(pady=5)
    
    def _create_ignore_section(self, parent):
        """Section des motifs d'ignorance personnalisés."""
        content = self._create_card(parent, "🔍 Motifs d'Ignorance Personnalisés (optionnel)")
        
        info = ctk.CTkLabel(
            content,
            text="Ajoutez vos propres motifs à ignorer en plus de ceux automatiques",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        )
        info.pack(anchor="w", pady=(0, 10))
        
        # Input
        input_frame = ctk.CTkFrame(content, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 10))
        
        self.pattern_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ex: \\[.*?\\] pour ignorer [tags]",
            height=36,
            font=ctk.CTkFont(size=11)
        )
        self.pattern_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        add_btn = ctk.CTkButton(
            input_frame,
            text="Ajouter",
            command=self._add_pattern,
            width=80,
            height=36,
            font=ctk.CTkFont(size=11)
        )
        add_btn.pack(side="right")
        
        # Raccourcis
        shortcuts_label = ctk.CTkLabel(
            content,
            text="⚡ Raccourcis rapides :",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#1F2937"
        )
        shortcuts_label.pack(anchor="w", pady=(10, 5))
        
        shortcuts_frame = ctk.CTkFrame(content, fg_color="transparent")
        shortcuts_frame.pack(fill="x")
        
        shortcuts = [
            (r"\[.*?\]", "Crochets"),
            (r"\(.*?\)", "Parenthèses"),
            (r"_\d+", "Numéros"),
            (r"\d{4}", "Années")
        ]
        
        for idx, (pattern, name) in enumerate(shortcuts):
            btn = ctk.CTkButton(
                shortcuts_frame,
                text=name,
                command=lambda p=pattern: self._add_pattern_shortcut(p),
                width=90,
                height=28,
                font=ctk.CTkFont(size=10),
                fg_color="#F3F4F6",
                text_color="#1F2937",
                hover_color="#E5E7EB"
            )
            btn.grid(row=idx//4, column=idx%4, padx=5, pady=5, sticky="w")
        
        # Container pour les motifs actifs
        self.patterns_container = ctk.CTkFrame(content, fg_color="transparent")
        self.patterns_container.pack(fill="x", pady=(10, 0))
            
    def _create_intelligence_section(self, parent):
        """Section de l'IA de regroupement."""
        content = self._create_card(parent, "🧠 Intelligence de Regroupement")
        
        info = ctk.CTkLabel(
            content,
            text="L'IA extrait automatiquement le nom principal et regroupe intelligemment",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        )
        info.pack(anchor="w", pady=(0, 15))
        
        modes = [
            ("strict", "🎯 Strict", "Regroupe uniquement les noms très similaires"),
            ("normal", "⚖️ Normal", "Équilibre entre précision et regroupement (recommandé)"),
            ("permissif", "🌐 Permissif", "Regroupe même les noms peu similaires")
        ]
        
        for value, title, description in modes:
            mode_frame = ctk.CTkFrame(content, fg_color="#F9FAFB", corner_radius=8)
            mode_frame.pack(fill="x", pady=5)
            
            radio = ctk.CTkRadioButton(
                mode_frame,
                text=title,
                variable=self.grouping_mode,
                value=value,
                font=ctk.CTkFont(size=12, weight="bold"),
                radiobutton_width=20,
                radiobutton_height=20
            )
            radio.pack(anchor="w", padx=15, pady=(10, 5))
            
            desc_label = ctk.CTkLabel(
                mode_frame,
                text=description,
                font=ctk.CTkFont(size=10),
                text_color="#6B7280"
            )
            desc_label.pack(anchor="w", padx=40, pady=(0, 10))
        
    def _create_destination_section(self, parent):
        content = self._create_card(parent, "📂 Destination")
        
        custom_check = ctk.CTkCheckBox(
            content,
            text="Utiliser un dossier de destination personnalisé",
            variable=self.use_custom_destination,
            command=self._toggle_destination,
            font=ctk.CTkFont(size=12),
            checkbox_width=20,
            checkbox_height=20
        )
        custom_check.pack(anchor="w", pady=(0, 10))
        
        self.dest_frame = ctk.CTkFrame(content, fg_color="transparent")
        
        self.dest_entry = ctk.CTkEntry(
            self.dest_frame,
            textvariable=self.destination_folder,
            placeholder_text="Choisir un dossier",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.dest_btn = ctk.CTkButton(
            self.dest_frame,
            text="Choisir",
            command=self._browse_destination,
            width=100,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.dest_btn.pack(side="right")
        
    def _create_action_buttons(self, parent):
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        center_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        center_frame.pack(expand=True)
        
        preview_btn = ctk.CTkButton(
            center_frame,
            text="🔍 Prévisualiser",
            command=self._preview,
            width=250,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        preview_btn.pack(side="left", padx=5)
        
        self.action_btn = ctk.CTkButton(
            center_frame,
            text="🚀 Lancer le Tri Intelligent",
            command=self._organize,
            width=250,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        self.action_btn.pack(side="left", padx=5)
        
    # === CALLBACKS ===
    
    def _browse_source(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier source")
        if folder:
            self.source_folder.set(folder)
            
    def _browse_destination(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier de destination")
        if folder:
            self.destination_folder.set(folder)
            
    def _on_sort_type_change(self):
        if self.sort_type.get() == "folders":
            self.file_types_card.pack_forget()
        else:
            self.file_types_card.pack(fill="x", pady=10)
            
    def _toggle_destination(self):
        if self.use_custom_destination.get():
            self.dest_frame.pack(fill="x")
        else:
            self.dest_frame.pack_forget()
            self.destination_folder.set("")
    
    def _add_pattern(self):
        """Ajoute un motif manuellement."""
        pattern = self.pattern_entry.get().strip()
        if pattern and pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
            self.pattern_entry.delete(0, 'end')
            self._update_patterns_display()
            
    def _add_pattern_shortcut(self, pattern):
        """Ajoute un motif depuis un raccourci."""
        if pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
            self._update_patterns_display()
            messagebox.showinfo("Motif ajouté", f"Motif '{pattern}' ajouté avec succès")
            
    def _update_patterns_display(self):
        """Met à jour l'affichage des motifs actifs."""
        for widget in self.patterns_container.winfo_children():
            widget.destroy()
            
        if self.ignore_patterns:
            label = ctk.CTkLabel(
                self.patterns_container,
                text="📋 Motifs actifs :",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#1F2937"
            )
            label.pack(anchor="w", pady=(5, 5))
            
            textbox = ctk.CTkTextbox(
                self.patterns_container,
                height=60,
                font=ctk.CTkFont(size=10),
                fg_color="#F9FAFB"
            )
            textbox.pack(fill="x")
            textbox.insert("1.0", ", ".join(self.ignore_patterns))
            textbox.configure(state="disabled")
            
            clear_btn = ctk.CTkButton(
                self.patterns_container,
                text="🗑️ Tout effacer",
                command=self._clear_patterns,
                width=100,
                height=28,
                font=ctk.CTkFont(size=10),
                fg_color="#EF4444",
                hover_color="#DC2626"
            )
            clear_btn.pack(anchor="w", pady=(5, 0))
    
    def _clear_patterns(self):
        """Efface tous les motifs."""
        if messagebox.askyesno("Confirmation", "Effacer tous les motifs ?"):
            self.ignore_patterns.clear()
            self._update_patterns_display()
            
    # === LOGIQUE ===
    
    def _get_items_to_process(self) -> List[Path]:
        source = Path(self.source_folder.get())
        if not source.exists():
            raise ValueError("Le dossier source n'existe pas")
            
        items = []
        sort_type = self.sort_type.get()
        
        if sort_type in ("files", "both"):
            selected_types = [k for k, v in self.file_type_vars.items() if v.get()]
            extensions = []
            for file_type in selected_types:
                extensions.extend(self.FILE_TYPES.get(file_type, []))
                
            for item in source.iterdir():
                if item.is_file() and (not extensions or item.suffix.lower() in extensions):
                    items.append(item)
                    
        if sort_type in ("folders", "both"):
            for item in source.iterdir():
                if item.is_dir():
                    items.append(item)
                    
        return items
        
    def _preview(self):
        if not self.source_folder.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier source")
            return
            
        try:
            items = self._get_items_to_process()
            if not items:
                messagebox.showinfo("Prévisualisation", "Aucun élément trouvé")
                return
                
            mode = self.grouping_mode.get()
            groups = IntelligentGrouper.group_by_intelligence(items, mode, self.ignore_patterns)
            
            if not groups:
                messagebox.showinfo("Prévisualisation", "Aucun regroupement possible avec ce mode.\nEssayez le mode 'Permissif'.")
                return
                
            preview_text = f"✅ {len(groups)} groupes seront créés pour {sum(len(v) for v in groups.values())} éléments\n\n"
            preview_text += f"Mode: {mode.upper()}\n\n"
            
            for group_name, group_items in list(groups.items())[:5]:
                preview_text += f"📁 {group_name} ({len(group_items)} éléments)\n"
                for item in group_items[:3]:
                    preview_text += f"   • {item.name}\n"
                if len(group_items) > 3:
                    preview_text += f"   ... et {len(group_items) - 3} autres\n"
                preview_text += "\n"
                
            if len(groups) > 5:
                preview_text += f"... et {len(groups) - 5} autres groupes"
                
            messagebox.showinfo("Prévisualisation", preview_text)
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            
    def _organize(self):
        if not self.source_folder.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier source")
            return
            
        confirm_msg = "Voulez-vous lancer le tri intelligent ?\n\n"
        if self.consolidate_first.get():
            confirm_msg += "✓ Consolidation des dossiers en double\n"
        confirm_msg += "✓ Fusion automatique des dossiers similaires"
        
        if not messagebox.askyesno("Confirmation", confirm_msg):
            return
            
        try:
            base_folder = Path(self.destination_folder.get()) if self.use_custom_destination.get() else Path(self.source_folder.get())
            mode = self.grouping_mode.get()
            
            # NOUVEAU : Consolidation des dossiers en double
            consolidated_folders = 0
            consolidated_files = 0
            
            if self.consolidate_first.get():
                consolidated_folders, consolidated_files = IntelligentGrouper.consolidate_duplicate_folders(base_folder, mode, self.ignore_patterns)
            
            # Tri normal
            items = self._get_items_to_process()
            if not items:
                if consolidated_folders > 0:
                    summary = f"✅ Consolidation terminée !\n\n"
                    summary += f"🔀 {consolidated_folders} dossiers consolidés\n"
                    summary += f"📦 {consolidated_files} fichiers déplacés"
                    messagebox.showinfo("Succès", summary)
                else:
                    messagebox.showinfo("Terminé", "Aucun élément trouvé")
                return
                
            groups = IntelligentGrouper.group_by_intelligence(items, mode)
            
            if not groups and consolidated_folders == 0:
                messagebox.showinfo("Terminé", "Aucun regroupement nécessaire")
                return
            
            # Détecter les dossiers existants pour fusion
            existing_folders = {}
            for item in base_folder.iterdir():
                if item.is_dir():
                    existing_folders[item.name] = item
            
            moved_count = 0
            reused_folders = 0
            merged_folders = 0
            
            thresholds = {
                "strict": 0.85,
                "normal": 0.65,
                "permissif": 0.45
            }
            threshold = thresholds.get(mode, 0.65)
            
            for group_name, group_items in groups.items():
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', group_name) or "groupe_sans_nom"
                
                target_folder = None
                folder_existed = False
                was_merged = False
                
                for existing_name, existing_path in existing_folders.items():
                    similarity = IntelligentGrouper.calculate_smart_similarity(safe_name, existing_name)
                    
                    if similarity >= threshold:
                        target_folder = existing_path
                        folder_existed = True
                        was_merged = True
                        merged_folders += 1
                        break
                
                if target_folder is None:
                    target_folder = base_folder / safe_name
                    folder_existed = target_folder.exists()
                
                target_folder.mkdir(exist_ok=True)
                
                if folder_existed and not was_merged:
                    reused_folders += 1
                    
                for item in group_items:
                    try:
                        destination = target_folder / item.name
                        
                        if destination.exists():
                            base = destination.stem if destination.suffix else destination.name
                            suffix = destination.suffix
                            counter = 1
                            while destination.exists():
                                destination = target_folder / f"{base}_{counter}{suffix}"
                                counter += 1
                                
                        shutil.move(str(item), str(destination))
                        moved_count += 1
                    except Exception:
                        pass
                        
            summary = f"✅ Tri intelligent terminé !\n\n"
            summary += f"Mode utilisé: {mode.upper()}\n"
            if consolidated_folders > 0:
                summary += f"🔀 {consolidated_folders} dossiers consolidés ({consolidated_files} fichiers)\n"
            summary += f"📦 {moved_count} éléments déplacés\n"
            if merged_folders > 0:
                summary += f"🔀 {merged_folders} dossiers fusionnés automatiquement\n"
            if reused_folders > 0:
                summary += f"🔄 {reused_folders} dossiers réutilisés\n"
                
            messagebox.showinfo("Succès", summary)
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


def main():
    app = SmartSorterV4()
    app.mainloop()


if __name__ == "__main__":
    main()
