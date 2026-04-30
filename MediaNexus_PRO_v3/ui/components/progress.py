"""
MediaNexus PRO v3.2 - Progress Components
"""
import customtkinter as ctk

class SyncProgressBar(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Synchronisation en cours")
        self.geometry("550x220")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self._cancelled = False

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=20)

        self.status_label = ctk.CTkLabel(main, text="Préparation...", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(anchor="w")

        self.item_label = ctk.CTkLabel(main, text="", font=ctk.CTkFont(size=12), text_color="#94A3B8", wraplength=480)
        self.item_label.pack(anchor="w", pady=5)

        self.progress_bar = ctk.CTkProgressBar(main, width=490, height=20)
        self.progress_bar.pack(pady=15)
        self.progress_bar.set(0)

        self.stats_label = ctk.CTkLabel(main, text="0/0  |  ✅ 0  |  ❌ 0", font=ctk.CTkFont(size=11), text_color="#64748B")
        self.stats_label.pack(anchor="w")

        self.source_label = ctk.CTkLabel(main, text="Source: -", font=ctk.CTkFont(size=10), text_color="#3B82F6")
        self.source_label.pack(anchor="w", pady=(5, 0))

        self.cancel_btn = ctk.CTkButton(main, text="Annuler", width=100, fg_color="#EF4444", command=self.on_cancel)
        self.cancel_btn.pack(pady=15)

    def update_progress(self, progress):
        state_texts = {
            "idle": "En attente",
            "scanning": "Scan des fichiers...",
            "fetching": "Récupération des données...",
            "completed": "Terminé !",
            "cancelled": "Annulé",
            "error": "Erreur"
        }

        self.status_label.configure(text=state_texts.get(progress.state.value, "..."))
        self.item_label.configure(text=progress.current_item)
        self.progress_bar.set(progress.percentage / 100)
        self.stats_label.configure(
            text=f"{progress.processed_items}/{progress.total_items}  |  ✅ {progress.success_count}  |  ❌ {progress.error_count}"
        )
        self.source_label.configure(text=f"Source: {progress.current_source}")

        if progress.state.value in ("completed", "cancelled", "error"):
            self.cancel_btn.configure(text="Fermer", fg_color="#475569")

    def on_cancel(self):
        self._cancelled = True
        self.destroy()

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled
