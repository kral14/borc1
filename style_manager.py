# borc/style_manager.py

from PyQt6.QtCore import QSettings, QSize # QSize importu əlavə edildi
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from themes import DARK_TEMPLATE, LIGHT_TEMPLATE

# --- Ayarların İdarə Edilməsi ---

def save_theme_setting(theme_name):
    settings = QSettings("MySoft", "BorcIzlemeApp")
    settings.setValue("theme", theme_name)

def load_theme_setting():
    settings = QSettings("MySoft", "BorcIzlemeApp")
    return settings.value("theme", "dark") # İlkin tema

ZOOM_LEVELS = {
    "75%": 0.75, "85%": 0.85, "100%": 1.0, "115%": 1.15, "125%": 1.25, "150%": 1.50
}

def save_zoom_setting(scale_factor):
    settings = QSettings("MySoft", "BorcIzlemeApp")
    settings.setValue("zoom_scale", scale_factor)

def load_zoom_setting():
    settings = QSettings("MySoft", "BorcIzlemeApp")
    return settings.value("zoom_scale", 1.0, type=float) # İlkin miqyas

# --- Dinamik Stil Kodunun Yaradılması ---

def generate_stylesheet(theme_name, scale_factor):
    """Miqyasa və temaya uyğun dinamik stil kodu yaradır."""
    
    # 100% miqyas (scale_factor=1.0) üçün baza ölçülər
    base_font_size = 11
    base_padding_v = 8
    base_padding_h = 16
    base_radius = 5
    base_nav_padding_v = 10
    base_nav_padding_h = 20
    base_margin = 3
    
    # Temaya uyğun şablonu seç
    template = DARK_TEMPLATE if theme_name == 'dark' else LIGHT_TEMPLATE

    # Şablondakı dəyişənləri miqyasa vurulmuş dəyərlərlə əvəz et
    stylesheet = template.replace("@@FONT_SIZE@@", str(int(base_font_size * scale_factor)))
    stylesheet = stylesheet.replace("@@PADDING_V@@", str(int(base_padding_v * scale_factor)))
    stylesheet = stylesheet.replace("@@PADDING_H@@", str(int(base_padding_h * scale_factor)))
    stylesheet = stylesheet.replace("@@RADIUS@@", str(int(base_radius * scale_factor)))
    stylesheet = stylesheet.replace("@@MARGIN@@", str(int(base_margin * scale_factor)))
    stylesheet = stylesheet.replace("@@NAV_PADDING_V@@", str(int(base_nav_padding_v * scale_factor)))
    stylesheet = stylesheet.replace("@@NAV_PADDING_H@@", str(int(base_nav_padding_h * scale_factor)))
    
    return stylesheet

# === YENİ FUNKSİYA BURADADIR ===
def get_scaled_icon_size(base_size=24):
    """
    Yadda saxlanılan miqyas faktoruna əsasən
    dinamik ikon ölçüsü (QSize) qaytarır.
    """
    scale = load_zoom_setting()
    scaled_size = int(base_size * scale)
    return QSize(scaled_size, scaled_size)

# --- Stilin Tətbiq Edilməsi ---

def apply_app_style():
    """Yadda saxlanılan ayarları oxuyur və proqrama tətbiq edir."""
    app = QApplication.instance()
    if not app:
        return
    
    theme = load_theme_setting()
    scale = load_zoom_setting()
    
    final_stylesheet = generate_stylesheet(theme, scale)
    app.setStyleSheet(final_stylesheet)

    # İkonların mövzu yolunu təyin etmək
    QIcon.setThemeSearchPaths(QIcon.themeSearchPaths() + ['./icons'])
    QIcon.setThemeName('default')