#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Sorter v4.0 - IA de Regroupement Intelligent
===================================================
Nouvelle approche : extraction intelligente du nom principal
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
    def extract_core_name(filename: str) -> str:
        """
        Extrait le nom principal d'un fichier de manière intelligente.
        
        Exemples:
        - "Watch Dynamite Kiss Episode 2 English Sub - KissAsian" → "Dynamite Kiss"
        - "Dynamite Kiss - Dynamite Kiss - 01 VOSTFR - 01 - Voirdrama" → "Dynamite Kiss"
        - "Dynamite.Kiss.S01E07" → "Dynamite Kiss"
        """
        # Enlever l'extension
        name = Path(filename).stem
        
        # Appliquer tous les patterns de nettoyage
        for pattern in IntelligentGrouper.NOISE_PATTERNS:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
        
        # Nettoyer les séparateurs
        name = re.sub(r'[._-]+', ' ', name)
        
        # Enlever les mots courants de début/fin
        noise_words = [
            'watch', 'episode', 'ep', 'english', 'sub', 'vostfr', 'vf', 'vo',
            'french', 'multi', 'complete', 'season', 'saison', 'series',
            'kissasian', 'voirdrama', 'streaming', 'download', 'torrent'
        ]
        
        words = name.split()
        filtered_words = []
        
        for word in words:
            word_lower = word.lower()
            # Garder le mot si ce n'est pas un mot de bruit et qu'il a au moins 2 caractères
            if word_lower not in noise_words and len(word) >= 2 and not word.isdigit():
                filtered_words.append(word)
        
        # Reconstruire le nom
        core_name = ' '.join(filtered_words).strip()
        
        # Si le nom est vide, utiliser les 2-3 premiers mots significatifs
        if not core_name and words:
            core_name = ' '.join(words[:3])
        
        return core_name or "Unknown"
    
    @staticmethod
    def calculate_smart_similarity(name1: str, name2: str) -> float:
        """
        Calcule la similarité de manière intelligente.
        Combine plusieurs métriques pour une meilleure précision.
        """
        # Normaliser
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        
        # 1. Similarité de séquence (SequenceMatcher)
        seq_sim = SequenceMatcher(None, n1, n2).ratio()
        
        # 2. Similarité de mots (Jaccard)
        words1 = set(n1.split())
        words2 = set(n2.split())
        if words1 and words2:
            jaccard = len(words1 & words2) / len(words1 | words2)
        else:
            jaccard = 0.0
        
        # 3. Sous-chaîne commune la plus longue
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
        
        # 4. Vérifier si l'un contient l'autre
        contains_sim = 0.0
        if n1 in n2 or n2 in n1:
            contains_sim = 0.8
        
        # Combiner les métriques avec des poids
        final_score = (
            seq_sim * 0.3 +      # 30% séquence
            jaccard * 0.4 +      # 40% mots communs
            lcs_sim * 0.2 +      # 20% sous-chaîne
            contains_sim * 0.1   # 10% contenance
        )
        
        return final_score
    
    @staticmethod
    def group_by_intelligence(items: List[Path], mode: str = "normal") -> Dict[str, List[Path]]:
        """
        Regroupe les éléments de manière intelligente.
        
        Args:
            items: Liste des fichiers/dossiers
            mode: "strict", "normal", ou "permissif"
        """
        # Définir les seuils selon le mode
        thresholds = {
            "strict": 0.85,
            "normal": 0.65,
            "permissif": 0.45
        }
        threshold = thresholds.get(mode, 0.65)
        
        # Extraire les noms principaux
        core_names = {}
        for item in items:
            core_name = IntelligentGrouper.extract_core_name(item.name)
            core_names[item] = core_name
        
        # Regrouper par similarité
        groups = defaultdict(list)
        processed = set()
        
        for item in items:
            if item in processed:
                continue
            
            core_name = core_names[item]
            
            # Chercher un groupe existant similaire
            group_found = False
            for group_key in list(groups.keys()):
                similarity = IntelligentGrouper.calculate_smart_similarity(core_name, group_key)
                
                if similarity >= threshold:
                    groups[group_key].append(item)
                    processed.add(item)
                    group_found = True
                    break
            
            # Si aucun groupe trouvé, créer un nouveau
            if not group_found:
                groups[core_name].append(item)
                processed.add(item)
        
        # Retourner uniquement les groupes avec au moins 2 éléments
        return {k: v for k, v in groups.items() if len(v) > 1}


class SmartSorterV4(ctk.CTk):
    """Smart Sorter v4.0 avec IA de regroupement."""
    
    FILE_TYPES = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
        'Vidéos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus']
    }
    
    def __init__(self):
        super().__init__()
        
        self.title("Smart Sorter v4.0 - IA")
        self.geometry("850x850")
        self.minsize(750, 800)
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.source_folder = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.sort_type = tk.StringVar(value="files")
        self.use_custom_destination = tk.BooleanVar(value=False)
        self.grouping_mode = tk.StringVar(value="normal")  # Nouveau : mode de regroupement
        
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
        self._create_intelligence_section(scroll_frame)  # NOUVEAU
        self._create_destination_section(scroll_frame)
        
        self._create_action_buttons(main_container)
        
    def _create_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🧠 Smart Sorter v4.0",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1F2937"
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header,
            text="Regroupement intelligent avec IA",
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
            
    def _create_intelligence_section(self, parent):
        """NOUVEAU : Section de l'IA de regroupement."""
        content = self._create_card(parent, "🧠 Intelligence de Regroupement")
        
        info = ctk.CTkLabel(
            content,
            text="L'IA extrait automatiquement le nom principal et regroupe intelligemment",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        )
        info.pack(anchor="w", pady=(0, 15))
        
        # Modes de regroupement
        modes = [
            ("strict", "🎯 Strict", "Regroupe uniquement les noms très similaires"),
            ("normal", "⚖️ Normal", "Équilibre entre précision et regroupement (recommandé)"),
            ("permissif", "🌐 Permissif", "Regroupe même les noms peu similaires")
        ]
        
        for value, title, description in modes:
            # Frame pour chaque mode
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
        
        # Exemple
        example_frame = ctk.CTkFrame(content, fg_color="#EFF6FF", corner_radius=8)
        example_frame.pack(fill="x", pady=(15, 0))
        
        example_title = ctk.CTkLabel(
            example_frame,
            text="💡 Exemple d'extraction intelligente :",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#1F2937"
        )
        example_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        examples = [
            '"Watch Dynamite Kiss Episode 2" → "Dynamite Kiss"',
            '"Dynamite.Kiss.S01E07.1080p" → "Dynamite Kiss"',
            '"Dynamite Kiss - 01 VOSTFR" → "Dynamite Kiss"'
        ]
        
        for ex in examples:
            ex_label = ctk.CTkLabel(
                example_frame,
                text=f"  • {ex}",
                font=ctk.CTkFont(size=10),
                text_color="#3B82F6"
            )
            ex_label.pack(anchor="w", padx=15, pady=2)
        
        ctk.CTkLabel(example_frame, text="").pack(pady=5)  # Spacing
        
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
                
            # Utiliser l'IA de regroupement
            mode = self.grouping_mode.get()
            groups = IntelligentGrouper.group_by_intelligence(items, mode)
            
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
            
        if not messagebox.askyesno("Confirmation", "Voulez-vous lancer le tri intelligent ?\n\nNote: Les dossiers similaires existants seront fusionnés automatiquement."):
            return
            
        try:
            items = self._get_items_to_process()
            if not items:
                messagebox.showinfo("Terminé", "Aucun élément trouvé")
                return
                
            mode = self.grouping_mode.get()
            groups = IntelligentGrouper.group_by_intelligence(items, mode)
            
            if not groups:
                messagebox.showinfo("Terminé", "Aucun regroupement nécessaire")
                return
                
            base_folder = Path(self.destination_folder.get()) if self.use_custom_destination.get() else Path(self.source_folder.get())
            
            # NOUVEAU : Détecter les dossiers existants pour fusion
            existing_folders = {}
            for item in base_folder.iterdir():
                if item.is_dir():
                    existing_folders[item.name] = item
            
            moved_count = 0
            reused_folders = 0
            merged_folders = 0  # NOUVEAU : Compteur de fusions
            
            # Définir le seuil selon le mode
            thresholds = {
                "strict": 0.85,
                "normal": 0.65,
                "permissif": 0.45
            }
            threshold = thresholds.get(mode, 0.65)
            
            for group_name, group_items in groups.items():
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', group_name) or "groupe_sans_nom"
                
                # NOUVEAU : Vérifier si un dossier similaire existe déjà
                target_folder = None
                folder_existed = False
                was_merged = False
                
                # Chercher un dossier existant similaire
                for existing_name, existing_path in existing_folders.items():
                    similarity = IntelligentGrouper.calculate_smart_similarity(safe_name, existing_name)
                    
                    if similarity >= threshold:
                        # Dossier similaire trouvé → FUSION
                        target_folder = existing_path
                        folder_existed = True
                        was_merged = True
                        merged_folders += 1
                        break
                
                # Si aucun dossier similaire, utiliser le nom prévu
                if target_folder is None:
                    target_folder = base_folder / safe_name
                    folder_existed = target_folder.exists()
                
                # Créer le dossier si nécessaire
                target_folder.mkdir(exist_ok=True)
                
                if folder_existed and not was_merged:
                    reused_folders += 1
                    
                # Déplacer les fichiers
                for item in group_items:
                    try:
                        destination = target_folder / item.name
                        
                        # Gérer les conflits de noms
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
