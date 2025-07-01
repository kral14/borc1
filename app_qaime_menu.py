# app_qaime_menu.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

class QaimeMenuWidget(QWidget):
    alis_clicked = pyqtSignal()
    satis_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Əsas layout
        main_layout = QVBoxLayout(self)
        main_layout.addStretch(1) # Yuxarıdan boşluq

        # Düymələri saxlamaq üçün horizontal layout
        button_layout = QHBoxLayout()
        button_layout.addStretch(1) # Soldan boşluq

        # Düymələr üçün ümumi stil
        btn_style = """
            QPushButton {
                font-size: 22pt;
                font-weight: bold;
                padding: 40px;
                border-radius: 15px;
                background-color: #555555;
                color: white;
                min-width: 300px;
                min-height: 200px;
            }
            QPushButton:hover {
                background-color: #6E6E6E;
            }
        """

        # Alış Qaimələri düyməsi
        self.btn_alis = QPushButton("Alış\nQaimələri")
        self.btn_alis.setStyleSheet(btn_style)
        self.btn_alis.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.btn_alis.clicked.connect(self.alis_clicked.emit)
        button_layout.addWidget(self.btn_alis)

        # Satış Qaimələri düyməsi
        self.btn_satis = QPushButton("Satış\nQaimələri")
        self.btn_satis.setStyleSheet(btn_style)
        self.btn_satis.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.btn_satis.clicked.connect(self.satis_clicked.emit)
        button_layout.addWidget(self.btn_satis)

        button_layout.addStretch(1) # Sağdan boşluq
        main_layout.addLayout(button_layout)
        main_layout.addStretch(1) # Aşağıdan boşluq

        self.setLayout(main_layout)