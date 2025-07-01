# app_mal_widget.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, 
                             QStackedWidget, QMessageBox, QAbstractItemView, QHeaderView, QStyle, QToolButton)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, QSize, Qt

import database
from ui_mal_form import Ui_MalForm

# --- Mal Formasının Məntiqi ---
class MalFormWidget(QWidget):
    form_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_MalForm()
        self.ui.setupUi(self)
        self.current_product_id = None
        
        self.ui.btn_save.clicked.connect(self.save_product)
        self.ui.btn_cancel.clicked.connect(self.close_form)
        self.load_suppliers_to_combobox()

    def load_suppliers_to_combobox(self):
        self.ui.combo_supplier.clear()
        self.ui.combo_supplier.addItem("Satıcı seçin...", None) # Defolt seçim
        try:
            suppliers = database.get_all_suppliers()
            for supplier in suppliers:
                self.ui.combo_supplier.addItem(supplier['name'], supplier['id'])
        except Exception as e:
            print(f"Satıcıları yükləmək mümkün olmadı: {e}")

    def set_edit_mode(self, product_id):
        self.load_suppliers_to_combobox() # Form açılan kimi satıcıları yenilə
        self.current_product_id = product_id
        product = database.get_product_by_id(product_id)
        if product:
            self.ui.edit_name.setText(product['name'])
            self.ui.edit_barcode.setText(product['barcode'])
            self.ui.edit_category.setText(product['category'])
            self.ui.edit_code.setText(product['product_code'])
            self.ui.edit_article.setText(product['article'])
            self.ui.spin_purchase_price.setValue(product['purchase_price'] or 0)
            self.ui.spin_sale_price.setValue(product['sale_price'] or 0)
            self.ui.spin_stock.setValue(product['stock'] or 0)
            
            # Satıcını ComboBox-da seç
            supplier_id = product['supplier_id']
            if supplier_id:
                index = self.ui.combo_supplier.findData(supplier_id)
                if index != -1:
                    self.ui.combo_supplier.setCurrentIndex(index)

    def set_add_mode(self):
        self.load_suppliers_to_combobox() # Form açılan kimi satıcıları yenilə
        self.current_product_id = None
        self.ui.edit_name.clear()
        self.ui.edit_barcode.clear()
        self.ui.edit_category.clear()
        self.ui.edit_code.clear()
        self.ui.edit_article.clear()
        self.ui.spin_purchase_price.setValue(0)
        self.ui.spin_sale_price.setValue(0)
        self.ui.spin_stock.setValue(0)
        self.ui.combo_supplier.setCurrentIndex(0)

    def save_product(self):
        # Məlumatları formadan yığmaq
        name = self.ui.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Xəta", "Mal adı boş ola bilməz.")
            return

        barcode = self.ui.edit_barcode.text().strip()
        category = self.ui.edit_category.text().strip()
        product_code = self.ui.edit_code.text().strip()
        article = self.ui.edit_article.text().strip()
        purchase_price = self.ui.spin_purchase_price.value()
        sale_price = self.ui.spin_sale_price.value()
        stock = self.ui.spin_stock.value()
        
        supplier_id = self.ui.combo_supplier.currentData()

        # Baza əməliyyatları
        args = (name, barcode, product_code, article, category, supplier_id, purchase_price, sale_price, stock)
        if self.current_product_id is None:
            success = database.add_product(*args)
        else:
            success = database.update_product(self.current_product_id, *args)
        
        if success:
            QMessageBox.information(self, "Uğurlu", "Mal məlumatları yadda saxlanıldı.")
            self.close_form()
        else:
            QMessageBox.critical(self, "Xəta", "Əməliyyat zamanı xəta baş verdi.")

    def close_form(self):
        self.form_closed.emit()

# --- Mal Cədvəli və İdarəetmə Paneli ---
class MalListWidget(QWidget):
    def __init__(self, stacked_widget, form_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.form_widget = form_widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5); layout.setSpacing(10)
        
        toolbar = QToolBar("Mal Əməliyyatları")
        toolbar.setIconSize(QSize(32, 32)); toolbar.setStyleSheet("QToolBar { border: none; }")
        layout.addWidget(toolbar)
        
        style = self.style()
        self.action_add = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Yeni Mal", self)
        self.action_edit = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Düzəliş Et", self)
        self.action_delete = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "Sil", self)
        
        for action in [self.action_add, self.action_edit, self.action_delete]:
            tool_button = QToolButton(); tool_button.setDefaultAction(action)
            tool_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            tool_button.setStyleSheet("QToolButton{padding:5px;border:1px solid transparent;border-radius:5px} QToolButton:hover{background-color:#555555;border:1px solid #666666}")
            toolbar.addWidget(tool_button)

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Adı", "Barkod", "Kateqoriya", "Alındığı Yer", "Alış Qiyməti", "Satış Qiyməti", "Stok"])
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.table_widget.setStyleSheet("QTableWidget{background-color:#3C3C3C;alternate-background-color:#464646;gridline-color:#5A5A5A;color:#FFFFFF;border:1px solid #5A5A5A;font-size:11pt} QTableWidget::item{padding:5px} QHeaderView::section{background-color:#555555;color:#FFFFFF;padding:5px;border:1px solid #666666;font-weight:bold} QTableWidget::item:selected{background-color:#007BFF;color:white}")

        self.action_add.triggered.connect(self.add_new_product)
        self.action_edit.triggered.connect(self.edit_product)
        self.action_delete.triggered.connect(self.delete_product)
        
        self.load_products()

    def load_products(self):
        self.table_widget.setRowCount(0)
        try: products = database.get_all_products()
        except Exception as e:
            QMessageBox.critical(self, "Baza Xətası", f"Mal məlumatlarını yükləmək mümkün olmadı:\n{e}"); products = []
        if products:
            for row, p in enumerate(products):
                self.table_widget.insertRow(row)
                self.table_widget.setItem(row, 0, QTableWidgetItem(str(p['id'])))
                self.table_widget.setItem(row, 1, QTableWidgetItem(p['name']))
                self.table_widget.setItem(row, 2, QTableWidgetItem(p['barcode']))
                self.table_widget.setItem(row, 3, QTableWidgetItem(p['category']))
                self.table_widget.setItem(row, 4, QTableWidgetItem(p['supplier_name']))
                self.table_widget.setItem(row, 5, QTableWidgetItem(f"{p['purchase_price']:.2f} AZN"))
                self.table_widget.setItem(row, 6, QTableWidgetItem(f"{p['sale_price']:.2f} AZN"))
                self.table_widget.setItem(row, 7, QTableWidgetItem(str(p['stock'])))
        self.table_widget.hideColumn(0)
        
    def add_new_product(self):
        self.form_widget.set_add_mode()
        self.stacked_widget.setCurrentWidget(self.form_widget)
        
    def edit_product(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, düzəliş etmək üçün bir mal seçin.")
            return
        product_id = int(self.table_widget.item(selected_row, 0).text())
        self.form_widget.set_edit_mode(product_id)
        self.stacked_widget.setCurrentWidget(self.form_widget)
        
    def delete_product(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, silmək üçün bir mal seçin.")
            return
        product_id = int(self.table_widget.item(selected_row, 0).text())
        product_name = self.table_widget.item(selected_row, 1).text()
        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', f"'{product_name}' adlı malı silməyə əminsinizmi?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_product(product_id): self.load_products(); QMessageBox.information(self, "Uğurlu", "Mal silindi.")
            else: QMessageBox.critical(self, "Xəta", "Malı silmək mümkün olmadı.")

# --- Əsas İdarəedici Widget ---
class MalManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.form_widget = MalFormWidget()
        self.list_widget = MalListWidget(self.stacked_widget, self.form_widget)
        self.stacked_widget.addWidget(self.list_widget); self.stacked_widget.addWidget(self.form_widget)
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0,0,0,0); main_layout.addWidget(self.stacked_widget)
        self.form_widget.form_closed.connect(self.show_list_and_refresh)
        
    def show_list_and_refresh(self):
        self.list_widget.load_products()
        self.stacked_widget.setCurrentWidget(self.list_widget)