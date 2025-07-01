from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtGui import QFont
from app_logger import logger # Global logger-i import edirik

class LoggerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Proses Gedişatı (Log)")
        
        layout = QVBoxLayout(self)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        font = QFont("Courier New", 10)
        self.log_display.setFont(font)
        self.log_display.setStyleSheet("background-color: #2E2E2E; color: #FFFFFF; border: 1px solid #555;")
        
        clear_button = QPushButton("Təmizlə")
        clear_button.clicked.connect(self.log_display.clear)

        layout.addWidget(self.log_display)
        layout.addWidget(clear_button)

        # Global logger-in siqnalını bu pəncərədəki funksiyaya bağlayırıq
        logger.message_logged.connect(self.add_message)

    def add_message(self, message):
        """Yeni log mesajını pəncərəyə əlavə edir."""
        self.log_display.append(message)