"""
MediaNexus PRO v3.2 - Dialog Components
Dialogues standardisés pour une expérience utilisateur cohérente.
"""
import os
import customtkinter as ctk
from pathlib import Path
from theme import SIZES, ThemeManager
from PIL import Image

class BaseDialog(ctk.CTkToplevel):
    """Classe de base pour tous les dialogues du système."""
    def __init__(self, parent, title="Dialogue", width=500, height=400, theme_manager=None):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.theme_manager = theme_manager or (parent.theme_manager if hasattr(parent, 'theme_manager') else None)
        
        # Centrer sur le parent
        self.after(10, self._center_on_parent)
        
        # Configuration visuelle
        if self.theme_manager:
            theme = self.theme_manager.current_theme
            self.configure(fg_color=theme["bg_primary"])
            
        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set() # Modal
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

    def _center_on_parent(self):
        self.update_idletasks()
        parent = self.master
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        
        dw = self.winfo_width()
        dh = self.winfo_height()
        
        x = px + (pw // 2) - (dw // 2)
        y = py + (ph // 2) - (dh // 2)
        
        self.geometry(f"+{x}+{y}")

class StatsDialog(BaseDialog):
    """Dialogue affichant les statistiques de la bibliothèque."""
    def __init__(self, parent, lib_name, stats, theme_manager):
        super().__init__(parent, title=f"Stats : {lib_name}", width=650, height=550, theme_manager=theme_manager)
        self._build_ui(stats)

    def _build_ui(self, stats):
        theme = self.theme_manager.current_theme
        
        ctk.CTkLabel(
            self.content, text="📊 Statistiques de Collection",
            font=ctk.CTkFont(size=SIZES["text_4xl"], weight="bold"),
            text_color=theme["accent_primary"]
        ).pack(pady=(10, 30))

        grid = ctk.CTkFrame(self.content, fg_color="transparent")
        grid.pack(fill="both", expand=True)

        # Helper pour cartes
        def add_card(icon, value, label, color, r, c):
            card = ctk.CTkFrame(grid, fg_color=color, corner_radius=15)
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(card, text=icon, font=("Arial", 32)).pack(pady=(15, 5))
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=28, weight="bold")).pack()
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12), text_color="#E2E8F0").pack(pady=(0, 15))

        grid.columnconfigure((0, 1, 2), weight=1)
        
        add_card("📚", stats['total'], "Total", "#1E293B", 0, 0)
        add_card("✅", stats['synced'], "Synchronisés", "#065F46", 0, 1)
        add_card("⏳", stats['pending'], "En attente", "#92400E", 0, 2)
        add_card("❌", stats['errors'], "Erreurs", "#7F1D1D", 1, 0)
        add_card("⭐", f"{stats['avg_score']:.1f}", "Score Moyen", "#1E40AF", 1, 1)
        add_card("📈", f"{stats['completion']:.0f}%", "Complétion", "#065F46", 1, 2)

        ctk.CTkButton(
            self.content, text="Fermer", command=self.destroy,
            height=40, fg_color=theme["bg_tertiary"], hover_color=theme["bg_quaternary"]
        ).pack(pady=20, fill="x")

class SettingsDialog(BaseDialog):
    """Dialogue de configuration de bibliothèque."""
    def __init__(self, parent, lib, on_save, theme_manager):
        super().__init__(parent, title=f"Paramètres : {lib['name']}", width=500, height=600, theme_manager=theme_manager)
        self.lib = lib
        self.on_save = on_save
        self._build_ui()

    def _build_ui(self):
        theme = self.theme_manager.current_theme
        
        ctk.CTkLabel(
            self.content, text="⚙️ Configuration de Collection",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 20))

        # Nom
        ctk.CTkLabel(self.content, text="Nom de la bibliothèque", anchor="w").pack(fill="x", pady=(10, 5))
        self.name_entry = ctk.CTkEntry(self.content, height=40)
        self.name_entry.insert(0, self.lib.get('name', ''))
        self.name_entry.pack(fill="x")

        # Type de média
        ctk.CTkLabel(self.content, text="Type de contenu", anchor="w").pack(fill="x", pady=(15, 5))
        self.type_var = ctk.StringVar(value=self.lib.get('type', 'Films / Séries'))
        type_menu = ctk.CTkOptionMenu(
            self.content, values=["Films / Séries", "Animés", "Jeux PC"],
            variable=self.type_var, height=40
        )
        type_menu.pack(fill="x")

        # Langue
        ctk.CTkLabel(self.content, text="Langue des métadonnées", anchor="w").pack(fill="x", pady=(15, 5))
        self.lang_var = ctk.StringVar(value=self.lib.get('preferred_lang', 'fr-FR'))
        lang_menu = ctk.CTkOptionMenu(
            self.content, values=["fr-FR", "en-US", "es-ES", "de-DE", "ja-JP"],
            variable=self.lang_var, height=40
        )
        lang_menu.pack(fill="x")

        # Source
        ctk.CTkLabel(self.content, text="Source prioritaire", anchor="w").pack(fill="x", pady=(15, 5))
        sources = ["Automatique", "Multi-Sources", "TMDB", "OMDB", "TVmaze", "Jikan", "RAWG", "IGDB"]
        self.source_var = ctk.StringVar(value=self.lib.get('source', 'Automatique'))
        source_menu = ctk.CTkOptionMenu(
            self.content, values=sources,
            variable=self.source_var, height=40
        )
        source_menu.pack(fill="x")

        # Option traduction
        self.translate_var = ctk.BooleanVar(value=True)
        self.translate_check = ctk.CTkCheckBox(
            self.content, text="Traduire automatiquement le synopsis si nécessaire",
            variable=self.translate_var, font=ctk.CTkFont(size=12)
        )
        self.translate_check.pack(fill="x", pady=(20, 0))

        def save():
            new_data = {
                "name": self.name_entry.get(),
                "type": self.type_var.get(),
                "lang": self.lang_var.get(),
                "source": self.source_var.get(),
                "translate": self.translate_var.get()
            }
            self.on_save(new_data, self)

        ctk.CTkButton(
            self.content, text="💾 SAUVEGARDER LES MODIFICATIONS", command=save,
            height=50, fg_color=theme["accent_success"], hover_color=theme["accent_success_hover"],
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=30, fill="x")

class MediaDetailsDialog(BaseDialog):
    """Dialogue affichant les détails d'un média."""
    def __init__(self, parent, item, cache_dir, theme_manager):
        super().__init__(parent, title=item.get('title', 'Détails'), width=950, height=650, theme_manager=theme_manager)
        self._build_ui(item, cache_dir)

    def _build_ui(self, item, cache_dir):
        theme = self.theme_manager.current_theme
        self.configure(fg_color="#020617") # Style sombre premium pour les détails
        
        main = ctk.CTkFrame(self.content, fg_color="transparent")
        main.pack(fill="both", expand=True)

        # Poster
        poster_frame = ctk.CTkFrame(main, width=300, height=450, fg_color="#1E293B", corner_radius=15)
        poster_frame.pack(side="left")
        poster_frame.pack_propagate(False)

        poster_path = cache_dir / f"poster_{item['id']}.jpg"
        if poster_path.exists():
            img = ctk.CTkImage(Image.open(poster_path), size=(300, 450))
            ctk.CTkLabel(poster_frame, image=img, text="").pack()
        else:
            ctk.CTkLabel(poster_frame, text="🎬", font=("Arial", 80), text_color="#475569").pack(expand=True)

        # Infos
        info = ctk.CTkFrame(main, fg_color="transparent")
        info.pack(side="right", fill="both", expand=True, padx=(40, 0))

        ctk.CTkLabel(
            info, text=item.get('title', 'Sans titre'),
            font=ctk.CTkFont(size=32, weight="bold"), wraplength=500, justify="left",
            text_color="#FFFFFF"
        ).pack(anchor="w")

        # Métadonnées
        meta_parts = []
        if item.get('release_date'): meta_parts.append(f"📅 {item['release_date']}")
        if item.get('score'): meta_parts.append(f"⭐ {item['score']}")
        
        seasons = item.get('seasons_count')
        episodes = item.get('episodes_count')
        if seasons: meta_parts.append(f"📂 {seasons} Saisons")
        if episodes: meta_parts.append(f"🎬 {episodes} Épisodes")
        
        if item.get('airing_status'): meta_parts.append(f"📺 {item['airing_status']}")

        ctk.CTkLabel(
            info, text="  |  ".join(meta_parts),
            font=ctk.CTkFont(size=14), text_color=theme["accent_primary"]
        ).pack(anchor="w", pady=10)

        # Synopsis
        ctk.CTkLabel(
            info, text="SYNOPSIS",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B"
        ).pack(anchor="w", pady=(30, 5))

        txt = ctk.CTkTextbox(info, height=200, font=("Inter", 13), fg_color="#0F172A", border_width=1, border_color="#334155")
        txt.pack(fill="x")
        txt.insert("1.0", item.get('summary') or "Aucun synopsis disponible.")
        txt.configure(state="disabled")

        # Boutons d'action
        btn_row = ctk.CTkFrame(info, fg_color="transparent")
        btn_row.pack(fill="x", pady=25)

        local_path = item.get('local_path')
        if local_path and Path(local_path).exists():
            ctk.CTkButton(
                btn_row, text="🚀 LANCER", height=50, fg_color="#2563EB",
                font=ctk.CTkFont(weight="bold"),
                command=lambda: os.startfile(local_path)
            ).pack(side="left", fill="x", expand=True, padx=(0, 10))

            ctk.CTkButton(
                btn_row, text="📂", width=50, height=50, fg_color="#475569",
                command=lambda: os.startfile(os.path.dirname(local_path))
            ).pack(side="right")

        # Bouton fermer
        ctk.CTkButton(
            info, text="Fermer", command=self.destroy,
            height=40, fg_color="#475569"
        ).pack(side="bottom", anchor="e", pady=20)

class LibraryDialog(BaseDialog):
    """Dialogue d'ajout/édition de bibliothèque."""
    def __init__(self, parent, on_save, theme_manager):
        super().__init__(parent, title="Nouvelle Bibliothèque", width=450, height=500, theme_manager=theme_manager)
        self.on_save = on_save
        self._build_ui()

    def _build_ui(self):
        from tkinter import filedialog
        theme = self.theme_manager.current_theme
        
        ctk.CTkLabel(
            self.content, text="Configuration", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=30)

        self.name_entry = ctk.CTkEntry(self.content, placeholder_text="Nom de la collection", height=40)
        self.name_entry.pack(fill="x", pady=10)

        self.type_menu = ctk.CTkOptionMenu(self.content, values=["Films / Séries", "Animés", "Jeux PC"], height=40)
        self.type_menu.pack(fill="x", pady=10)

        self.path_var = ctk.StringVar(value="Aucun dossier")
        
        def pick_path():
            p = filedialog.askdirectory()
            if p: self.path_var.set(p)

        ctk.CTkButton(
            self.content, text="📂 Dossier Source", command=pick_path,
            height=40, fg_color=theme["bg_tertiary"]
        ).pack(pady=20, fill="x")

        ctk.CTkLabel(self.content, textvariable=self.path_var, font=ctk.CTkFont(size=11), text_color=theme["accent_primary"]).pack()

        def save():
            if self.name_entry.get() and self.path_var.get() != "Aucun dossier":
                self.on_save(self.name_entry.get(), self.type_menu.get(), self.path_var.get(), self)

        ctk.CTkButton(
            self.content, text="CRÉER", command=save, height=50,
            fg_color=theme["accent_success"], hover_color=theme["accent_success_hover"],
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=40, fill="x")

class LoginDialog(BaseDialog):
    """Dialogue de connexion par mot de passe."""
    def __init__(self, parent, profile, on_success, theme_manager):
        super().__init__(parent, title=f"Connexion - {profile['name']}", width=400, height=350, theme_manager=theme_manager)
        self.profile = profile
        self.on_success = on_success
        self._build_ui()

    def _build_ui(self):
        theme = self.theme_manager.current_theme
        
        ctk.CTkLabel(
            self.content, text=f"🔐 Connexion à {self.profile['name']}",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=theme["accent_primary"]
        ).pack(pady=20)
        
        ctk.CTkLabel(
            self.content, text="Mot de passe", anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=theme["text_secondary"]
        ).pack(fill="x", pady=(10, 5))
        
        self.password_entry = ctk.CTkEntry(
            self.content, height=45, placeholder_text="Entrez votre mot de passe", show="•",
            corner_radius=8, border_width=1, border_color=theme["border_default"],
            fg_color=theme["bg_tertiary"], text_color=theme["text_primary"]
        )
        self.password_entry.pack(fill="x")
        self.password_entry.focus()
        
        def attempt_login():
            if self.on_success(self.profile, self.password_entry.get()):
                self.destroy()
            else:
                self.password_entry.delete(0, 'end')

        btn_row = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_row.pack(pady=30, fill="x")

        ctk.CTkButton(
            btn_row, text="Annuler", width=120, height=45,
            fg_color="transparent", border_width=2, border_color=theme["border_default"],
            command=self.destroy
        ).pack(side="left", padx=5, expand=True)
        
        ctk.CTkButton(
            btn_row, text="Connexion", width=120, height=45,
            fg_color=theme["accent_primary"], command=attempt_login
        ).pack(side="right", padx=5, expand=True)
        
        self.bind('<Return>', lambda e: attempt_login())

class ProfileCreationDialog(BaseDialog):
    """Dialogue de création de profil."""
    def __init__(self, parent, on_save, theme_manager):
        super().__init__(parent, title="Nouveau Profil", width=400, height=500, theme_manager=theme_manager)
        self.on_save = on_save
        self._build_ui()

    def _build_ui(self):
        theme = self.theme_manager.current_theme
        
        ctk.CTkLabel(
            self.content, text="💎 Nouveau profil",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=theme["accent_primary"]
        ).pack(pady=(0, 20))
        
        self.name_entry = ctk.CTkEntry(self.content, height=45, placeholder_text="Nom du profil")
        self.name_entry.pack(fill="x", pady=10)

        self.pass_entry = ctk.CTkEntry(self.content, height=45, placeholder_text="Mot de passe", show="•")
        self.pass_entry.pack(fill="x", pady=10)

        self.confirm_entry = ctk.CTkEntry(self.content, height=45, placeholder_text="Confirmez le mot de passe", show="•")
        self.confirm_entry.pack(fill="x", pady=10)

        def save():
            name = self.name_entry.get().strip()
            pwd = self.pass_entry.get()
            if pwd != self.confirm_entry.get():
                from tkinter import messagebox
                messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
                return
            if name:
                self.on_save(name, pwd, self)

        ctk.CTkButton(
            self.content, text="CRÉER", command=save, height=50,
            fg_color=theme["accent_success"], font=ctk.CTkFont(weight="bold")
        ).pack(pady=30, fill="x")
