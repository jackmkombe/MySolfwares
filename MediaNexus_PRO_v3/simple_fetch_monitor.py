"""
MediaNexus PRO v3.2 - Simple Fetch Monitor
"""
import customtkinter as ctk

class SimpleFetchMonitor:
    def __init__(self):
        self.history = []

    def log(self, message):
        self.history.append(message)

    def log_request(self, api, media_type, success, duration, error=None):
        status = "✅" if success else "❌"
        msg = f"[{status}] {api} | {media_type} | {duration:.2f}s"
        if error:
            msg += f" | ⚠️ {error}"
        self.log(msg)

    def get_current_stats(self):
        total = len(self.history)
        success = sum(1 for m in self.history if "✅" in m)
        return {
            "total_requests": total,
            "success_rate": (success / total * 100) if total > 0 else 0,
            "most_used_api": "Multiple", # Simplifié
            "most_common_media": "Automatique" # Simplifié
        }

class SimpleMonitorDialog(ctk.CTkToplevel):
    def __init__(self, parent, monitor):
        super().__init__(parent)
        self.title("Surveillance du Fetching")
        self.geometry("600x400")
        
        self.text = ctk.CTkTextbox(self, width=580, height=380)
        self.text.pack(padx=10, pady=10)
        
        for entry in monitor.history:
            self.text.insert("end", entry + "\n")
