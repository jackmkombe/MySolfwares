#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Sorter v5.0 - PRO Version
================================================
Optimisations : Multi-threading, Barre de progression, Logs en temps réel, Caching.
"""

import os
import re
import shutil
import tkinter as tk
import threading
import time
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
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
    """Moteur de regroupement intelligent optimisé."""
    
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
    
    _core_name_cache = {}

    @staticmethod
    def extract_core_name(filename: str, custom_patterns: List[str] = None) -> str:
        cache_key = (filename, tuple(custom_patterns) if custom_patterns else None)
        if cache_key in IntelligentGrouper._core_name_cache:
            return IntelligentGrouper._core_name_cache[cache_key]

        name = Path(filename).stem
        for pattern in IntelligentGrouper.NOISE_PATTERNS:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
        
        if custom_patterns:
            for pattern in custom_patterns:
                try:
                    name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
                except re.error: pass
        
        name = re.sub(r'[._-]+', ' ', name)
        noise_words = {
            'watch', 'episode', 'ep', 'english', 'sub', 'vostfr', 'vf', 'vo',
            'french', 'multi', 'complete', 'season', 'saison', 'series',
            'kissasian', 'voirdrama', 'streaming', 'download', 'torrent'
        }
        
        words = name.split()
        filtered = [w for w in words if w.lower() not in noise_words and len(w) >= 2 and not w.isdigit()]
        core_name = ' '.join(filtered).strip() or ' '.join(words[:3]).strip()
        
        result = core_name or "Unknown"
        IntelligentGrouper._core_name_cache[cache_key] = result
        return result

    @staticmethod
    def calculate_smart_similarity(name1: str, name2: str) -> float:
        n1, n2 = name1.lower().strip(), name2.lower().strip()
        if n1 == n2: return 1.0
        
        seq_sim = SequenceMatcher(None, n1, n2).ratio()
        
        w1, w2 = set(n1.split()), set(n2.split())
        jaccard = len(w1 & w2) / len(w1 | w2) if w1 | w2 else 0
        
        contains_sim = 0.8 if n1 in n2 or n2 in n1 else 0.0
        
        # Approximation de LCS simplifiée pour la performance
        common = os.path.commonprefix([n1, n2])
        lcs_sim = len(common) / max(len(n1), len(n2)) if max(len(n1), len(n2)) > 0 else 0
        
        return (seq_sim * 0.3 + jaccard * 0.4 + lcs_sim * 0.2 + contains_sim * 0.1)

    @staticmethod
    def consolidate_duplicate_folders(base_folder: Path, mode: str = "normal", 
                                     custom_patterns: List[str] = None, 
                                     cons_type: str = "merge") -> Tuple[int, int]:
        """Consolide les dossiers en double selon le type choisi : group, merge, ou cleanup."""
        threshold = {"strict": 0.85, "normal": 0.65, "permissif": 0.45}.get(mode, 0.65)
        folders = [item for item in base_folder.iterdir() if item.is_dir()]
        
        if not folders: return 0, 0
        
        folder_groups = defaultdict(list)
        processed = set()
        
        for folder in folders:
            if folder in processed: continue
            core_name = IntelligentGrouper.extract_core_name(folder.name, custom_patterns)
            
            best_match = None
            max_sim = 0
            for group_key in folder_groups.keys():
                sim = IntelligentGrouper.calculate_smart_similarity(core_name, group_key)
                if sim >= threshold and sim > max_sim:
                    max_sim = sim
                    best_match = group_key
                    
            if best_match:
                folder_groups[best_match].append(folder)
            else:
                folder_groups[core_name].append(folder)
            processed.add(folder)
            
        consolidated_count, files_moved = 0, 0
        for group_name, group_folders in folder_groups.items():
            if len(group_folders) <= 1: continue
            
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', group_name)
            consolidated_folder = base_folder / safe_name
            
            cnt = 1
            while consolidated_folder.exists() and consolidated_folder not in group_folders:
                consolidated_folder = base_folder / f"{safe_name}_{cnt}"
                cnt += 1
            
            consolidated_folder.mkdir(exist_ok=True)
            
            for folder in group_folders:
                if folder == consolidated_folder: continue
                
                if cons_type == "group":
                    # Mode 1 : On déplace le dossier entier dedans
                    try:
                        dest = consolidated_folder / folder.name
                        shutil.move(str(folder), str(dest))
                        files_moved += 1 # On compte le dossier comme 1 action
                    except: pass
                else:
                    # Mode 2 & 3 : On vide le contenu
                    for item in folder.iterdir():
                        try:
                            dest = consolidated_folder / item.name
                            if dest.exists():
                                stem, suffix = (dest.stem, dest.suffix) if dest.is_file() else (dest.name, "")
                                c = 1
                                while (consolidated_folder / f"{stem}_{c}{suffix}").exists(): c += 1
                                dest = consolidated_folder / f"{stem}_{c}{suffix}"
                            shutil.move(str(item), str(dest))
                            files_moved += 1
                        except: pass
                    
                    if cons_type == "cleanup":
                        # Mode 3 : On supprime le dossier source vide
                        try: folder.rmdir() 
                        except: pass
            
            consolidated_count += len(group_folders)
            
        return consolidated_count, files_moved

    @staticmethod
    def group_by_intelligence(items: List[Path], mode: str = "normal", 
                              custom_patterns: List[str] = None, progress_callback=None) -> Dict[str, List[Path]]:
        threshold = {"strict": 0.85, "normal": 0.65, "permissif": 0.45}.get(mode, 0.65)
        
        core_names = {}
        total = len(items)
        for i, item in enumerate(items):
            core_names[item] = IntelligentGrouper.extract_core_name(item.name, custom_patterns)
            if progress_callback: progress_callback(i / (total * 2)) # Les 50 premiers %

        groups = defaultdict(list)
        processed = set()
        
        for i, item in enumerate(items):
            if item in processed: continue
            cname = core_names[item]
            
            best_match = None
            max_sim = 0
            
            for group_key in groups.keys():
                sim = IntelligentGrouper.calculate_smart_similarity(cname, group_key)
                if sim >= threshold and sim > max_sim:
                    max_sim = sim
                    best_match = group_key
            
            if best_match:
                groups[best_match].append(item)
            else:
                groups[cname].append(item)
            processed.add(item)
            
            if progress_callback: progress_callback(0.5 + (i / (total * 2))) # Les 50 derniers %
            
        return {k: v for k, v in groups.items() if len(v) > 1}


class SmartSorterPRO(ctk.CTk):
    """Smart Sorter v5.0 - Version Professionnelle Optimisée."""
    
    FILE_TYPES = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
        'Vidéos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus']
    }

    def __init__(self):
        super().__init__()
        self.title("Smart Sorter v5.0 PRO")
        self.geometry("950x950")
        self.minsize(850, 900)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # UI Variables
        self.source_folder = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.sort_type = tk.StringVar(value="files")
        self.use_custom_destination = tk.BooleanVar(value=False)
        self.grouping_mode = tk.StringVar(value="normal")
        self.consolidate_first = tk.BooleanVar(value=True)
        self.consolidation_type = tk.StringVar(value="merge") # group, merge, cleanup
        self.ignore_patterns = []
        self.is_processing = False

        self.file_type_vars = {t: tk.BooleanVar(value=True) for t in self.FILE_TYPES}
        
        # Icône de la fenêtre
        try:
            if os.path.exists("app_icon.ico"):
                self.iconbitmap("app_icon.ico")
        except:
            pass

        self._setup_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f'{w}x{h}+{x}+{y}')

    def _setup_ui(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        self._create_header(self.main_container)
        
        # Scrollable area
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.scroll_frame._parent_canvas.configure(yscrollincrement=20)
        
        def _on_mousewheel(event):
            self.scroll_frame._parent_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.scroll_frame._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self._create_source_section(self.scroll_frame)
        self._create_sort_type_section(self.scroll_frame)
        self._create_file_types_section(self.scroll_frame)
        self._create_consolidation_section(self.scroll_frame)
        self._create_ignore_section(self.scroll_frame)
        self._create_intelligence_section(self.scroll_frame)
        self._create_destination_section(self.scroll_frame)
        
        # Progress and status (NEW)
        self.status_container = ctk.CTkFrame(self.main_container, fg_color="#1E293B", corner_radius=10)
        self.status_container.pack(fill="x", pady=10)
        
        self.status_label = ctk.CTkLabel(self.status_container, text="Prêt", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.status_container, width=800)
        self.progress_bar.pack(padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        
        self.log_area = ctk.CTkTextbox(self.status_container, height=80, font=ctk.CTkFont(size=10), fg_color="#0F172A")
        self.log_area.pack(fill="x", padx=10, pady=(0, 10))
        self.log_area.configure(state="disabled")

        self._create_action_buttons(self.main_container)

    def _create_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="🚀 Smart Sorter v5.0 PRO", font=ctk.CTkFont(size=32, weight="bold"), text_color="#3B82F6").pack(anchor="w")
        ctk.CTkLabel(header, text="Algorithmes Avancés - Multi-threading - Performance Optimisée", font=ctk.CTkFont(size=14), text_color="#94A3B8").pack(anchor="w")

    def _create_card(self, parent, title, icon=""):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color="#1E293B", border_width=1, border_color="#334155")
        card.pack(fill="x", pady=8)
        ctk.CTkLabel(card, text=f"{icon} {title}", font=ctk.CTkFont(size=15, weight="bold"), text_color="#F8FAFC").pack(anchor="w", padx=20, pady=(15, 10))
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(0, 15))
        return content

    def _create_source_section(self, parent):
        c = self._create_card(parent, "Dossier Source", "📁")
        f = ctk.CTkFrame(c, fg_color="transparent")
        f.pack(fill="x")
        ctk.CTkEntry(f, textvariable=self.source_folder, placeholder_text="Cliquez sur Choisir...", height=40).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(f, text="Choisir", command=self._browse_source, width=100, height=40, font=ctk.CTkFont(weight="bold")).pack(side="right")

    def _create_sort_type_section(self, parent):
        c = self._create_card(parent, "Type de Tri", "🔀")
        for v, t in [("files", "📄 Uniquement les fichiers"), ("folders", "📁 Uniquement les dossiers"), ("both", "📦 Fichiers + Dossiers")]:
            ctk.CTkRadioButton(c, text=t, variable=self.sort_type, value=v, command=self._on_sort_type_change).pack(anchor="w", pady=5)

    def _create_file_types_section(self, parent):
        c = self._create_card(parent, "Filtres de Fichiers", "🎯")
        self.file_types_card = c.master
        for t, var in self.file_type_vars.items():
            ctk.CTkCheckBox(c, text=t, variable=var).pack(side="left", padx=10)

    def _create_consolidation_section(self, parent):
        c = self._create_card(parent, "Consolidation des Doubles", "📦")
        ctk.CTkCheckBox(c, text="Fusionner les dossiers similaires avant le tri", 
                        variable=self.consolidate_first, font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        # Sélecteur de mode de consolidation
        mode_f = ctk.CTkFrame(c, fg_color="transparent")
        mode_f.pack(fill="x", pady=(10, 5))
        
        ctk.CTkLabel(mode_f, text="Stratégie :", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(side="left", padx=(0, 10))
        
        self.cons_seg = ctk.CTkSegmentedButton(mode_f, values=["Regrouper", "Fusionner", "Nettoyer"],
                                              command=self._on_cons_mode_change)
        self.cons_seg.pack(side="left", fill="x", expand=True)
        self.cons_seg.set("Fusionner")
        
        self.cons_desc = ctk.CTkLabel(c, text="Mode Fusion : Tout mettre à plat dans un seul dossier", 
                                     font=ctk.CTkFont(size=11), text_color="#3B82F6")
        self.cons_desc.pack(anchor="w", pady=(5, 0))

    def _on_cons_mode_change(self, val):
        mapping = {"Regrouper": "group", "Fusionner": "merge", "Nettoyer": "cleanup"}
        descs = {
            "Regrouper": "📦 Mode Dossier Commun : Conserve vos dossiers tels quels dans un dossier parent.",
            "Fusionner": "🔄 Mode Fusion : Déplace tous les fichiers dans un seul dossier (structure à plat).",
            "Nettoyer": "🗑️ Mode Nettoyage : Fusionne tout et supprime les dossiers d'origine vides."
        }
        self.consolidation_type.set(mapping[val])
        self.cons_desc.configure(text=descs[val])

    def _create_ignore_section(self, parent):
        c = self._create_card(parent, "Motifs d'Ignorance", "🔍")
        
        # Guide
        ctk.CTkLabel(c, text="Ajoutez vos propres patterns (regex) pour nettoyer les noms :", 
                     font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(anchor="w", pady=(0, 10))
        
        # Input
        f = ctk.CTkFrame(c, fg_color="transparent")
        f.pack(fill="x", pady=5)
        self.pattern_entry = ctk.CTkEntry(f, placeholder_text="Ex: \\[TAG\\], (2024)...", height=36)
        self.pattern_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(f, text="Ajouter", command=self._add_pattern, width=80).pack(side="right")
        
        # Raccourcis restaurés
        shortcuts_f = ctk.CTkFrame(c, fg_color="transparent")
        shortcuts_f.pack(fill="x", pady=10)
        
        shortcuts = [(r"\[.*?\]", "Crochets"), (r"\(.*?\)", "Parenthèses"), (r"_\d+", "Numéros"), (r"\d{4}", "Années")]
        for idx, (p, n) in enumerate(shortcuts):
            b = ctk.CTkButton(shortcuts_f, text=n, command=lambda pat=p: self._add_pattern_shortcut(pat),
                              width=85, height=28, font=ctk.CTkFont(size=11),
                              fg_color="#334155", hover_color="#475569")
            b.grid(row=0, column=idx, padx=5)
        
        self.patterns_container = ctk.CTkFrame(c, fg_color="transparent")
        self.patterns_container.pack(fill="x", pady=5)
        self._update_patterns_display()

    def _add_pattern_shortcut(self, pattern):
        if pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
            self._update_patterns_display()

    def _create_intelligence_section(self, parent):
        c = self._create_card(parent, "Config IA", "🧠")
        for v, t, d in [("strict", "🎯 Strict", "90% de précision - Évite les erreurs"), 
                        ("normal", "⚖️ Normal", "Recommandé - Regroupements intelligents"), 
                        ("permissif", "🌐 Permissif", "Regroupe par thèmes larges")]:
            f = ctk.CTkFrame(c, fg_color="#0F172A", corner_radius=8)
            f.pack(fill="x", pady=3)
            ctk.CTkRadioButton(f, text=t, variable=self.grouping_mode, value=v).pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(f, text=d, font=ctk.CTkFont(size=10), text_color="#64748B").pack(side="right", padx=15)

    def _create_destination_section(self, parent):
        c = self._create_card(parent, "Destination", "📂")
        ctk.CTkCheckBox(c, text="Mode Ranger dans un autre dossier", variable=self.use_custom_destination, command=self._toggle_destination).pack(anchor="w")
        self.dest_frame = ctk.CTkFrame(c, fg_color="transparent")
        ctk.CTkEntry(self.dest_frame, textvariable=self.destination_folder, placeholder_text="Destination...", height=40).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.dest_frame, text="Choisir", command=self._browse_destination, width=80).pack(side="right")

    def _create_action_buttons(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=20)
        self.prev_btn = ctk.CTkButton(f, text="🔍 ANALYSER", command=self._preview, width=250, height=50, fg_color="#475569")
        self.prev_btn.pack(side="left", expand=True, padx=5)
        self.run_btn = ctk.CTkButton(f, text="🚀 LANCER LE TRI", command=self._start_organize, width=250, height=50, fg_color="#2563EB", font=ctk.CTkFont(weight="bold"))
        self.run_btn.pack(side="left", expand=True, padx=5)

    def _log(self, msg):
        self.log_area.configure(state="normal")
        self.log_area.insert("end", f"> {msg}\n")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")

    def _update_status(self, text, progress=None):
        self.status_label.configure(text=text)
        if progress is not None: self.progress_bar.set(progress)

    # === Callbacks & Logic ===

    def _browse_source(self): 
        p = filedialog.askdirectory()
        if p: self.source_folder.set(p)

    def _browse_destination(self): 
        p = filedialog.askdirectory()
        if p: self.destination_folder.set(p)

    def _on_sort_type_change(self):
        if self.sort_type.get() == "folders": self.file_types_card.pack_forget()
        else: self.file_types_card.pack(fill="x", pady=8, after=self.scroll_frame.winfo_children()[1])

    def _toggle_destination(self):
        if self.use_custom_destination.get(): self.dest_frame.pack(fill="x", pady=10)
        else: self.dest_frame.pack_forget()

    def _add_pattern(self):
        pat = self.pattern_entry.get().strip()
        if pat and pat not in self.ignore_patterns:
            self.ignore_patterns.append(pat)
            self.pattern_entry.delete(0, 'end')
            self._update_patterns_display()

    def _update_patterns_display(self):
        for w in self.patterns_container.winfo_children(): w.destroy()
        for p in self.ignore_patterns:
            tag = ctk.CTkFrame(self.patterns_container, fg_color="#334155", corner_radius=15)
            tag.pack(side="left", padx=3, pady=2)
            ctk.CTkLabel(tag, text=p, font=ctk.CTkFont(size=10)).pack(side="left", padx=(10, 5))
            ctk.CTkButton(tag, text="x", width=15, height=15, command=lambda x=p: self._remove_pattern(x), fg_color="#475569").pack(side="right", padx=(0, 5))

    def _remove_pattern(self, p):
        self.ignore_patterns.remove(p)
        self._update_patterns_display()

    def _get_items(self) -> List[Path]:
        src = Path(self.source_folder.get())
        if not src.exists(): raise ValueError("Dossier source introuvable")
        items = []
        stype = self.sort_type.get()
        if stype in ("files", "both"):
            exts = []
            for t, v in self.file_type_vars.items():
                if v.get(): exts.extend(self.FILE_TYPES[t])
            items.extend([f for f in src.iterdir() if f.is_file() and (not exts or f.suffix.lower() in exts)])
        if stype in ("folders", "both"):
            items.extend([d for d in src.iterdir() if d.is_dir()])
        return items

    def _preview(self):
        if not self.source_folder.get(): return messagebox.showerror("Erreur", "Sélectionnez une source")
        self._set_ui_state("processing")
        threading.Thread(target=self._preview_thread, daemon=True).start()

    def _preview_thread(self):
        try:
            items = self._get_items()
            self._update_status("Analyse intelligente en cours...", 0.1)
            groups = IntelligentGrouper.group_by_intelligence(items, self.grouping_mode.get(), self.ignore_patterns, 
                                                              lambda p: self._update_status(f"Analyse: {int(p*100)}%", p))
            
            res = f"Analyse terminée : {len(groups)} groupes détectés.\n\n"
            for k, v in list(groups.items())[:5]:
                res += f"📁 {k} ({len(v)} éléments)\n"
            if len(groups) > 5: res += f"... et {len(groups)-5} autres."
            
            self.after(0, lambda: messagebox.showinfo("Aperçu", res))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erreur", str(e)))
        finally:
            self.after(0, lambda: self._set_ui_state("ready"))

    def _start_organize(self):
        if not self.source_folder.get(): return messagebox.showerror("Erreur", "Source manquante")
        self._set_ui_state("processing")
        threading.Thread(target=self._organize_thread, daemon=True).start()

    def _organize_thread(self):
        try:
            base = Path(self.destination_folder.get()) if self.use_custom_destination.get() else Path(self.source_folder.get())
            mode = self.grouping_mode.get()
            
            # 1. Consolidation (MAJ v5.0.3)
            if self.consolidate_first.get():
                self._update_status("Consolidation des dossiers...", 0.1)
                self._log(f"Stratégie de consolidation : {self.consolidation_type.get()}")
                cf, cm = IntelligentGrouper.consolidate_duplicate_folders(
                    base, mode, self.ignore_patterns, self.consolidation_type.get()
                )
                if cf: self._log(f"Succès : {cf} dossiers traités ({cm} actions).")

            # 2. Tri
            items = self._get_items()
            self._update_status("Calcul du tri intelligent...", 0.2)
            groups = IntelligentGrouper.group_by_intelligence(items, mode, self.ignore_patterns, 
                                                              lambda p: self._update_status(f"IA: {int(p*100)}%", 0.2 + p*0.4))
            
            # 3. Actions
            total_items = sum(len(v) for v in groups.values())
            current = 0
            
            existing = {d.name: d for d in base.iterdir() if d.is_dir()}
            threshold = {"strict": 0.85, "normal": 0.65, "permissif": 0.45}.get(mode, 0.65)
            
            for gname, gitems in groups.items():
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', gname) or "Divers"
                target_folder = base / safe_name
                
                # Smart Fusion logic
                for ex_name, ex_path in existing.items():
                    if IntelligentGrouper.calculate_smart_similarity(safe_name, ex_name) >= threshold:
                        target_folder = ex_path
                        break
                
                target_folder.mkdir(exist_ok=True)
                
                for item in gitems:
                    dest = target_folder / item.name
                    if dest.exists():
                        stem, suffix = dest.stem, dest.suffix
                        cnt = 1
                        while (target_folder / f"{stem}_{cnt}{suffix}").exists(): cnt += 1
                        dest = target_folder / f"{stem}_{cnt}{suffix}"
                    
                    try:
                        shutil.move(str(item), str(dest))
                        self._log(f"Déplacé : {item.name} -> {target_folder.name}")
                    except Exception as e:
                        self._log(f"ERREUR : {item.name} ({str(e)})")
                    
                    current += 1
                    self._update_status(f"Tri: {current}/{total_items}", 0.6 + (current/total_items)*0.4)
            
            self.after(0, lambda: messagebox.showinfo("Succès", "Tri PRO terminé avec succès !"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erreur", str(e)))
        finally:
            self.after(0, lambda: self._set_ui_state("ready"))

    def _set_ui_state(self, state):
        if state == "processing":
            self.run_btn.configure(state="disabled", text="EN COURS...")
            self.prev_btn.configure(state="disabled")
            self.is_processing = True
            self.log_area.configure(state="normal")
            self.log_area.delete("1.0", "end")
            self.log_area.configure(state="disabled")
        else:
            self.run_btn.configure(state="normal", text="🚀 LANCER LE TRI")
            self.prev_btn.configure(state="normal")
            self.is_processing = False
            self.progress_bar.set(0)
            self.status_label.configure(text="Prêt")


if __name__ == "__main__":
    SmartSorterPRO().mainloop()
