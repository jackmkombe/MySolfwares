import customtkinter as ctk
from theme import SIZES

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, theme_manager, on_add_library, on_load_library, get_libraries, profile_id):
        theme = theme_manager.current_theme
        super().__init__(parent, width=SIZES["sidebar_width"], corner_radius=0, fg_color=theme["bg_secondary"])
        self.pack_propagate(False)
        
        self.theme_manager = theme_manager
        self.on_add_library = on_add_library
        self.on_load_library = on_load_library
        self.get_libraries = get_libraries
        self.profile_id = profile_id

        self.theme_manager.register_callback(self._on_theme_update)
        self._build_ui()

    def _on_theme_update(self, theme, mode):
        self.configure(fg_color=theme["bg_secondary"])
        self._build_ui()

    def _build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        theme = self.theme_manager.current_theme

        # Logo
        ctk.CTkLabel(
            self, text="🌐 MediaNexus",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=theme["accent_primary"]
        ).pack(pady=30)

        # Bouton nouvelle bibliothèque
        ctk.CTkButton(
            self, text="+ Bibliothèque", command=self.on_add_library,
            fg_color=theme["accent_primary"], font=ctk.CTkFont(weight="bold"),
            height=SIZES["button_md"]
        ).pack(pady=10, padx=20, fill="x")

        # Liste des bibliothèques
        ctk.CTkLabel(
            self, text="MES COLLECTIONS",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=theme["text_tertiary"]
        ).pack(pady=(20, 5), padx=20, anchor="w")

        self.lib_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.lib_scroll.pack(fill="both", expand=True, padx=5)

        self.refresh()

    def refresh(self):
        """Rafraîchit la liste des bibliothèques."""
        for widget in self.lib_scroll.winfo_children():
            widget.destroy()

        theme = self.theme_manager.current_theme
        libraries = self.get_libraries(self.profile_id)
        icons = {"Films / Séries": "🎬", "Animés": "🎌", "Jeux PC": "🎮"}

        for lib in libraries:
            icon = icons.get(lib['type'], "📁")
            btn = ctk.CTkButton(
                self.lib_scroll, text=f"{icon} {lib['name']}",
                anchor="w", fg_color="transparent",
                text_color=theme["text_secondary"],
                hover_color=theme["bg_elevated"],
                command=lambda l=lib: self.on_load_library(l)
            )
            btn.pack(fill="x", pady=2)
