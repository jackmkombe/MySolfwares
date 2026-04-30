import os
import re
import json
import sqlite3
import threading
import time
import requests
from pathlib import Path
from PIL import Image, ImageTk
from typing import List, Dict, Optional, Tuple
from urllib.request import urlretrieve
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
import tkinter as tk

# --- CONFIGURATION ET CONSTANTES ---
APP_NAME = "MediaNexus Ultra PRO"
VERSION = "2.0.0"
WORKING_DIR = Path("MediaNexus_Data")
DB_PATH = WORKING_DIR / "core.db"
CACHE_DIR = WORKING_DIR / "cache"
CONFIG_FILE = WORKING_DIR / "global_settings.json"

WORKING_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# --- LOGIQUE DE DONNÉES (SQLITE MULTI-PROFIL) ---
class DataEngine:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._initialize_schema()

    def _initialize_schema(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS profiles 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, avatar TEXT, theme TEXT, password TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS libraries 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER, name TEXT, type TEXT, paths TEXT, lang TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS media_items 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, lib_id INTEGER, raw_name TEXT, 
             title TEXT, summary TEXT, poster_url TEXT, release_date TEXT, score TEXT, 
             genres TEXT, seasons TEXT, episodes TEXT, duration TEXT, status TEXT, 
             local_path TEXT, sync_status TEXT)''')
        self.conn.commit()

# --- MOTEUR DE FETCHING (TMDB, JIKAN, RAWG) ---
class FetchEngine:
    def __init__(self, api_keys: Dict):
        self.keys = api_keys
        self.session = requests.Session()

    def fetch(self, query: str, mtype: str, lang: str = "fr-FR") -> Optional[Dict]:
        try:
            if mtype == "Films / Séries": return self._fetch_tmdb(query, lang)
            if mtype == "Animés": return self._fetch_jikan(query)
            if mtype == "Jeux PC": return self._fetch_rawg(query)
        except Exception as e: print(f"Fetch Error: {e}")
        return None

    def _fetch_tmdb(self, q, lang):
        key = self.keys.get("tmdb")
        if not key: return None
        url = f"https://api.themoviedb.org/3/search/multi?api_key={key}&query={q}&language={lang}"
        res = self.session.get(url, timeout=10).json()
        if res.get('results'):
            item = res['results'][0]
            is_tv = item.get('media_type') == 'tv'
            details = {"title": item.get('title') or item.get('name'), "summary": item.get('overview'),
                       "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                       "date": item.get('release_date') or item.get('first_air_date'), "score": str(item.get('vote_average')),
                       "seasons": "N/A", "episodes": "N/A", "status": "Terminé"}
            
            if is_tv:
                tv_url = f"https://api.themoviedb.org/3/tv/{item['id']}?api_key={key}&language={lang}"
                tv_res = self.session.get(tv_url).json()
                details.update({"seasons": str(tv_res.get('number_of_seasons', 1)), "episodes": str(tv_res.get('number_of_episodes', 1)),
                                "status": "En cours" if tv_res.get('status') == "Returning Series" else "Terminé"})
            return details
        return None

    def _fetch_jikan(self, q):
        url = f"https://api.jikan.moe/v4/anime?q={q}&limit=1"
        res = self.session.get(url, timeout=10).json()
        if res.get('data'):
            item = res['data'][0]
            return {"title": item['title_english'] or item['title'], "summary": item.get('synopsis'),
                    "poster": item['images']['jpg']['large_image_url'], "date": str(item.get('year', "N/A")),
                    "score": str(item.get('score', "N/A")), "seasons": "1", "episodes": str(item.get('episodes', "N/A")),
                    "status": "En cours" if item.get('airing') else "Terminé"}
        return None

    def _fetch_rawg(self, q):
        key = self.keys.get("rawg")
        if not key: return None
        url = f"https://api.rawg.io/api/games?key={key}&search={q}&page_size=1"
        res = self.session.get(url, timeout=10).json()
        if res.get('results'):
            item = res['results'][0]
            return {"title": item['name'], "summary": "Détails via RAWG", "poster": item.get('background_image'),
                    "date": item.get('released'), "score": str(item.get('rating')), "seasons": "N/A", 
                    "episodes": "N/A", "status": "Disponible"}
        return None

# --- UI : COMPOSANTS ET ÉCRANS ---
class MediaNexusUltra(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = DataEngine()
        self.load_settings()
        self.api = FetchEngine(self.settings.get("api_keys", {}))
        
        self.title(f"{APP_NAME}")
        self.geometry("1240x800")
        ctk.set_appearance_mode("dark")
        
        try:
            if os.path.exists("app_icon.ico"):
                self.iconbitmap("app_icon.ico")
        except: pass

        self._show_profiles()

    def load_settings(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f: self.settings = json.load(f)
        else:
            self.settings = {"api_keys": {"tmdb": "", "rawg": ""}}
            self.save_settings()

    def save_settings(self):
        with open(CONFIG_FILE, 'w') as f: json.dump(self.settings, f, indent=4)

    def _show_profiles(self):
        for w in self.winfo_children(): w.destroy()
        
        main_f = ctk.CTkFrame(self, fg_color="transparent")
        main_f.pack(fill="both", expand=True)

        ctk.CTkLabel(main_f, text="💎 BIENVENUE SUR MEDIANEXUS PRO", font=ctk.CTkFont(size=30, weight="bold"), text_color="#3B82F6").pack(pady=(80, 20))
        ctk.CTkLabel(main_f, text="Sélectionnez un profil pour accéder à vos bibliothèques", font=ctk.CTkFont(size=14), text_color="gray").pack(pady=(0, 40))

        prof_container = ctk.CTkFrame(main_f, fg_color="transparent")
        prof_container.pack(pady=20)

        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM profiles")
        profiles = cursor.fetchall()

        for p in profiles:
            p_f = ctk.CTkFrame(prof_container, fg_color="transparent")
            p_f.pack(side="left", padx=20)
            
            btn = ctk.CTkButton(p_f, text="👤", font=("Arial", 60), width=160, height=160, 
                                corner_radius=20, fg_color="#1E293B", hover_color="#3B82F6",
                                command=lambda prof=p: self._login(prof))
            btn.pack()
            ctk.CTkLabel(p_f, text=p[1], font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        add_f = ctk.CTkFrame(prof_container, fg_color="transparent")
        add_f.pack(side="left", padx=20)
        ctk.CTkButton(add_f, text="➕", font=("Arial", 60), width=160, height=160, 
                       corner_radius=20, border_width=2, border_color="#334155", fg_color="transparent",
                       command=self._ui_create_profile).pack()
        ctk.CTkLabel(add_f, text="Nouveau", font=ctk.CTkFont(size=16)).pack(pady=10)

    def _ui_create_profile(self):
        name = simpledialog.askstring("Nouveau Profil", "Entrez le nom du profil :")
        if name:
            cursor = self.db.conn.cursor()
            cursor.execute("INSERT INTO profiles (name, theme) VALUES (?, ?)", (name, "dark"))
            self.db.conn.commit()
            self._show_profiles()

    def _login(self, profile):
        self.current_profile = profile
        self._show_dashboard()

    def _show_dashboard(self):
        for w in self.winfo_children(): w.destroy()
        
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#0F172A")
        self.sidebar.pack(side="left", fill="y")
        
        self.content_area = ctk.CTkFrame(self, fg_color="#020617", corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)

        # Sidebar Header
        ctk.CTkLabel(self.sidebar, text="🌐 MediaNexus", font=ctk.CTkFont(size=22, weight="bold"), text_color="#3B82F6").pack(pady=30)
        ctk.CTkLabel(self.sidebar, text=f"Connecté : {self.current_profile[1]}", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 20))

        ctk.CTkButton(self.sidebar, text="+ Bibliothèque", command=self._ui_add_library, fg_color="#2563EB", font=ctk.CTkFont(weight="bold")).pack(pady=10, padx=20, fill="x")
        
        self.lib_nav = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.lib_nav.pack(fill="both", expand=True, padx=5, pady=10)
        self._refresh_lib_nav()

        ctk.CTkButton(self.sidebar, text="⚙️ Paramètres", fg_color="transparent", border_width=1, command=self._ui_settings).pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="🚪 Déconnexion", fg_color="transparent", text_color="#EF4444", command=self._show_profiles).pack(pady=20, padx=20, fill="x")

        self.welcome_msg = ctk.CTkLabel(self.content_area, text="Sélectionnez une bibliothèque pour voir votre collection", font=ctk.CTkFont(size=16), text_color="#64748B")
        self.welcome_msg.pack(expand=True)

    def _refresh_lib_nav(self):
        for w in self.lib_nav.winfo_children(): w.destroy()
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM libraries WHERE profile_id=?", (self.current_profile[0],))
        for lib in cursor.fetchall():
            icons = {"Films / Séries": "🎬", "Animés": "🎌", "Jeux PC": "🎮"}
            btn = ctk.CTkButton(self.lib_nav, text=f"{icons.get(lib[3], '📁')} {lib[2]}", 
                                anchor="w", fg_color="transparent", command=lambda l=lib: self._load_library(l))
            btn.pack(fill="x", pady=2)

    def _load_library(self, lib):
        self.current_lib = lib
        if hasattr(self, 'welcome_msg'): self.welcome_msg.destroy()
        for w in self.content_area.winfo_children(): w.destroy()
        
        header = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=30)
        
        ctk.CTkLabel(header, text=lib[2], font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")
        
        btn_f = ctk.CTkFrame(header, fg_color="transparent")
        btn_f.pack(side="right")
        
        ctk.CTkButton(btn_f, text="🔄 Synchroniser", command=self._action_sync, fg_color="#10B981", width=120).pack(side="right", padx=10)
        ctk.CTkButton(btn_f, text="🗑️", width=40, fg_color="#EF4444", command=self._action_delete_lib).pack(side="right")

        self.media_grid = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self.media_grid.pack(fill="both", expand=True, padx=20)
        self._refresh_grid()

    def _refresh_grid(self):
        for w in self.media_grid.winfo_children(): w.destroy()
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM media_items WHERE lib_id=?", (self.current_lib[0],))
        items = cursor.fetchall()

        row, col = 0, 0
        for item in items:
            self._create_card(item).grid(row=row, column=col, padx=12, pady=12)
            col += 1
            if col > 4: col = 0; row += 1

    def _create_card(self, item):
        card = ctk.CTkFrame(self.media_grid, width=175, height=270, fg_color="#1E293B", corner_radius=12)
        card.pack_propagate(False)
        
        lbl_img = ctk.CTkLabel(card, text="🎬", font=("Arial", 40))
        lbl_img.pack(pady=10, fill="both", expand=True)
        
        def load():
            path = CACHE_DIR / f"poster_{item[0]}.jpg"
            if not path.exists() and item[5]: 
                try: urlretrieve(item[5], path)
                except: pass
            if path.exists():
                img = ctk.CTkImage(Image.open(path), size=(150, 205))
                self.after(0, lambda: lbl_img.configure(image=img, text=""))
        
        threading.Thread(target=load, daemon=True).start()
        
        ctk.CTkLabel(card, text=item[3], font=ctk.CTkFont(size=12, weight="bold"), wraplength=155).pack(pady=(0, 10))
        
        card.bind("<Button-1>", lambda e: self._show_details(item))
        lbl_img.bind("<Button-1>", lambda e: self._show_details(item))
        return card

    def _show_details(self, item):
        # [id, lib_id, raw, title, summary, poster, date, score, genres, seasons, episodes, duration, status, path, sync]
        win = ctk.CTkToplevel(self)
        win.title(item[3]); win.geometry("950x650")
        win.attributes("-topmost", True)
        win.configure(fg_color="#020617")

        main_f = ctk.CTkFrame(win, fg_color="transparent")
        main_f.pack(fill="both", expand=True, padx=40, pady=40)

        # Poster Section
        poster_f = ctk.CTkFrame(main_f, width=300, height=450, fg_color="#1E293B", corner_radius=15)
        poster_f.pack(side="left")
        poster_f.pack_propagate(False)
        
        path = CACHE_DIR / f"poster_{item[0]}.jpg"
        if path.exists():
            img = ctk.CTkImage(Image.open(path), size=(300, 450))
            ctk.CTkLabel(poster_f, image=img, text="").pack()

        # Info Section
        info_f = ctk.CTkFrame(main_f, fg_color="transparent")
        info_f.pack(side="right", fill="both", expand=True, padx=(40, 0))

        ctk.CTkLabel(info_f, text=item[3], font=ctk.CTkFont(size=34, weight="bold"), wraplength=500, justify="left").pack(anchor="w")
        
        meta_line = f"📅 {item[6]}  |  ⭐ {item[7]}  |  Status: {item[12]}"
        ctk.CTkLabel(info_f, text=meta_line, font=ctk.CTkFont(size=14), text_color="#3B82F6").pack(anchor="w", pady=10)

        if item[9] != "N/A":
            sub_meta = f"📺 {item[9]} Saisons  |  🔢 {item[10]} Épisodes"
            ctk.CTkLabel(info_f, text=sub_meta, font=ctk.CTkFont(size=13, weight="bold"), text_color="#10B981").pack(anchor="w")

        ctk.CTkLabel(info_f, text="SYNOPSIS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B").pack(anchor="w", pady=(30, 5))
        txt = ctk.CTkTextbox(info_f, height=220, font=("Inter", 14), fg_color="#0F172A", border_width=1, border_color="#334155")
        txt.pack(fill="x", pady=5)
        txt.insert("1.0", item[4] or "Aucun synopsis disponible.")
        txt.configure(state="disabled")

        btn_row = ctk.CTkFrame(info_f, fg_color="transparent")
        btn_row.pack(fill="x", pady=25)
        
        ctk.CTkButton(btn_row, text="🚀 LANCER LE MÉDIA", height=50, fg_color="#2563EB", font=ctk.CTkFont(weight="bold"),
                       command=lambda: os.startfile(item[13])).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(btn_row, text="📂", width=50, height=50, fg_color="#475569", 
                       command=lambda: os.startfile(os.path.dirname(item[13]))).pack(side="right")

    def _action_sync(self):
        progress = ctk.CTkToplevel(self)
        progress.title("Synchronisation"); progress.geometry("500x200"); progress.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(progress, text="Préparation du scan...", wraplength=450)
        lbl.pack(pady=20)
        
        bar = ctk.CTkProgressBar(progress, width=400)
        bar.pack(pady=10); bar.set(0)

        def sync():
            paths = json.loads(self.current_lib[4])
            cursor = self.db.conn.cursor()
            
            for p in paths:
                root = Path(p)
                if not root.exists(): continue
                items = list(root.iterdir())
                total = len(items)
                
                for i, entry in enumerate(items):
                    if entry.is_dir() or entry.suffix.lower() in ['.mp4', '.mkv', '.avi', '.exe']:
                        self.after(0, lambda v=i/total, t=f"Traitement : {entry.name}": (bar.set(v), lbl.configure(text=t)))
                        
                        cursor.execute("SELECT id FROM media_items WHERE lib_id=? AND raw_name=?", (self.current_lib[0], entry.name))
                        if cursor.fetchone(): continue

                        clean = re.sub(r'[\.\[\(].*?[\.\)\]]', ' ', entry.stem).strip()
                        data = self.api.fetch(clean, self.current_lib[3], self.current_lib[5])
                        
                        if data:
                            cursor.execute('''INSERT INTO media_items 
                                (lib_id, raw_name, title, summary, poster_url, release_date, score, 
                                 seasons, episodes, duration, status, local_path, sync_status) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                (self.current_lib[0], entry.name, data['title'], data['summary'], data['poster'],
                                 data['date'], data['score'], data['seasons'], data['episodes'], "N/A", data['status'], str(entry), "synced"))
                            self.db.conn.commit()
                            self.after(0, self._refresh_grid)
            
            self.after(0, progress.destroy)

        threading.Thread(target=sync, daemon=True).start()

    def _ui_add_library(self):
        win = ctk.CTkToplevel(self)
        win.title("Nouvelle Bibliothèque"); win.geometry("450x500"); win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="Configuration de Bibliothèque", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=30)
        
        name_e = ctk.CTkEntry(win, placeholder_text="Nom (ex: Ma Collection de Films)", width=350, height=40)
        name_e.pack(pady=10)
        
        type_e = ctk.CTkOptionMenu(win, values=["Films / Séries", "Animés", "Jeux PC"], width=350, height=40)
        type_e.pack(pady=10)
        
        path_var = tk.StringVar(value="Aucun dossier sélectionné")
        def pick(): 
            d = filedialog.askdirectory()
            if d: path_var.set(d)
        
        ctk.CTkButton(win, text="📂 Sélectionner le Dossier Source", command=pick, width=350, height=40, fg_color="#475569").pack(pady=20)
        ctk.CTkLabel(win, textvariable=path_var, font=("Arial", 11), text_color="#3B82F6").pack()

        def save():
            if name_e.get() and path_var.get() != "Aucun dossier sélectionné":
                cursor = self.db.conn.cursor()
                cursor.execute("INSERT INTO libraries (profile_id, name, type, paths, lang) VALUES (?, ?, ?, ?, ?)", 
                               (self.current_profile[0], name_e.get(), type_e.get(), json.dumps([path_var.get()]), "fr-FR"))
                self.db.conn.commit()
                self._refresh_lib_nav()
                win.destroy()

        ctk.CTkButton(win, text="CRÉER LA BIBLIOTHÈQUE", command=save, height=50, fg_color="#22C55E", font=ctk.CTkFont(weight="bold")).pack(pady=40)

    def _ui_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Paramètres API"); win.geometry("500x450"); win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="Configuration des Clés API", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=30)
        
        tmdb_e = ctk.CTkEntry(win, placeholder_text="Clé API TMDB", width=400, height=40)
        tmdb_e.insert(0, self.settings["api_keys"].get("tmdb", ""))
        tmdb_e.pack(pady=10)
        
        rawg_e = ctk.CTkEntry(win, placeholder_text="Clé API RAWG", width=400, height=40)
        rawg_e.insert(0, self.settings["api_keys"].get("rawg", ""))
        rawg_e.pack(pady=10)

        def save():
            self.settings["api_keys"]["tmdb"] = tmdb_e.get().strip()
            self.settings["api_keys"]["rawg"] = rawg_e.get().strip()
            self.save_settings()
            self.api.keys = self.settings["api_keys"]
            win.destroy()
            messagebox.showinfo("Paramètres", "Configurations sauvegardées !")

        ctk.CTkButton(win, text="💾 SAUVEGARDER", command=save, height=50, fg_color="#2563EB").pack(pady=40)

    def _action_delete_lib(self):
        if messagebox.askyesno("Supprimer", f"Voulez-vous supprimer '{self.current_lib[2]}' ?"):
            cursor = self.db.conn.cursor()
            cursor.execute("DELETE FROM media_items WHERE lib_id=?", (self.current_lib[0],))
            cursor.execute("DELETE FROM libraries WHERE id=?", (self.current_lib[0],))
            self.db.conn.commit()
            self._show_dashboard()
            self._refresh_lib_nav()

if __name__ == "__main__":
    app = MediaNexusUltra()
    app.mainloop()
