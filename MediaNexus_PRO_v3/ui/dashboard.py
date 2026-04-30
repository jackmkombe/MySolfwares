"""
MediaNexus PRO v3.2 - Dashboard Principal
Interface principale avec système de thèmes dynamiques et API intégrées.
"""
import sys
import os
import time
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image

from core import DatabaseManager, MatchingEngine, CacheManager, SyncEngine

# Import des systèmes avancés
try:
    from smart_fetch_engine import SmartSynchronizer, SmartFetchEngine
    from advanced_fetch_config import AdvancedAPIConfig
    from simple_fetch_monitor import SimpleFetchMonitor, SimpleMonitorDialog
    ADVANCED_SYSTEMS = True
    print("✅ Systèmes avancés chargés avec succès")
except ImportError as e:
    print(f"⚠️ Systèmes avancés non disponibles: {e}")
    ADVANCED_SYSTEMS = False

from ui.sections.sidebar import Sidebar
from ui.sections.top_bar import TopBar
from ui.components import (
    MediaCard, SyncProgressBar, ToolTip, 
    StatsDialog, SettingsDialog, MediaDetailsDialog, LibraryDialog
)
from theme import SIZES

class Dashboard(ctk.CTkFrame):
    """
    Dashboard principal de l'application.
    Interface modulaire utilisant des composants externes.
    """

    def __init__(self, parent, profile: dict, db_manager, api_manager, 
                 cache_manager, cache_dir: Path, theme_manager, on_logout):
        super().__init__(parent, fg_color="transparent")
        self.profile = profile
        self.db = db_manager
        self.api = api_manager
        self.cache = cache_manager
        self.cache_dir = cache_dir
        self.theme_manager = theme_manager
        self.on_logout = on_logout
        
        # Initialiser les systèmes avancés
        if ADVANCED_SYSTEMS:
            self.api_config = AdvancedAPIConfig()
            self.synchronizer = SmartSynchronizer(db_manager, self.api_config)
            self.fetch_engine = SmartFetchEngine(self.api_config)
            self.fetch_monitor = SimpleFetchMonitor()
        else:
            self.synchronizer = None
            self.fetch_engine = None
            self.fetch_monitor = None

        self.current_lib = None
        self.view_mode = "grid"
        
        self.theme_manager.register_callback(self._on_theme_change)
        self._build_layout()

    def _on_theme_change(self, theme, mode):
        ctk.set_appearance_mode(mode)
        try:
            self.sidebar.configure(fg_color=theme["bg_secondary"])
            self.content.configure(fg_color=theme["bg_primary"])
            self._refresh_grid()
        except: pass

    def _build_layout(self):
        theme = self.theme_manager.current_theme
        
        # Barre supérieure déléguée au composant TopBar
        self.top_bar = TopBar(
            self, self.profile, self.theme_manager,
            on_toggle_theme=self._toggle_theme,
            on_manage_profiles=self._manage_profiles,
            on_ui_settings=self._ui_settings,
            on_logout=self.on_logout,
            on_configure_apis=self._configure_apis,
            on_open_monitor=self._open_monitor,
            advanced_systems=ADVANCED_SYSTEMS
        )
        self.top_bar.pack(side="top", fill="x")
        
        # Sidebar déléguée au composant Sidebar
        self.sidebar = Sidebar(
            self, self.theme_manager,
            on_add_library=self._ui_add_library,
            on_load_library=self._load_library,
            get_libraries=self.db.get_libraries,
            profile_id=self.profile['id']
        )
        self.sidebar.pack(side="left", fill="y")

        # Contenu principal
        self.content = ctk.CTkFrame(self, fg_color=theme["bg_primary"], corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

        self._show_welcome()

    def _show_welcome(self):
        """Affiche l'écran de bienvenue."""
        for widget in self.content.winfo_children():
            widget.destroy()

        theme = self.theme_manager.current_theme
        
        ctk.CTkLabel(
            self.content, text="Sélectionnez une bibliothèque",
            font=ctk.CTkFont(size=18), text_color=theme["text_tertiary"]
        ).pack(expand=True)



    def _load_library(self, lib: dict):
        """Charge et affiche une bibliothèque."""
        self.current_lib = lib
        theme = self.theme_manager.current_theme

        for widget in self.content.winfo_children():
            widget.destroy()

        # Header
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=30)

        ctk.CTkLabel(
            header, text=lib['name'],
            font=ctk.CTkFont(size=28, weight="bold"), text_color=theme["text_primary"]
        ).pack(side="left")

        # Boutons d'action (Taille accessible 48px)
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        btn_sync = ctk.CTkButton(
            btn_frame, text="🔄 Synchroniser", width=140, height=48,
            fg_color=theme["accent_success"], command=self._start_advanced_sync,
            font=ctk.CTkFont(size=14, weight="bold"), corner_radius=12,
            hover_color=theme["accent_success_hover"], border_width=0
        )
        btn_sync.pack(side="right", padx=10)

        # Bouton Statistiques
        btn_stats = ctk.CTkButton(
            btn_frame, text="📊", width=48, height=48,
            fg_color=theme["accent_secondary"], command=self._show_stats,
            corner_radius=12, font=ctk.CTkFont(size=18),
            hover_color=theme["accent_secondary_hover"], border_width=0
        )
        btn_stats.pack(side="right", padx=8)
        try:
            ToolTip(btn_stats, "Statistiques de la collection")
        except:
            pass

        # Bouton paramètres de la bibliothèque
        btn_settings = ctk.CTkButton(
            btn_frame, text="⚙️", width=48, height=48,
            fg_color=theme["accent_tertiary"], command=self._edit_library_settings,
            corner_radius=12, font=ctk.CTkFont(size=18),
            hover_color=theme["accent_tertiary_hover"], border_width=0
        )
        btn_settings.pack(side="right", padx=8)
        try:
            ToolTip(btn_settings, "Paramètres de la bibliothèque")
        except:
            pass

        btn_delete = ctk.CTkButton(
            btn_frame, text="🗑️", width=48, height=48, fg_color=theme["accent_error"],
            command=self._delete_library, corner_radius=12,
            font=ctk.CTkFont(size=18), hover_color=theme["accent_error_hover"],
            border_width=0
        )
        btn_delete.pack(side="right", padx=8)
        ToolTip(btn_delete, "Supprimer cette bibliothèque")

        # Zone de contrôles (Recherche + Filtres + Tri)
        controls = ctk.CTkFrame(self.content, fg_color=theme["bg_secondary"], corner_radius=12)
        controls.pack(fill="x", padx=30, pady=(0, 20))

        # Recherche
        search_frame = ctk.CTkFrame(controls, fg_color="transparent")
        search_frame.pack(side="left", padx=12, pady=12)
        
        ctk.CTkLabel(search_frame, text="🔍", font=("Arial", 16), text_color=theme["text_tertiary"]).pack(side="left", padx=(0, 8))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._on_search_change())
        
        self.search_entry = ctk.CTkEntry(
            search_frame, textvariable=self.search_var,
            placeholder_text="Rechercher...", width=300, height=40,
            corner_radius=8, border_width=1, border_color=theme["border_default"],
            fg_color=theme["bg_tertiary"], text_color=theme["text_primary"],
            placeholder_text_color=theme["text_muted"], font=ctk.CTkFont(size=13)
        )
        self.search_entry.pack(side="left")

        # Filtres rapides
        filter_frame = ctk.CTkFrame(controls, fg_color="transparent")
        filter_frame.pack(side="left", padx=20, pady=12)

        ctk.CTkLabel(filter_frame, text="Statut:", font=ctk.CTkFont(size=12, weight="bold"), text_color=theme["text_tertiary"]).pack(side="left", padx=(0, 8))
        self.status_filter = ctk.CTkOptionMenu(
            filter_frame, values=["Tous", "Synchronisé", "En attente", "Erreur"],
            width=130, height=40, command=lambda _: self._refresh_grid(),
            corner_radius=8, fg_color=theme["bg_tertiary"], button_color=theme["bg_secondary"],
            button_hover_color=theme["border_hover"],
            text_color=theme["text_primary"], font=ctk.CTkFont(size=12)
        )
        self.status_filter.set("Tous")
        self.status_filter.pack(side="left")

        # Tri
        sort_frame = ctk.CTkFrame(controls, fg_color="transparent")
        sort_frame.pack(side="left", padx=12, pady=12)

        ctk.CTkLabel(sort_frame, text="Trier par:", font=ctk.CTkFont(size=12, weight="bold"), text_color=theme["text_tertiary"]).pack(side="left", padx=(0, 8))
        self.sort_option = ctk.CTkOptionMenu(
            sort_frame, values=["Titre (A-Z)", "Titre (Z-A)", "Score (⬆)", "Score (⬇)", "Date (⬆)", "Date (⬇)"],
            width=140, height=40, command=lambda _: self._refresh_grid(),
            corner_radius=8, fg_color=theme["bg_tertiary"], button_color=theme["bg_secondary"],
            button_hover_color=theme["border_hover"],
            text_color=theme["text_primary"], font=ctk.CTkFont(size=12)
        )
        self.sort_option.set("Titre (A-Z)")
        self.sort_option.pack(side="left")

        # Statistiques compactes
        self.stats_label = ctk.CTkLabel(
            controls, text="📊 0 éléments", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#64748B"
        )
        self.stats_label.pack(side="right", padx=20, pady=12)

        # Conteneur pour les onglets
        self.tab_container = ctk.CTkFrame(self.content, fg_color="transparent")
        self.tab_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Initialiser avec la vue Collection
        self._change_tab("Collection")

    def _on_search_change(self):
        """Callback appelé lors de la saisie dans la recherche."""
        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)
        # Debouncing 300ms
        self._search_timer = self.after(300, self._refresh_grid)

    def _change_tab(self, tab_name: str):
        """Change l'onglet actuel (Collection ou Historique)."""
        # Vider le conteneur
        for widget in self.tab_container.winfo_children():
            widget.destroy()
        
        if tab_name == "Collection":
            self._show_collection_view()
        elif tab_name == "Historique":
            self._show_historique_view()
    
    def _show_collection_view(self):
        """Affiche la vue collection (grille d'éléments)."""
        theme = self.theme_manager.current_theme
        
        # Vue sélecteur pour la collection
        view_frame = ctk.CTkFrame(self.tab_container, fg_color="transparent")
        view_frame.pack(fill="x", pady=(0, 10))
        
        self.view_selector = ctk.CTkSegmentedButton(
            view_frame, values=["Grille", "Liste", "Compact"],
            command=self._change_view,
            fg_color=theme["bg_secondary"], selected_color=theme["accent_primary"],
            text_color=theme["text_secondary"], selected_hover_color=theme["accent_secondary"]
        )
        self.view_selector.set("Grille")
        self.view_selector.pack(side="right")
        
        # Conteneur pour la grille d'éléments
        self.items_container = ctk.CTkScrollableFrame(
            self.tab_container, fg_color="transparent", height=500
        )
        self.items_container.pack(fill="both", expand=True)
        
        # Alias pour compatibilité
        self.media_grid = self.items_container
        
        # Charger les éléments
        self._refresh_grid()
    
    def _show_historique_view(self):
        """Affiche la vue historique intégrée."""
        if not self.current_lib:
            return
            
        # Stats de l'historique
        stats = self.db.get_historique_stats(self.current_lib['id'])
        
        stats_frame = ctk.CTkFrame(self.tab_container, fg_color="#0F172A", corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 15))
        
        # Créer les étiquettes de statistiques
        for i, (label, color) in enumerate([
            ("Total", "#3B82F6"),
            ("Synchronisés", "#22C55E"),
            ("Non synchronisés", "#F59E0B"),
            ("Erreurs", "#EF4444")
        ]):
            frame = ctk.CTkFrame(stats_frame, fg_color="#1E293B", corner_radius=8)
            frame.pack(side="left", expand=True, fill="x", padx=5, pady=10)
            
            ctk.CTkLabel(
                frame, text=label, font=ctk.CTkFont(size=12),
                text_color="#94A3B8"
            ).pack(pady=(10, 2))
            
            value = stats.get(f"{label.lower()}_count" if label != "Total" else "total", 0)
            ctk.CTkLabel(
                frame, text=str(value), font=ctk.CTkFont(size=20, weight="bold"),
                text_color=color
            ).pack(pady=(0, 10))
        
        # Barre de recherche pour l'historique
        search_frame = ctk.CTkFrame(self.tab_container, fg_color="#0F172A", corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 15))
        
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(search_container, text="🔍", font=("Arial", 16)).pack(side="left", padx=(0, 10))
        
        self.historique_search_var = ctk.StringVar()
        self.historique_search_var.trace_add("write", lambda *args: self._on_historique_search_change())
        
        self.historique_search_entry = ctk.CTkEntry(
            search_container, textvariable=self.historique_search_var,
            placeholder_text="Rechercher dans l'historique...", width=400, height=35
        )
        self.historique_search_entry.pack(side="left", fill="x", expand=True)
        
        # Historique scrollable
        self.historique_scroll = ctk.CTkScrollableFrame(
            self.tab_container, fg_color="transparent", height=400
        )
        self.historique_scroll.pack(fill="both", expand=True)
        
        # Récupérer et afficher l'historique
        self._refresh_historique_view()
    
    def _create_historique_item_integrated(self, item: dict, parent):
        """Crée une carte d'élément d'historique intégrée."""
        frame = ctk.CTkFrame(
            parent, fg_color="#1E293B", corner_radius=8,
            border_width=1, border_color="#334155"
        )
        frame.pack(fill="x", pady=5, padx=5)
        
        # Conteneur principal
        main_frame = ctk.CTkFrame(frame, fg_color="transparent")
        main_frame.pack(fill="x", padx=15, pady=10)
        
        # Titre et statut
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x")
        
        # Déterminer le titre à afficher
        title = item.get('full_title') or item.get('title_only') or item['raw_name']
        
        # Icône de statut
        if item['was_synced']:
            status_icon = "✅"
            status_color = "#22C55E"
            status_text = "Synchronisé"
        elif item['sync_status_before_delete'] == 'error':
            status_icon = "❌"
            status_color = "#EF4444"
            status_text = "Erreur"
        else:
            status_icon = "⏳"
            status_color = "#F59E0B"
            status_text = "Non synchronisé"
        
        ctk.CTkLabel(
            title_frame, text=f"{status_icon} {title}",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#F1F5F9"
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame, text=status_text,
            font=ctk.CTkFont(size=11), text_color=status_color
        ).pack(side="right")
        
        # Métadonnées si synchronisé
        if item['was_synced'] and item.get('release_year'):
            meta_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            meta_frame.pack(fill="x", pady=(5, 0))
            
            meta_text = f"Année: {item['release_year']}"
            if item.get('score'):
                meta_text += f" • Score: {item['score']:.1f}/10"
            if item.get('api_source'):
                meta_text += f" • Source: {item['api_source'].upper()}"
            
            ctk.CTkLabel(
                meta_frame, text=meta_text,
                font=ctk.CTkFont(size=11), text_color="#94A3B8"
            ).pack(side="left")
        
        # Date de suppression
        ctk.CTkLabel(
            main_frame, text=f"Supprimé le: {item['deleted_at'][:10]}",
            font=ctk.CTkFont(size=10), text_color="#64748B"
        ).pack(side="right", pady=(5, 0))

    def _on_historique_search_change(self):
        """Callback appelé lors de la saisie dans la recherche d'historique."""
        if hasattr(self, '_historique_search_timer'):
            self.after_cancel(self._historique_search_timer)
        # Debouncing 300ms
        self._historique_search_timer = self.after(300, self._refresh_historique_view)
    
    def _refresh_historique_view(self):
        """Rafraîchit la vue historique avec filtre de recherche."""
        if not hasattr(self, 'historique_scroll'):
            return
            
        # Vider le conteneur
        for widget in self.historique_scroll.winfo_children():
            widget.destroy()
        
        # Récupérer l'historique
        all_historique = self.db.get_historique(self.current_lib['id'], limit=100)
        
        # Filtrer par recherche si nécessaire
        filtered_historique = all_historique
        if hasattr(self, 'historique_search_var'):
            query = self.historique_search_var.get().lower()
            if query:
                filtered_historique = [
                    item for item in all_historique
                    if (item.get('full_title') or item.get('title_only') or item['raw_name']).lower().find(query) != -1
                    or (item.get('original_title') and item['original_title'].lower().find(query) != -1)
                    or (item.get('api_source') and item['api_source'].lower().find(query) != -1)
                ]
        
        if not filtered_historique:
            ctk.CTkLabel(
                self.historique_scroll, text="📚 Aucun élément trouvé",
                font=ctk.CTkFont(size=16), text_color="#64748B"
            ).pack(pady=50)
            return
        
        # Afficher les éléments filtrés
        for item in filtered_historique:
            self._create_historique_item_integrated(item, self.historique_scroll)

    def _show_stats(self):
        """Affiche un dashboard de statistiques de la bibliothèque."""
        if not self.current_lib: return
        items = self.db.get_items(self.current_lib['id'])
        
        synced = len([i for i in items if i.get('sync_status') == 'synced'])
        total = len(items)
        stats = {
            'total': total,
            'synced': synced,
            'pending': len([i for i in items if i.get('sync_status') == 'pending']),
            'errors': len([i for i in items if i.get('sync_status') == 'error']),
            'avg_score': sum([float(i.get('score') or 0) for i in items if i.get('score')]) / (len([i for i in items if i.get('score')]) or 1),
            'completion': (synced / total * 100) if total > 0 else 0
        }
        StatsDialog(self, self.current_lib['name'], stats, self.theme_manager)

    def _edit_library_settings(self):
        """Dialogue de modification des paramètres de bibliothèque."""
        if not self.current_lib: return

        def on_save(new_data, dialog):
            try:
                self.db.update_library(
                    self.current_lib['id'],
                    new_data['name'],
                    new_data['type'],
                    new_data['source'],
                    new_data['lang'],
                    new_data['translate']
                )
                # Mettre à jour l'objet local
                self.current_lib.update({
                    'name': new_data['name'],
                    'type': new_data['type'],
                    'source': new_data['source'],
                    'preferred_lang': new_data['lang'],
                    'translate_synopsis': 1 if new_data['translate'] else 0
                })
                dialog.destroy()
                self._load_library(self.current_lib) # Rafraîchir tout (nom Sidebar etc)
                messagebox.showinfo("Succès", "Bibliothèque mise à jour avec succès !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de mettre à jour : {e}")

        SettingsDialog(self, self.current_lib, on_save, self.theme_manager)

        # Zone de grille scrollable
        self.media_grid = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.media_grid.pack(fill="both", expand=True, padx=20)

        self._refresh_grid()

    def _refresh_grid(self):
        """Rafraîchit l'affichage avec recherche, filtres et tri."""
        for widget in self.media_grid.winfo_children():
            widget.destroy()

        if not self.current_lib:
            return

        # Récupération brute
        all_items = self.db.get_items(self.current_lib['id'])

        if not all_items:
            # État vide moderne
            empty_container = ctk.CTkFrame(self.media_grid, fg_color="transparent")
            empty_container.pack(expand=True, pady=100)
            
            ctk.CTkLabel(
                empty_container, text="📦",
                font=("Arial", 80)
            ).pack(pady=(0, 20))
            
            ctk.CTkLabel(
                empty_container, text="Collection Vide",
                font=ctk.CTkFont(size=24, weight="bold")
            ).pack()
            
            ctk.CTkLabel(
                empty_container, text="Aucun média détecté dans cette bibliothèque.",
                font=ctk.CTkFont(size=14), text_color="#94A3B8"
            ).pack(pady=5)
            
            ctk.CTkButton(
                empty_container, text="🔄 Lancer la Synchronisation",
                command=self._start_sync, height=50, width=250,
                fg_color="#10B981", font=ctk.CTkFont(weight="bold")
            ).pack(pady=30)
            
            if hasattr(self, 'stats_label'):
                self.stats_label.configure(text="📊 0 éléments")
            return

        # --- FILTRAGE ---
        filtered_items = all_items

        # Filtre recherche
        if hasattr(self, 'search_var'):
            query = self.search_var.get().lower()
            if query:
                filtered_items = [
                    item for item in filtered_items
                    if query in (item.get('title') or '').lower() or 
                       query in (item.get('raw_name') or '').lower()
                ]

        # Filtre statut
        if hasattr(self, 'status_filter'):
            status_map = {
                "Synchronisé": "synced",
                "En attente": "pending",
                "Erreur": "error"
            }
            selected = self.status_filter.get()
            if selected != "Tous":
                target_status = status_map.get(selected)
                filtered_items = [item for item in filtered_items if item.get('sync_status') == target_status]

        # --- TRI ---
        if hasattr(self, 'sort_option'):
            sort_choice = self.sort_option.get()
            
            if sort_choice == "Titre (A-Z)":
                filtered_items.sort(key=lambda x: (x.get('title') or x.get('raw_name', '')).lower())
            elif sort_choice == "Titre (Z-A)":
                filtered_items.sort(key=lambda x: (x.get('title') or x.get('raw_name', '')).lower(), reverse=True)
            elif sort_choice == "Score (⬆)":
                filtered_items.sort(key=lambda x: float(x.get('score') or 0))
            elif sort_choice == "Score (⬇)":
                filtered_items.sort(key=lambda x: float(x.get('score') or 0), reverse=True)
            elif sort_choice == "Date (⬆)":
                filtered_items.sort(key=lambda x: x.get('release_date') or "0000")
            elif sort_choice == "Date (⬇)":
                filtered_items.sort(key=lambda x: x.get('release_date') or "0000", reverse=True)

        # Mise à jour statistiques
        if hasattr(self, 'stats_label'):
            total = len(all_items)
            shown = len(filtered_items)
            synced = len([i for i in all_items if i.get('sync_status') == 'synced'])
            self.stats_label.configure(text=f"📊 {shown}/{total} éléments • ✅ {synced} synchronisés")

        # Calcul responsive des colonnes
        self.update_idletasks()
        container_width = self.media_grid.winfo_width()
        card_width_with_padding = 175 + 24
        
        if container_width > 100:
            calculated_cols = max(1, container_width // card_width_with_padding)
        else:
            calculated_cols = {"grid": 5, "compact": 3, "list": 1}.get(self.view_mode, 5)

        # Affichage des cartes
        row, col = 0, 0
        for item in filtered_items:
            card = MediaCard(
                self.media_grid, item, self.cache_dir, self.theme_manager,
                on_click=self._show_item_details
            )
            card.grid(row=row, column=col, padx=12, pady=12, sticky="n")
            col += 1
            if col >= calculated_cols:
                col = 0
                row += 1
        
        self.media_grid.bind("<Configure>", lambda e: self._on_grid_resize())

    def _change_view(self, value):
        """Change le mode d'affichage."""
        modes = {"Grille": "grid", "Liste": "list", "Compact": "compact"}
        self.view_mode = modes.get(value, "grid")
        self._refresh_grid()

    def _on_grid_resize(self):
        """Callback appelé lors du redimensionnement du container."""
        # Debouncing pour éviter trop de recalculs
        if hasattr(self, '_resize_timer'):
            self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(300, self._refresh_grid)

    def _start_sync(self):
        """Lance la synchronisation."""
        if not self.current_lib:
            return

        # Création de la fenêtre de progression
        progress_window = SyncProgressBar(self)

        # Configuration du moteur de sync (MatchingEngine déjà importé en haut)
        sync_engine = SyncEngine(self.db, self.api, self.cache, MatchingEngine, monitor=self.fetch_monitor)

        def on_progress(progress):
            if not progress_window.winfo_exists():
                sync_engine.cancel()
                return
            self.after(0, lambda: progress_window.update_progress(progress))

        def on_complete():
            self.after(0, self._refresh_grid)
            # Afficher un résumé si le monitoring est actif
            if ADVANCED_SYSTEMS and self.fetch_monitor:
                stats = self.fetch_monitor.get_current_stats()
                if stats['total_requests'] > 0:
                    msg = f"✅ Sync terminée!\nPassages API: {stats['total_requests']}\nSuccès: {stats['success_rate']:.1f}%"
                    self.after(500, lambda: messagebox.showinfo("Stats Sync", msg))

        sync_engine.set_progress_callback(on_progress)
        sync_engine.set_completion_callback(on_complete)
        sync_engine.start_sync(self.current_lib)

    def _show_item_details(self, item: dict):
        """Affiche les détails d'un média via le dialogue modulaire."""
        MediaDetailsDialog(self, item, self.cache_dir, self.theme_manager)

    def _delete_library(self):
        """Supprime la bibliothèque courante."""
        if not self.current_lib:
            return

        if messagebox.askyesno("Supprimer", f"Supprimer '{self.current_lib['name']}' ?"):
            self.db.delete_library(self.current_lib['id'])
            self.current_lib = None
            self._refresh_lib_list()
            self._show_welcome()

    def _ui_add_library(self):
        """Dialogue d'ajout de bibliothèque via le composant modulaire."""
        def on_save(name, lib_type, path, dialog):
            self.db.create_library(self.profile['id'], name, lib_type, [path])
            self._refresh_lib_list()
            dialog.destroy()
            messagebox.showinfo("Succès", f"Bibliothèque '{name}' créée !")

        LibraryDialog(self, on_save, self.theme_manager)

    def _toggle_theme(self):
        """Change le mode de thème (Dark/Light)."""
        new_mode = "light" if self.theme_manager.current_mode == "dark" else "dark"
        self.theme_manager.set_mode(new_mode)

    def _configure_apis(self):
        """Ouvre le dialogue de configuration des API (système avancé)."""
        if ADVANCED_SYSTEMS:
            from ui.api_config import APIConfigDialog
            APIConfigDialog(self, self.db)
        else:
            self._ui_settings()

    def _ui_settings(self):
        """Dialogue des paramètres API classique (fallback)."""
        theme = self.theme_manager.current_theme
        win = ctk.CTkToplevel(self)
        win.title("Paramètres API")
        win.geometry("500x450")
        win.attributes("-topmost", True)
        win.configure(fg_color=theme["bg_primary"])

        ctk.CTkLabel(
            win, text="Configuration API", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=30)

        tmdb_entry = ctk.CTkEntry(win, placeholder_text="Clé TMDB (Films/Séries)", width=400, height=40)
        tmdb_entry.pack(pady=10)
        if self.api.keys.get('tmdb'): tmdb_entry.insert(0, self.api.keys['tmdb'])

        rawg_entry = ctk.CTkEntry(win, placeholder_text="Clé RAWG (Jeux)", width=400, height=40)
        rawg_entry.pack(pady=10)
        if self.api.keys.get('rawg'): rawg_entry.insert(0, self.api.keys['rawg'])

        def save():
            keys = {
                "tmdb": tmdb_entry.get().strip(),
                "rawg": rawg_entry.get().strip()
            }
            self.api.update_keys(keys)
            win.destroy()
            messagebox.showinfo("OK", "Clés mises à jour !")

        ctk.CTkButton(
            win, text="💾 SAUVEGARDER", command=save, height=50, 
            fg_color=theme["accent_primary"]
        ).pack(pady=40)

    def _open_monitor(self):
        """Ouvre le moniteur de fetching."""
        if ADVANCED_SYSTEMS and self.fetch_monitor:
            from simple_fetch_monitor import SimpleMonitorDialog
            SimpleMonitorDialog(self, self.fetch_monitor)
        else:
            messagebox.showinfo("Info", "Moniteur non disponible.")

    def _start_advanced_sync(self):
        """Lance la synchronisation intelligente."""
        if ADVANCED_SYSTEMS and self.synchronizer:
            # Pour l'instant on utilise le moteur classique mais on pourrait utiliser le SmartSynchronizer
            self._start_sync()
        else:
            self._start_sync()

    def _refresh_lib_list(self):
        """Demande à la sidebar de se rafraîchir."""
        if hasattr(self, 'sidebar'):
            self.sidebar.refresh()

    def _manage_profiles(self):
        """Affiche l'écran de gestion des profils."""
        win = ctk.CTkToplevel(self)
        win.title("Gestion des Profils")
        win.geometry("800x600")
        win.attributes("-topmost", True)
        
        theme = self.theme_manager.current_theme
        
        # Header
        header = ctk.CTkFrame(win, fg_color=theme["bg_secondary"], height=80)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text="👥 Gestion des Profils",
            font=ctk.CTkFont(size=24, weight="bold"), text_color=theme["text_primary"]
        ).pack(pady=25)
        
        # Liste des profils
        profiles_frame = ctk.CTkScrollableFrame(win, fg_color="transparent", height=400)
        profiles_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Charger les profils
        profiles = self.db.get_profiles()
        
        for profile in profiles:
            self._create_profile_management_card(profiles_frame, profile, theme, win)
    
    def _create_profile_management_card(self, parent, profile: dict, theme: dict, parent_win):
        """Crée une carte de gestion de profil."""
        card = ctk.CTkFrame(
            parent, fg_color=theme["bg_secondary"],
            border_width=1, border_color=theme["border_default"]
        )
        card.pack(fill="x", pady=10, padx=5)
        
        # Contenu principal
        main_frame = ctk.CTkFrame(card, fg_color="transparent")
        main_frame.pack(fill="x", padx=20, pady=15)
        
        # Info profil
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        # Nom et statut
        name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_frame.pack(fill="x")
        
        is_current = profile['id'] == self.profile['id']
        status_text = " (Connecté)" if is_current else ""
        status_color = theme["accent_primary"] if is_current else theme["text_secondary"]
        
        ctk.CTkLabel(
            name_frame, text=f"👤 {profile['name']}{status_text}",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=status_color
        ).pack(side="left")
        
        # Thème
        ctk.CTkLabel(
            info_frame, text=f"Thème: {profile.get('theme', 'dark').title()}",
            font=ctk.CTkFont(size=12), text_color=theme["text_secondary"]
        ).pack(pady=(5, 0))
        
        # Mot de passe
        has_password = "🔐 Protégé" if profile.get('password_hash') else "🔓 Non protégé"
        ctk.CTkLabel(
            info_frame, text=f"Sécurité: {has_password}",
            font=ctk.CTkFont(size=12), text_color=theme["text_secondary"]
        ).pack(pady=(2, 0))
        
        # Boutons d'action
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        # Bouton éditer
        ctk.CTkButton(
            buttons_frame, text="✏️ Éditer", width=100, height=35,
            fg_color=theme["accent_secondary"], command=lambda: self._edit_profile_management(profile, parent_win)
        ).pack(pady=2)
        
        # Bouton supprimer (désactivé si profil courant)
        delete_color = theme["bg_tertiary"] if is_current else theme["accent_error"]
        delete_state = "disabled" if is_current else "normal"
        
        ctk.CTkButton(
            buttons_frame, text="🗑️ Supprimer", width=100, height=35,
            fg_color=delete_color, state=delete_state,
            command=lambda: self._delete_profile_management(profile, parent_win) if not is_current else None
        ).pack(pady=2)
    
    def _edit_profile_management(self, profile: dict, parent_win):
        """Dialogue d'édition de profil."""
        win = ctk.CTkToplevel(parent_win)
        win.title=f"Éditer {profile['name']}"
        win.geometry("450x450")
        win.attributes("-topmost", True)
        win.resizable(False, False)
        
        theme = self.theme_manager.current_theme
        
        # Centrer la fenêtre
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (450 // 2)
        y = (win.winfo_screenheight() // 2) - (450 // 2)
        win.geometry(f"450x450+{x}+{y}")
        
        ctk.CTkLabel(
            win, text=f"✏️ Éditer le profil '{profile['name']}'",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=theme["accent_primary"]
        ).pack(pady=25)
        
        # Nom (non modifiable)
        ctk.CTkLabel(
            win, text="Nom du profil", anchor="w",
            font=ctk.CTkFont(size=14), text_color=theme["text_secondary"]
        ).pack(padx=40, fill="x", pady=(20, 5))
        
        name_entry = ctk.CTkEntry(win, width=350, height=40)
        name_entry.insert(0, profile['name'])
        name_entry.configure(state="disabled")
        name_entry.pack(padx=40)
        
        # Thème
        ctk.CTkLabel(
            win, text="Thème", anchor="w",
            font=ctk.CTkFont(size=14), text_color=theme["text_secondary"]
        ).pack(padx=40, fill="x", pady=(20, 5))
        
        theme_var = ctk.StringVar(value=profile.get('theme', 'dark'))
        theme_menu = ctk.CTkOptionMenu(win, values=["dark", "light"], variable=theme_var, width=350, height=40)
        theme_menu.pack(padx=40)
        
        # Mot de passe actuel
        ctk.CTkLabel(
            win, text="Mot de passe actuel", anchor="w",
            font=ctk.CTkFont(size=14), text_color=theme["text_secondary"]
        ).pack(padx=40, fill="x", pady=(20, 5))
        
        current_password_entry = ctk.CTkEntry(win, width=350, height=40, placeholder_text="Laisser vide pour ne pas changer", show="•")
        current_password_entry.pack(padx=40)
        
        # Nouveau mot de passe
        ctk.CTkLabel(
            win, text="Nouveau mot de passe", anchor="w",
            font=ctk.CTkFont(size=14), text_color=theme["text_secondary"]
        ).pack(padx=40, fill="x", pady=(20, 5))
        
        new_password_entry = ctk.CTkEntry(win, width=350, height=40, placeholder_text="Laisser vide pour ne pas changer", show="•")
        new_password_entry.pack(padx=40)
        
        # Confirmation nouveau mot de passe
        ctk.CTkLabel(
            win, text="Confirmer le nouveau mot de passe", anchor="w",
            font=ctk.CTkFont(size=14), text_color=theme["text_secondary"]
        ).pack(padx=40, fill="x", pady=(20, 5))
        
        confirm_new_entry = ctk.CTkEntry(win, width=350, height=40, placeholder_text="Confirmer le nouveau mot de passe", show="•")
        confirm_new_entry.pack(padx=40)
        
        def save():
            new_theme = theme_var.get()
            current_password = current_password_entry.get()
            new_password = new_password_entry.get()
            confirm_new = confirm_new_entry.get()
            
            # Vérifier le mot de passe actuel si changement
            if new_password and not current_password:
                messagebox.showerror("Erreur", "Entrez le mot de passe actuel pour le changer")
                return
                
            if new_password and new_password != confirm_new:
                messagebox.showerror("Erreur", "Les nouveaux mots de passe ne correspondent pas")
                return
            
            # Vérifier le mot de passe actuel
            if current_password:
                import hashlib
                current_hash = hashlib.sha256(current_password.encode()).hexdigest()
                if current_hash != profile.get('password_hash'):
                    messagebox.showerror("Erreur", "Mot de passe actuel incorrect")
                    return
            
            try:
                # Mettre à jour le thème
                cursor = self.db._get_connection().cursor()
                cursor.execute("UPDATE profiles SET theme=? WHERE id=?", (new_theme, profile['id']))
                
                # Mettre à jour le mot de passe si nécessaire
                if new_password:
                    import hashlib
                    new_hash = hashlib.sha256(new_password.encode()).hexdigest()
                    cursor.execute("UPDATE profiles SET password_hash=? WHERE id=?", (new_hash, profile['id']))
                
                self.db._get_connection().commit()
                
                # Si c'est le profil courant, appliquer le thème immédiatement
                if profile['id'] == self.profile['id']:
                    self.theme_manager.set_mode(new_theme)
                    self.profile['theme'] = new_theme
                
                win.destroy()
                parent_win.destroy()  # Fermer la fenêtre de gestion
                self._manage_profiles()  # Rafraîchir la liste
                messagebox.showinfo("Succès", "Profil mis à jour avec succès !")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la mise à jour : {e}")
        
        # Boutons
        button_frame = ctk.CTkFrame(win, fg_color="transparent")
        button_frame.pack(pady=25)
        
        ctk.CTkButton(
            button_frame, text="Annuler", width=120, height=40,
            fg_color="transparent", border_width=1, border_color=theme["border_default"],
            command=win.destroy
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame, text="Sauvegarder", width=120, height=40,
            fg_color=theme["accent_primary"], command=save
        ).pack(side="left", padx=10)
    
    def _delete_profile_management(self, profile: dict, parent_win):
        """Supprime un profil après confirmation."""
        if messagebox.askyesno(
            "Supprimer le profil", 
            f"Êtes-vous sûr de vouloir supprimer le profil '{profile['name']}' ?\n\n"
            "Toutes ses bibliothèques et données seront PERDUES.\n"
            "Cette action est IRRÉVERSIBLE."
        ):
            try:
                self.db.delete_profile(profile['id'])
                parent_win.destroy()  # Fermer la fenêtre de gestion
                self._manage_profiles()  # Rafraîchir la liste
                messagebox.showinfo("Succès", f"Profil '{profile['name']}' supprimé avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")

