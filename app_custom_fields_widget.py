# app_custom_fields_widget.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView, QHeaderView, QInputDialog, QToolButton, QStyle
)
from PyQt6.QtGui import QAction, QIcon, QFont, QColor
from PyQt6.QtCore import Qt, QSize
import database

class CustomFieldsManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xüsusi Sahə Ayarları")
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QToolBar("Ayarlar")
        toolbar.setIconSize(QSize(24, 24))
        layout.addWidget(toolbar)

        action_add = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Yeni Sahə Yarat", self)
        self.action_edit = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Düzəliş Et", self)
        
        # DÜZƏLİŞ: Səhv ikon adı (SP_DialogYesNoButton) düzgün olanla (SP_BrowserReload) əvəz edildi.
        self.action_toggle = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "Aktiv/Passiv Et", self)
        
        self.action_delete = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton), "Seçilmişi Sil", self)
        
        toolbar.addAction(action_add)
        toolbar.addAction(self.action_edit)
        toolbar.addAction(self.action_toggle)
        toolbar.addSeparator()
        toolbar.addAction(self.action_delete)

        # Cədvəl
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Sahə Adı (Görünən)", "Açar Söz (Sistem üçün)", "Status"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.hideColumn(0)
        layout.addWidget(self.table)
        self.table.itemDoubleClicked.connect(self.edit_field)

        # Siqnallar
        action_add.triggered.connect(self.add_field)
        self.action_edit.triggered.connect(self.edit_field)
        self.action_toggle.triggered.connect(self.toggle_status)
        self.action_delete.triggered.connect(self.delete_field)

        self.load_fields()

    def load_fields(self):
        self.table.setRowCount(0)
        fields = database.get_custom_field_definitions()
        if not fields: return

        for field in fields:
            row = self.table.rowCount()
            self.table.insertRow(row)

            is_active = field.get('is_active', True)
            status_text = "Aktiv" if is_active else "Passiv"
            status_item = QTableWidgetItem(status_text)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(field['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(field['field_name']))
            self.table.setItem(row, 2, QTableWidgetItem(field['field_key']))
            self.table.setItem(row, 3, status_item)

            if not is_active:
                font = QFont()
                font.setItalic(True)
                gray_color = QColor("#9E9E9E")
                for col in range(1, 4):
                    self.table.item(row, col).setFont(font)
                    self.table.item(row, col).setForeground(gray_color)

    def get_selected_field_info(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, cədvəldən bir sahə seçin.")
            return None, None, None, None
        
        field_id = int(self.table.item(selected_row, 0).text())
        field_name = self.table.item(selected_row, 1).text()
        field_key = self.table.item(selected_row, 2).text()
        status = self.table.item(selected_row, 3).text()
        return field_id, field_name, field_key, status

    def edit_field(self):
        field_id, old_name, old_key, _ = self.get_selected_field_info()
        if not field_id: return

        new_name, ok1 = QInputDialog.getText(self, "Sahə Adını Dəyiş", "Yeni adı daxil edin:", text=old_name)
        if not ok1 or not new_name.strip(): return
        
        new_key, ok2 = QInputDialog.getText(self, "Açar Sözü Dəyiş", "Yeni açar sözü daxil edin:", text=old_key)
        if not ok2 or not new_key.strip(): return

        if database.update_custom_field_definition(field_id, new_key, new_name):
            self.load_fields()
        else:
            QMessageBox.warning(self, "Xəta", "Sahəni yeniləmək mümkün olmadı. Açar söz unikal olmalıdır.")

    def toggle_status(self):
        field_id, field_name, _, _ = self.get_selected_field_info()
        if not field_id: return

        if database.toggle_custom_field_active_status(field_id):
            self.load_fields()
        else:
            QMessageBox.critical(self, "Xəta", "Statusu dəyişmək mümkün olmadı.")

    def delete_field(self):
        field_id, field_name, _, _ = self.get_selected_field_info()
        if not field_id: return
        
        reply = QMessageBox.question(self, "Silməni Təsdiqlə", f"'{field_name}' sahəsini silməyə əminsinizmi?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_custom_field_definition(field_id):
                QMessageBox.information(self, "Uğurlu", "Sahə silindi.")
                self.load_fields()
            else:
                QMessageBox.critical(self, "Xəta", "Sahəni silmək mümkün olmadı.")

    def add_field(self):
        field_name, ok = QInputDialog.getText(self, "Yeni Sahə", "Sahənin adını daxil edin (məs: Ölçü Vahidi):")
        if ok and field_name:
            field_key, ok2 = QInputDialog.getText(self, "Açar Söz", f"'{field_name}' üçün sistemdə istifadə ediləcək açar sözü daxil edin (yalnız latın hərfləri, boşluqsuz, məs: olcu_vahidi):")
            if ok2 and field_key:
                if database.add_custom_field_definition(field_key, field_name):
                    QMessageBox.information(self, "Uğurlu", "Yeni sahə uğurla yaradıldı.")
                    self.load_fields()
                else:
                    QMessageBox.warning(self, "Xəta", "Bu açar söz artıq mövcuddur və ya xəta baş verdi.")