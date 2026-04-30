#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Sorter - Organisateur Intelligent de Fichiers
====================================================
Version 3.1 - Interface Moderne Optimisée

Corrections v3.1:
- Scroll plus fluide
- Taille optimale sans scroll
- Boutons avec largeur max fixe
- Raccourcis fonctionnels
"""

import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from difflib import SequenceMatcher

try:
    import customtkinter as ctk
except ImportError:
    print("❌ CustomTkinter n'est pas installé")
    print("Installation automatique...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk


class SmartSorter(ctk.CTk):
    """Application moderne de tri intelligent de fichiers."""
    
    FILE_TYPES = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
        'Vidéos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus']
    }
    
    def __init__(self):
        super().__init__()
        
        # Configuration optimale de la fenêtre
        self.title("Smart Sorter")
        self.geometry("850x950")  # Taille optimale pour tout afficher
        self.minsize(750, 850)
        
        # Thème
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.source_folder = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.sort_type = tk.StringVar(value="files")
        self.use_custom_destination = tk.BooleanVar(value=False)
        self.similarity_threshold = tk.DoubleVar(value=0.7)
        self.ignore_patterns = []
        
        # Checkboxes pour types de fichiers
        self.file_type_vars = {
            'Images': tk.BooleanVar(value=True),
            'Vidéos': tk.BooleanVar(value=True),
            'Documents': tk.BooleanVar(value=True),
            'Audio': tk.BooleanVar(value=True)
        }
        
        self._setup_ui()
        self.center_window()
        
    def center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        # Container principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Header
        self._create_header(main_container)
        
        # Frame scrollable avec scroll FLUIDE
        scroll_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent",
            scrollbar_button_color="#3B82F6",
            scrollbar_button_hover_color="#2563EB"
        )
        scroll_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # Améliorer la fluidité du scroll
        scroll_frame._parent_canvas.configure(yscrollincrement=10)  # Scroll plus fluide
        
        # Bind mousewheel pour scroll fluide
        def _on_mousewheel(event):
            scroll_frame._parent_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        scroll_frame._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Sections
        self._create_source_section(scroll_frame)
        self._create_sort_type_section(scroll_frame)
        self._create_file_types_section(scroll_frame)
        self._create_ignore_section(scroll_frame)
        self._create_similarity_section(scroll_frame)
        self._create_destination_section(scroll_frame)
        
        # Boutons d'action
        self._create_action_buttons(main_container)
        
    def _create_header(self, parent):
        """Crée l'en-tête."""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🗂️ Smart Sorter",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1F2937"
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header,
            text="Organisez vos fichiers automatiquement",
            font=ctk.CTkFont(size=13),
            text_color="#6B7280"
        )
        subtitle.pack(anchor="w", pady=(2, 0))
        
    def _create_card(self, parent, title):
        """Crée une carte."""
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
        """Section source."""
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
        """Section type de tri."""
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
        """Section types de fichiers."""
        content = self._create_card(parent, "🎯 Types de Fichiers (optionnel)")
        self.file_types_card = content.master  # Sauvegarder la carte
        
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
            
    def _create_ignore_section(self, parent):
        """Section nettoyage des noms."""
        content = self._create_card(parent, "🔍 Nettoyage des Noms (optionnel)")
        
        info = ctk.CTkLabel(
            content,
            text="Ignorez certains motifs dans les noms (ex: tags, numéros, etc.)",
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
            
        # Container pour les motifs actifs (créé dynamiquement)
        self.patterns_container = ctk.CTkFrame(content, fg_color="transparent")
        self.patterns_container.pack(fill="x", pady=(10, 0))
        
    def _create_similarity_section(self, parent):
        """Section similarité."""
        content = self._create_card(parent, "📊 Seuil de Similarité")
        
        info = ctk.CTkLabel(
            content,
            text="Plus la valeur est élevée, plus les noms doivent être similaires",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        )
        info.pack(anchor="w", pady=(0, 10))
        
        slider_frame = ctk.CTkFrame(content, fg_color="transparent")
        slider_frame.pack(fill="x")
        
        self.similarity_slider = ctk.CTkSlider(
            slider_frame,
            from_=0.0,
            to=1.0,
            variable=self.similarity_threshold,
            command=self._update_similarity_label,
            width=500,
            height=20
        )
        self.similarity_slider.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        self.similarity_label = ctk.CTkLabel(
            slider_frame,
            text=f"{self.similarity_threshold.get():.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3B82F6",
            width=50
        )
        self.similarity_label.pack(side="right")
        
    def _create_destination_section(self, parent):
        """Section destination."""
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
        """Boutons d'action avec largeur max fixe."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Container centré avec largeur max
        center_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        center_frame.pack(expand=True)
        
        # Bouton prévisualiser - LARGEUR FIXE
        preview_btn = ctk.CTkButton(
            center_frame,
            text="🔍 Prévisualiser",
            command=self._preview,
            width=250,  # Largeur fixe
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        preview_btn.pack(side="left", padx=5)
        
        # Bouton principal - LARGEUR FIXE
        self.action_btn = ctk.CTkButton(
            center_frame,
            text="🚀 Lancer le Tri",
            command=self._organize,
            width=250,  # Largeur fixe
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
            self.file_types_card.pack(fill="x", pady=10, after=self.file_types_card.master.winfo_children()[1])
            
    def _toggle_destination(self):
        if self.use_custom_destination.get():
            self.dest_frame.pack(fill="x")
        else:
            self.dest_frame.pack_forget()
            self.destination_folder.set("")
            
    def _update_similarity_label(self, value):
        self.similarity_label.configure(text=f"{float(value):.2f}")
        
    def _add_pattern(self):
        """Ajoute un motif manuellement."""
        pattern = self.pattern_entry.get().strip()
        if pattern and pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
            self.pattern_entry.delete(0, 'end')
            self._update_patterns_display()
            
    def _add_pattern_shortcut(self, pattern):
        """Ajoute un motif depuis un raccourci - CORRIGÉ."""
        if pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
            self._update_patterns_display()
            messagebox.showinfo("Motif ajouté", f"Motif '{pattern}' ajouté avec succès")
            
    def _update_patterns_display(self):
        """Met à jour l'affichage des motifs actifs - CORRIGÉ."""
        # Nettoyer le container
        for widget in self.patterns_container.winfo_children():
            widget.destroy()
            
        if self.ignore_patterns:
            # Label
            label = ctk.CTkLabel(
                self.patterns_container,
                text="📋 Motifs actifs :",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#1F2937"
            )
            label.pack(anchor="w", pady=(5, 5))
            
            # Textbox
            textbox = ctk.CTkTextbox(
                self.patterns_container,
                height=60,
                font=ctk.CTkFont(size=10),
                fg_color="#F9FAFB"
            )
            textbox.pack(fill="x")
            textbox.insert("1.0", ", ".join(self.ignore_patterns))
            textbox.configure(state="disabled")
            
            # Bouton effacer
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
    
    def _clean_name(self, name: str) -> str:
        cleaned = name
        for pattern in self.ignore_patterns:
            try:
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
            except re.error:
                pass
        return re.sub(r'\s+', ' ', cleaned).strip()
        
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
        
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
        
    def _preview(self):
        if not self.source_folder.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier source")
            return
            
        try:
            items = self._get_items_to_process()
            if not items:
                messagebox.showinfo("Prévisualisation", "Aucun élément trouvé")
                return
                
            groups = self._group_items(items)
            if not groups:
                messagebox.showinfo("Prévisualisation", "Aucun regroupement possible.\nEssayez de réduire le seuil de similarité.")
                return
                
            preview_text = f"✅ {len(groups)} groupes seront créés pour {sum(len(v) for v in groups.values())} éléments\n\n"
            for group_name, group_items in list(groups.items())[:5]:
                preview_text += f"📁 {group_name} ({len(group_items)} éléments)\n"
                
            if len(groups) > 5:
                preview_text += f"\n... et {len(groups) - 5} autres groupes"
                
            messagebox.showinfo("Prévisualisation", preview_text)
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            
    def _organize(self):
        if not self.source_folder.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier source")
            return
            
        if not messagebox.askyesno("Confirmation", "Voulez-vous lancer le tri ?"):
            return
            
        try:
            items = self._get_items_to_process()
            if not items:
                messagebox.showinfo("Terminé", "Aucun élément trouvé")
                return
                
            groups = self._group_items(items)
            if not groups:
                messagebox.showinfo("Terminé", "Aucun regroupement nécessaire")
                return
                
            base_folder = Path(self.destination_folder.get()) if self.use_custom_destination.get() else Path(self.source_folder.get())
            
            moved_count = 0
            reused_folders = 0
            
            for group_name, group_items in groups.items():
                clean_folder_name = self._clean_name(group_name)
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', clean_folder_name) or "groupe_sans_nom"
                group_folder = base_folder / safe_name
                
                folder_existed = group_folder.exists()
                group_folder.mkdir(exist_ok=True)
                if folder_existed:
                    reused_folders += 1
                    
                for item in group_items:
                    try:
                        destination = group_folder / item.name
                        if destination.exists():
                            base = destination.stem if destination.suffix else destination.name
                            suffix = destination.suffix
                            counter = 1
                            while destination.exists():
                                destination = group_folder / f"{base}_{counter}{suffix}"
                                counter += 1
                                
                        shutil.move(str(item), str(destination))
                        moved_count += 1
                    except Exception:
                        pass
                        
            summary = f"✅ Tri terminé avec succès !\n\n"
            summary += f"📦 {moved_count} éléments déplacés\n"
            if reused_folders > 0:
                summary += f"🔄 {reused_folders} dossiers réutilisés\n"
                
            messagebox.showinfo("Succès", summary)
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


def main():
    app = SmartSorter()
    app.mainloop()


if __name__ == "__main__":
    main()
