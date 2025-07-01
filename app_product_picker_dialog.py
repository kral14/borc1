# app_product_picker_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QTableWidget, QPushButton, QMessageBox,
                             QDialogButtonBox, QAbstractItemView, QHeaderView, QTableWidgetItem)
from PyQt6.QtCore import pyqtSignal, Qt
import database

class ProductPickerDialog(QDialog):
    product_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Məhsul Seçin")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QDialog { background-color: #3C3C3C; color: white; }
            QLineEdit { background-color: #555555; border: 1px solid #666666; padding: 5px; border-radius: 5px; }
            QTableWidget { background-color: #3C3C3C; alternate-background-color: #464646; gridline-color: #5A5A5A; }
            QHeaderView::section { background-color: #555555; padding: 5px; border: 1px solid #666666; font-weight: bold; }
            QPushButton { padding: 8px 16px; background-color: #007BFF; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #0056b3; }
        """)

        layout = QVBoxLayout(self)

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Məhsulun adı, kodu və ya barkoduna görə axtar...")
        self.search_box.textChanged.connect(self.filter_products)
        layout.addWidget(self.search_box)

        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Adı", "Barkod", "Alış Qiyməti", "Satış Qiyməti", "Stok Qalığı"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.hideColumn(0)
        self.table.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.table)
        
        button_box = QDialogButtonBox(self)
        self.select_button = QPushButton("Seç")
        button_box.addButton(self.select_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.load_products()

    def load_products(self):
        self.products = database.get_all_products()
        self.table.setRowCount(0)
        for row, product in enumerate(self.products):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.table.setItem(row, 2, QTableWidgetItem(product['barcode']))
            self.table.setItem(row, 3, QTableWidgetItem(f"{product['purchase_price']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{product['sale_price']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(str(product['stock'])))

    def filter_products(self):
        search_text = self.search_box.text().lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            barcode_item = self.table.item(row, 2)
            match = (search_text in name_item.text().lower() or
                     (barcode_item and search_text in barcode_item.text().lower()))
            self.table.setRowHidden(row, not match)
            
    def accept_selection(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa bir məhsul seçin.")
            return
        
        product_id = int(self.table.item(selected_row, 0).text())
        selected_product = next((p for p in self.products if p['id'] == product_id), None)
        
        if selected_product:
            # DÜZƏLİŞ BURADADIR: 'DictRow' obyekti 'dict'-ə çevrilir
            self.product_selected.emit(dict(selected_product))
            self.accept()