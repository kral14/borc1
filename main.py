# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
import traceback
from main_app_window import MainAppWindow
import database

# --- YENI: Proqramın çökməsinin qarşısını alan funksiya ---
def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Bu funksiya tutulmamış bütün xətaları idarə edir.
    Proqramın çökməsi əvəzinə ekranda xəta mesajı göstərir.
    """
    # Xətanın detallarını formatlaşdırır
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # İstifadəçiyə göstəriləcək pəncərə
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setText("Gözlənilməyən xəta baş verdi!")
    msg_box.setInformativeText("Xəta haqqında detallı məlumat aşağıdadır.")
    msg_box.setDetailedText(error_msg)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()

# Xəta idarəetmə funksiyasını sistemə bağlayır
sys.excepthook = handle_exception

def main():
    print("Verilənlər bazası cədvəlləri yoxlanılır...")
    database.create_tables() # Paketdən funksiyanı çağırırıq
    print("Yoxlama tamamlandı.")
    
    app = QApplication(sys.argv)
    window = MainAppWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()