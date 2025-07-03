# column_settings_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QHBoxLayout, QHeaderView, QAbstractItemView,
                             QCheckBox, QWidget, QSpacerItem, QSizePolicy, QListWidget,
                             QDialogButtonBox, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QSettings
from app_logger import logger # Faylın başına logger importunu əlavə edin
class AddColumnDialog(QDialog):
    def __init__(self, available_columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sütun Əlavə Et")
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        for col_data in available_columns:
            self.list_widget.addItem(col_data['header'])
        layout.addWidget(QLabel("Cədvələ əlavə etmək üçün sütun(ları) seçin:"))
        layout.addWidget(self.list_widget)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_headers(self):
        return [item.text() for item in self.list_widget.selectedItems()]

class ColumnSettingsDialog(QDialog):
    def __init__(self, settings_group, master_list, parent=None):
        super().__init__(parent)
        self.settings_group = settings_group
        self.master_column_list = master_list
        self.setWindowTitle("Sütun Ayarları")
        self.setMinimumSize(800, 550)
        self.settings = QSettings("MySoft", "BorcIzlemeApp")

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Sütun Adı", "Göstər", "Eni (px)", "Avtomatik En", "Eni Kilidlə", "Sıralama Aktiv"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        layout.addWidget(self.table)
        
        controls_layout = QHBoxLayout()
        self.btn_add = QPushButton("+ Əlavə Et")
        self.btn_remove = QPushButton("- Çıxart")
        self.btn_up = QPushButton("Yuxarı Qaldır")
        self.btn_down = QPushButton("Aşağı Endir")
        controls_layout.addWidget(self.btn_add)
        controls_layout.addWidget(self.btn_remove)
        controls_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        controls_layout.addWidget(self.btn_up)
        controls_layout.addWidget(self.btn_down)
        layout.addLayout(controls_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)

        self.populate_table()

        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        self.btn_add.clicked.connect(self.add_column)
        self.btn_remove.clicked.connect(self.remove_column)
        self.btn_up.clicked.connect(self.move_row_up)
        self.btn_down.clicked.connect(self.move_row_down)

    def populate_table(self):
        self.table.setRowCount(0)
        column_settings = self.settings.value(f"{self.settings_group}/columns", [])
        
        if not self._are_settings_valid(column_settings):
            column_settings = self._create_default_settings_list()

        for setting in sorted(column_settings, key=lambda x: x.get('visual_index', 999)):
            self.add_row_to_table(setting)
    
    def add_row_to_table(self, setting_data):
        row = self.table.rowCount()
        self.table.insertRow(row)

        header_text = next((col['header'] for col in self.master_column_list if col['key'] == setting_data['key']), "Naməlum")
        
        item_name = QTableWidgetItem(header_text)
        item_name.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item_name.setData(Qt.ItemDataRole.UserRole, setting_data['key'])
        self.table.setItem(row, 0, item_name)

        self.create_checkbox_cell(row, 1, setting_data.get('visible', True))
        item_width = QTableWidgetItem(str(setting_data.get('width', 100)))
        self.table.setItem(row, 2, item_width)
        self.create_checkbox_cell(row, 3, setting_data.get('auto_width', False))
        self.create_checkbox_cell(row, 4, setting_data.get('locked', False))
        self.create_checkbox_cell(row, 5, setting_data.get('sortable', True))

        self.table.cellWidget(row, 3).findChild(QCheckBox).stateChanged.connect(
            lambda state, r=row: self.toggle_width_editability(r)
        )
        self.toggle_width_editability(row)
            
    def add_column(self):
        active_keys = {self.table.item(row, 0).data(Qt.ItemDataRole.UserRole) for row in range(self.table.rowCount())}
        available_columns = [col for col in self.master_column_list if col['key'] not in active_keys]
        
        if not available_columns:
            QMessageBox.information(self, "Məlumat", "Əlavə ediləcək başqa sütun yoxdur.")
            return
            
        dialog = AddColumnDialog(available_columns, self)
        if dialog.exec():
            selected_headers = dialog.get_selected_headers()
            for header in selected_headers:
                col_data = next((col for col in self.master_column_list if col['header'] == header), None)
                if col_data:
                    default_setting = {
                        'key': col_data['key'], 'visible': True, 'width': col_data.get('default_width', 100),
                        'auto_width': False, 'locked': False, 'sortable': True, 'visual_index': self.table.rowCount()
                    }
                    self.add_row_to_table(default_setting)

    def remove_column(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def create_checkbox_cell(self, row, col, is_checked):
        chk = QCheckBox()
        chk.setChecked(is_checked)
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(chk)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, col, widget)

    def toggle_width_editability(self, row):
        width_item = self.table.item(row, 2)
        auto_chk = self.table.cellWidget(row, 3).findChild(QCheckBox)
        is_auto = auto_chk.isChecked()
        
        if is_auto:
            width_item.setText("Avto")
            width_item.setFlags(width_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        else:
            if not width_item.text().isnumeric():
                width_item.setText("100")
            width_item.setFlags(width_item.flags() | Qt.ItemFlag.ItemIsEditable)

    def move_row_up(self):
        row = self.table.currentRow()
        if row > 0:
            self.table.insertRow(row - 1)
            for col in range(self.table.columnCount()):
                self.table.setItem(row - 1, col, self.table.takeItem(row + 1, col))
                if self.table.cellWidget(row + 1, col):
                    self.table.setCellWidget(row - 1, col, self.table.cellWidget(row + 1, col))
            self.table.removeRow(row + 1)
            self.table.selectRow(row - 1)

    def move_row_down(self):
        row = self.table.currentRow()
        if row != -1 and row < self.table.rowCount() - 1:
            self.table.insertRow(row + 2)
            for col in range(self.table.columnCount()):
                self.table.setItem(row + 2, col, self.table.takeItem(row, col))
                if self.table.cellWidget(row, col):
                    self.table.setCellWidget(row + 2, col, self.table.cellWidget(row, col))
            self.table.removeRow(row)
            self.table.selectRow(row + 1)
            
    def save_settings(self):
        column_settings = []
        for row in range(self.table.rowCount()):
            setting = {
                'key': self.table.item(row, 0).data(Qt.ItemDataRole.UserRole),
                'visible': self.table.cellWidget(row, 1).findChild(QCheckBox).isChecked(),
                'width': int(self.table.item(row, 2).text()) if self.table.item(row, 2).text().isnumeric() else 100,
                'auto_width': self.table.cellWidget(row, 3).findChild(QCheckBox).isChecked(),
                'locked': self.table.cellWidget(row, 4).findChild(QCheckBox).isChecked(),
                'sortable': self.table.cellWidget(row, 5).findChild(QCheckBox).isChecked(),
                'visual_index': row
            }
            column_settings.append(setting)
        self.settings.setValue(f"{self.settings_group}/columns", column_settings)
        self.accept()
        
    def _create_default_settings_list(self):
        default_settings = []
        visual_index = 0
        for col_data in self.master_column_list:
            if col_data.get('default_visible', True):
                default_settings.append({
                    'key': col_data['key'], 'header': col_data['header'], 'visible': True, 'width': col_data.get('default_width', 100),
                    'auto_width': False, 'locked': False, 'sortable': True, 'visual_index': visual_index
                })
                visual_index += 1
        return default_settings
        
    def _are_settings_valid(self, settings_list):
        if not isinstance(settings_list, list): return False
        for item in settings_list:
            if not isinstance(item, dict) or 'key' not in item or 'visual_index' not in item:
                return False
        return True

def load_table_settings(table_widget, settings_group, master_list):
    settings = QSettings("MySoft", "BorcIzlemeApp")
    column_settings = settings.value(f"{settings_group}/columns", [])

    # YENİ VƏ TƏKMİL YOXLAMA MƏNTİQİ
    is_valid = True
    if not isinstance(column_settings, list) or not column_settings:
        is_valid = False
    else:
        master_keys = {item['key'] for item in master_list}
        for item in column_settings:
            # Yaddaşdakı hər bir sütunun açar sözünün mövcud proqram kodunda olub-olmadığını yoxlayırıq
            if not isinstance(item, dict) or 'key' not in item or 'visual_index' not in item or item.get('key') not in master_keys:
                is_valid = False
                logger.log(f"Köhnəlmiş sütun ayarı tapıldı: '{item.get('key')}'. '{settings_group}' cədvəli standart ayarlara sıfırlanır.")
                break
    
    if not is_valid:
        # Ayarlar etibarsız və ya köhnədirsə, standart ayarları yenidən qururuq
        settings.remove(f"{settings_group}/columns") # Köhnə ayarları tamamilə sil
        default_settings = []
        visual_index = 0
        for col_data in master_list:
            if col_data.get('default_visible', True):
                default_settings.append({
                    'key': col_data['key'], 'visible': True,
                    'width': col_data.get('default_width', 100),
                    'auto_width': False, 'locked': False, 'sortable': True,
                    'visual_index': visual_index
                })
                visual_index += 1
        column_settings = default_settings
        settings.setValue(f"{settings_group}/columns", column_settings)

    visible_columns = [s for s in column_settings if s.get('visible', True)]
    visible_columns.sort(key=lambda x: x.get('visual_index', 999))

    table_widget.setColumnCount(len(visible_columns))
    
    header_labels = []
    column_map = {}
    header = table_widget.horizontalHeader()

    for visual_index, setting in enumerate(visible_columns):
        key = setting['key']
        master_data = next((item for item in master_list if item['key'] == key), None)
        if not master_data:
            continue
        
        header_labels.append(master_data['header'])
        column_map[key] = visual_index

        if setting.get('auto_width', False):
             header.setSectionResizeMode(visual_index, QHeaderView.ResizeMode.ResizeToContents)
        else:
            header.setSectionResizeMode(visual_index, QHeaderView.ResizeMode.Interactive)
            table_widget.setColumnWidth(visual_index, setting.get('width', 100))
        
        if setting.get('locked', False):
            header.setSectionResizeMode(visual_index, QHeaderView.ResizeMode.Fixed)

    table_widget.setHorizontalHeaderLabels(header_labels)

    from custom_header import CustomHeaderView
    if isinstance(header, CustomHeaderView):
        sortable_indices = []
        for visual_index, setting in enumerate(visible_columns):
             if setting.get('sortable', True):
                 sortable_indices.append(visual_index)
        
        header.set_sortable_columns(sortable_indices)
    
    table_widget.setSortingEnabled(True)
    
    return column_map
    settings = QSettings("MySoft", "BorcIzlemeApp")
    column_settings = settings.value(f"{settings_group}/columns", [])

    is_valid = True
    if not isinstance(column_settings, list):
        is_valid = False
    else:
        for item in column_settings:
            if not isinstance(item, dict) or 'key' not in item or 'visual_index' not in item:
                is_valid = False
                break
    
    if not is_valid or not column_settings:
        default_settings = []
        visual_index = 0
        for col_data in master_list:
            if col_data.get('default_visible', True):
                default_settings.append({
                    'key': col_data['key'], 'visible': True,
                    'width': col_data.get('default_width', 100),
                    'auto_width': False, 'locked': False, 'sortable': True,
                    'visual_index': visual_index
                })
                visual_index += 1
        column_settings = default_settings
        settings.setValue(f"{settings_group}/columns", column_settings)

    visible_columns = [s for s in column_settings if s.get('visible', True)]
    visible_columns.sort(key=lambda x: x.get('visual_index', 999))

    table_widget.setColumnCount(len(visible_columns))
    
    header_labels = []
    column_map = {}
    header = table_widget.horizontalHeader()

    for visual_index, setting in enumerate(visible_columns):
        key = setting['key']
        master_data = next((item for item in master_list if item['key'] == key), None)
        if not master_data:
            continue
        
        header_labels.append(master_data['header'])
        column_map[key] = visual_index

        if setting.get('auto_width', False):
             header.setSectionResizeMode(visual_index, QHeaderView.ResizeMode.ResizeToContents)
        else:
            header.setSectionResizeMode(visual_index, QHeaderView.ResizeMode.Interactive)
            table_widget.setColumnWidth(visual_index, setting.get('width', 100))
        
        if setting.get('locked', False):
            header.setSectionResizeMode(visual_index, QHeaderView.ResizeMode.Fixed)

    table_widget.setHorizontalHeaderLabels(header_labels)

    from custom_header import CustomHeaderView
    if isinstance(header, CustomHeaderView):
        sortable_indices = []
        for visual_index, setting in enumerate(visible_columns):
             if setting.get('sortable', True):
                 sortable_indices.append(visual_index)
        
        header.set_sortable_columns(sortable_indices)
    
    table_widget.setSortingEnabled(True)
    
    return column_map