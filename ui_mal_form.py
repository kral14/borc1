# borc/ui_mal_form.py
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MalForm(object):
    def setupUi(self, MalForm):
        MalForm.setObjectName("MalForm")
        MalForm.resize(850, 700)
        MalForm.setStyleSheet("""
            QWidget {
                color: #e0e0e0;
                background-color: #2c2c2c;
                font-size: 11pt;
            }
            QGroupBox {
                background-color: #383838;
                border: 1px solid #555555;
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #555555;
                border-radius: 4px;
            }
            QLabel {
                background-color: transparent;
                font-weight: normal;
            }
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit {
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #4a4a4a;
            }
            QTabWidget::pane {
                border-top: 2px solid #555555;
            }
            QTabBar::tab {
                background: #383838;
                border: 1px solid #555555;
                border-bottom-color: #2c2c2c;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
                padding: 10px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #4a4a4a;
            }
            QTabBar::tab:selected {
                border-color: #777777;
                border-bottom-color: #4a4a4a;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
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

        self.verticalLayout = QtWidgets.QVBoxLayout(MalForm)
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout.setSpacing(15)

        self.tabWidget = QtWidgets.QTabWidget(MalForm)
        self.verticalLayout.addWidget(self.tabWidget)

        # Tab 1: Əsas Məlumatlar
        self.tab_main = QtWidgets.QWidget()
        self.tabWidget.addTab(self.tab_main, "Əsas Məlumatlar")
        self.formLayout_main = QtWidgets.QFormLayout(self.tab_main)
        
        self.label_name = QtWidgets.QLabel("Malın Adı:", self.tab_main)
        self.edit_name = QtWidgets.QLineEdit(self.tab_main)
        self.formLayout_main.addRow(self.label_name, self.edit_name)

        self.label_category = QtWidgets.QLabel("Kateqoriya:", self.tab_main)
        self.combo_category = QtWidgets.QComboBox(self.tab_main)
        self.formLayout_main.addRow(self.label_category, self.combo_category)

        self.label_supplier = QtWidgets.QLabel("Satıcı:", self.tab_main)
        self.combo_supplier = QtWidgets.QComboBox(self.tab_main)
        self.formLayout_main.addRow(self.label_supplier, self.combo_supplier)

        self.label_is_food = QtWidgets.QLabel("Məhsul Növü:", self.tab_main)
        self.combo_is_food = QtWidgets.QComboBox(self.tab_main)
        self.combo_is_food.addItems(["Qida", "Qeyri-Qida"])
        self.formLayout_main.addRow(self.label_is_food, self.combo_is_food)
        
        self.label_article = QtWidgets.QLabel("Artikul:", self.tab_main)
        self.edit_article = QtWidgets.QLineEdit(self.tab_main)
        self.formLayout_main.addRow(self.label_article, self.edit_article)
        
        self.label_code = QtWidgets.QLabel("Kodu:", self.tab_main)
        self.edit_code = QtWidgets.QLineEdit(self.tab_main)
        self.formLayout_main.addRow(self.label_code, self.edit_code)

        # Tab 2: Anbar və Miqdar
        self.tab_stock = QtWidgets.QWidget()
        self.tabWidget.addTab(self.tab_stock, "Anbar və Miqdar")
        self.layout_stock_tab = QtWidgets.QVBoxLayout(self.tab_stock)

        group_conversion = QtWidgets.QGroupBox("Miqdar Çevrilməsi")
        formLayout_conversion = QtWidgets.QFormLayout(group_conversion)
        self.label_pieces_in_block = QtWidgets.QLabel("Blokdakı ədəd sayı:", group_conversion)
        self.spin_pieces_in_block = QtWidgets.QSpinBox(group_conversion)
        self.spin_pieces_in_block.setMaximum(9999)
        formLayout_conversion.addRow(self.label_pieces_in_block, self.spin_pieces_in_block)
        self.label_pieces_in_box = QtWidgets.QLabel("Qutudakı ədəd sayı:", group_conversion)
        self.spin_pieces_in_box = QtWidgets.QSpinBox(group_conversion)
        self.spin_pieces_in_box.setMaximum(99999)
        formLayout_conversion.addRow(self.label_pieces_in_box, self.spin_pieces_in_box)
        self.layout_stock_tab.addWidget(group_conversion)

        group_location = QtWidgets.QGroupBox("Anbar Məlumatı")
        formLayout_location = QtWidgets.QFormLayout(group_location)
        self.label_warehouse = QtWidgets.QLabel("Anbar:", group_location)
        self.edit_warehouse = QtWidgets.QLineEdit(group_location)
        formLayout_location.addRow(self.label_warehouse, self.edit_warehouse)
        self.label_shelf = QtWidgets.QLabel("Rəf:", group_location)
        self.edit_shelf = QtWidgets.QLineEdit(group_location)
        formLayout_location.addRow(self.label_shelf, self.edit_shelf)
        self.label_row = QtWidgets.QLabel("Sıra:", group_location)
        self.edit_row = QtWidgets.QLineEdit(group_location)
        formLayout_location.addRow(self.label_row, self.edit_row)
        self.layout_stock_tab.addWidget(group_location)
        
        group_stock = QtWidgets.QGroupBox("Mövcud Qalıq")
        formLayout_stock_main = QtWidgets.QFormLayout(group_stock)
        self.label_stock = QtWidgets.QLabel("Əsas Vahidlə Stok (ədəd):", group_stock)
        self.spin_stock = QtWidgets.QSpinBox(group_stock)
        self.spin_stock.setMaximum(999999)
        formLayout_stock_main.addRow(self.label_stock, self.spin_stock)
        self.layout_stock_tab.addWidget(group_stock)
        self.layout_stock_tab.addStretch()

        # Tab 3: Barkodlar
        self.tab_barcodes = QtWidgets.QWidget()
        self.tabWidget.addTab(self.tab_barcodes, "Barkodlar")
        self.formLayout_barcodes = QtWidgets.QFormLayout(self.tab_barcodes)
        
        self.label_barcode_unit = QtWidgets.QLabel("Ədəd Barkodu:", self.tab_barcodes)
        self.edit_barcode_unit = QtWidgets.QLineEdit(self.tab_barcodes)
        self.formLayout_barcodes.addRow(self.label_barcode_unit, self.edit_barcode_unit)
        
        self.label_barcode_block = QtWidgets.QLabel("Blok Barkodu:", self.tab_barcodes)
        self.edit_barcode_block = QtWidgets.QLineEdit(self.tab_barcodes)
        self.formLayout_barcodes.addRow(self.label_barcode_block, self.edit_barcode_block)
        
        self.label_barcode_box = QtWidgets.QLabel("Qutu Barkodu:", self.tab_barcodes)
        self.edit_barcode_box = QtWidgets.QLineEdit(self.tab_barcodes)
        self.formLayout_barcodes.addRow(self.label_barcode_box, self.edit_barcode_box)

        # Tab 4: Tarixçə və Qiymət
        self.tab_price_date = QtWidgets.QWidget()
        self.tabWidget.addTab(self.tab_price_date, "Tarixçə və Qiymət")
        self.layout_price_tab = QtWidgets.QVBoxLayout(self.tab_price_date)
        
        group_dates = QtWidgets.QGroupBox("Tarixçə")
        formLayout_dates = QtWidgets.QFormLayout(group_dates)
        self.label_prod_date = QtWidgets.QLabel("İstehsal Tarixi:", group_dates)
        self.date_prod = QtWidgets.QDateEdit(group_dates)
        self.date_prod.setCalendarPopup(True)
        self.date_prod.setDisplayFormat("dd.MM.yyyy")
        formLayout_dates.addRow(self.label_prod_date, self.date_prod)
        self.label_exp_date = QtWidgets.QLabel("Son İstifadə Tarixi:", group_dates)
        self.date_exp = QtWidgets.QDateEdit(group_dates)
        self.date_exp.setCalendarPopup(True)
        self.date_exp.setDisplayFormat("dd.MM.yyyy")
        formLayout_dates.addRow(self.label_exp_date, self.date_exp)
        self.label_shelf_life = QtWidgets.QLabel("Yararlılıq müddəti:", group_dates)
        self.label_shelf_life_value = QtWidgets.QLabel("Hesablanır...", group_dates)
        font = self.label_shelf_life_value.font(); font.setBold(True); self.label_shelf_life_value.setFont(font)
        formLayout_dates.addRow(self.label_shelf_life, self.label_shelf_life_value)
        self.layout_price_tab.addWidget(group_dates)
        
        group_pricing = QtWidgets.QGroupBox("Qiymət")
        formLayout_pricing = QtWidgets.QFormLayout(group_pricing)
        self.label_purchase_price = QtWidgets.QLabel("Alış Qiyməti (AZN):", group_pricing)
        self.spin_purchase_price = QtWidgets.QDoubleSpinBox(group_pricing)
        self.spin_purchase_price.setMaximum(999999.99)
        formLayout_pricing.addRow(self.label_purchase_price, self.spin_purchase_price)
        self.label_sale_price = QtWidgets.QLabel("Satış Qiyməti (AZN):", group_pricing)
        self.spin_sale_price = QtWidgets.QDoubleSpinBox(group_pricing)
        self.spin_sale_price.setMaximum(999999.99)
        formLayout_pricing.addRow(self.label_sale_price, self.spin_sale_price)
        self.label_uom = QtWidgets.QLabel("Ölçü Vahidi:", group_pricing)
        self.combo_uom = QtWidgets.QComboBox(group_pricing)
        self.combo_uom.addItems(["ədəd", "qutu", "blok", "kq", "qram", "metr", "litr"])
        formLayout_pricing.addRow(self.label_uom, self.combo_uom)
        self.layout_price_tab.addWidget(group_pricing)
        self.layout_price_tab.addStretch()

        # Tab 5: Xüsusi Sahələr
        self.tab_custom = QtWidgets.QWidget()
        self.tabWidget.addTab(self.tab_custom, "Xüsusi Sahələr")
        self.custom_fields_layout = QtWidgets.QFormLayout(self.tab_custom)

        # DÜYMƏLƏR ÜÇÜN DÜZƏLİŞ EDİLMİŞ HİSSƏ
        self.buttonBox = QtWidgets.QHBoxLayout()
        self.buttonBox.addStretch(1) 
        self.btn_cancel = QtWidgets.QPushButton("Ləğv Et", MalForm)
        self.btn_cancel.setObjectName("btn_cancel")
        self.buttonBox.addWidget(self.btn_cancel) # DÜZGÜN METOD
        self.btn_save = QtWidgets.QPushButton("Yadda Saxla", MalForm)
        self.buttonBox.addWidget(self.btn_save) # DÜZGÜN METOD
        self.verticalLayout.addLayout(self.buttonBox)

        self.retranslateUi(MalForm)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MalForm)

    def retranslateUi(self, MalForm):
        _translate = QtCore.QCoreApplication.translate
        MalForm.setWindowTitle(_translate("MalForm", "Mal Məlumatları"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_main), _translate("MalForm", "Əsas Məlumatlar"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_stock), _translate("MalForm", "Anbar və Miqdar"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_barcodes), _translate("MalForm", "Barkodlar"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_price_date), _translate("MalForm", "Tarixçə və Qiymət"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_custom), _translate("MalForm", "Xüsusi Sahələr"))