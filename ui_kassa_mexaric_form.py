# ui_kassa_mexaric_form.py
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_KassaMexaricForm(object):
    def setupUi(self, KassaMexaricForm):
        KassaMexaricForm.setObjectName("KassaMexaricForm")
        KassaMexaricForm.resize(550, 380)
        KassaMexaricForm.setStyleSheet("""
            # ... (ui_kassa_medaxil_form.py-dakı stil kodunun eynisi) ...
        """)

        self.verticalLayout = QtWidgets.QVBoxLayout(KassaMexaricForm)
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        self.groupBox = QtWidgets.QGroupBox("Məxaric Detalları", KassaMexaricForm)
        self.verticalLayout.addWidget(self.groupBox)
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setContentsMargins(20, 20, 20, 20)
        self.formLayout.setVerticalSpacing(15)

        self.label_supplier = QtWidgets.QLabel("Tədarükçü (Satıcı):", self.groupBox)
        self.combo_supplier = QtWidgets.QComboBox(self.groupBox)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_supplier)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.combo_supplier)

        self.label_invoice = QtWidgets.QLabel("Ödənilən Alış Qaiməsi:", self.groupBox)
        self.combo_invoice = QtWidgets.QComboBox(self.groupBox)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_invoice)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.combo_invoice)

        self.label_date = QtWidgets.QLabel("Məxaric Tarixi:", self.groupBox)
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

        self.label_notes = QtWidgets.QLabel("Təsvir/Qeyd:", self.groupBox)
        self.edit_notes = QtWidgets.QTextEdit(self.groupBox)
        self.edit_notes.setFixedHeight(60)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_notes)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_notes)

        self.buttonBox = QtWidgets.QHBoxLayout()
        self.buttonBox.addStretch(1)
        self.btn_cancel = QtWidgets.QPushButton("Ləğv Et", KassaMexaricForm)
        self.buttonBox.addWidget(self.btn_cancel)
        self.btn_save = QtWidgets.QPushButton("Yadda Saxla", KassaMexaricForm)
        self.buttonBox.addWidget(self.btn_save)
        self.verticalLayout.addStretch(1)
        self.verticalLayout.addLayout(self.buttonBox)

        style = KassaMexaricForm.style()
        self.btn_cancel.setIcon(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogCancelButton))
        self.btn_save.setIcon(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton))

        self.retranslateUi(KassaMexaricForm)
        QtCore.QMetaObject.connectSlotsByName(KassaMexaricForm)

    def retranslateUi(self, KassaMexaricForm):
        _translate = QtCore.QCoreApplication.translate
        KassaMexaricForm.setWindowTitle(_translate("KassaMexaricForm", "Kassa Məxaric Əməliyyatı"))