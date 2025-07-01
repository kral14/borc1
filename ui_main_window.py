# ui_main_window.py
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        # Bütün pəncərə üçün tünd fon tətbiq edək
        MainWindow.setStyleSheet("background-color: #2E2E2E; color: white;")

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        
        # Sol tərəfdəki menyu üçün Frame
        self.menuFrame = QtWidgets.QFrame(parent=self.centralwidget)
        self.menuFrame.setMinimumSize(QtCore.QSize(200, 0))
        self.menuFrame.setMaximumSize(QtCore.QSize(250, 16777215))
        # Menyu arxa fonu bir az daha açıq rəngdə olsun
        self.menuFrame.setStyleSheet("background-color: #3C3C3C; border-radius: 10px;")
        self.menuFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.menuFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.menuFrame.setObjectName("menuFrame")
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.menuFrame)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10) # Kənarlardan boşluq
        self.verticalLayout.setSpacing(15) # Düymələr arası məsafə
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Ümumi düymə stili
        button_style = """
            QPushButton {
                color: white;
                background-color: #555555;
                border: 1px solid #666666;
                padding: 10px;
                border-radius: 8px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #6E6E6E;
            }
            QPushButton:pressed {
                background-color: #4A4A4A;
            }
        """
        
        # Düymələr
        self.btn_musteriler = QtWidgets.QPushButton("Müştərilər", parent=self.menuFrame)
        self.btn_musteriler.setStyleSheet(button_style)
        self.btn_musteriler.setMinimumHeight(40)
        self.verticalLayout.addWidget(self.btn_musteriler)
        
        self.btn_saticilar = QtWidgets.QPushButton("Satıcılar", parent=self.menuFrame)
        self.btn_saticilar.setStyleSheet(button_style)
        self.btn_saticilar.setMinimumHeight(40)
        self.verticalLayout.addWidget(self.btn_saticilar)
        
        self.btn_mallar = QtWidgets.QPushButton("Mallar", parent=self.menuFrame)
        self.btn_mallar.setStyleSheet(button_style)
        self.btn_mallar.setMinimumHeight(40)
        self.verticalLayout.addWidget(self.btn_mallar)
        
        self.btn_qaimeler = QtWidgets.QPushButton("Qaimələr", parent=self.menuFrame)
        self.btn_qaimeler.setStyleSheet(button_style)
        self.btn_qaimeler.setMinimumHeight(40)
        self.verticalLayout.addWidget(self.btn_qaimeler)

        self.verticalLayout.addStretch() # Düymələri yuxarıda saxlayır
        
        self.gridLayout.addWidget(self.menuFrame, 0, 0, 1, 1)
        
        # Sağ tərəfdəki əsas hissə
        self.mainContentFrame = QtWidgets.QFrame(parent=self.centralwidget)
        self.mainContentFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.mainContentFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.mainContentFrame.setObjectName("mainContentFrame")
        self.mainContentFrame.setStyleSheet("background-color: #2E2E2E; border: none;")
        
        self.contentLayout = QtWidgets.QVBoxLayout(self.mainContentFrame)
        self.contentLayout.setObjectName("contentLayout")
        
        self.label = QtWidgets.QLabel("Xoş Gəlmisiniz!\n\nƏməliyyat seçmək üçün soldakı menyudan istifadə edin.", parent=self.mainContentFrame)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 18pt; color: #CCCCCC;")
        self.contentLayout.addWidget(self.label)
        
        self.gridLayout.addWidget(self.mainContentFrame, 0, 1, 1, 1)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setStyleSheet("color: #CCCCCC;")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Borc İzləmə Sistemi"))