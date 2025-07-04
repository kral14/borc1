# theme_manager.py

import os
from PyQt5.QtWidgets import QApplication

class ThemeManager:
    def __init__(self, app):
        self.app = app
        # Stil fayllarının yerləşdiyi qovluğun yolu
        self.styles_dir = os.path.join(os.path.dirname(__file__), 'styles')
        self.themes = {
            "light": os.path.join(self.styles_dir, 'light.qss'),
            "dark": os.path.join(self.styles_dir, 'dark.qss')
        }
        self.current_theme = 'light' # Başlanğıc tema

    def load_stylesheet(self, theme_name):
        """Stil faylını oxuyur və məzmununu qaytarır."""
        path = self.themes.get(theme_name)
        if path and os.path.exists(path):
            with open(path, "r", encoding='utf-8') as file:
                return file.read()
        print(f"Stil faylı tapılmadı və ya səhvdir: {path}")
        return ""

    def apply_theme(self, theme_name):
        """Seçilmiş temanı tətbiq edir."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            stylesheet = self.load_stylesheet(theme_name)
            self.app.setStyleSheet(stylesheet)
            # Tətbiq olunduqdan sonra bütün pəncərələrin yenilənməsi üçün siqnal göndərə bilərik
            self.app.paletteChanged.emit(self.app.palette())
        else:
            print(f"Tema tapılmadı: {theme_name}")
            
    def get_current_theme(self):
        return self.current_theme