import os
import re
import json
import sqlite3
import threading
import requests
from pathlib import Path
from PIL import Image, ImageTk
from urllib.request import urlretrieve
from typing import List, Dict, Optional
import customtkinter as ctk
from tkinter import filedialog, messagebox

# --- CONFIGURATION GLOBALE ---
APP_NAME = "OmniNexus Manager"
VERSION = "1.0.0"
CONFIG_FILE = "config.json"
DATABASE_FILE = "library_data.db"
CACHE_DIR = Path("cache_posters")
DEFAULT_THEME = "dark"

# Création du cache d'images
CACHE_DIR.mkdir(exist_ok=True)

# --- LOGIQUE DE NETTOYAGE DE NOMS (INGÉNIERIE SENIOR) ---
class NameCleaner:
    @staticmethod
    def clean(name: str) -> str:
        """Nettoie les noms de fichiers/dossiers pour optimiser la recherche API."""
        name = Path(name).stem
        patterns = [
            r'\[.*?\]', r'\(.*?\)', r'\.(?:1080p|720p|480p|2160p|4K)',
            r'\.(?:BluRay|WEB-DL|WEBRip|HDTV|DVDRip)', r'\.(?:x264|x265|H264|H265|HEVC)',
            r'\.(?:AAC|AC3|DTS|MP3)', r'_(?:VOSTFR|VOSTA|VF|VO|MULTI)',
            r'\.S\d{2}E\d{2}', r'\.Episode\.\d+', r'\.E\d{2,3}', r'\d{4}',
            r'\.(?:PROPER|REPACK|INTERNAL)', r'- ?\w+$'
        ]
        for pattern in patterns:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
        name = re.sub(r'[._-]+', ' ', name)
        return ' '.join(name.split()).strip()

# --- GESTIONNAIRE DE BASE DE DONNÉES ---
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS libraries 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, path TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS media_items 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, lib_id INTEGER, 
                           title TEXT, official_title TEXT, summary TEXT, 
                           release_date TEXT, score TEXT, genres TEXT, 
                           poster_path TEXT, local_path TEXT)''')
        self.conn.commit()

# --- MOTEUR D'INTERROGATION API (MULTI-SOURCES) ---
class APIManager:
    def __init__(self, config):
        self.config = config

    def fetch_metadata(self, name: str, media_type: str) -> Optional[Dict]:
        try:
            if media_type == "Films / Séries":
                return self._fetch_tmdb(name)
            elif media_type == "Animés":
                return self._fetch_jikan(name)
            elif media_type == "Jeux PC":
                return self._fetch_rawg(name)
        except Exception as e:
            print(f"Erreur API ({media_type}): {e}")
        return None

    def _fetch_tmdb(self, name: str):
        api_key = self.config.get("tmdb_key")
        if not api_key: return None
        url = f"https://api.themoviedb.org/3/search/multi?api_key={api_key}&query={name}&language=fr-FR"
        try:
            res = requests.get(url, timeout=10).json()
            if res.get('results'):
                item = res['results'][0]
                return {
                    "title": item.get('title') or item.get('name'),
                    "summary": item.get('overview', "Pas de résumé."),
                    "date": item.get('release_date') or item.get('first_air_date'),
                    "score": str(item.get('vote_average')),
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None
                }
        except: return None
        return None

    def _fetch_jikan(self, name: str):
        url = f"https://api.jikan.moe/v4/anime?q={name}&limit=1"
        try:
            res = requests.get(url, timeout=10).json()
            if res.get('data'):
                item = res['data'][0]
                return {
                    "title": item['title_english'] or item['title'],
                    "summary": item.get('synopsis', "N/A"),
                    "date": str(item.get('year', "N/A")),
                    "score": str(item.get('score', "N/A")),
                    "poster": item['images']['jpg']['large_image_url']
                }
        except: return None
        return None

    def _fetch_rawg(self, name: str):
        api_key = self.config.get("rawg_key")
        if not api_key: return None
        url = f"https://api.rawg.io/api/games?key={api_key}&search={name}&page_size=1"
        try:
            res = requests.get(url, timeout=10).json()
            if res.get('results'):
                item = res['results'][0]
                return {
                    "title": item.get('name'),
                    "summary": "Consultez RAWG pour plus de détails.",
                    "date": item.get('released'),
                    "score": str(item.get('rating', "N/A")),
                    "poster": item.get('background_image')
                }
        except: return None
        return None

# --- UI : COMPOSANTS PERSONNALISÉS ---
class MediaCard(ctk.CTkFrame):
    def __init__(self, parent, item, command=None):
        super().__init__(parent, fg_color="#1E293B", corner_radius=12, width=190, height=310, border_width=1, border_color="#334155")
        self.item = item
        
        # Gestion de l'image
        try:
            img_path = CACHE_DIR / f"{item[0]}.jpg"
            if not img_path.exists() and item[8]:
                urlretrieve(item[8], img_path)
            
            pil_img = Image.open(img_path if img_path.exists() else "placeholder.png")
            ctk_img = ctk.CTkImage(pil_img, size=(170, 240))
            
            self.img_label = ctk.CTkLabel(self, image=ctk_img, text="")
            self.img_label.pack(pady=10, padx=10)
        except:
            self.img_label = ctk.CTkLabel(self, text="🎬\nAucune Image", height=240, font=ctk.CTkFont(size=14))
            self.img_label.pack(pady=10)

        self.title_label = ctk.CTkLabel(self, text=item[3] or item[2], font=ctk.CTkFont(size=12, weight="bold"), wraplength=170, height=40)
        self.title_label.pack(pady=(0, 5), padx=5)

        if command:
            self.bind("<Button-1>", lambda e: command(item))
            self.img_label.bind("<Button-1>", lambda e: command(item))
            self.title_label.bind("<Button-1>", lambda e: command(item))

# --- APPLICATION PRINCIPALE ---
class OmniNexusApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Init Data
        self.db = DatabaseManager()
        self.load_config()
        self.api = APIManager(self.config)
        self.current_lib_id = None

        # Window Config
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("1200x800")
        ctk.set_appearance_mode(DEFAULT_THEME)
        
        try:
            if os.path.exists("app_icon.ico"):
                self.iconbitmap("app_icon.ico")
        except: pass

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_content()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"tmdb_key": "", "rawg_key": ""}
            self.save_config()

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0F172A")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="🌐 OmniNexus", font=ctk.CTkFont(size=24, weight="bold"), text_color="#3B82F6").pack(pady=30)
        
        ctk.CTkButton(self.sidebar, text="+ Nouvelle Bibliothèque", command=self._show_add_library, 
                       fg_color="#2563EB", hover_color="#1D4ED8", font=ctk.CTkFont(weight="bold")).pack(pady=10, padx=20)
        
        ctk.CTkLabel(self.sidebar, text="MES COLLECTIONS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B").pack(pady=(30, 10), padx=20, anchor="w")
        
        self.lib_nav_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.lib_nav_frame.pack(fill="both", expand=True)
        self._refresh_sidebar_libs()

        ctk.CTkButton(self.sidebar, text="⚙️ Paramètres", fg_color="transparent", border_width=1, border_color="#334155", 
                       command=self._show_settings).pack(pady=20, padx=20)

    def _refresh_sidebar_libs(self):
        for widget in self.lib_nav_frame.winfo_children():
            widget.destroy()
        
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id, name, type FROM libraries")
        for lib in cursor.fetchall():
            icons = {"Films / Séries": "🎬", "Animés": "🎌", "Jeux PC": "🎮"}
            icon = icons.get(lib[2], "📁")
            btn = ctk.CTkButton(self.lib_nav_frame, text=f"{icon} {lib[1]}", 
                                fg_color="transparent", anchor="w",
                                text_color="#F8FAFC",
                                command=lambda l=lib: self._load_library(l[0]))
            btn.pack(fill="x", padx=10, pady=2)

    def _build_main_content(self):
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=30, pady=20)
        
        self.header_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.header_frame.pack(fill="x")
        
        self.content_title = ctk.CTkLabel(self.header_frame, text="Bienvenue sur OmniNexus PRO", font=ctk.CTkFont(size=28, weight="bold"))
        self.content_title.pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_view, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, pady=20)
        
        self._build_welcome_screen()

    def _build_welcome_screen(self):
        msg = "Selectionnez une bibliothèque ou créez-en une nouvelle pour commencer."
        ctk.CTkLabel(self.scroll_frame, text=msg, font=ctk.CTkFont(size=16), text_color="#94A3B8").pack(expand=True, pady=150)

    def _show_add_library(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nouvelle Bibliothèque")
        dialog.geometry("450x500")
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Configuration Globale", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=25)
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Nom de la collection (ex: Mes Films HD)", width=350, height=40)
        name_entry.pack(pady=10)
        
        type_var = tk.StringVar(value="Films / Séries")
        type_menu = ctk.CTkOptionMenu(dialog, values=["Films / Séries", "Animés", "Jeux PC"], variable=type_var, width=350, height=40)
        type_menu.pack(pady=10)
        
        path_var = tk.StringVar()
        def _pick_path(): 
            p = filedialog.askdirectory()
            if p: path_var.set(p)
        
        ctk.CTkButton(dialog, text="📂 Sélectionner le dossier média", command=_pick_path, width=350, height=40, fg_color="#475569").pack(pady=15)
        ctk.CTkLabel(dialog, textvariable=path_var, font=ctk.CTkFont(size=11), text_color="#3B82F6", wraplength=400).pack()

        def _save():
            if name_entry.get() and path_var.get():
                cursor = self.db.conn.cursor()
                cursor.execute("INSERT INTO libraries (name, type, path) VALUES (?, ?, ?)", 
                               (name_entry.get(), type_var.get(), path_var.get()))
                self.db.conn.commit()
                self._refresh_sidebar_libs()
                dialog.destroy()
                messagebox.showinfo("Succès", "Bibliothèque configurée avec succès !")
            else:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")

        ctk.CTkButton(dialog, text="💾 CRÉER LA BIBLIOTHÈQUE", command=_save, height=50, fg_color="#22C55E", font=ctk.CTkFont(weight="bold")).pack(pady=40)

    def _load_library(self, lib_id):
        self.current_lib_id = lib_id
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name, type FROM libraries WHERE id=?", (lib_id,))
        lib = cursor.fetchone()
        self.content_title.configure(text=f"{lib[0]}")
        
        # Barre d'outils
        tool_bar = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        tool_bar.pack(fill="x", pady=(0, 20))
        
        ctk.CTkButton(tool_bar, text="🔄 Synchroniser (Scan)", command=self._start_scan, 
                       fg_color="#3B82F6", width=180, height=35, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Grille de cartes
        self.grid_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        self._refresh_media_grid()

    def _refresh_media_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM media_items WHERE lib_id=?", (self.current_lib_id,))
        items = cursor.fetchall()
        
        if not items:
            ctk.CTkLabel(self.grid_frame, text="Aucun élément. Cliquez sur Synchroniser pour commencer.", 
                         font=ctk.CTkFont(size=14), text_color="#64748B").pack(pady=100)
            return

        row, col = 0, 0
        max_cols = 5 # Adaptatif selon la largeur potentiellement
        for item in items:
            card = MediaCard(self.grid_frame, item, command=self._show_details)
            card.grid(row=row, column=col, padx=12, pady=12)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def _start_scan(self):
        threading.Thread(target=self._scan_process, daemon=True).start()

    def _scan_process(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT path, type FROM libraries WHERE id=?", (self.current_lib_id,))
        lib_path, lib_type = cursor.fetchone()
        
        source = Path(lib_path)
        if not source.exists():
            self.after(0, lambda: messagebox.showerror("Erreur", f"Dossier introuvable : {lib_path}"))
            return

        # On scanne fichiers et dossiers
        items = [f for f in source.iterdir() if f.is_dir() or (f.is_file() and f.suffix.lower() in ['.mp4', '.mkv', '.avi', '.exe'])]
        
        for item in items:
            cursor.execute("SELECT id FROM media_items WHERE lib_id=? AND title=?", (self.current_lib_id, item.name))
            if cursor.fetchone(): continue
            
            clean_name = NameCleaner.clean(item.name)
            data = self.api.fetch_metadata(clean_name, lib_type)
            
            if data:
                cursor.execute('''INSERT INTO media_items 
                                  (lib_id, title, official_title, summary, release_date, score, poster_path, local_path) 
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                               (self.current_lib_id, item.name, data['title'], data['summary'], 
                                data['date'], data['score'], data['poster'], str(item)))
                self.db.conn.commit()
                self.after(0, self._refresh_media_grid)

    def _show_details(self, item):
        dialog = ctk.CTkToplevel(self)
        dialog.title(item[3] or item[2])
        dialog.geometry("850x550")
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color="#0F172A")

        main_f = ctk.CTkFrame(dialog, fg_color="transparent")
        main_f.pack(fill="both", expand=True, padx=30, pady=30)

        # Poster
        try:
            img_path = CACHE_DIR / f"{item[0]}.jpg"
            if img_path.exists():
                img = Image.open(img_path)
                ctk_img = ctk.CTkImage(img, size=(280, 420))
                ctk.CTkLabel(main_f, image=ctk_img, text="").pack(side="left", padx=(0, 30))
        except: pass

        # Infos
        info_f = ctk.CTkFrame(main_f, fg_color="transparent")
        info_f.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(info_f, text=item[3] or item[2], font=ctk.CTkFont(size=28, weight="bold"), wraplength=450, anchor="w", justify="left").pack(anchor="w")
        
        meta_f = ctk.CTkFrame(info_f, fg_color="transparent")
        meta_f.pack(fill="x", pady=10)
        ctk.CTkLabel(meta_f, text=f"📅 {item[5]}", font=ctk.CTkFont(size=14), text_color="#94A3B8").pack(side="left")
        ctk.CTkLabel(meta_f, text=f" ⭐ {item[6]}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#EAB308").pack(side="left", padx=20)
        
        ctk.CTkLabel(info_f, text="SYNOPSIS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B").pack(anchor="w", pady=(20, 5))
        txt = ctk.CTkTextbox(info_f, height=220, font=ctk.CTkFont(size=13), fg_color="#1E293B", border_width=1, border_color="#334155")
        txt.pack(fill="x")
        txt.insert("1.0", item[4])
        txt.configure(state="disabled")

        btn_f = ctk.CTkFrame(info_f, fg_color="transparent")
        btn_f.pack(fill="x", pady=20)
        
        ctk.CTkButton(btn_f, text="🚀 LANCER / OUVRIR", command=lambda: os.startfile(item[9]), 
                       height=45, fg_color="#2563EB", font=ctk.CTkFont(weight="bold")).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(btn_f, text="🗑️", width=45, height=45, fg_color="#EF4444", 
                       command=lambda: self._delete_item(item[0], dialog)).pack(side="right")

    def _delete_item(self, item_id, dialog):
        if messagebox.askyesno("Supprimer", "Retirer cet élément de la bibliothèque ?"):
            cursor = self.db.conn.cursor()
            cursor.execute("DELETE FROM media_items WHERE id=?", (item_id,))
            self.db.conn.commit()
            dialog.destroy()
            self._refresh_media_grid()

    def _show_settings(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Paramètres OmniNexus")
        dialog.geometry("500x450")
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Configuration des Sources", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=30)
        
        ctk.CTkLabel(dialog, text="TMDB API KEY (Films/Séries):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=50)
        tmdb_entry = ctk.CTkEntry(dialog, placeholder_text="Copiez votre clé ici...", width=400, height=35)
        tmdb_entry.insert(0, self.config.get("tmdb_key", ""))
        tmdb_entry.pack(pady=(5, 15))
        
        ctk.CTkLabel(dialog, text="RAWG API KEY (Jeux PC):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=50)
        rawg_entry = ctk.CTkEntry(dialog, placeholder_text="Copiez votre clé ici...", width=400, height=35)
        rawg_entry.insert(0, self.config.get("rawg_key", ""))
        rawg_entry.pack(pady=(5, 15))

        def _save_keys():
            self.config["tmdb_key"] = tmdb_entry.get().strip()
            self.config["rawg_key"] = rawg_entry.get().strip()
            self.save_config()
            self.api.config = self.config
            dialog.destroy()
            messagebox.showinfo("OmniNexus", "Clés API enregistrées !")

        ctk.CTkButton(dialog, text="💾 SAUVEGARDER LES RÉGLAGES", command=_save_keys, height=45, fg_color="#22C55E").pack(pady=40)

if __name__ == "__main__":
    app = OmniNexusApp()
    app.mainloop()
