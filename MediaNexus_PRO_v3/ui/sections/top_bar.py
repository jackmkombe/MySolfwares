import customtkinter as ctk
from theme import SIZES
from ui.components import ToolTip

class TopBar(ctk.CTkFrame):
    def __init__(self, parent, profile, theme_manager, on_toggle_theme, on_manage_profiles, 
                 on_ui_settings, on_logout, on_configure_apis, on_open_monitor, advanced_systems=False):
        theme = theme_manager.current_theme
        super().__init__(parent, height=SIZES["header_height"]-20, corner_radius=0, fg_color=theme["bg_secondary"])
        self.pack_propagate(False)
        
        self.profile = profile
        self.theme_manager = theme_manager
        self.advanced_systems = advanced_systems
        self.callbacks = {
            'theme': on_toggle_theme,
            'profiles': on_manage_profiles,
            'settings': on_ui_settings,
            'logout': on_logout,
            'apis': on_configure_apis,
            'monitor': on_open_monitor
        }
        
        self.theme_manager.register_callback(self._on_theme_update)
        self._build_ui()

    def _on_theme_update(self, theme, mode):
        self.configure(fg_color=theme["bg_secondary"])
        self._build_ui() # Rebuild to apply colors to all children

    def _build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        theme = self.theme_manager.current_theme
        
        # Conteneur principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Section gauche - Nom du profil
        left_section = ctk.CTkFrame(main_container, fg_color="transparent")
        left_section.pack(side="left", fill="x", expand=True)
        
        profile_frame = ctk.CTkFrame(left_section, fg_color="transparent")
        profile_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(
            profile_frame, text="👤", font=ctk.CTkFont(size=18), text_color=theme["accent_primary"]
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            profile_frame, text=self.profile['name'],
            font=ctk.CTkFont(size=14, weight="bold"), text_color=theme["text_primary"]
        ).pack(side="left")
        
        # Section droite
        right_section = ctk.CTkFrame(main_container, fg_color="transparent")
        right_section.pack(side="right")
        
        def add_btn(icon, cmd, tip, hover_key):
            btn = ctk.CTkButton(
                right_section, text=icon, width=40, height=40,
                fg_color="transparent", border_width=1,
                border_color=theme["border_default"],
                corner_radius=8, command=cmd,
                font=ctk.CTkFont(size=18),
                hover_color=theme[hover_key]
            )
            btn.pack(side="left", padx=5)
            try: ToolTip(btn, tip)
            except: pass

        add_btn("🌙" if self.theme_manager.is_dark else "☀️", 
                self.callbacks['theme'], "Basculer le mode", "accent_primary")
        add_btn("👥", self.callbacks['profiles'], "Gestion des profils", "accent_secondary")
        add_btn("⚙️", self.callbacks['settings'], "Paramètres", "accent_tertiary")
        
        if self.advanced_systems:
            add_btn("🔑", self.callbacks['apis'], "Configuration API", "accent_primary")
            add_btn("📊", self.callbacks['monitor'], "Moniteur", "accent_secondary")
            
        add_btn("🚪", self.callbacks['logout'], "Déconnexion", "accent_error")
