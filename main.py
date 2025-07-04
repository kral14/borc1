# borc/main.py

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
import traceback
from main_app_window import MainAppWindow
import database
import style_manager

def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Bu funksiya tutulmamış bütün xətaları idarə edir.
    Proqramın çökməsi əvəzinə ekranda xəta mesajı göstərir.
    """
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setText("Gözlənilməyən xəta baş verdi!")
    msg_box.setInformativeText("Xəta haqqında detallı məlumat aşağıdadır.")
    msg_box.setDetailedText(error_msg)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()

sys.excepthook = handle_exception

def main():
    app = QApplication(sys.argv)
    
    style_manager.apply_app_style()

    app.setApplicationName("AnbarSmarte")
    app.setWindowIcon(QIcon("./icons/app_icon.png"))

    print("Verilənlər bazası yoxlanılır...")
    database.create_tables()
    database.create_indexes()
    print("Yoxlama tamamlandı.")
    
    window = MainAppWindow()
    
    # Əsas pəncərəni qlobal olaraq əlçatan edirik
    app.setProperty("main_window", window)
    
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()