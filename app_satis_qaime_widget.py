# app_satis_qaime_widget.py
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, QStackedWidget,
                             QMessageBox, QAbstractItemView, QHeaderView, QStyle, QToolButton,
                             QComboBox, QLabel, QLineEdit, QSizePolicy, QTextEdit)
from PyQt6.QtGui import QAction, QFont, QColor, QKeySequence
from PyQt6.QtCore import pyqtSignal, QSize, Qt, QDate, QEvent, QSettings

import database
from ui_satis_qaime_form import Ui_SatisQaimeForm
from satis_qaime_config import MASTER_COLUMN_LIST
from column_settings_dialog import ColumnSettingsDialog, load_table_settings

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try: return float(self.data(Qt.ItemDataRole.UserRole)) < float(other.data(Qt.ItemDataRole.UserRole))
        except (ValueError, TypeError): return super().__lt__(other)

class SatisQaimeListWidget(QWidget):
    add_invoice_requested = pyqtSignal()
    view_invoice_requested = pyqtSignal(int)
    edit_invoice_requested = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        toolbar = QToolBar("Satış Qaiməsi Əməliyyatları")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setStyleSheet("QToolBar { border: none; }")
        layout.addWidget(toolbar)
        style = self.style()
        action_add = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Yeni Qaimə", self)
        action_edit = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Düzəliş Et", self)
        action_view = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DesktopIcon), "Bax", self)
        action_delete = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "Sil", self)
        action_toggle_active = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Aktiv/Deaktiv", self)
        for action in [action_add, action_edit, action_view, action_delete, action_toggle_active]:
            tool_button = QToolButton()
            tool_button.setDefaultAction(action)
            tool_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            tool_button.setStyleSheet("QToolButton{padding:5px;border:1px solid transparent;border-radius:5px} QToolButton:hover{background-color:#555555;border:1px solid #666666}")
            toolbar.addWidget(tool_button)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        label_filter = QLabel(" Axtar: ")
        label_filter.setStyleSheet("font-weight: bold; font-size: 11pt;")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Qaimə №, müştəri, qeyd və ya məbləğə görə axtar...")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.setMinimumWidth(300)
        self.search_box.setStyleSheet("padding: 5px; border-radius: 5px; background-color: #555555; border: 1px solid #666666;")
        self.search_box.textChanged.connect(self.filter_table)
        toolbar.addWidget(label_filter)
        toolbar.addWidget(self.search_box)
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)
        self.table_widget.itemDoubleClicked.connect(self.double_click_edit_invoice)
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setColumnCount(9)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Qaimə №", "Müştəri", "Tarix", "Son Ödəmə", "Qalan Gün", "Qeyd", "Yekun Məbləğ", "Status"])
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_widget.resizeColumnsToContents()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        self.table_widget.setStyleSheet("QTableWidget { background-color: #3C3C3C; alternate-background-color: #464646; gridline-color: #5A5A5A; color: #FFFFFF; border: 1px solid #5A5A5A; font-size: 11pt; } QTableWidget::item { padding: 5px; } QHeaderView::section { background-color: #555555; color: #FFFFFF; padding: 5px; border: 1px solid #666666; font-weight: bold; } QTableWidget::item:selected { background-color: #007BFF; color: white; }")
        self.table_widget.hideColumn(0)
        action_add.triggered.connect(self.add_invoice_requested.emit)
        action_edit.triggered.connect(self.edit_invoice)
        action_view.triggered.connect(self.view_invoice)
        action_delete.triggered.connect(self.delete_invoice)
        action_toggle_active.triggered.connect(self.toggle_active_status)
        self.load_invoices()

    def filter_table(self, text):
        for row in range(self.table_widget.rowCount()):
            match = False
            for col in range(1, self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item and text.lower() in item.text().lower(): match = True; break
            self.table_widget.setRowHidden(row, not match)

    def load_invoices(self):
        self.search_box.clear()
        self.table_widget.setSortingEnabled(False)
        self.table_widget.setRowCount(0)
        invoices = database.get_all_sales_invoices()
        if not invoices:
            self.table_widget.setSortingEnabled(True); return
        today = datetime.date.today()
        for row, inv in enumerate(invoices):
            self.table_widget.insertRow(row)
            due_date = inv.get('due_date')
            days_left_item = QTableWidgetItem()
            days_left_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if due_date and not inv['is_paid']:
                delta = due_date - today
                days_left = delta.days
                days_left_item.setText(str(days_left))
                if days_left < 0: days_left_item.setBackground(QColor('#a22222')); days_left_item.setForeground(QColor('white'))
                elif days_left <= 3: days_left_item.setBackground(QColor('#c89619'))
                else: days_left_item.setBackground(QColor('#227022'))
            else:
                days_left_item.setText("-")
            total_amount = inv['total_amount']
            amount_item = NumericTableWidgetItem(f"{total_amount:.2f} AZN")
            amount_item.setData(Qt.ItemDataRole.UserRole, total_amount)
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            status = "Ödənilib" if inv['is_paid'] else "Ödənilməyib"
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(inv['id'])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(inv['invoice_number']))
            self.table_widget.setItem(row, 2, QTableWidgetItem(inv['customer_name']))
            self.table_widget.setItem(row, 3, QTableWidgetItem(inv['invoice_date'].strftime('%d-%m-%Y')))
            self.table_widget.setItem(row, 4, QTableWidgetItem(due_date.strftime('%d-%m-%Y') if due_date else "-"))
            self.table_widget.setItem(row, 5, days_left_item)
            self.table_widget.setItem(row, 6, QTableWidgetItem(inv.get('notes', '')))
            self.table_widget.setItem(row, 7, amount_item)
            self.table_widget.setItem(row, 8, QTableWidgetItem(status))
            if not inv['is_active']:
                font = QFont(); font.setItalic(True)
                for col in range(1, 9):
                    item = self.table_widget.item(row, col)
                    if item: item.setFont(font); item.setForeground(QColor('gray'))
        self.table_widget.setSortingEnabled(True)
        self.table_widget.resizeColumnsToContents()

    def get_selected_invoice_id(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0: return None
        return int(self.table_widget.item(selected_row, 0).text())

    def view_invoice(self):
        invoice_id = self.get_selected_invoice_id()
        if invoice_id: self.view_invoice_requested.emit(invoice_id)
        else: QMessageBox.warning(self, "Xəbərdarlıq", "Baxmaq üçün bir qaimə seçin.")

    def edit_invoice(self):
        invoice_id = self.get_selected_invoice_id()
        if invoice_id: self.edit_invoice_requested.emit(invoice_id)
        else: QMessageBox.warning(self, "Xəbərdarlıq", "Düzəliş etmək üçün bir qaimə seçin.")

    def double_click_edit_invoice(self, item): self.edit_invoice()

    def delete_invoice(self):
        invoice_id = self.get_selected_invoice_id()
        if not invoice_id: QMessageBox.warning(self, "Xəbərdarlıq", "Silmək üçün bir qaimə seçin."); return
        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', "Bu əməliyyat geri qaytarılmır və stoklar geri artırılacaq!\nƏminsinizmi?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_sales_invoice(invoice_id): self.load_invoices(); QMessageBox.information(self, "Uğurlu", "Qaimə silindi.")
            else: QMessageBox.critical(self, "Xəta", "Qaiməni silmək mümkün olmadı.")

    def toggle_active_status(self):
        invoice_id = self.get_selected_invoice_id()
        if not invoice_id: QMessageBox.warning(self, "Xəbərdarlıq", "Statusunu dəyişmək üçün bir qaimə seçin."); return
        if database.toggle_sales_invoice_status(invoice_id): self.load_invoices(); QMessageBox.information(self, "Uğurlu", "Qaimə statusu dəyişdirildi.")
        else: QMessageBox.critical(self, "Xəta", "Statusu dəyişmək mümkün olmadı.")


class SatisQaimeFormWidget(QWidget):
    form_closed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_SatisQaimeForm()
        self.ui.setupUi(self)
        self.products = []
        self.block_signals = False
        self.current_invoice_id = None
        self.original_items = []
        self.column_map = {}
        self.setup_toolbar_and_shortcuts()
        self.setup_table()
        self.ui.btn_save.clicked.connect(self.save_invoice)
        self.ui.btn_cancel.clicked.connect(self.form_closed.emit)
        self.ui.table_items.cellChanged.connect(self.on_cell_changed)
        self.ui.table_items.installEventFilter(self)
        self.load_customers_to_combobox()

    def setup_toolbar_and_shortcuts(self):
        style = self.style()
        self.ui.action_add_row.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)); self.ui.action_add_row.setText("Əlavə Et")
        self.ui.action_add_row.setToolTip("Yeni boş sətir əlavə edir (Insert)")
        self.ui.action_delete_row.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)); self.ui.action_delete_row.setText("Sil")
        self.ui.action_delete_row.setToolTip("Seçilmiş sətri silir (Delete)"); self.ui.action_delete_row.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        copy_icon = style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.action_copy_row = QAction(copy_icon, "Kopyala", self)
        self.action_copy_row.setToolTip("Seçilmiş sətri kopyalayır (F9)"); self.action_copy_row.setShortcut(QKeySequence(Qt.Key.Key_F9))
        self.ui.table_toolbar.addAction(self.action_copy_row)
        self.ui.table_toolbar.addSeparator()
        settings_icon = style.standardIcon(QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton)
        self.action_settings = QAction(settings_icon, "Ayarlar", self)
        self.action_settings.setToolTip("Cədvəl sütunlarını tənzimləyir")
        self.ui.table_toolbar.addAction(self.action_settings)
        self.ui.btn_save.setToolTip("Qaiməni yadda saxlayır (Ctrl+Enter)")
        self.ui.btn_cancel.setToolTip("Formadan çıxır (Esc)"); self.ui.btn_cancel.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        save_action = QAction("Yadda Saxla", self)
        save_action.setShortcut(QKeySequence("Ctrl+Return")); save_action.triggered.connect(self.save_invoice)
        self.addAction(save_action)
        self.ui.action_add_row.triggered.connect(lambda: self.add_row())
        self.ui.action_delete_row.triggered.connect(self.delete_row)
        self.action_copy_row.triggered.connect(self.copy_row)
        self.action_settings.triggered.connect(self.open_column_settings)

    def setup_table(self):
        from custom_header import CustomHeaderView
        from PyQt6.QtCore import Qt
        header = CustomHeaderView(Qt.Orientation.Horizontal, self.ui.table_items)
        self.ui.table_items.setHorizontalHeader(header)
        self.column_map = load_table_settings(self.ui.table_items, "SatisQaimeTable", MASTER_COLUMN_LIST)

    def open_column_settings(self):
        dialog = ColumnSettingsDialog("SatisQaimeTable", MASTER_COLUMN_LIST, self)
        if dialog.exec():
            self.column_map = load_table_settings(self.ui.table_items, "SatisQaimeTable", MASTER_COLUMN_LIST)
            
    def eventFilter(self, source, event):
        if source is self.ui.table_items and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Insert:
                self.add_row(); return True
            col_key = self.get_key_by_col_index(self.ui.table_items.currentColumn())
            if event.key() == Qt.Key.Key_F4 and col_key == 'product_name':
                combo = self.ui.table_items.cellWidget(self.ui.table_items.currentRow(), self.ui.table_items.currentColumn())
                if combo: combo.showPopup(); return True
        return super(SatisQaimeFormWidget, self).eventFilter(source, event)

    def get_col_index(self, key): return self.column_map.get(key, -1)

    def get_key_by_col_index(self, index):
        for key, idx in self.column_map.items():
            if idx == index: return key
        return None

    def add_row(self, item_data=None, is_enabled=True):
        self.block_signals = True
        row_count = self.ui.table_items.rowCount()
        self.ui.table_items.insertRow(row_count)
        for key, col_index in self.column_map.items():
            item = NumericTableWidgetItem() if key not in ['product_id', 'product_name'] else QTableWidgetItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.table_items.setItem(row_count, col_index, item)
            if key == 'product_name':
                combo_products = QComboBox()
                combo_products.addItem("Mal seçin...", None)
                if self.products:
                    for p in self.products: combo_products.addItem(f"{p['name']} (Qalıq: {p['stock']})", p['id'])
                combo_products.setEnabled(is_enabled)
                self.ui.table_items.setCellWidget(row_count, col_index, combo_products)
                combo_products.currentIndexChanged.connect(lambda index, r=row_count: self.product_selected(r, index))
        
        col_qty = self.get_col_index('quantity')
        if col_qty != -1: self.ui.table_items.item(row_count, col_qty).setText("1")
        col_price = self.get_col_index('unit_price')
        if col_price != -1: self.ui.table_items.item(row_count, col_price).setText("0.00")
        col_disc = self.get_col_index('discount_percent')
        if col_disc != -1: self.ui.table_items.item(row_count, col_disc).setText("0.00")
        
        if item_data:
            col_prod_name = self.get_col_index('product_name')
            if col_prod_name != -1:
                combo = self.ui.table_items.cellWidget(row_count, col_prod_name)
                if combo:
                    product_id = int(item_data.get('product_id', 0))
                    index = combo.findData(product_id)
                    if index != -1: combo.setCurrentIndex(index)
            for key, value in item_data.items():
                col_idx = self.get_col_index(key)
                if col_idx != -1: self.ui.table_items.item(row_count, col_idx).setText(str(value))
        
        self.block_signals = False
        self.recalculate_row(row_count)
        col_prod_name = self.get_col_index('product_name')
        if col_prod_name != -1: self.ui.table_items.setCurrentCell(row_count, col_prod_name)
    
    def product_selected(self, row, combo_index):
        if self.block_signals: return
        self.block_signals = True
        col_name_idx = self.get_col_index('product_name')
        combo = self.ui.table_items.cellWidget(row, col_name_idx)
        if not combo: self.block_signals = False; return
        product_id = combo.currentData()
        product = next((p for p in self.products if p['id'] == product_id), None)
        if product:
            if product['stock'] <= 0 and not self.current_invoice_id:
                QMessageBox.warning(self, "Anbar Xətası", f"'{product['name']}' adlı malın anbar qalığı 0-dır.\nBu malı sata bilməzsiniz.")
                combo.setCurrentIndex(0)
                self.block_signals = False; return
            for key, value in product.items():
                col_idx = self.get_col_index(key)
                if col_idx != -1:
                    if key == 'sale_price': key = 'unit_price' # Uyğunlaşdırma
                    col_idx_form = self.get_col_index(key)
                    if col_idx_form != -1:
                         self.ui.table_items.item(row, col_idx_form).setText(str(value))
        self.block_signals = False
        self.recalculate_row(row)

    def copy_row(self):
        current_row = self.ui.table_items.currentRow()
        if current_row < 0: return
        item_data = {}
        for key, col_idx in self.column_map.items():
            item = self.ui.table_items.item(current_row, col_idx)
            item_data[key] = item.text() if item else ""
        self.add_row(item_data=item_data)
        
    def on_cell_changed(self, row, column):
        if self.block_signals: return
        self.recalculate_row(row)
        
    def recalculate_row(self, row):
        self.block_signals = True
        try:
            quantity = float(self.ui.table_items.item(row, self.get_col_index('quantity')).text() or 0)
            price = float(self.ui.table_items.item(row, self.get_col_index('unit_price')).text() or 0)
            discount = float(self.ui.table_items.item(row, self.get_col_index('discount_percent')).text() or 0)
            final_price = price * (1 - discount / 100)
            line_total = quantity * final_price
            if self.get_col_index('final_price') != -1: self.ui.table_items.item(row, self.get_col_index('final_price')).setText(f"{final_price:.2f}")
            if self.get_col_index('line_total') != -1: self.ui.table_items.item(row, self.get_col_index('line_total')).setText(f"{line_total:.2f}")
        except (ValueError, TypeError, AttributeError, ZeroDivisionError): pass
        finally:
            self.block_signals = False
            self.update_totals()

    def update_totals(self):
        total_amount, total_discount = 0.0, 0.0
        for row in range(self.ui.table_items.rowCount()):
            try:
                total_amount += float(self.ui.table_items.item(row, self.get_col_index('line_total')).text() or 0)
                price = float(self.ui.table_items.item(row, self.get_col_index('unit_price')).text() or 0)
                final_price = float(self.ui.table_items.item(row, self.get_col_index('final_price')).text() or 0)
                quantity = float(self.ui.table_items.item(row, self.get_col_index('quantity')).text() or 0)
                total_discount += quantity * (price - final_price)
            except (ValueError, AttributeError, TypeError): continue
        self.ui.label_total_amount.setText(f"{total_amount:.2f} AZN")
        self.ui.label_total_discount_amount.setText(f"{total_discount:.2f} AZN")

    def save_invoice(self):
        customer_id = self.ui.combo_customer.currentData()
        if not customer_id: QMessageBox.warning(self, "Xəta", "Zəhmət olmasa, müştəri seçin."); return
        items_to_save, total_amount, stock_issues = [], 0, []
        for row in range(self.ui.table_items.rowCount()):
            try:
                if float(self.ui.table_items.item(row, self.get_col_index('quantity')).text() or 0) <= 0: continue
                product = next((p for p in self.products if p['id'] == int(self.ui.table_items.item(row, self.get_col_index('product_id')).text())), None)
                if not product: continue
                original_quantity = next((i['quantity'] for i in self.original_items if i['product_id'] == product['id']), 0) if self.current_invoice_id else 0
                effective_stock = product['stock'] + original_quantity
                quantity = int(self.ui.table_items.item(row, self.get_col_index('quantity')).text())
                if quantity > effective_stock: stock_issues.append(f"'{product['name']}': Anbarda {effective_stock} var, siz {quantity} satmaq istəyirsiniz.")
                item_data = {}
                for key in ['product_id', 'quantity', 'unit_price', 'discount_percent', 'line_total']:
                    item_data[key] = float(self.ui.table_items.item(row, self.get_col_index(key)).text())
                total_amount += item_data.get('line_total', 0)
                items_to_save.append({'product_id': int(item_data['product_id']), 'quantity': item_data['quantity'], 'unit_price': item_data['unit_price'], 'discount': item_data['discount_percent'], 'line_total': item_data['line_total']})
            except (ValueError, TypeError, AttributeError) as e:
                QMessageBox.warning(self, "Məlumat Xətası", f"Cədvəldəki {row+1}-ci sətir düzgün deyil: {e}"); return
        if not items_to_save: QMessageBox.warning(self, "Xəta", "Qaiməyə heç bir mal daxil edilməyib."); return
        if stock_issues:
            if QMessageBox.question(self, "Anbar Qalığı Xəbərdarlığı", "Diqqət! Bəzi mallar üçün anbar qalığı yetərli deyil:\n\n" + "\n".join(stock_issues) + "\n\nDavam etsəniz, anbar mənfiyə düşəcək. Əminsinizmi?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No: return
        invoice_number = self.ui.edit_invoice_no.text()
        invoice_date = self.ui.date_edit.date().toString("yyyy-MM-dd")
        due_date = self.ui.date_due.date().toString("yyyy-MM-dd") if hasattr(self.ui, 'date_due') else None
        notes = self.ui.edit_notes.toPlainText() if hasattr(self.ui, 'edit_notes') else ""
        success = database.update_sales_invoice(self.current_invoice_id, customer_id, invoice_number, invoice_date, due_date, notes, total_amount, items_to_save) if self.current_invoice_id else database.add_sales_invoice(customer_id, invoice_number, invoice_date, due_date, notes, total_amount, items_to_save)
        if success: QMessageBox.information(self, "Uğurlu", "Əməliyyat uğurla tamamlandı."); self.form_closed.emit()
        else: QMessageBox.critical(self, "Xəta", "Əməliyyat zamanı xəta baş verdi.")

    def _fill_form_data(self, invoice_id, enabled):
        details = database.get_sales_invoice_details(invoice_id)
        if not details or not details.get('invoice'):
            QMessageBox.critical(self, "Xəta", "Qaimə məlumatları tapılmadı."); return False
        self.original_items = details.get('items', [])
        inv = details['invoice']
        self.ui.edit_invoice_no.setText(inv['invoice_number'])
        self.ui.date_edit.setDate(inv['invoice_date'])
        if hasattr(self.ui, 'date_due') and inv.get('due_date'): self.ui.date_due.setDate(inv['due_date'])
        if hasattr(self.ui, 'edit_notes'): self.ui.edit_notes.setText(inv.get('notes', ''))
        if inv['customer_id']:
            index = self.ui.combo_customer.findData(inv['customer_id'])
            if index != -1: self.ui.combo_customer.setCurrentIndex(index)
        self.ui.table_items.setRowCount(0)
        if self.original_items:
            for item in self.original_items: self.add_row(item_data=item, is_enabled=enabled)
        self.update_totals()
        return True

    def set_form_enabled(self, enabled):
        self.ui.combo_customer.setEnabled(enabled)
        self.ui.edit_invoice_no.setReadOnly(not enabled)
        self.ui.date_edit.setEnabled(enabled)
        if hasattr(self.ui, 'date_due'): self.ui.date_due.setEnabled(enabled)
        if hasattr(self.ui, 'edit_notes'): self.ui.edit_notes.setEnabled(enabled)
        self.ui.table_toolbar.setVisible(enabled)
        self.ui.table_items.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers if enabled else QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.btn_save.setVisible(enabled)

    def set_view_mode(self, invoice_id):
        self.current_invoice_id = invoice_id
        self.load_products_list()
        self.set_form_enabled(False)
        if not self._fill_form_data(invoice_id, enabled=False): self.form_closed.emit()
        self.ui.btn_cancel.setText("Geri Qayıt")

    def set_edit_mode(self, invoice_id):
        self.current_invoice_id = invoice_id
        self.load_products_list()
        self.set_form_enabled(True)
        if not self._fill_form_data(invoice_id, enabled=True): self.form_closed.emit()
        self.ui.btn_cancel.setText("Ləğv Et")

    def set_add_mode(self, invoice_number=""):
        self.current_invoice_id = None
        self.original_items = []
        self.load_products_list()
        self.ui.combo_customer.setCurrentIndex(0)
        self.ui.edit_invoice_no.setText(invoice_number)
        self.ui.date_edit.setDate(QDate.currentDate())
        if hasattr(self.ui, 'date_due'): self.ui.date_due.setDate(QDate.currentDate().addDays(14))
        if hasattr(self.ui, 'edit_notes'): self.ui.edit_notes.clear()
        self.ui.table_items.setRowCount(0)
        self.add_row()
        self.update_totals()
        self.set_form_enabled(True)
        self.ui.btn_cancel.setText("Ləğv Et")

    def load_customers_to_combobox(self):
        self.ui.combo_customer.clear(); self.ui.combo_customer.addItem("Müştəri seçin...", None)
        customers = database.get_all_customers_with_debt()
        if customers:
            for customer in customers: self.ui.combo_customer.addItem(customer['name'], customer['id'])

    def load_products_list(self): self.products = database.get_all_products()
    def delete_row(self):
        current_row = self.ui.table_items.currentRow()
        if current_row >= 0: self.ui.table_items.removeRow(current_row); self.update_totals()

class SatisQaimeManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.list_widget = SatisQaimeListWidget()
        self.form_widget = SatisQaimeFormWidget()
        self.stacked_widget.addWidget(self.list_widget)
        self.stacked_widget.addWidget(self.form_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        self.list_widget.add_invoice_requested.connect(self.show_add_form)
        self.list_widget.view_invoice_requested.connect(self.show_view_form)
        self.list_widget.edit_invoice_requested.connect(self.show_edit_form)
        self.form_widget.form_closed.connect(self.show_list_and_refresh)
        self.stacked_widget.setCurrentWidget(self.list_widget)
        
    def show_add_form(self):
        next_invoice_num = database.get_next_sales_invoice_number()
        self.form_widget.set_add_mode(next_invoice_num)
        self.stacked_widget.setCurrentWidget(self.form_widget)
    def show_view_form(self, invoice_id):
        self.form_widget.set_view_mode(invoice_id)
        self.stacked_widget.setCurrentWidget(self.form_widget)
    def show_edit_form(self, invoice_id):
        self.form_widget.set_edit_mode(invoice_id)
        self.stacked_widget.setCurrentWidget(self.form_widget)
    def show_list_and_refresh(self):
        self.list_widget.load_invoices()
        self.stacked_widget.setCurrentWidget(self.list_widget)