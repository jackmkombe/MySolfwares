"""
MediaNexus PRO v3.2 - Interface de Configuration API
Interface pour configurer les clés API et gérer les sources de données
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Dict, Callable
import sys
from pathlib import Path

# Import absolu pour éviter les erreurs de packages
sys.path.insert(0, str(Path(__file__).parent.parent))
from api.synchronizer import MediaSynchronizer
from core.database import DatabaseManager

from ui.components import BaseDialog

class APIConfigDialog(BaseDialog):
    """Dialogue de configuration des clés API."""
    
    def __init__(self, parent, db_manager: DatabaseManager, on_configured: Callable = None):
        super().__init__(parent, title="Configuration des API", width=700, height=600, theme_manager=parent.theme_manager if hasattr(parent, 'theme_manager') else None)
        
        self.db = db_manager
        self.synchronizer = MediaSynchronizer(db_manager)
        self.on_configured = on_configured
        self.theme = self.theme_manager.current_theme
        
        self._build_ui()
        self._load_current_keys()
    
    def _build_ui(self):
        """Construit l'interface utilisateur."""
        # Header
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(pady=20, padx=30, fill="x")
        
        ctk.CTkLabel(
            header, text="🔑 Configuration des Clés API",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.theme["text_primary"]
        ).pack()
        
        ctk.CTkLabel(
            header, text="Configurez vos clés API pour une synchronisation optimale",
            font=ctk.CTkFont(size=12),
            text_color=self.theme["text_secondary"]
        ).pack(pady=(5, 0))
        
        # Scrollable Frame pour les API
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.content, fg_color="transparent", corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.api_entries = {}
        self._build_api_sections()
        
        # Boutons d'action
        button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        button_frame.pack(pady=20, padx=30, fill="x")
        
        # Bouton tester
        self.test_btn = ctk.CTkButton(
            button_frame, text="🧪 Tester les connexions",
            command=self._test_connections,
            fg_color=self.theme["accent_secondary"],
            height=40
        )
        self.test_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Bouton sauvegarder
        self.save_btn = ctk.CTkButton(
            button_frame, text="💾 Sauvegarder",
            command=self._save_keys,
            fg_color=self.theme["accent_primary"],
            height=40
        )
        self.save_btn.pack(side="right", fill="x", expand=True)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.content, text="",
            font=ctk.CTkFont(size=11),
            text_color=self.theme["text_secondary"]
        )
        self.status_label.pack(pady=(0, 10))
    
    def _build_api_sections(self):
        """Construit les sections pour chaque API."""
        api_status = self.synchronizer.get_api_status()
        
        # Films & Séries
        self._add_api_section(
            "🎬 Films & Séries",
            [
                ("omdb", api_status["omdb"]),
                ("tmdb", api_status["tmdb"]),
                ("tvmaze", api_status["tvmaze"])
            ]
        )
        
        # Animés & Mangas
        self._add_api_section(
            "📺 Animés & Mangas",
            [
                ("jikan", api_status["jikan"]),
                ("animeapi", api_status["animeapi"]),
                ("animembed", api_status["animembed"])
            ]
        )
        
        # Jeux Vidéo
        self._add_api_section(
            "🎮 Jeux Vidéo",
            [
                ("rawg", api_status["rawg"]),
                ("igdb", api_status["igdb"])
            ]
        )
    
    def _add_api_section(self, title: str, apis: list):
        """Ajoute une section d'API."""
        # Section header
        section_frame = ctk.CTkFrame(self.scroll_frame, fg_color=self.theme["bg_secondary"])
        section_frame.pack(fill="x", pady=(10, 5), padx=10)
        
        ctk.CTkLabel(
            section_frame, text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme["text_primary"]
        ).pack(pady=10, padx=15, anchor="w")
        
        # API entries
        for api_id, api_info in apis:
            self._add_api_entry(section_frame, api_id, api_info)
    
    def _add_api_entry(self, parent, api_id: str, api_info: Dict):
        """Ajoute une entrée pour une API."""
        # Frame pour l'API
        api_frame = ctk.CTkFrame(parent, fg_color="transparent")
        api_frame.pack(fill="x", pady=5, padx=15, anchor="w")
        
        # Status indicator
        status_color = self.theme["accent_success"] if api_info["configured"] else self.theme["accent_error"]
        status_text = "✅ Configurée" if api_info["configured"] else "❌ Non configurée"
        
        status_label = ctk.CTkLabel(
            api_frame, text=status_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=status_color,
            width=120
        )
        status_label.pack(side="left", padx=(0, 10))
        
        # API name
        name_label = ctk.CTkLabel(
            api_frame, text=api_info["name"],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.theme["text_primary"],
            width=150
        )
        name_label.pack(side="left", padx=(0, 10))
        
        # Description
        desc_label = ctk.CTkLabel(
            api_frame, text=api_info["description"],
            font=ctk.CTkFont(size=10),
            text_color=self.theme["text_secondary"],
            width=120
        )
        desc_label.pack(side="left", padx=(0, 10))
        
        # Input field (seulement si clé requise)
        if api_info.get("free", True) and api_id not in ["tvmaze", "jikan", "animeapi", "animembed"]:
            entry = ctk.CTkEntry(
                api_frame, 
                placeholder_text="Clé API...",
                width=200,
                height=32,
                fg_color=self.theme["bg_tertiary"] if hasattr(self.theme, "bg_tertiary") else self.theme["bg_secondary"],
                text_color=self.theme["text_primary"],
                border_color=self.theme["border_default"] if hasattr(self.theme, "border_default") else "#505050"
            )
            entry.pack(side="right", padx=10)
            self.api_entries[api_id] = entry
            
            # IGDB nécessite aussi un Client ID
            if api_id == "igdb":
                client_id_entry = ctk.CTkEntry(
                    api_frame,
                    placeholder_text="Client ID...",
                    width=150,
                    height=32,
                    fg_color=self.theme["bg_tertiary"] if hasattr(self.theme, "bg_tertiary") else self.theme["bg_secondary"],
                    text_color=self.theme["text_primary"]
                )
                client_id_entry.pack(side="right", padx=5)
                self.api_entries["igdb_client_id"] = client_id_entry
        else:
            # Label "Gratuit" pour les API sans clé
            free_label = ctk.CTkLabel(
                api_frame, text="🆓 Gratuit",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=self.theme["accent_success"],
                width=80
            )
            free_label.pack(side="right", padx=10)
        
        # URL label
        url_label = ctk.CTkLabel(
            api_frame, text=api_info["url"],
            font=ctk.CTkFont(size=8),
            text_color=self.theme["text_muted"] if hasattr(self.theme, "text_muted") else "#888888",
            width=300
        )
        url_label.pack(side="right", padx=5)
    
    def _load_current_keys(self):
        """Charge les clés API actuellement configurées."""
        try:
            with open("api_keys.json", "r") as f:
                import json
                keys = json.load(f)
                
                for api_id, entry in self.api_entries.items():
                    if api_id in keys:
                        entry.delete(0, "end")
                        entry.insert(0, keys[api_id])
        except:
            pass  # Fichier n'existe pas encore
    
    def _test_connections(self):
        """Teste les connexions aux API configurées."""
        self.status_label.configure(text="🧪 Test des connexions en cours...")
        self.update()
        
        # Collecter les clés
        keys = {}
        for api_id, entry in self.api_entries.items():
            key = entry.get().strip()
            if key:
                keys[api_id] = key
        
        # Configurer temporairement
        original_keys = {}
        try:
            with open("api_keys.json", "r") as f:
                original_keys = json.load(f)
        except:
            original_keys = {}
        
        # Tester
        success = self.synchronizer.configure_api_keys(keys)
        
        if success:
            self.status_label.configure(
                text="✅ Test réussi! Les clés API sont valides.",
                text_color=self.theme["accent_success"]
            )
        else:
            self.status_label.configure(
                text="❌ Erreur lors du test. Vérifiez vos clés.",
                text_color=self.theme["accent_error"]
            )
        
        # Restaurer les clés originales si le test échoue
        if not success and original_keys:
            self.synchronizer.configure_api_keys(original_keys)
    
    def _save_keys(self):
        """Sauvegarde les clés API."""
        keys = {}
        for api_id, entry in self.api_entries.items():
            key = entry.get().strip()
            if key:
                keys[api_id] = key
        
        if self.synchronizer.configure_api_keys(keys):
            self.status_label.configure(
                text="✅ Clés API sauvegardées avec succès!",
                text_color=self.theme["accent_success"]
            )
            
            # Notifier le parent
            if self.on_configured:
                self.on_configured(keys)
            
            # Fermer après un court délai
            self.after(1500, self.destroy)
        else:
            self.status_label.configure(
                text="❌ Erreur lors de la sauvegarde des clés.",
                text_color=self.theme["accent_error"]
            )

class APIStatusDialog(ctk.CTkToplevel):
    """Dialogue de statut des API."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        super().__init__(parent)
        
        self.synchronizer = MediaSynchronizer(db_manager)
        
        self.title("Statut des API")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        # Thème
        self.theme = parent.theme_manager.current_theme if hasattr(parent, 'theme_manager') else {
            "bg_primary": "#202020",
            "bg_secondary": "#2D2D2D",
            "text_primary": "#FFFFFF",
            "text_secondary": "#F3F3F3",
            "accent_primary": "#0078D4"
        }
        
        self.configure(fg_color=self.theme["bg_primary"])
        self._build_ui()
    
    def _build_ui(self):
        """Construit l'interface de statut."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=20, padx=30, fill="x")
        
        ctk.CTkLabel(
            header, text="📊 Statut des API",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.theme["text_primary"]
        ).pack()
        
        # Status
        api_status = self.synchronizer.get_api_status()
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Compter les API configurées
        configured_count = sum(1 for api in api_status.values() if api["configured"])
        total_count = len(api_status)
        
        # Résumé
        summary_frame = ctk.CTkFrame(scroll_frame, fg_color=self.theme["bg_secondary"])
        summary_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            summary_frame,
            text=f"📈 {configured_count}/{total_count} API configurées",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme["text_primary"]
        ).pack(pady=15, padx=20)
        
        # Détails par API
        for api_id, info in api_status.items():
            self._add_status_item(scroll_frame, info)
        
        # Bouton fermer
        close_btn = ctk.CTkButton(
            self, text="Fermer",
            command=self.destroy,
            fg_color=self.theme["accent_primary"],
            height=40
        )
        close_btn.pack(pady=20, padx=30, fill="x")
    
    def _add_status_item(self, parent, api_info: Dict):
        """Ajoute un élément de statut."""
        item_frame = ctk.CTkFrame(parent, fg_color=self.theme["bg_secondary"])
        item_frame.pack(fill="x", pady=5, padx=10)
        
        # Status
        status_color = self.theme["accent_success"] if api_info["configured"] else self.theme["accent_error"]
        status_icon = "✅" if api_info["configured"] else "❌"
        
        ctk.CTkLabel(
            item_frame, text=status_icon,
            font=ctk.CTkFont(size=16),
            text_color=status_color,
            width=30
        ).pack(side="left", padx=15)
        
        # Info
        info_text = f"{api_info['name']} - {api_info['description']}"
        if api_info.get("free", True):
            info_text += " (Gratuit)"
        
        ctk.CTkLabel(
            item_frame, text=info_text,
            font=ctk.CTkFont(size=12),
            text_color=self.theme["text_primary"],
            anchor="w"
        ).pack(side="left", padx=10, fill="x", expand=True)
        
        # Config button
        if not api_info["configured"]:
            config_btn = ctk.CTkButton(
                item_frame, text="Configurer",
                width=100,
                height=30,
                fg_color=self.theme["accent_secondary"]
            )
            config_btn.pack(side="right", padx=15)
