# ui_musteri_form.py
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MusteriForm(object):
    def setupUi(self, MusteriForm):
        MusteriForm.setObjectName("MusteriForm")
        MusteriForm.resize(400, 300)
        MusteriForm.setStyleSheet("""
            QWidget {
                background-color: #3C3C3C;
                color: white;
            }
            QLabel {
                font-size: 11pt;
            }
            QLineEdit {
                background-color: #555555;
                border: 1px solid #666666;
                padding: 5px;
                border-radius: 5px;
                font-size: 11pt;
            }
            QPushButton {
                color: white;
                background-color: #007BFF;
                border: 1px solid #666666;
                padding: 8px;
                border-radius: 8px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton#btn_cancel {
                background-color: #6c757d;
            }
            QPushButton#btn_cancel:hover {
                background-color: #5a6268;
            }
        """)
        self.verticalLayout = QtWidgets.QVBoxLayout(MusteriForm)
        self.formLayout = QtWidgets.QFormLayout()
        
        self.label_name = QtWidgets.QLabel("Ad, Soyad:", MusteriForm)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_name)
        self.edit_name = QtWidgets.QLineEdit(MusteriForm)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_name)
        
        self.label_phone = QtWidgets.QLabel("Telefon:", MusteriForm)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_phone)
        self.edit_phone = QtWidgets.QLineEdit(MusteriForm)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_phone)
        
        self.label_address = QtWidgets.QLabel("Ünvan:", MusteriForm)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_address)
        self.edit_address = QtWidgets.QLineEdit(MusteriForm)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_address)
        
        self.verticalLayout.addLayout(self.formLayout)
        
        self.buttonBox = QtWidgets.QHBoxLayout()
        self.btn_save = QtWidgets.QPushButton("Yadda Saxla", MusteriForm)
        self.btn_cancel = QtWidgets.QPushButton("Ləğv Et", MusteriForm)
        self.btn_cancel.setObjectName("btn_cancel")
        self.buttonBox.addStretch()
        self.buttonBox.addWidget(self.btn_cancel)
        self.buttonBox.addWidget(self.btn_save)
        
        self.verticalLayout.addLayout(self.buttonBox)
        self.verticalLayout.addStretch()

        self.retranslateUi(MusteriForm)
        QtCore.QMetaObject.connectSlotsByName(MusteriForm)

    def retranslateUi(self, MusteriForm):
        _translate = QtCore.QCoreApplication.translate
        MusteriForm.setWindowTitle(_translate("MusteriForm", "Müştəri Məlumatları"))