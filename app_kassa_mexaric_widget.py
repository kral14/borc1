# app_kassa_mexaric_widget.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, 
                             QStackedWidget, QMessageBox, QAbstractItemView, QHeaderView, QStyle, QToolButton)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, QSize, Qt

import database
from ui_kassa_mexaric_form import Ui_KassaMexaricForm

class KassaMexaricFormWidget(QWidget):
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
        toolbar = QToolBar("Məxaric Əməliyyatları")
        layout.addWidget(toolbar)
        self.action_add = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Yeni Məxaric", self)
        toolbar.addAction(self.action_add)
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Tarix", "Tədarükçü", "Qaimə №", "Məbləğ"])
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.hideColumn(0)
        self.action_add.triggered.connect(self.add_new_expense)
        self.load_expenses()

    def load_expenses(self):
        self.table_widget.setRowCount(0)
        expenses = database.get_all_cash_expenses()
        if not expenses: return
        for row, expense in enumerate(expenses):
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(expense['id'])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(expense['expense_date'].strftime('%d-%m-%Y')))
            self.table_widget.setItem(row, 2, QTableWidgetItem(expense['supplier_name'] or 'Ümumi xərc'))
            self.table_widget.setItem(row, 3, QTableWidgetItem(expense['invoice_number'] or '-'))
            self.table_widget.setItem(row, 4, QTableWidgetItem(f"{expense['amount']:.2f} AZN"))

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
        self.list_widget.load_expenses()
        self.stacked_widget.setCurrentWidget(self.list_widget)