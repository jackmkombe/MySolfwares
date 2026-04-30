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
from collections import defaultdict
from difflib import SequenceMatcher
from urllib.request import urlretrieve
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk

# --- CONFIGURATION ET CONSTANTES ---
APP_NAME = "MediaNexus Ultra"
VERSION = "1.1.0"
DB_PATH = "medianexus_core.db"
CACHE_DIR = Path("media_cache")
CONFIG_DIR = Path("config")
EXPORT_DIR = Path("exports")
CACHE_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)
DEFAULT_THEME = "dark"

# --- ENGINE : MATCHING ET SIMILARITÉ INTÉLLIGENTE ---
class MatchingEngine:
    @staticmethod
    def clean_title(raw_name: str) -> Tuple[str, str]:
        """Nettoyage heuristique avancé des noms de fichiers/dossiers."""
        name = Path(raw_name).stem
        noise = [
            r'\[.*?\]', r'\(.*?\)', r'\.(1080p|720p|480p|2160p|4K)',
            r'\.(BluRay|WEB-DL|WEBRip|HDTV|DVDRip|BRRip)',
            r'\.(x264|x265|H264|H265|HEVC)', r'\.(AAC|AC3|DTS|MP3)',
            r'_(VOSTFR|VOSTA|VF|VO|MULTI)', r'\.S\d{2}E\d{2}', 
            r'\.E\d{2,3}', r'-(.*?)$'
        ]
        for p in noise:
            name = re.sub(p, ' ', name, flags=re.IGNORECASE)
        
        year_match = re.search(r'\b(19|20)\d{2}\b', name)
        year = year_match.group(0) if year_match else ""
        
        name = re.sub(r'[._-]', ' ', name)
        name = ' '.join(name.split()).strip()
        return name, year

    @staticmethod
    def get_similarity(a: str, b: str) -> float:
        if not a or not b: return 0.0
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# --- ENGINE : PERSISTENCE ET DONNÉES (SQLITE) ---
class DataCore:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._setup_schema()

    def _setup_schema(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS libraries 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, paths TEXT, config TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS items 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, lib_id INTEGER, raw_name TEXT, 
             title TEXT, summary TEXT, release_date TEXT, score TEXT, genres TEXT, 
             poster_url TEXT, local_path TEXT, status TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS api_cache 
            (key TEXT PRIMARY KEY, value TEXT, timestamp REAL)''')
        self.conn.commit()

# --- ENGINE : APIs ET FETCHING ---
class APICore:
    def __init__(self, settings: Dict):
        self.settings = settings
        self.session = requests.Session()

    def fetch(self, query: str, mtype: str, year: str = "") -> Optional[Dict]:
        try:
            if mtype == "Films / Séries":
                return self._tmdb_search(query, year)
            elif mtype == "Animés":
                return self._jikan_search(query)
            elif mtype == "Jeux PC":
                return self._rawg_search(query)
        except Exception as e:
            print(f"API Error: {e}")
        return None

    def _tmdb_search(self, q, y):
        key = self.settings.get("tmdb_key")
        if not key: return None
        url = f"https://api.themoviedb.org/3/search/multi?api_key={key}&query={q}&language=fr-FR"
        data = self.session.get(url, timeout=10).json()
        if data.get('results'):
            best = data['results'][0]
            return {
                "title": best.get('title') or best.get('name'),
                "summary": best.get('overview'),
                "date": best.get('release_date') or best.get('first_air_date'),
                "score": str(best.get('vote_average')),
                "poster": f"https://image.tmdb.org/t/p/w500{best.get('poster_path')}" if best.get('poster_path') else None
            }
        return None

    def _jikan_search(self, q):
        url = f"https://api.jikan.moe/v4/anime?q={q}&limit=1"
        data = self.session.get(url, timeout=10).json()
        if data.get('data'):
            best = data['data'][0]
            return {
                "title": best['title_english'] or best['title'],
                "summary": best.get('synopsis'),
                "date": str(best.get('year', "N/A")),
                "score": str(best.get('score', "N/A")),
                "poster": best['images']['jpg']['large_image_url']
            }
        return None

    def _rawg_search(self, q):
        key = self.settings.get("rawg_key")
        if not key: return None
        url = f"https://api.rawg.io/api/games?key={key}&search={q}&page_size=1"
        data = self.session.get(url, timeout=10).json()
        if data.get('results'):
            best = data['results'][0]
            return {
                "title": best['name'],
                "summary": "Détails via RAWG API",
                "date": best.get('released'),
                "score": str(best.get('rating')),
                "poster": best.get('background_image')
            }
        return None

# --- UI : COMPOSANTS ET FENÊTRE PRINCIPALE ---
class MediaCard(ctk.CTkFrame):
    def __init__(self, parent, item, click_callback):
        super().__init__(parent, fg_color="#1E293B", corner_radius=12, width=180, height=300, border_width=1, border_color="#334155")
        self.item = item
        self.pack_propagate(False)
        # Image / Poster
        self.poster_label = ctk.CTkLabel(self, text="🎬", font=("Arial", 40), text_color="#475569")
        self.poster_label.pack(pady=10, fill="both", expand=True)

        # Titre
        self.title_label = ctk.CTkLabel(self, text=item[3] or item[2], font=ctk.CTkFont(size=12, weight="bold"), 
                                        wraplength=160, height=45)
        self.title_label.pack(pady=(0, 10), padx=5)

        # Badge de statut si confiance basse
        if item[10] == "check":
            self.badge = ctk.CTkLabel(self, text="À VÉRIFIER", font=ctk.CTkFont(size=9, weight="bold"), 
                                       fg_color="#EF4444", text_color="white", corner_radius=4)
            self.badge.place(x=10, y=10)

        threading.Thread(target=self._load_image, daemon=True).start()
        
        self.bind("<Button-1>", lambda e: click_callback(item))
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda e: click_callback(item))

    def _load_image(self):
        try:
            cache_file = CACHE_DIR / f"{self.item[0]}.jpg"
            if not cache_file.exists() and self.item[8]:
                urlretrieve(self.item[8], cache_file)
            
            if cache_file.exists():
                img = Image.open(cache_file)
                ctk_img = ctk.CTkImage(img, size=(160, 220))
                self.after(0, lambda: self.poster_label.configure(image=ctk_img, text=""))
        except: pass

class MediaNexusApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.core = DataCore()
        self.settings = self._load_settings()
        self.api = APICore(self.settings)
        
        self.title(f"{APP_NAME} Ultra v{VERSION}")
        self.geometry("1200x850")
        ctk.set_appearance_mode("dark")
        
        try:
            if os.path.exists("app_icon.ico"):
                self.iconbitmap("app_icon.ico")
        except: pass

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._init_ui()
        self._load_libraries()

    def _init_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0F172A")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="💎 MEDIANEXUS", font=ctk.CTkFont(size=22, weight="bold"), text_color="#3B82F6").pack(pady=30)
        
        self.btn_new = ctk.CTkButton(self.sidebar, text="+ Nouvelle Bibliothèque", command=self._ui_add_library, fg_color="#2563EB")
        self.btn_new.pack(pady=10, padx=20, fill="x")

        self.btn_import = ctk.CTkButton(self.sidebar, text="📥 Importer Config", command=self._action_import_lib, 
                                         fg_color="transparent", border_width=1, border_color="#334155")
        self.btn_import.pack(pady=5, padx=20, fill="x")
        
        self.lib_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.lib_scroll.pack(fill="both", expand=True, padx=5, pady=10)
        
        self.btn_settings = ctk.CTkButton(self.sidebar, text="⚙️ Paramètres Globaux", command=self._ui_settings, fg_color="transparent", border_width=1)
        self.btn_settings.pack(pady=20, padx=20, fill="x")

        self.main_area = ctk.CTkFrame(self, fg_color="#020617", corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        
        self.header = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.header.pack(fill="x", padx=30, pady=20)
        
        self.title_label = ctk.CTkLabel(self.header, text="Bienvenue", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(side="left")

        self.btn_scan = ctk.CTkButton(self.header, text="🔄 Synchroniser", command=self._action_scan, width=140, height=35, fg_color="#10B981")
        
        self.btn_lib_actions = ctk.CTkOptionMenu(self.header, values=["Gérer...", "Modifier", "Dupliquer", "Exporter JSON", "Supprimer"],
                                                command=self._on_lib_action, width=120)
        
        self.grid_container = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=20, pady=10)

    def _load_settings(self):
        path = CONFIG_DIR / "settings.json"
        if path.exists(): return json.load(path.open())
        return {"tmdb_key": "", "rawg_key": "", "confidence_threshold": 0.6}

    def _save_settings(self):
        (CONFIG_DIR / "settings.json").write_text(json.dumps(self.settings, indent=4))

    def _load_libraries(self):
        for w in self.lib_scroll.winfo_children(): w.destroy()
        cursor = self.core.conn.cursor()
        cursor.execute("SELECT id, name, type FROM libraries")
        for lib in cursor.fetchall():
            btn = ctk.CTkButton(self.lib_scroll, text=f"{lib[1]}", anchor="w", fg_color="transparent", 
                                command=lambda l=lib: self._select_library(l))
            btn.pack(fill="x", pady=2)

    def _select_library(self, lib):
        self.current_lib = lib
        self.title_label.configure(text=f"{lib[1]} ({lib[2]})")
        self.btn_scan.pack(side="right", padx=10)
        self.btn_lib_actions.pack(side="right")
        self.btn_lib_actions.set("Gérer...")
        self._refresh_grid()

    def _on_lib_action(self, choice):
        if choice == "Modifier": self._ui_add_library(edit_mode=True)
        elif choice == "Dupliquer": self._action_duplicate_lib()
        elif choice == "Exporter JSON": self._action_export_lib()
        elif choice == "Supprimer": self._action_delete_lib()
        self.btn_lib_actions.set("Gérer...")

    def _refresh_grid(self):
        for w in self.grid_container.winfo_children(): w.destroy()
        cursor = self.core.conn.cursor()
        cursor.execute("SELECT * FROM items WHERE lib_id=?", (self.current_lib[0],))
        items = cursor.fetchall()
        
        row, col = 0, 0
        for item in items:
            card = MediaCard(self.grid_container, item, self._ui_item_details)
            card.grid(row=row, column=col, padx=15, pady=15)
            col += 1
            if col > 4: col = 0; row += 1

    def _action_scan(self):
        if not hasattr(self, 'current_lib'): return
        self.btn_scan.configure(state="disabled", text="Scan en cours...")
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        cursor = self.core.conn.cursor()
        cursor.execute("SELECT paths, type FROM libraries WHERE id=?", (self.current_lib[0],))
        paths_json, lib_type = cursor.fetchone()
        paths = json.loads(paths_json)
        
        for p in paths:
            source = Path(p)
            if not source.exists(): continue
            
            for entry in source.iterdir():
                cursor.execute("SELECT id FROM items WHERE lib_id=? AND raw_name=?", (self.current_lib[0], entry.name))
                if cursor.fetchone(): continue
                # Matching Intelligent avec seuil
                clean_name, year = MatchingEngine.clean_title(entry.name)
                data = self.api.fetch(clean_name, lib_type, year)
                
                if data:
                    # Calculer confiance
                    score = MatchingEngine.get_similarity(clean_name, data['title'])
                    status = "synced" if score >= self.settings.get("confidence_threshold", 0.6) else "check"
                    
                    cursor.execute('''INSERT INTO items 
                        (lib_id, raw_name, title, summary, release_date, score, genres, poster_url, local_path, status) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (self.current_lib[0], entry.name, data['title'], data['summary'], 
                         data['date'], data['score'], "", data['poster'], str(entry), status))
                    self.core.conn.commit()
                    self.after(0, self._refresh_grid)
        
        self.after(0, lambda: self.btn_scan.configure(state="normal", text="🔄 Synchroniser"))

    # --- INTERFACE : DIALOGUES ---
    def _ui_add_library(self, edit_mode=False):
        win = ctk.CTkToplevel(self)
        win.title("Modifier" if edit_mode else "Nouvelle Bibliothèque")
        win.geometry("450x550")
        win.attributes("-topmost", True)
        
        # Pré-remplissage en mode édition
        current_name = ""
        current_type = "Films / Séries"
        current_path = "Aucun dossier"
        if edit_mode and hasattr(self, 'current_lib'):
            cursor = self.core.conn.cursor()
            cursor.execute("SELECT name, type, paths FROM libraries WHERE id=?", (self.current_lib[0],))
            current_name, current_type, paths_json = cursor.fetchone()
            current_path = json.loads(paths_json)[0]

        ctk.CTkLabel(win, text="Nom de la collection:", anchor="w", font=ctk.CTkFont(weight="bold")).pack(padx=30, pady=(30, 0), fill="x")
        name_e = ctk.CTkEntry(win, height=35)
        name_e.insert(0, current_name)
        name_e.pack(padx=30, pady=5, fill="x")
        
        ctk.CTkLabel(win, text="Type de contenu:", anchor="w", font=ctk.CTkFont(weight="bold")).pack(padx=30, pady=15, fill="x")
        type_e = ctk.CTkOptionMenu(win, values=["Films / Séries", "Animés", "Jeux PC"], height=35)
        type_e.set(current_type)
        type_e.pack(padx=30, pady=5, fill="x")
        
        path_var = tk.StringVar(value=current_path)
        def pick(): 
            d = filedialog.askdirectory()
            if d: path_var.set(d)
        
        ctk.CTkButton(win, text="� Sélectionner le Dossier Source", command=pick, height=40, fg_color="#475569").pack(padx=30, pady=25, fill="x")
        ctk.CTkLabel(win, textvariable=path_var, font=("Arial", 10), text_color="#94A3B8").pack(padx=30)

        def save():
            if name_e.get() and path_var.get() != "Aucun dossier":
                c = self.core.conn.cursor()
                if edit_mode:
                    c.execute("UPDATE libraries SET name=?, type=?, paths=? WHERE id=?", 
                             (name_e.get(), type_e.get(), json.dumps([path_var.get()]), self.current_lib[0]))
                else:
                    c.execute("INSERT INTO libraries (name, type, paths, config) VALUES (?, ?, ?, ?)", 
                             (name_e.get(), type_e.get(), json.dumps([path_var.get()]), "{}"))
                self.core.conn.commit()
                self._load_libraries()
                win.destroy()
                if edit_mode: self._select_library((self.current_lib[0], name_e.get(), type_e.get()))
        
        ctk.CTkButton(win, text="CONFIRMER" if edit_mode else "CRÉER", command=save, 
                       height=45, fg_color="#10B981", font=ctk.CTkFont(weight="bold")).pack(pady=40, padx=30, fill="x")

    def _ui_item_details(self, item):
        win = ctk.CTkToplevel(self)
        win.title(item[3])
        win.geometry("800x500")
        win.attributes("-topmost", True)
        
        main = ctk.CTkFrame(win, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        img_f = ctk.CTkFrame(main, width=280, height=420, fg_color="#1E293B")
        img_f.pack(side="left", padx=(0, 20))
        img_f.pack_propagate(False)
        
        try:
            cache_file = CACHE_DIR / f"{item[0]}.jpg"
            if cache_file.exists():
                img = Image.open(cache_file)
                ctk_img = ctk.CTkImage(img, size=(280, 420))
                ctk.CTkLabel(img_f, image=ctk_img, text="").pack()
        except: pass

        info_f = ctk.CTkFrame(main, fg_color="transparent")
        info_f.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(info_f, text=item[3], font=ctk.CTkFont(size=24, weight="bold"), wraplength=450, anchor="w").pack(fill="x")
        ctk.CTkLabel(info_f, text=f"📅 {item[5]}  ⭐ {item[6]}", text_color="#F59E0B").pack(anchor="w", pady=5)
        
        box = ctk.CTkTextbox(info_f, height=200, font=("Arial", 12))
        box.pack(fill="x", pady=15)
        box.insert("1.0", item[4] or "Aucun résumé disponible.")
        box.configure(state="disabled")

        ctk.CTkButton(info_f, text="🚀 Ouvrir l'emplacement", command=lambda: os.startfile(os.path.dirname(item[9]))).pack(side="bottom", fill="x")

    def _ui_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Paramètres Globaux")
        win.geometry("450x400")
        win.attributes("-topmost", True)
        
        ctk.CTkLabel(win, text="Configuration des APIs", font=("Arial", 18, "bold")).pack(pady=20)
        
        tmdb_e = ctk.CTkEntry(win, placeholder_text="TMDB API Key (Films/Séries)", width=350)
        tmdb_e.insert(0, self.settings.get("tmdb_key", ""))
        tmdb_e.pack(pady=10)
        
        rawg_e = ctk.CTkEntry(win, placeholder_text="RAWG API Key (Jeux PC)", width=350)
        rawg_e.insert(0, self.settings.get("rawg_key", ""))
        rawg_e.pack(pady=10)
        
        def save():
            self.settings["tmdb_key"] = tmdb_e.get()
            self.settings["rawg_key"] = rawg_e.get()
            self._save_settings()
            self.api.settings = self.settings
            win.destroy()
            messagebox.showinfo("Succès", "Paramètres sauvegardés.")

        ctk.CTkButton(win, text="SAUVEGARDER", command=save, fg_color="#3B82F6").pack(pady=40)

    # --- ACTIONS AVANCÉES ---
    def _action_duplicate_lib(self):
        if not hasattr(self, 'current_lib'): return
        cursor = self.core.conn.cursor()
        cursor.execute("SELECT name, type, paths, config FROM libraries WHERE id=?", (self.current_lib[0],))
        n, t, p, c = cursor.fetchone()
        cursor.execute("INSERT INTO libraries (name, type, paths, config) VALUES (?, ?, ?, ?)", 
                       (f"{n} (Copie)", t, p, c))
        self.core.conn.commit()
        self._load_libraries()
        messagebox.showinfo("Omni", "Bibliothèque dupliquée !")

    def _action_export_lib(self):
        if not hasattr(self, 'current_lib'): return
        cursor = self.core.conn.cursor()
        cursor.execute("SELECT name, type, paths, config FROM libraries WHERE id=?", (self.current_lib[0],))
        data = cursor.fetchone()
        export_data = {"name": data[0], "type": data[1], "paths": json.loads(data[2]), "config": json.loads(data[3])}
        
        path = EXPORT_DIR / f"export_{data[0].replace(' ', '_')}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Export", f"Configuration exportée dans :\n{path}")

    def _action_import_lib(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")])
        if not file_path: return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            cursor = self.core.conn.cursor()
            cursor.execute("INSERT INTO libraries (name, type, paths, config) VALUES (?, ?, ?, ?)", 
                           (d['name'], d['type'], json.dumps(d['paths']), json.dumps(d['config'])))
            self.core.conn.commit()
            self._load_libraries()
            messagebox.showinfo("Import", "Configuration importée avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'import : {e}")

    def _action_delete_lib(self):
        if not hasattr(self, 'current_lib'): return
        if messagebox.askyesno("Supprimer", f"Voulez-vous vraiment supprimer la bibliothèque '{self.current_lib[1]}' ?\nLes métadonnées seront effacées."):
            cursor = self.db.conn.cursor() # self.db ou self.core.conn
            cursor.execute("DELETE FROM items WHERE lib_id=?", (self.current_lib[0],))
            cursor.execute("DELETE FROM libraries WHERE id=?", (self.current_lib[0],))
            self.core.conn.commit()
            self.current_lib = None
            self.title_label.configure(text="Bienvenue")
            self.btn_scan.pack_forget()
            self.btn_lib_actions.pack_forget()
            self._load_libraries()
            self._refresh_grid()

if __name__ == "__main__":
    app = MediaNexusApp()
    app.mainloop()
