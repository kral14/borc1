# app_kassa_medaxil_widget.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, 
                             QStackedWidget, QMessageBox, QAbstractItemView, QHeaderView, QStyle, QToolButton)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, QSize, Qt

import database
from ui_kassa_medaxil_form import Ui_KassaMedaxilForm

class KassaMedaxilFormWidget(QWidget):
    form_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_KassaMedaxilForm()
        self.ui.setupUi(self)

        self.ui.btn_save.clicked.connect(self.save_payment)
        self.ui.btn_cancel.clicked.connect(self.form_closed.emit)
        self.ui.combo_customer.currentIndexChanged.connect(self.on_customer_selected)
        self.ui.combo_invoice.currentIndexChanged.connect(self.on_invoice_selected)

    def start_new_payment(self):
        self.ui.combo_customer.clear()
        self.ui.combo_customer.addItem("Müştəri seçin...", None)
        customers = database.get_all_customers_with_debt()
        for cust in customers:
            if cust['total_debt'] > 0: # Yalnız borcu olanları göstər
                self.ui.combo_customer.addItem(f"{cust['name']} (Borc: {cust['total_debt']:.2f} AZN)", cust['id'])

        self.ui.combo_invoice.clear()
        self.ui.spin_amount.setValue(0)
        self.ui.edit_notes.clear()

    def on_customer_selected(self, index):
        self.ui.combo_invoice.clear()
        customer_id = self.ui.combo_customer.currentData()
        if customer_id:
            invoices = database.get_unpaid_invoices_for_customer(customer_id)
            self.ui.combo_invoice.addItem("Qaimə seçin...", None)
            for inv in invoices:
                self.ui.combo_invoice.addItem(f"{inv['invoice_number']} (Qalıq borc: {inv['remaining_debt']:.2f} AZN)", inv)

    def on_invoice_selected(self, index):
        invoice_data = self.ui.combo_invoice.currentData()
        if invoice_data:
            self.ui.spin_amount.setValue(invoice_data['remaining_debt'])
            self.ui.spin_amount.setMaximum(invoice_data['remaining_debt'])
        else:
            self.ui.spin_amount.setValue(0)
            self.ui.spin_amount.setMaximum(999999.99)

    def save_payment(self):
        customer_id = self.ui.combo_customer.currentData()
        invoice_data = self.ui.combo_invoice.currentData()
        amount = self.ui.spin_amount.value()
        payment_date = self.ui.date_edit.date().toString("yyyy-MM-dd")
        notes = self.ui.edit_notes.toPlainText()

        if not customer_id or not invoice_data:
            QMessageBox.warning(self, "Xəta", "Müştəri və qaimə seçilməlidir.")
            return
        if amount <= 0:
            QMessageBox.warning(self, "Xəta", "Ödəniş məbləği 0-dan böyük olmalıdır.")
            return

        success = database.add_customer_payment(customer_id, invoice_data['id'], amount, payment_date, notes)
        if success:
            QMessageBox.information(self, "Uğurlu", "Ödəniş uğurla qeydə alındı.")
            self.form_closed.emit()
        else:
            QMessageBox.critical(self, "Xəta", "Ödəniş zamanı xəta baş verdi.")

class KassaMedaxilListWidget(QWidget):
    def __init__(self, stacked_widget, form_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.form_widget = form_widget
        layout = QVBoxLayout(self)

        toolbar = QToolBar("Mədaxil Əməliyyatları")
        layout.addWidget(toolbar)

        self.action_add = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Yeni Mədaxil", self)
        toolbar.addAction(self.action_add)

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Tarix", "Müştəri", "Qaimə №", "Məbləğ"])
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.hideColumn(0)

        self.action_add.triggered.connect(self.add_new_payment)
        self.load_payments()

    def load_payments(self):
        self.table_widget.setRowCount(0)
        payments = database.get_all_payments()
        if not payments: return
        for row, payment in enumerate(payments):
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(payment['id'])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(payment['payment_date'].strftime('%d-%m-%Y')))
            self.table_widget.setItem(row, 2, QTableWidgetItem(payment['customer_name']))
            self.table_widget.setItem(row, 3, QTableWidgetItem(payment['invoice_number']))
            self.table_widget.setItem(row, 4, QTableWidgetItem(f"{payment['amount']:.2f} AZN"))

    def add_new_payment(self):
        self.form_widget.start_new_payment()
        self.stacked_widget.setCurrentWidget(self.form_widget)

class KassaMedaxilManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.form_widget = KassaMedaxilFormWidget()
        self.list_widget = KassaMedaxilListWidget(self.stacked_widget, self.form_widget)
        self.stacked_widget.addWidget(self.list_widget)
        self.stacked_widget.addWidget(self.form_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.stacked_widget)
        self.form_widget.form_closed.connect(self.show_list_and_refresh)

    def show_list_and_refresh(self):
        self.list_widget.load_payments()
        self.stacked_widget.setCurrentWidget(self.list_widget)