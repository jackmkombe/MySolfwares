"""
MediaNexus PRO v3.2 - Card Components
"""
import threading
import customtkinter as ctk
from pathlib import Path
from PIL import Image
from urllib.request import urlretrieve
from theme import SIZES

class MediaCard(ctk.CTkFrame):
    def __init__(self, parent, item: dict, cache_dir: Path, theme_manager, on_click=None):
        theme = theme_manager.current_theme
        super().__init__(parent, fg_color=theme["bg_tertiary"], corner_radius=SIZES["radius_lg"], 
                         width=175, height=290, border_width=1, border_color=theme["border_default"])
        self.item = item
        self.cache_dir = cache_dir
        self.on_click = on_click
        self.theme_manager = theme_manager
        self.pack_propagate(False)
        
        self.default_border = theme["border_default"]
        self.hover_border = theme["accent_primary"]

        self.poster_label = ctk.CTkLabel(
            self, text="⏳", font=("Arial", 40), text_color=theme["text_muted"]
        )
        self.poster_label.pack(pady=10, fill="both", expand=True)

        # Titre
        title = item.get('title') or item.get('raw_name', 'Sans titre')
        self.title_label = ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(size=SIZES["text_sm"], weight="bold"),
            wraplength=155, height=35, text_color=theme["text_primary"],
            anchor="w", justify="left"
        )
        self.title_label.pack(side="top", pady=(0, 2), padx=10, fill="x")

        # Métadonnées (Saisons, Épisodes, Année)
        metadata_text = []
        year = item.get('release_year')
        if year: metadata_text.append(str(year))
        
        seasons = item.get('seasons_count')
        episodes = item.get('episodes_count')
        
        if seasons: metadata_text.append(f"{seasons} Sais.")
        if episodes: metadata_text.append(f"{episodes} Ép.")
        
        info_str = " | ".join(metadata_text) if metadata_text else ""
        
        self.info_label = ctk.CTkLabel(
            self, text=info_str, font=ctk.CTkFont(size=SIZES["text_xs"]),
            text_color=theme["text_tertiary"], anchor="w"
        )
        self.info_label.pack(side="top", pady=(0, 10), padx=10, fill="x")

        threading.Thread(target=self._load_poster_safe, daemon=True).start()
        self._bind_hover_effects(self)
        self._bind_click(self)

    def _bind_hover_effects(self, widget):
        widget.bind("<Enter>", self._on_hover_enter)
        widget.bind("<Leave>", self._on_hover_leave)
        for child in widget.winfo_children():
            self._bind_hover_effects(child)

    def _bind_click(self, widget):
        widget.bind("<Button-1>", lambda e: self.on_click(self.item) if self.on_click else None)
        for child in widget.winfo_children():
            self._bind_click(child)

    def _on_hover_enter(self, event):
        self.configure(border_color=self.hover_border, border_width=2)
        self.configure(cursor="hand2")

    def _on_hover_leave(self, event):
        self.configure(border_color=self.default_border, border_width=1)

    def _load_poster_safe(self):
        try:
            item_id = self.item.get('id')
            poster_url = self.item.get('poster_url')
            if not poster_url: return

            cache_path = self.cache_dir / f"poster_{item_id}.jpg"
            if not cache_path.exists():
                urlretrieve(poster_url, cache_path)

            with Image.open(cache_path) as img:
                img.verify()
            
            img = Image.open(cache_path)
            ctk_img = ctk.CTkImage(img, size=(150, 210))
            if self.winfo_exists():
                self.after(0, lambda: self._safe_update_ui(ctk_img))
            
        except Exception as e:
            if 'cache_path' in locals() and cache_path.exists(): 
                try: cache_path.unlink()
                except: pass

    def _safe_update_ui(self, ctk_img):
        """Met à jour le poster seulement si le widget existe encore."""
        try:
            if self.winfo_exists():
                self.poster_label.configure(image=ctk_img, text="")
        except:
            pass

class ProfileCard(ctk.CTkFrame):
    def __init__(self, parent, profile: dict, theme: dict, on_click=None, on_delete=None):
        super().__init__(parent, fg_color="transparent")
        self.profile = profile

        self.avatar_btn = ctk.CTkButton(
            self, text="👤", font=("Arial", 50), width=140, height=140,
            corner_radius=20, fg_color=theme['bg_tertiary'], hover_color=theme['accent_primary'],
            command=lambda: on_click(profile) if on_click else None
        )
        self.avatar_btn.pack()

        ctk.CTkLabel(
            self, text=profile['name'], 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme['text_primary']
        ).pack(pady=8)
