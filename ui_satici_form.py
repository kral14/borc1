# ui_satici_form.py
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_SaticiForm(object):
    def setupUi(self, SaticiForm):
        SaticiForm.setObjectName("SaticiForm")
        SaticiForm.resize(400, 300)
        SaticiForm.setStyleSheet("""
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
        self.verticalLayout = QtWidgets.QVBoxLayout(SaticiForm)
        self.formLayout = QtWidgets.QFormLayout()
        
        self.label_name = QtWidgets.QLabel("Satıcı Adı:", SaticiForm)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_name)
        self.edit_name = QtWidgets.QLineEdit(SaticiForm)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_name)
        
        self.label_contact = QtWidgets.QLabel("Əlaqədar şəxs:", SaticiForm)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_contact)
        self.edit_contact = QtWidgets.QLineEdit(SaticiForm)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_contact)

        self.label_phone = QtWidgets.QLabel("Telefon:", SaticiForm)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_phone)
        self.edit_phone = QtWidgets.QLineEdit(SaticiForm)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_phone)
        
        self.label_address = QtWidgets.QLabel("Ünvan:", SaticiForm)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_address)
        self.edit_address = QtWidgets.QLineEdit(SaticiForm)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_address)
        
        self.verticalLayout.addLayout(self.formLayout)
        
        self.buttonBox = QtWidgets.QHBoxLayout()
        self.btn_save = QtWidgets.QPushButton("Yadda Saxla", SaticiForm)
        self.btn_cancel = QtWidgets.QPushButton("Ləğv Et", SaticiForm)
        self.btn_cancel.setObjectName("btn_cancel")
        self.buttonBox.addStretch()
        self.buttonBox.addWidget(self.btn_cancel)
        self.buttonBox.addWidget(self.btn_save)
        
        self.verticalLayout.addLayout(self.buttonBox)
        self.verticalLayout.addStretch()

        self.retranslateUi(SaticiForm)
        QtCore.QMetaObject.connectSlotsByName(SaticiForm)

    def retranslateUi(self, SaticiForm):
        _translate = QtCore.QCoreApplication.translate
        SaticiForm.setWindowTitle(_translate("SaticiForm", "Satıcı Məlumatları"))