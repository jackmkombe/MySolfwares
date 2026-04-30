"""
MediaNexus PRO v3.2 - Écran de Sélection de Profils
Interface de login style console (PlayStation/Xbox) avec thèmes dynamiques.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import customtkinter as ctk
from tkinter import messagebox
from ui.components import ProfileCard, LoginDialog, ProfileCreationDialog

class ProfilesScreen(ctk.CTkFrame):
    """
    Écran de sélection de profil utilisateur.
    Premier écran affiché au lancement.
    """

    def __init__(self, parent, db_manager, theme_manager, on_profile_selected):
        super().__init__(parent, fg_color="transparent")
        self.db = db_manager
        self.theme_manager = theme_manager
        self.on_profile_selected = on_profile_selected
        
        # Enregistrer le callback pour les changements de thème
        self.theme_manager.register_callback(self._on_theme_change)

        self._build_ui()

    def _on_theme_change(self, theme, mode):
        """Callback appelé lors du changement de thème."""
        try:
            # Vérifier si le widget existe toujours
            if self.winfo_exists():
                # Recréer l'UI avec le nouveau thème
                for widget in self.winfo_children():
                    widget.destroy()
                self._build_ui()
        except:
            # Le widget a été détruit, ignorer le callback
            pass

    def _build_ui(self):
        # Récupérer le thème actuel
        theme = self.theme_manager.current_theme
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(60, 40))

        ctk.CTkLabel(
            header, text="💎 MEDIANEXUS PRO",
            font=ctk.CTkFont(size=36, weight="bold"), text_color=theme["accent_primary"]
        ).pack()

        ctk.CTkLabel(
            header, text="Sélectionnez votre profil",
            font=ctk.CTkFont(size=16), text_color=theme["text_tertiary"]
        ).pack(pady=10)

        # Container des profils
        self.profiles_container = ctk.CTkFrame(self, fg_color="transparent")
        self.profiles_container.pack(pady=30)

        self._load_profiles()

    def _load_profiles(self):
        """Charge et affiche tous les profils."""
        theme = self.theme_manager.current_theme
        
        for widget in self.profiles_container.winfo_children():
            widget.destroy()

        profiles = self.db.get_profiles()

        for profile in profiles:
            card = ProfileCard(
                self.profiles_container,
                profile,
                theme,
                on_click=self._select_profile,
                on_delete=self._delete_profile
            )
            card.pack(side="left", padx=20)

        # Bouton "Ajouter"
        add_frame = ctk.CTkFrame(self.profiles_container, fg_color="transparent")
        add_frame.pack(side="left", padx=20)

        ctk.CTkButton(
            add_frame, text="➕", font=("Arial", 50), width=140, height=140,
            corner_radius=20, fg_color="transparent", border_width=2, border_color=theme["border_default"],
            hover_color=theme["hover_overlay"], command=self._create_profile
        ).pack()

        ctk.CTkLabel(add_frame, text="Nouveau", font=ctk.CTkFont(size=15), text_color=theme["text_secondary"]).pack(pady=8)

    def _select_profile(self, profile: dict):
        """Demande le mot de passe via le dialogue modulaire."""
        if not profile.get('password_hash'):
            self.on_profile_selected(profile)
            return
            
        def on_login(prof, password):
            if self.db.verify_password(prof['id'], password):
                self.on_profile_selected(prof)
                return True
            else:
                messagebox.showerror("Erreur", "Mot de passe incorrect")
                return False

        LoginDialog(self, profile, on_login, self.theme_manager)

    def _create_profile(self):
        """Dialogue de création de profil via le dialogue modulaire."""
        def on_save(name, password, dialog):
            try:
                self.db.create_profile(name, password=password)
                self._load_profiles()
                dialog.destroy()
                messagebox.showinfo("Succès", f"Profil '{name}' créé avec succès !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la création : {e}")

        ProfileCreationDialog(self, on_save, self.theme_manager)

    def _delete_profile(self, profile: dict):
        """Suppression d'un profil après confirmation."""
        if messagebox.askyesno("Supprimer", f"Supprimer le profil '{profile['name']}' ?\nToutes ses bibliothèques seront effacées."):
            self.db.delete_profile(profile['id'])
            self._load_profiles()
