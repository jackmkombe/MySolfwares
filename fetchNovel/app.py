import customtkinter as ctk
import threading
from scraper import NovelScraper
import os
from tkinter import filedialog

# Design Tokens (Windows 11 Fluent inspired)
ACCENT_BLUE = "#0067c0"
ACCENT_HOVER = "#005aab"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FetchNovel - Fluent Edition")
        self.geometry("900x750")
        
        # Main Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Content

        # 1. HEADER
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        
        self.logo_label = ctk.CTkLabel(self.header_frame, text="FetchNovel", font=ctk.CTkFont(family="Segoe UI Variable Display", size=26, weight="bold"))
        self.logo_label.pack(side="left")
        
        self.status_badge = ctk.CTkLabel(self.header_frame, text="PRÊT", 
                                        fg_color=("#EBEBEB", "#3a3a3a"), text_color="#50C878",
                                        corner_radius=12, width=80, height=24,
                                        font=ctk.CTkFont(family="Segoe UI Variable Small", size=11, weight="bold"))
        self.status_badge.pack(side="left", padx=20)

        self.theme_menu = ctk.CTkOptionMenu(self.header_frame, values=["Dark", "Light", "System"],
                                           width=100, height=32, corner_radius=8,
                                           command=self.change_appearance_mode_event)
        self.theme_menu.pack(side="right")
        self.theme_menu.set("Dark")

        # 2. CONTENT AREA
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=0)
        self.main_container.grid_columnconfigure((0, 1), weight=1, uniform="group1")

        # URL Input
        self.add_label("Lien du premier chapitre (Start URL)", 0, 0, 2)
        self.url_entry = self.add_entry("https://...", 1, 0, 2)
        self.url_entry.insert(0, "https://novelhi.com/s/Douluo-Dalu-4-Ultimate-Fighting/1")

        # Configure Grid with 24px gap for the 4-input area
        # We'll use two rows for the 4 small inputs
        
        # Row 1: Selector & Batch
        self.add_label("Sélecteur de contenu (ID/Class)", 2, 0)
        self.selector_entry = self.add_entry("#readcontent", 3, 0)
        self.selector_entry.grid(padx=(0, 12)) # 12px right

        self.add_label("Chapitres par fichier", 2, 1)
        self.batch_entry = self.add_entry("10", 3, 1)
        self.batch_entry.grid(padx=(12, 0)) # 12px left
        self.batch_entry.insert(0, "10")

        # Row 2: Total & Delay
        self.add_label("Total à récupérer", 4, 0)
        self.total_entry = self.add_entry("50", 5, 0)
        self.total_entry.grid(padx=(0, 12))
        self.total_entry.insert(0, "50")

        self.add_label("Délai furtif (secondes)", 4, 1)
        self.delay_entry = self.add_entry("2", 5, 1)
        self.delay_entry.grid(padx=(12, 0))
        self.delay_entry.insert(0, "2")

        # Translation Option
        self.translate_var = ctk.BooleanVar(value=False)
        self.translate_cb = ctk.CTkCheckBox(self.main_container, text="Traduire en français (Google Translate)", 
                                           variable=self.translate_var,
                                           font=ctk.CTkFont(family="Segoe UI Variable Small", size=13),
                                           fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER)
        self.translate_cb.grid(row=6, column=0, columnspan=2, sticky="w", pady=(15, 5))

        # Path
        self.add_label("Dossier d'enregistrement", 7, 0, 2)
        self.path_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.path_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        self.path_frame.grid_columnconfigure(0, weight=1)
        
        self.dir_entry = ctk.CTkEntry(self.path_frame, height=40, corner_radius=8)
        self.dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.dir_entry.insert(0, os.path.join(os.path.expanduser("~"), "Documents", "NovelDownloads"))
        
        self.browse_btn = ctk.CTkButton(self.path_frame, text="Parcourir", width=110, height=40, 
                                       fg_color=("#E5E5E5", "#3a3a3a"), text_color=("#000000", "#FFFFFF"),
                                       hover_color=("#D5D5D5", "#4a4a4a"), corner_radius=8,
                                       command=self.browse_callback)
        self.browse_btn.grid(row=0, column=1)

        # 3. ACTION BUTTONS
        self.btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.btn_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.start_btn = ctk.CTkButton(self.btn_frame, text="Démarrer le fetching", height=48, 
                                      fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER, corner_radius=10,
                                      font=ctk.CTkFont(family="Segoe UI Variable Display", size=15, weight="bold"),
                                      command=self.start_callback)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.stop_btn = ctk.CTkButton(self.btn_frame, text="Arrêter", height=48, 
                                     fg_color="transparent", border_width=2, border_color="#FF4500",
                                     text_color="#FF4500", hover_color=("#FFF0F0", "#331010"), corner_radius=10,
                                     state="disabled", command=self.stop_callback)
        self.stop_btn.pack(side="left", expand=True, fill="x")

        # 4. LOGS
        self.log_label = ctk.CTkLabel(self.main_container, text="Activité & Logs", font=ctk.CTkFont(family="Segoe UI Variable Small", size=14, weight="bold"))
        self.log_label.grid(row=10, column=0, sticky="w", pady=(15, 5))
        self.textbox = ctk.CTkTextbox(self.main_container, corner_radius=10, border_width=1)
        self.textbox.grid(row=11, column=0, columnspan=2, sticky="nsew", pady=(0, 20))
        self.main_container.grid_rowconfigure(11, weight=1)

        self.scraper = None

    def add_label(self, text, r, c, cs=1):
        lbl = ctk.CTkLabel(self.main_container, text=text, font=ctk.CTkFont(family="Segoe UI Variable Small", size=13))
        lbl.grid(row=r, column=c, columnspan=cs, sticky="w", pady=(10, 2))
        if cs == 1:
            if c == 0: lbl.grid(padx=(0, 12))
            else: lbl.grid(padx=(12, 0))
        return lbl

    def add_entry(self, placeholder, r, c, cs=1):
        ent = ctk.CTkEntry(self.main_container, placeholder_text=placeholder, height=40, corner_radius=8)
        ent.grid(row=r, column=c, columnspan=cs, sticky="ew", pady=(0, 10))
        return ent

    def change_appearance_mode_event(self, mode):
        ctk.set_appearance_mode(mode)

    def log(self, message):
        self.textbox.insert("end", f"{message}\n")
        self.textbox.see("end")

    def start_callback(self):
        url = self.url_entry.get()
        selector = self.selector_entry.get()
        output_dir = self.dir_entry.get()
        try:
            batch_size = int(self.batch_entry.get())
            total_chapters = int(self.total_entry.get())
            delay = float(self.delay_entry.get())
        except ValueError:
            self.log("Erreur : Les champs numériques (chapitres, total, délai) sont invalides.")
            return

        if not url:
            self.log("Erreur : L'URL de départ est requise.")
            return

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_badge.configure(text="EN COURS", text_color="#FFD700")
        self.textbox.delete("0.0", "end")
        
        translate_enabled = self.translate_var.get()
        self.scraper = NovelScraper(url, selector, batch_size, output_dir=output_dir, delay=delay, translate=translate_enabled, update_log_callback=self.log)
        self.thread = threading.Thread(target=self.run_scraper, args=(total_chapters,))
        self.thread.daemon = True
        self.thread.start()

    def run_scraper(self, total):
        try:
            self.scraper.run(total)
        finally:
            self.after(0, self.reset_buttons)

    def reset_buttons(self, status="PRÊT"):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_badge.configure(text=status, text_color="#50C878" if status in ["PRÊT", "TERMINÉ"] else "#FF4500")

    def stop_callback(self):
        if self.scraper:
            self.scraper.stop()
            self.status_badge.configure(text="ARRÊT...", text_color="#FF4500")
            self.log("Demande d'arrêt envoyée... Enregistrement en cours.")

    def browse_callback(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory.replace('/', '\\'))

if __name__ == "__main__":
    app = App()
    app.mainloop()
