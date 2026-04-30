#!/usr/bin/env python3
"""
MediaNexus PRO v3.0
===================
Gestionnaire de collections multimédias professionnel.

Architecture:
- /core : Logique métier (database, matching, sync, cache)
- /api : Providers API (TMDB, Jikan, RAWG)
- /ui : Interface graphique (profils, dashboard, composants)
- config.py : Configuration globale

Usage:
    python main.py

Build:
    pyinstaller --onefile --windowed --name="MediaNexus_PRO" --clean main.py
"""
import os
import sys

# Ajout du répertoire courant au path pour les imports relatifs
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from config import APP_NAME, APP_VERSION, DB_PATH, CACHE_DIR
from theme import ThemeManager, SIZES
from core import DatabaseManager, MatchingEngine, CacheManager
from api import APIManager
from ui import ProfilesScreen, Dashboard

class MediaNexusPRO(ctk.CTk):
    """
    Application principale MediaNexus PRO.
    Point d'entrée et coordinateur des écrans.
    """

    def __init__(self):
        super().__init__()

        # Initialisation du gestionnaire de thèmes
        self.theme_manager = ThemeManager("dark")
        
        # Configuration de CustomTkinter pour correspondre à notre thème
        ctk.set_appearance_mode("dark")  # Initialisation en dark mode

        # Configuration de la fenêtre
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1280x850")
        self.minsize(1024, 700)
        
        # Application du thème CTk
        # Note: déjà configuré ci-dessus avec ctk.set_appearance_mode("dark")

        # Icône (si disponible)
        try:
            if os.path.exists("app_icon.ico"):
                self.iconbitmap("app_icon.ico")
        except Exception:
            pass

        # Initialisation des modules core
        self.db = DatabaseManager(DB_PATH)
        self.cache = CacheManager(self.db)
        self.api = APIManager()

        # État
        self.current_profile = None

        # Affichage de l'écran de profils
        self._show_profiles_screen()

    def _show_profiles_screen(self):
        """Affiche l'écran de sélection de profil."""
        self._clear_content()
        
        self.profiles_screen = ProfilesScreen(
            self, self.db, self.theme_manager, on_profile_selected=self._on_profile_selected
        )
        self.profiles_screen.pack(fill="both", expand=True)

    def _on_profile_selected(self, profile: dict):
        """Callback appelé lors de la sélection d'un profil."""
        self.current_profile = profile
        # Application immédiate du thème du profil
        theme = profile.get('theme', 'dark')
        self.theme_manager.set_mode(theme)
        self._show_dashboard()

    def _show_dashboard(self):
        """Affiche le dashboard principal."""
        self._clear_content()

        self.dashboard = Dashboard(
            self,
            profile=self.current_profile,
            db_manager=self.db,
            api_manager=self.api,
            cache_manager=self.cache,
            cache_dir=CACHE_DIR,
            theme_manager=self.theme_manager,
            on_logout=self._logout
        )
        self.dashboard.pack(fill="both", expand=True)

    def _logout(self):
        """Déconnexion du profil."""
        self.current_profile = None
        
        # Détruire proprement le dashboard
        if hasattr(self, 'dashboard'):
            self.dashboard.destroy()
            delattr(self, 'dashboard')
        
        # Réinitialiser l'apparence CustomTkinter au thème par défaut
        ctk.set_appearance_mode("dark")
        self.theme_manager.set_mode("dark")
        
        # Réafficher l'écran des profils SANS détruire tout
        self._show_profiles_screen()

    def _clear_content(self):
        """Nettoie le contenu actuel en préservant la structure de base."""
        # Ne détruire que le contenu spécifique (dashboard ou profiles_screen)
        if hasattr(self, 'dashboard'):
            self.dashboard.destroy()
            delattr(self, 'dashboard')
        elif hasattr(self, 'profiles_screen'):
            self.profiles_screen.destroy()
            delattr(self, 'profiles_screen')
        
        # Nettoyer les callbacks de thème pour éviter les erreurs
        self.theme_manager.callbacks.clear()


def main():
    """Point d'entrée principal."""
    app = MediaNexusPRO()
    app.mainloop()


if __name__ == "__main__":
    main()
