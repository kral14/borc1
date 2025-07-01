# app_satici_widget.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, 
                             QStackedWidget, QMessageBox, QAbstractItemView, QHeaderView, QStyle, QToolButton)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, QSize, Qt

import database
from ui_satici_form import Ui_SaticiForm

# --- Satıcı Formasının Məntiqi (Dəyişiklik yoxdur) ---
class SaticiFormWidget(QWidget):
    form_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_SaticiForm()
        self.ui.setupUi(self)
        self.current_supplier_id = None
        
        self.ui.btn_save.clicked.connect(self.save_supplier)
        self.ui.btn_cancel.clicked.connect(self.close_form)
        
    def set_edit_mode(self, supplier_id):
        self.current_supplier_id = supplier_id
        supplier = database.get_supplier_by_id(supplier_id)
        if supplier:
            self.ui.edit_name.setText(supplier['name'])
            self.ui.edit_contact.setText(supplier['contact_person'])
            self.ui.edit_phone.setText(supplier['phone'])
            self.ui.edit_address.setText(supplier['address'])

    def set_add_mode(self):
        self.current_supplier_id = None
        self.ui.edit_name.clear()
        self.ui.edit_contact.clear()
        self.ui.edit_phone.clear()
        self.ui.edit_address.clear()

    def save_supplier(self):
        name = self.ui.edit_name.text().strip()
        contact = self.ui.edit_contact.text().strip()
        phone = self.ui.edit_phone.text().strip()
        address = self.ui.edit_address.text().strip()

        if not name:
            QMessageBox.warning(self, "Xəta", "Satıcı adı boş ola bilməz.")
            return

        if self.current_supplier_id is None:
            success = database.add_supplier(name, contact, phone, address)
        else:
            success = database.update_supplier(self.current_supplier_id, name, contact, phone, address)
        
        if success:
            QMessageBox.information(self, "Uğurlu", "Məlumatlar yadda saxlanıldı.")
            self.close_form()
        else:
            QMessageBox.critical(self, "Xəta", "Əməliyyat zamanı xəta baş verdi.")

    def close_form(self):
        self.form_closed.emit()


# --- Satıcı Cədvəli və İdarəetmə Paneli (CƏDVƏL YENİLƏNİB) ---
class SaticiListWidget(QWidget):
    def __init__(self, stacked_widget, form_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.form_widget = form_widget

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        toolbar = QToolBar("Satıcı Əməliyyatları")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setStyleSheet("QToolBar { border: none; }")
        layout.addWidget(toolbar)
        
        style = self.style()
        self.action_add = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Yeni Satıcı", self)
        self.action_edit = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Düzəliş Et", self)
        self.action_delete = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "Sil", self)
        
        for action in [self.action_add, self.action_edit, self.action_delete]:
            tool_button = QToolButton()
            tool_button.setDefaultAction(action)
            tool_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            tool_button.setStyleSheet("""
                QToolButton { padding: 5px; border: 1px solid transparent; border-radius: 5px; }
                QToolButton:hover { background-color: #555555; border: 1px solid #666666; }
            """)
            toolbar.addWidget(tool_button)

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # === YENİLƏMƏ: SÜTUN SAYI VƏ BAŞLIQLAR ===
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Satıcı Adı", "Əlaqədar Şəxs", "Telefon", "Ünvan", "Bizim Borcumuz"])
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.table_widget.setStyleSheet("""
            QTableWidget { background-color: #3C3C3C; alternate-background-color: #464646; gridline-color: #5A5A5A; color: #FFFFFF; border: 1px solid #5A5A5A; font-size: 11pt; }
            QTableWidget::item { padding: 5px; }
            QHeaderView::section { background-color: #555555; color: #FFFFFF; padding: 5px; border: 1px solid #666666; font-weight: bold; }
            QTableWidget::item:selected { background-color: #007BFF; color: white; }
        """)

        self.action_add.triggered.connect(self.add_new_supplier)
        self.action_edit.triggered.connect(self.edit_supplier)
        self.action_delete.triggered.connect(self.delete_supplier)
        
        self.load_suppliers()

    def load_suppliers(self):
        self.table_widget.setRowCount(0)
        try:
            suppliers = database.get_all_suppliers()
        except Exception as e:
            QMessageBox.critical(self, "Baza Xətası", f"Satıcı məlumatlarını yükləmək mümkün olmadı:\n{e}")
            suppliers = []

        if suppliers:
            # === YENİLƏMƏ: CƏDVƏLİ DOLDURARKƏN BORC SÜTUNU ƏLAVƏ EDİLİR ===
            for row_num, supplier in enumerate(suppliers):
                self.table_widget.insertRow(row_num)
                self.table_widget.setItem(row_num, 0, QTableWidgetItem(str(supplier['id'])))
                self.table_widget.setItem(row_num, 1, QTableWidgetItem(supplier['name']))
                self.table_widget.setItem(row_num, 2, QTableWidgetItem(supplier['contact_person']))
                self.table_widget.setItem(row_num, 3, QTableWidgetItem(supplier['phone']))
                self.table_widget.setItem(row_num, 4, QTableWidgetItem(supplier['address']))
                self.table_widget.setItem(row_num, 5, QTableWidgetItem(f"{supplier['total_debt']:.2f} AZN")) # Borc
        
        self.table_widget.hideColumn(0)
        
    def add_new_supplier(self):
        self.form_widget.set_add_mode()
        self.stacked_widget.setCurrentWidget(self.form_widget)
        
    def edit_supplier(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, düzəliş etmək üçün bir satıcı seçin.")
            return
            
        supplier_id = int(self.table_widget.item(selected_row, 0).text())
        self.form_widget.set_edit_mode(supplier_id)
        self.stacked_widget.setCurrentWidget(self.form_widget)
        
    def delete_supplier(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, silmək üçün bir satıcı seçin.")
            return

        supplier_id = int(self.table_widget.item(selected_row, 0).text())
        supplier_name = self.table_widget.item(selected_row, 1).text()

        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', 
                                     f"'{supplier_name}' adlı satıcını silməyə əminsinizmi?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_supplier(supplier_id):
                self.load_suppliers()
                QMessageBox.information(self, "Uğurlu", "Satıcı silindi.")
            else:
                QMessageBox.critical(self, "Xəta", "Satıcını silmək mümkün olmadı.")

# --- Əsas İdarəedici Widget (Dəyişiklik yoxdur) ---
class SaticiManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.form_widget = SaticiFormWidget()
        self.list_widget = SaticiListWidget(self.stacked_widget, self.form_widget)
        
        self.stacked_widget.addWidget(self.list_widget)
        self.stacked_widget.addWidget(self.form_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.stacked_widget)
        
        self.form_widget.form_closed.connect(self.show_list_and_refresh)
        
    def show_list_and_refresh(self):
        self.list_widget.load_suppliers()
        self.stacked_widget.setCurrentWidget(self.list_widget)