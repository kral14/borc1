# ui_mal_form.py
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MalForm(object):
    def setupUi(self, MalForm):
        MalForm.setObjectName("MalForm")
        MalForm.resize(450, 450)
        MalForm.setStyleSheet("""
            QWidget { background-color: #3C3C3C; color: white; }
            QLabel { font-size: 11pt; }
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
                background-color: #555555; border: 1px solid #666666; padding: 5px; border-radius: 5px; font-size: 11pt;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: url(down_arrow.png); } /* Gələcəkdə ikon əlavə etmək olar */
            QPushButton {
                color: white; background-color: #007BFF; border: 1px solid #666666;
                padding: 8px; border-radius: 8px; font-size: 11pt; font-weight: bold;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton#btn_cancel { background-color: #6c757d; }
            QPushButton#btn_cancel:hover { background-color: #5a6268; }
        """)
        self.verticalLayout = QtWidgets.QVBoxLayout(MalForm)
        self.formLayout = QtWidgets.QFormLayout()
        
        self.label_name = QtWidgets.QLabel("Malın Adı:", MalForm)
        self.edit_name = QtWidgets.QLineEdit(MalForm)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_name)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_name)

        self.label_barcode = QtWidgets.QLabel("Barkodu:", MalForm)
        self.edit_barcode = QtWidgets.QLineEdit(MalForm)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_barcode)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_barcode)

        self.label_category = QtWidgets.QLabel("Cinsi/Kateqoriyası:", MalForm)
        self.edit_category = QtWidgets.QLineEdit(MalForm)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_category)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_category)

        self.label_supplier = QtWidgets.QLabel("Alındığı Yer (Satıcı):", MalForm)
        self.combo_supplier = QtWidgets.QComboBox(MalForm)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_supplier)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.combo_supplier)

        self.label_code = QtWidgets.QLabel("Kodu:", MalForm)
        self.edit_code = QtWidgets.QLineEdit(MalForm)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_code)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_code)

        self.label_article = QtWidgets.QLabel("Artikul:", MalForm)
        self.edit_article = QtWidgets.QLineEdit(MalForm)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_article)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edit_article)
        
        self.label_purchase_price = QtWidgets.QLabel("Alış Qiyməti (AZN):", MalForm)
        self.spin_purchase_price = QtWidgets.QDoubleSpinBox(MalForm)
        self.spin_purchase_price.setMaximum(999999.99)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_purchase_price)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.FieldRole, self.spin_purchase_price)
        
        self.label_sale_price = QtWidgets.QLabel("Satış Qiyməti (AZN):", MalForm)
        self.spin_sale_price = QtWidgets.QDoubleSpinBox(MalForm)
        self.spin_sale_price.setMaximum(999999.99)
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_sale_price)
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.FieldRole, self.spin_sale_price)

        self.label_stock = QtWidgets.QLabel("Stok Qalıq:", MalForm)
        self.spin_stock = QtWidgets.QSpinBox(MalForm)
        self.spin_stock.setMaximum(999999)
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_stock)
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.ItemRole.FieldRole, self.spin_stock)

        self.verticalLayout.addLayout(self.formLayout)
        
        self.buttonBox = QtWidgets.QHBoxLayout()
        self.btn_save = QtWidgets.QPushButton("Yadda Saxla")
        self.btn_cancel = QtWidgets.QPushButton("Ləğv Et")
        self.btn_cancel.setObjectName("btn_cancel")
        self.buttonBox.addStretch()
        self.buttonBox.addWidget(self.btn_cancel)
        self.buttonBox.addWidget(self.btn_save)
        
        self.verticalLayout.addLayout(self.buttonBox)
        
    def retranslateUi(self, MalForm):
        MalForm.setWindowTitle("Mal Məlumatları")