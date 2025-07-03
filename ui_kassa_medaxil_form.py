# ui_kassa_medaxil_form.py (Yenilənmiş dizayn ilə)
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_KassaMedaxilForm(object):
    def setupUi(self, KassaMedaxilForm):
        KassaMedaxilForm.setObjectName("KassaMedaxilForm")
        KassaMedaxilForm.resize(550, 380) # Ölçü daha kompakt edildi
        KassaMedaxilForm.setStyleSheet("""
            QWidget {
                background-color: #3C3C3C;
                color: #e0e0e0;
                font-size: 11pt;
            }
            QGroupBox {
                background-color: #424242;
                border: 1px solid #555555;
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
            }
            QLabel {
                background-color: transparent;
                font-weight: normal;
            }
            QComboBox, QDateEdit, QDoubleSpinBox, QTextEdit {
                background-color: #555555;
                border: 1px solid #666666;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton {
                color: white;
                background-color: #007BFF;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
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
        
        self.verticalLayout = QtWidgets.QVBoxLayout(KassaMedaxilForm)
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        
        # Elementləri qruplaşdırırıq
        self.groupBox = QtWidgets.QGroupBox("Ödəniş Detalları", KassaMedaxilForm)
        self.verticalLayout.addWidget(self.groupBox)
        
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setContentsMargins(20, 20, 20, 20)
        self.formLayout.setVerticalSpacing(15)

        self.label_customer = QtWidgets.QLabel("Müştəri:", self.groupBox)
        self.combo_customer = QtWidgets.QComboBox(self.groupBox)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_customer)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.combo_customer)
        
        self.label_invoice = QtWidgets.QLabel("Ödənilən Qaimə:", self.groupBox)
        self.combo_invoice = QtWidgets.QComboBox(self.groupBox)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_invoice)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.combo_invoice)

        self.label_date = QtWidgets.QLabel("Ödəniş Tarixi:", self.groupBox)
        self.date_edit = QtWidgets.QDateEdit(self.groupBox)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_date)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.date_edit)

        self.label_amount = QtWidgets.QLabel("Məbləğ (AZN):", self.groupBox)
        self.spin_amount = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.spin_amount.setMaximum(999999.99)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_amount)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.spin_amount)

        self.label_notes = QtWidgets.QLabel("Qeyd:", self.groupBox)
        self.edit_notes = QtWidgets.QTextEdit(self.groupBox)
        self.edit_notes.setFixedHeight(60)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_notes)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_notes)

        # Düymələri sağa çəkirik
        self.buttonBox = QtWidgets.QHBoxLayout()
        self.buttonBox.addStretch(1) # Boşluq əlavə edirik
        
        self.btn_cancel = QtWidgets.QPushButton("Ləğv Et", KassaMedaxilForm)
        self.btn_cancel.setObjectName("btn_cancel")
        self.buttonBox.addWidget(self.btn_cancel)
        
        self.btn_save = QtWidgets.QPushButton("Yadda Saxla", KassaMedaxilForm)
        self.buttonBox.addWidget(self.btn_save)
        
        self.verticalLayout.addStretch(1) # Formanı yuxarıda saxlayır
        self.verticalLayout.addLayout(self.buttonBox)

        # İkonları təyin edirik
        style = KassaMedaxilForm.style()
        self.btn_cancel.setIcon(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogCancelButton))
        self.btn_save.setIcon(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton))

        self.retranslateUi(KassaMedaxilForm)
        QtCore.QMetaObject.connectSlotsByName(KassaMedaxilForm)

    def retranslateUi(self, KassaMedaxilForm):
        _translate = QtCore.QCoreApplication.translate
        KassaMedaxilForm.setWindowTitle(_translate("KassaMedaxilForm", "Kassa Mədaxil Əməliyyatı"))