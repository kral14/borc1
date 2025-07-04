# app_musteri_widget.py (YENİLƏNMİŞ)

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, 
                             QStackedWidget, QMessageBox, QAbstractItemView, QHeaderView, QStyle, QToolButton)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, QSize, Qt
import database
from ui_musteri_form import Ui_MusteriForm
import style_manager

# MusteriFormWidget sinfi olduğu kimi qalır...
class MusteriFormWidget(QWidget):
    #... (içində dəyişiklik yoxdur)
    form_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_MusteriForm()
        self.ui.setupUi(self)
        self.current_customer_id = None
        self.ui.btn_save.clicked.connect(self.save_customer)
        self.ui.btn_cancel.clicked.connect(self.close_form)
        
    def set_edit_mode(self, customer_id):
        self.current_customer_id = customer_id
        customer = database.get_customer_by_id(customer_id)
        if customer:
            self.ui.edit_name.setText(customer['name'])
            self.ui.edit_phone.setText(customer['phone'])
            self.ui.edit_address.setText(customer['address'])

    def set_add_mode(self):
        self.current_customer_id = None
        self.ui.edit_name.clear()
        self.ui.edit_phone.clear()
        self.ui.edit_address.clear()

    def save_customer(self):
        name = self.ui.edit_name.text().strip()
        phone = self.ui.edit_phone.text().strip()
        address = self.ui.edit_address.text().strip()
        if not name:
            QMessageBox.warning(self, "Xəta", "Ad və Soyad boş ola bilməz.")
            return
        if self.current_customer_id is None:
            success = database.add_customer(name, phone, address)
        else:
            success = database.update_customer(self.current_customer_id, name, phone, address)
        if success:
            QMessageBox.information(self, "Uğurlu", "Məlumatlar yadda saxlanıldı.")
            self.close_form()
        else:
            QMessageBox.critical(self, "Xəta", "Əməliyyat zamanı xəta baş verdi.")

    def close_form(self):
        self.form_closed.emit()


class MusteriListWidget(QWidget):
    def __init__(self, stacked_widget, form_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.form_widget = form_widget

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Toolbarı self-də saxlayırıq ki, sonra ölçüsünü dəyişə bilək
        self.toolbar = QToolBar("Müştəri Əməliyyatları")
        layout.addWidget(self.toolbar)
        
        style = self.style()
        self.action_add = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Yeni Müştəri", self)
        self.action_edit = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Düzəliş Et", self)
        self.action_delete = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "Sil", self)
        
        for action in [self.action_add, self.action_edit, self.action_delete]:
            tool_button = QToolButton()
            tool_button.setDefaultAction(action)
            tool_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            self.toolbar.addWidget(tool_button)

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # ... cədvəl parametrləri ...
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Ad, Soyad", "Telefon", "Ünvan", "Borc"])
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table_widget.hideColumn(0)
        
        self.action_add.triggered.connect(self.add_new_customer)
        self.action_edit.triggered.connect(self.edit_customer)
        self.action_delete.triggered.connect(self.delete_customer)
        
        self.load_customers()
        # Komponentləri ilk dəfə yaradanda ölçülərini təyin edirik
        self.apply_dynamic_styles()

    def apply_dynamic_styles(self):
        """
        Bu metod proqramın miqyasına uyğun olaraq, QSS ilə idarə olunmayan
        elementləri (məsələn ikon ölçüsü) yeniləyir.
        """
        # === YENİLİK BURADADIR ===
        base_icon_size = 24  # İkonun baza ölçüsü
        self.toolbar.setIconSize(style_manager.get_scaled_icon_size(base_size=base_icon_size))
        
        # Gələcəkdə sətir hündürlüyü kimi digər elementləri də buradan idarə etmək olar
        # base_row_height = 30
        # scale = style_manager.load_zoom_setting()
        # for row in range(self.table_widget.rowCount()):
        #     self.table_widget.setRowHeight(row, int(base_row_height * scale))

    # ... load_customers, add_new_customer, edit_customer, delete_customer metodları olduğu kimi qalır ...
    def load_customers(self):
        self.table_widget.setRowCount(0)
        try:
            customers = database.get_all_customers_with_debt()
        except Exception as e:
            QMessageBox.critical(self, "Baza Xətası", f"Müştəri məlumatlarını yükləmək mümkün olmadı:\n{e}")
            customers = []
        if customers:
            for row_num, customer in enumerate(customers):
                self.table_widget.insertRow(row_num)
                self.table_widget.setItem(row_num, 0, QTableWidgetItem(str(customer['id'])))
                self.table_widget.setItem(row_num, 1, QTableWidgetItem(customer['name']))
                self.table_widget.setItem(row_num, 2, QTableWidgetItem(customer['phone']))
                self.table_widget.setItem(row_num, 3, QTableWidgetItem(customer['address']))
                self.table_widget.setItem(row_num, 4, QTableWidgetItem(f"{customer['total_debt']:.2f} AZN"))
        self.table_widget.hideColumn(0)
        
    def add_new_customer(self):
        self.form_widget.set_add_mode()
        self.stacked_widget.setCurrentWidget(self.form_widget)
        
    def edit_customer(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Xəbərdarlıq", "Düzəliş etmək üçün bir müştəri seçin.")
            return
        customer_id = int(self.table_widget.item(selected_row, 0).text())
        self.form_widget.set_edit_mode(customer_id)
        self.stacked_widget.setCurrentWidget(self.form_widget)
        
    def delete_customer(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Xəbərdarlıq", "Silmək üçün bir müştəri seçin.")
            return
        customer_id = int(self.table_widget.item(selected_row, 0).text())
        customer_name = self.table_widget.item(selected_row, 1).text()
        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', 
                                     f"'{customer_name}' adlı müştərini silməyə əminsinizmi?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_customer(customer_id):
                self.load_customers()
                QMessageBox.information(self, "Uğurlu", "Müştəri silindi.")
            else:
                QMessageBox.critical(self, "Xəta", "Müştərini silmək mümkün olmadı.")

class MusteriManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.stacked_widget = QStackedWidget()
        self.form_widget = MusteriFormWidget()
        self.list_widget = MusteriListWidget(self.stacked_widget, self.form_widget)
        
        self.stacked_widget.addWidget(self.list_widget)
        self.stacked_widget.addWidget(self.form_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.stacked_widget)
        
        self.form_widget.form_closed.connect(self.show_list_and_refresh)
        
        # === YENİLİK BURADADIR ===
        # Əsas pəncərədən gələn siqnalı list_widget-in metoduna bağlayırıq
        main_win = QApplication.instance().property("main_window")
        if main_win:
            main_win.settings_changed.connect(self.list_widget.apply_dynamic_styles)
        
    def show_list_and_refresh(self):
        self.list_widget.load_customers()
        self.stacked_widget.setCurrentWidget(self.list_widget)