"""
MediaNexus PRO v3.2 - Système de Thèmes Dynamiques
"""

# Définition des palettes complètes
THEMES = {
    "dark": {
        # Arrière-plans (style Windows Dark)
        "bg_primary": "#202020",      # Fond principal (Windows dark)
        "bg_secondary": "#2D2D2D",    # Sidebar (Windows dark secondary)
        "bg_tertiary": "#3C3C3C",     # Cards (Windows dark tertiary)
        "bg_quaternary": "#505050",   # Borders (Windows dark borders)
        "bg_elevated": "#404040",     # Elevated surfaces
        
        # Textes (style Windows Dark)
        "text_primary": "#FFFFFF",      # Titres (pure white)
        "text_secondary": "#F3F3F3",  # Corps (light gray)
        "text_tertiary": "#CCCCCC",   # Muted (medium gray)
        "text_muted": "#888888",      # Disabled (dark gray)
        
        # Accents principaux (Windows style)
        "accent_primary": "#0078D4",   # Windows blue
        "accent_primary_hover": "#106EBE",
        "accent_primary_light": "#40A0FF",
        
        "accent_secondary": "#8B5CF6",  # Violet
        "accent_secondary_hover": "#7C3AED",
        
        "accent_tertiary": "#6366F1",   # Indigo
        "accent_tertiary_hover": "#4F46E5",
        
        # Accents sémantiques
        "accent_success": "#107C10",   # Windows green
        "accent_success_hover": "#0E6E0E",
        "accent_warning": "#FF8C00",   # Windows orange
        "accent_warning_hover": "#E67E00",
        "accent_error": "#D83B01",     # Windows red
        "accent_error_hover": "#C2351A",
        "accent_info": "#0078D4",      # Windows blue
        "accent_info_hover": "#106EBE",
        
        # États UI (Windows style)
        "border_default": "#505050",
        "border_focus": "#0078D4",
        "border_hover": "#606060",
        "hover_overlay": "#3C3C3C",
        "active_overlay": "#505050",
        "disabled": "#404040",
        
        # Ombres et effets
        "shadow_sm": "rgba(0, 0, 0, 0.2)",
        "shadow_md": "rgba(0, 0, 0, 0.3)",
        "shadow_lg": "rgba(0, 0, 0, 0.4)",
    },
    "light": {
        # Arrière-plans (Premium Light)
        "bg_primary": "#F8FAFC",      # Fond principal (Slate 50)
        "bg_secondary": "#FFFFFF",    # Sidebar (Pure white)
        "bg_tertiary": "#FFFFFF",     # Cards
        "bg_quaternary": "#E2E8F0",   # Borders (Slate 200)
        "bg_elevated": "#FFFFFF",     
        
        # Textes (High Contrast Slate)
        "text_primary": "#0F172A",      # Titres (Slate 900)
        "text_secondary": "#334155",    # Corps (Slate 700)
        "text_tertiary": "#64748B",     # Muted (Slate 500)
        "text_muted": "#94A3B8",        # Disabled (Slate 400)
        
        # Accents principaux (Vibrant Blue)
        "accent_primary": "#2563EB",   # Blue 600
        "accent_primary_hover": "#1D4ED8",
        "accent_primary_light": "#DBEAFE",
        
        "accent_secondary": "#7C3AED",  # Violet 600
        "accent_secondary_hover": "#6D28D9",
        
        "accent_tertiary": "#4F46E5",   # Indigo 600
        "accent_tertiary_hover": "#4338CA",
        
        # Accents sémantiques (Standard Safe Colors)
        "accent_success": "#059669",   # Emerald 600
        "accent_success_hover": "#047857",
        "accent_warning": "#D97706",   # Amber 600
        "accent_warning_hover": "#B45309",
        "accent_error": "#DC2626",     # Red 600
        "accent_error_hover": "#B91C1C",
        "accent_info": "#0891B2",      # Cyan 600
        "accent_info_hover": "#0E7490",
        
        # États UI
        "border_default": "#E2E8F0",
        "border_focus": "#2563EB",
        "border_hover": "#CBD5E1",
        "hover_overlay": "#F1F5F9",
        "active_overlay": "#E2E8F0",
        "disabled": "#F1F5F9",
        
        # Ombres et effets (Plus douces)
        "shadow_sm": "rgba(0, 0, 0, 0.05)",
        "shadow_md": "rgba(0, 0, 0, 0.08)",
        "shadow_lg": "rgba(0, 0, 0, 0.12)",
    }
}

def get_theme(mode: str = "dark") -> dict:
    """Retourne la palette complète pour un mode donné."""
    return THEMES.get(mode, THEMES["dark"])

# Tailles standardisées (Design System)
SIZES = {
    # Heights - Accessibilité WCAG (min 44px)
    "button_xs": 32,
    "button_sm": 36,
    "button_md": 44,  # Touch-friendly optimal
    "button_lg": 52,
    "button_xl": 60,
    
    # Inputs
    "input_sm": 36,
    "input_md": 44,
    "input_lg": 52,
    
    # Widths
    "icon_button": 48,  # WCAG compliant
    "action_button": 140,
    "sidebar_width": 260,
    "header_height": 80,
    
    # Spacing - Système de 4px
    "space_1": 4,    # xs
    "space_2": 8,    # sm
    "space_3": 12,   # md
    "space_4": 16,   # lg
    "space_5": 20,   # xl
    "space_6": 24,   # 2xl
    "space_8": 32,   # 3xl
    "space_10": 40,  # 4xl
    "space_12": 48,  # 5xl
    
    # Border Radius
    "radius_xs": 4,
    "radius_sm": 6,
    "radius_md": 8,   # Standard
    "radius_lg": 12,  # Cards
    "radius_xl": 16,  # Large cards
    "radius_2xl": 20, # Modals
    
    # Typography - Échelle typographique
    "text_xs": 10,    # Labels, metadata
    "text_sm": 11,    # Small text
    "text_base": 13,  # Body text
    "text_md": 14,    # Subheadings
    "text_lg": 15,    # Large body
    "text_xl": 16,    # Small headings
    "text_2xl": 18,   # Headings
    "text_3xl": 20,   # Large headings
    "text_4xl": 24,   # Display headings
    "text_5xl": 32,   # Hero text
    
    # Font weights
    "font_light": 300,
    "font_normal": 400,
    "font_medium": 500,
    "font_semibold": 600,
    "font_bold": 700,
    "font_extrabold": 800,
    
    # Line heights
    "leading_tight": 1.2,
    "leading_normal": 1.4,
    "leading_relaxed": 1.6,
    
    # Z-index
    "z_dropdown": 1000,
    "z_modal": 1050,
    "z_tooltip": 1100,
    "z_notification": 1200,
}

class ThemeManager:
    """Gestionnaire centralisé de thèmes avec callbacks et accès simplifié."""
    
    def __init__(self, initial_mode="dark"):
        self.current_mode = initial_mode
        self.current_theme = get_theme(initial_mode)
        self.callbacks = []
    
    def register_callback(self, callback):
        """Enregistre un callback appelé lors du changement de thème."""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """Désenregistre un callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def set_mode(self, mode: str):
        """Change le mode de thème et notifie tous les callbacks."""
        if mode not in THEMES:
            return
        
        self.current_mode = mode
        self.current_theme = get_theme(mode)
        
        # Notifier tous les callbacks
        for callback in self.callbacks:
            try:
                callback(self.current_theme, mode)
            except Exception as e:
                print(f"Error in theme callback: {e}")
    
    def get(self, key: str, default: str = "#000000") -> str:
        """Accès sécurisé à une couleur du thème actuel."""
        return self.current_theme.get(key, default)

    @property
    def is_dark(self) -> bool:
        return self.current_mode == "dark"
