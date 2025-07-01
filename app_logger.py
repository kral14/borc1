from PyQt6.QtCore import QObject, pyqtSignal

class AppLogger(QObject):
    # Yeni mesaj gəldikdə bu siqnal işə düşəcək
    message_logged = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def log(self, message):
        print(f"[LOG] {message}") # Ehtiyat üçün terminala da yazırıq
        self.message_logged.emit(message)

# Proqramın hər yerindən çağıra biləcəyimiz tək bir logger instansiyası
logger = AppLogger()