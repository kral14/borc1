# app_kassa_mexaric_widget.py (Silmə, Filtrləmə və Yekun məbləğ ilə)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, 
                             QStackedWidget, QMessageBox, QAbstractItemView, QHeaderView, 
                             QStyle, QHBoxLayout, QLabel, QComboBox, QSizePolicy)
from PyQt6.QtGui import QAction, QFont, QColor
from PyQt6.QtCore import pyqtSignal, QSize, Qt

import database
from ui_kassa_mexaric_form import Ui_KassaMexaricForm

class KassaMexaricFormWidget(QWidget):
    # ... (Bu sinifdə dəyişiklik yoxdur) ...
    form_closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.ui = Ui_KassaMexaricForm()
        self.ui.setupUi(self)
        self.ui.btn_save.clicked.connect(self.save_expense)
        self.ui.btn_cancel.clicked.connect(self.form_closed.emit)
        self.ui.combo_supplier.currentIndexChanged.connect(self.on_supplier_selected)
        self.ui.combo_invoice.currentIndexChanged.connect(self.on_invoice_selected)
    def start_new_expense(self):
        self.ui.combo_supplier.clear()
        self.ui.combo_supplier.addItem("Tədarükçü seçin...", None)
        suppliers = database.get_all_suppliers()
        for sup in suppliers:
            if sup['total_debt'] > 0:
                self.ui.combo_supplier.addItem(f"{sup['name']} (Borcumuz: {sup['total_debt']:.2f} AZN)", sup['id'])
        self.ui.combo_invoice.clear()
        self.ui.spin_amount.setValue(0)
        self.ui.edit_notes.clear()
    def on_supplier_selected(self, index):
        self.ui.combo_invoice.clear()
        supplier_id = self.ui.combo_supplier.currentData()
        if supplier_id:
            invoices = database.get_unpaid_purchase_invoices_for_supplier(supplier_id)
            self.ui.combo_invoice.addItem("Alış qaiməsini seçin...", None)
            for inv in invoices:
                self.ui.combo_invoice.addItem(f"{inv['invoice_number']} (Qalıq borc: {inv['remaining_debt']:.2f} AZN)", inv)
    def on_invoice_selected(self, index):
        invoice_data = self.ui.combo_invoice.currentData()
        if invoice_data:
            self.ui.spin_amount.setValue(invoice_data['remaining_debt'])
            self.ui.spin_amount.setMaximum(invoice_data['remaining_debt'])
            self.ui.edit_notes.setText(f"'{invoice_data['invoice_number']}' nömrəli qaimə üzrə ödəniş.")
        else:
            self.ui.spin_amount.setValue(0)
            self.ui.spin_amount.setMaximum(999999.99)
    def save_expense(self):
        supplier_id = self.ui.combo_supplier.currentData()
        invoice_data = self.ui.combo_invoice.currentData()
        amount = self.ui.spin_amount.value()
        expense_date = self.ui.date_edit.date().toString("yyyy-MM-dd")
        description = self.ui.edit_notes.toPlainText()
        if not supplier_id or not invoice_data:
            QMessageBox.warning(self, "Xəta", "Tədarükçü və alış qaiməsi seçilməlidir.")
            return
        if amount <= 0:
            QMessageBox.warning(self, "Xəta", "Məxaric məbləği 0-dan böyük olmalıdır.")
            return
        success = database.add_supplier_payment(supplier_id, invoice_data['id'], amount, expense_date, description)
        if success:
            QMessageBox.information(self, "Uğurlu", "Məxaric uğurla qeydə alındı.")
            self.form_closed.emit()
        else:
            QMessageBox.critical(self, "Xəta", "Məxaric zamanı xəta baş verdi.")

class KassaMexaricListWidget(QWidget):
    def __init__(self, stacked_widget, form_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.form_widget = form_widget
        layout = QVBoxLayout(self)
        
        # --- Toolbar və Filtrləmə ---
        top_bar_layout = QHBoxLayout()
        toolbar = QToolBar("Məxaric Əməliyyatları")
        top_bar_layout.addWidget(toolbar)

        style = self.style()
        self.action_add = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Yeni Məxaric", self)
        self.action_delete = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "Sil", self)
        toolbar.addAction(self.action_add)
        toolbar.addAction(self.action_delete)

        top_bar_layout.addStretch()
        top_bar_layout.addWidget(QLabel("Filtrlə:"))
        self.combo_supplier_filter = QComboBox()
        self.combo_supplier_filter.setMinimumWidth(250)
        top_bar_layout.addWidget(self.combo_supplier_filter)
        layout.addLayout(top_bar_layout)
        
        # --- Cədvəl ---
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Tarix", "Tədarükçü", "Qaimə №", "Məbləğ", "Təsvir/Qeyd"])
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table_widget.hideColumn(0)

        # --- Yekun Məlumatlar ---
        summary_layout = QHBoxLayout()
        summary_layout.addStretch()
        self.label_total_expense = QLabel("Cəmi Məxaric: 0.00 AZN")
        self.label_total_expense.setStyleSheet("font-weight: bold; font-size: 12pt;")
        summary_layout.addWidget(self.label_total_expense)
        layout.addLayout(summary_layout)

        self.action_add.triggered.connect(self.add_new_expense)
        self.action_delete.triggered.connect(self.delete_expense)
        self.combo_supplier_filter.currentIndexChanged.connect(self.filter_list)
        
        self.populate_filter_combo()
        self.load_expenses()

    def populate_filter_combo(self):
        self.combo_supplier_filter.blockSignals(True)
        self.combo_supplier_filter.clear()
        self.combo_supplier_filter.addItem("Bütün Tədarükçülər", None)
        suppliers = database.get_all_suppliers()
        for sup in suppliers:
            self.combo_supplier_filter.addItem(sup['name'], sup['id'])
        self.combo_supplier_filter.blockSignals(False)

    def filter_list(self):
        supplier_id = self.combo_supplier_filter.currentData()
        self.load_expenses(supplier_id)

    def load_expenses(self, supplier_id=None):
        self.table_widget.setRowCount(0)
        expenses = database.get_all_cash_expenses(supplier_id)
        total_expense = 0

        if not expenses: 
            self.label_total_expense.setText("Cəmi Məxaric: 0.00 AZN")
            return
            
        for row, expense in enumerate(expenses):
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(expense['id'])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(expense['expense_date'].strftime('%d-%m-%Y')))
            self.table_widget.setItem(row, 2, QTableWidgetItem(expense['supplier_name'] or 'Ümumi xərc'))
            self.table_widget.setItem(row, 3, QTableWidgetItem(expense['invoice_number'] or '-'))
            
            amount_item = QTableWidgetItem(f"{expense['amount']:.2f} AZN")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_widget.setItem(row, 4, amount_item)
            
            self.table_widget.setItem(row, 5, QTableWidgetItem(expense['description']))
            
            total_expense += expense['amount']
        
        self.label_total_expense.setText(f"Cəmi Məxaric: {total_expense:.2f} AZN")

    def delete_expense(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Xəbərdarlıq", "Silmək üçün bir məxaric seçin.")
            return

        expense_id = int(self.table_widget.item(selected_row, 0).text())
        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', 
                                     "Bu məxarici silməyə əminsinizmi? Bu əməliyyat tədarükçüyə olan borcunuzu geri artıracaq.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_supplier_payment(expense_id):
                QMessageBox.information(self, "Uğurlu", "Məxaric silindi.")
                self.filter_list() # Cədvəli yenilə
            else:
                QMessageBox.critical(self, "Xəta", "Məxarici silmək mümkün olmadı.")

    def add_new_expense(self):
        self.form_widget.start_new_expense()
        self.stacked_widget.setCurrentWidget(self.form_widget)
            
class KassaMexaricManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.form_widget = KassaMexaricFormWidget()
        self.list_widget = KassaMexaricListWidget(self.stacked_widget, self.form_widget)
        self.stacked_widget.addWidget(self.list_widget)
        self.stacked_widget.addWidget(self.form_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.stacked_widget)
        self.form_widget.form_closed.connect(self.show_list_and_refresh)
        
    def show_list_and_refresh(self):
        self.list_widget.populate_filter_combo()
        self.list_widget.load_expenses()
        self.stacked_widget.setCurrentWidget(self.list_widget)