# app_mal_widget.py

import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem,
                             QMessageBox, QAbstractItemView, QHeaderView, QStyle, QToolButton,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog, QLabel, QLineEdit, QDialog,
                             QSizePolicy) # DÜZƏLİŞ: QSizePolicy bura əlavə edildi
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import pyqtSignal, QSize, Qt, QDate

import database
from ui_mal_form import Ui_MalForm

# MalFormWidget sinfi olduğu kimi qalır
class MalFormWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MalForm()
        self.ui.setupUi(self)
        self.current_product_id = None
        self.dynamic_widgets = []

        self.ui.btn_save.clicked.connect(self.save_and_accept)
        self.ui.btn_cancel.clicked.connect(self.reject)
        
        self.ui.date_exp.dateChanged.connect(self._update_shelf_life)
        self.ui.date_prod.dateChanged.connect(self._update_shelf_life)

    def save_and_accept(self):
        if self.save_product():
            self.accept()

    def _clear_dynamic_widgets(self):
        for widget_list in self.dynamic_widgets:
            if widget_list['label']:
                widget_list['label'].deleteLater()
            if widget_list['widget']:
                widget_list['widget'].deleteLater()
        self.dynamic_widgets = []

    def _create_dynamic_widgets(self, product_data=None):
        self._clear_dynamic_widgets()
        custom_fields = database.get_custom_field_definitions(active_only=True)
        is_visible = bool(custom_fields)
        self.ui.tabWidget.setTabVisible(4, is_visible)
        if not is_visible:
            return
        product_attributes = {}
        if product_data:
            attrs = product_data.get('custom_attributes')
            if attrs is not None:
                product_attributes = attrs
        for field in custom_fields:
            label = QLabel(f"{field['field_name']}:", self)
            line_edit = QLineEdit(self)
            if field['field_key'] in product_attributes:
                line_edit.setText(str(product_attributes.get(field['field_key'], '')))
            line_edit.setProperty("field_key", field['field_key'])
            self.ui.custom_fields_layout.addRow(label, line_edit)
            self.dynamic_widgets.append({'label': label, 'widget': line_edit})

    def _update_shelf_life(self):
        expiry_date = self.ui.date_exp.date().toPyDate()
        today = datetime.date.today()
        if expiry_date < today:
            self.ui.label_shelf_life_value.setText("<font color='red'>Vaxtı bitib</font>")
        else:
            days_left = (expiry_date - today).days
            self.ui.label_shelf_life_value.setText(f"<font color='lime'>{days_left} gün</font>")

    def set_edit_mode(self, product_id):
        self.setWindowTitle("Mal Məlumatlarına Düzəliş")
        self.load_comboboxes()
        self.current_product_id = product_id
        product = database.get_product_by_id(product_id)
        if not product:
            QMessageBox.critical(self, "Xəta", "Məhsul məlumatları tapılmadı.")
            self.reject()
            return
        self.ui.edit_name.setText(product['name'])
        self.ui.edit_article.setText(product.get('article', ''))
        self.ui.edit_code.setText(product.get('product_code', ''))
        self.ui.combo_is_food.setCurrentIndex(0 if product.get('is_food_product', True) else 1)
        if product.get('category_id'):
            index = self.ui.combo_category.findData(product['category_id'])
            if index != -1: self.ui.combo_category.setCurrentIndex(index)
        if product.get('supplier_id'):
            index = self.ui.combo_supplier.findData(product['supplier_id'])
            if index != -1: self.ui.combo_supplier.setCurrentIndex(index)
        self.ui.spin_pieces_in_block.setValue(product.get('pieces_in_block', 0))
        self.ui.spin_pieces_in_box.setValue(product.get('pieces_in_box', 0))
        self.ui.edit_warehouse.setText(product.get('warehouse_location', ''))
        self.ui.edit_shelf.setText(product.get('shelf_location', ''))
        self.ui.edit_row.setText(product.get('row_location', ''))
        self.ui.spin_stock.setValue(product.get('stock', 0))
        self.ui.edit_barcode_unit.setText(product.get('barcode_unit', ''))
        self.ui.edit_barcode_block.setText(product.get('barcode_block', ''))
        self.ui.edit_barcode_box.setText(product.get('barcode_box', ''))
        self.ui.spin_purchase_price.setValue(product.get('purchase_price', 0))
        self.ui.spin_sale_price.setValue(product.get('sale_price', 0))
        if product.get('production_date'): self.ui.date_prod.setDate(product['production_date'])
        if product.get('expiry_date'): self.ui.date_exp.setDate(product['expiry_date'])
        if product.get('unit_of_measure'): self.ui.combo_uom.setCurrentText(product['unit_of_measure'])
        self._update_shelf_life()
        self._create_dynamic_widgets(product)
        self.ui.tabWidget.setCurrentIndex(0)


    def set_add_mode(self):
        self.setWindowTitle("Yeni Mal Yarat")
        self.load_comboboxes()
        self.current_product_id = None
        for w in [self.ui.edit_name, self.ui.edit_article, self.ui.edit_code, self.ui.edit_barcode_unit,
                  self.ui.edit_barcode_block, self.ui.edit_barcode_box, self.ui.edit_warehouse, 
                  self.ui.edit_shelf, self.ui.edit_row]: w.clear()
        for s in [self.ui.spin_purchase_price, self.ui.spin_sale_price]: s.setValue(0)
        for s in [self.ui.spin_stock, self.ui.spin_pieces_in_block, self.ui.spin_pieces_in_box]: s.setValue(0)
        for c in [self.ui.combo_supplier, self.ui.combo_category, self.ui.combo_is_food, self.ui.combo_uom]: c.setCurrentIndex(0)
        today = QDate.currentDate()
        self.ui.date_prod.setDate(today)
        self.ui.date_exp.setDate(today.addYears(1))
        self._update_shelf_life()
        self._create_dynamic_widgets()
        self.ui.tabWidget.setCurrentIndex(0)
        
    def load_comboboxes(self):
        self.ui.combo_supplier.clear()
        self.ui.combo_supplier.addItem("Satıcı seçin...", None)
        suppliers = database.get_all_suppliers()
        if suppliers:
            for supplier in suppliers:
                self.ui.combo_supplier.addItem(supplier['name'], supplier['id'])
        self.ui.combo_category.clear()
        self.ui.combo_category.addItem("Kateqoriya/Qovluq seçin...", None)
        categories = database.get_all_categories()
        if categories:
            for category in sorted(categories, key=lambda x: x['name']):
                 self.ui.combo_category.addItem(category['name'], category['id'])

    def save_product(self):
        name = self.ui.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Xəta", "Mal adı boş ola bilməz.")
            self.ui.tabWidget.setCurrentIndex(0)
            return False
        custom_attributes = {}
        for item in self.dynamic_widgets:
            field_key = item['widget'].property("field_key")
            value = item['widget'].text().strip()
            if field_key and value:
                custom_attributes[field_key] = value
        data = {
            "name": self.ui.edit_name.text().strip(), "product_code": self.ui.edit_code.text().strip(),
            "article": self.ui.edit_article.text().strip(), "category_id": self.ui.combo_category.currentData(),
            "supplier_id": self.ui.combo_supplier.currentData(), "purchase_price": self.ui.spin_purchase_price.value(),
            "sale_price": self.ui.spin_sale_price.value(), "stock": self.ui.spin_stock.value(),
            "custom_attributes": custom_attributes, "is_food_product": self.ui.combo_is_food.currentIndex() == 0,
            "pieces_in_box": self.ui.spin_pieces_in_box.value(), "pieces_in_block": self.ui.spin_pieces_in_block.value(),
            "barcode_unit": self.ui.edit_barcode_unit.text().strip(), "barcode_box": self.ui.edit_barcode_box.text().strip(),
            "barcode_block": self.ui.edit_barcode_block.text().strip(), "unit_of_measure": self.ui.combo_uom.currentText(),
            "production_date": self.ui.date_prod.date().toPyDate(), "expiry_date": self.ui.date_exp.date().toPyDate(),
            "warehouse_location": self.ui.edit_warehouse.text().strip(), "shelf_location": self.ui.edit_shelf.text().strip(),
            "row_location": self.ui.edit_row.text().strip()
        }
        if self.current_product_id is None:
            success = database.add_product(**data)
        else:
            success = database.update_product(self.current_product_id, **data)
        if not success:
            QMessageBox.critical(self, "Xəta", "Əməliyyat zamanı xəta baş verdi.")
        return success

# MalListWidget sinfi axtarış funksionallığı ilə yenilənir
class MalListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.all_products = []
        self.categories = []
        self.column_map = {}
        self.master_column_list = []
        self._search_target_column_key = None
        self._default_search_placeholder = "Mal adı, kodu, barkodu və ya qiymətə görə axtar..."

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        toolbar = QToolBar("Mal Əməliyyatları")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("QToolBar { border: none; }")
        
        style = self.style()
        self.action_add_category = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DirIcon), "Yeni Qovluq", self)
        self.action_add = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Yeni Mal", self)
        self.action_edit = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Düzəliş Et", self)
        self.action_delete = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "Sil", self)
        self.action_settings = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton), "Sütun Ayarları", self)

        for action in [self.action_add_category, self.action_add, self.action_edit, self.action_delete]:
            toolbar.addAction(action)
        toolbar.addSeparator()
        toolbar.addAction(self.action_settings)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        label_filter = QLabel("Axtar: ")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self._default_search_placeholder)
        self.search_box.setClearButtonEnabled(True)
        self.search_box.setMinimumWidth(300)
        self.search_box.textChanged.connect(self.apply_filters)
        toolbar.addWidget(label_filter)
        toolbar.addWidget(self.search_box)
        main_layout.addWidget(toolbar)
        
        self.action_add_category.triggered.connect(self.add_new_category)
        self.action_add.triggered.connect(self.add_new_product)
        self.action_edit.triggered.connect(self.edit_product)
        self.action_delete.triggered.connect(self.delete_product)
        self.action_settings.triggered.connect(self.open_column_settings)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabel("Qovluqlar")
        self.category_tree.setMaximumWidth(350)
        self.category_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.category_tree.customContextMenuRequested.connect(self.show_category_context_menu)
        self.splitter.addWidget(self.category_tree)
        self.category_tree.currentItemChanged.connect(self.apply_filters)

        self.table_widget = QTableWidget()
        self.table_widget.itemDoubleClicked.connect(self.edit_product)
        self.splitter.addWidget(self.table_widget)
        self.splitter.setSizes([250, 750])

        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet("QTableWidget { background-color: #3C3C3C; alternate-background-color: #464646; gridline-color: #5A5A5A; color: #FFFFFF; border: 1px solid #5A5A5A; font-size: 11pt; } QTableWidget::item { padding: 5px; } QHeaderView::section { background-color: #555555; color: #FFFFFF; padding: 5px; border: 1px solid #666666; font-weight: bold; } QTableWidget::item:selected { background-color: #007BFF; color: white; }")
        
        self.load_data()
        self.setup_shortcuts()

    def setup_shortcuts(self):
        find_action = QAction("Find", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.handle_find_request)
        self.addAction(find_action)

    def handle_find_request(self):
        current_col_index = self.table_widget.currentColumn()
        target_key = None
        for key, col_idx in self.column_map.items():
            if col_idx == current_col_index:
                target_key = key
                break
        
        if target_key:
            self._search_target_column_key = target_key
            header_text = self.table_widget.horizontalHeaderItem(current_col_index).text()
            self.search_box.setPlaceholderText(f"Axtarış: {header_text}...")
            self.search_box.setFocus()
            self.search_box.selectAll()

    def apply_filters(self, *args):
        current_item = self.category_tree.currentItem()
        if not current_item:
            filtered_by_cat = self.all_products
        else:
            category_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            if category_id == "all":
                filtered_by_cat = self.all_products
            else:
                filtered_by_cat = [p for p in self.all_products if p.get('category_id') == category_id]
        
        search_text = self.search_box.text().lower()
        if not search_text:
            if self._search_target_column_key:
                self._search_target_column_key = None
                self.search_box.setPlaceholderText(self._default_search_placeholder)
            final_filtered_list = filtered_by_cat
        else:
            final_filtered_list = []
            for product in filtered_by_cat:
                match = False
                if self._search_target_column_key:
                    value = product.get(self._search_target_column_key)
                    if value and search_text in str(value).lower():
                        match = True
                else:
                    for key in self.column_map.keys():
                        value = product.get(key)
                        if key.startswith('custom_'):
                            if product.get('custom_attributes'):
                                c_value = product['custom_attributes'].get(key.replace('custom_', ''))
                                if c_value and search_text in str(c_value).lower():
                                    match = True
                                    break
                        elif value and search_text in str(value).lower():
                            match = True
                            break
                if match:
                    final_filtered_list.append(product)

        self.display_products(final_filtered_list)

    def setup_columns(self):
        from column_settings_dialog import load_table_settings
        standard_columns = [
            {'key': 'id', 'header': 'ID', 'default_visible': False},
            {'key': 'name', 'header': 'Adı', 'default_visible': True, 'default_width': 250},
            {'key': 'barcode_unit', 'header': 'Ədəd Barkodu', 'default_visible': False, 'default_width': 120},
            {'key': 'category_name', 'header': 'Kateqoriya', 'default_visible': True, 'default_width': 150},
            {'key': 'supplier_name', 'header': 'Alındığı Yer', 'default_visible': True, 'default_width': 150},
            {'key': 'purchase_price', 'header': 'Alış Qiyməti', 'default_visible': True, 'default_width': 100},
            {'key': 'sale_price', 'header': 'Satış Qiyməti', 'default_visible': True, 'default_width': 100},
            {'key': 'stock', 'header': 'Stok', 'default_visible': True, 'default_width': 80},
        ]
        custom_fields = database.get_custom_field_definitions(active_only=True)
        custom_columns = []
        if custom_fields:
            for field in custom_fields:
                custom_columns.append({
                    'key': f"custom_{field['field_key']}",
                    'header': field['field_name'],
                    'default_visible': False,
                    'default_width': 120,
                })
        self.master_column_list = standard_columns + custom_columns
        self.column_map = load_table_settings(self.table_widget, "MalListTable", self.master_column_list)
        
    def display_products(self, products):
        self.table_widget.setRowCount(0)
        if not products: return
        for row_num, product in enumerate(products):
            self.table_widget.insertRow(row_num)
            for key, col_index in self.column_map.items():
                if col_index is None: continue
                item_text = ""
                if key.startswith('custom_'):
                    field_key = key.replace('custom_', '')
                    if product.get('custom_attributes') and field_key in product['custom_attributes']:
                        item_text = str(product['custom_attributes'][field_key])
                else:
                    value = product.get(key)
                    if isinstance(value, (int, float)):
                        item_text = f"{value:.2f}" if key.endswith('_price') else str(value)
                    elif value is not None:
                        item_text = str(value)
                self.table_widget.setItem(row_num, col_index, QTableWidgetItem(item_text))
    
    def load_data(self):
        self.setup_columns()
        self.populate_category_tree()
        self.all_products = database.get_all_products()
        current_item = self.category_tree.currentItem()
        if not current_item and self.category_tree.topLevelItemCount() > 0:
            self.category_tree.setCurrentItem(self.category_tree.topLevelItem(0))
        self.apply_filters()

    def on_category_selected(self, current, previous):
        self.apply_filters()
    
    # ... sinifin qalan metodları (open_column_settings, add_new_product, edit_product və s.) olduğu kimi qalır
    def open_column_settings(self):
        from column_settings_dialog import ColumnSettingsDialog
        self.setup_columns() 
        dialog = ColumnSettingsDialog("MalListTable", self.master_column_list, self)
        if dialog.exec():
            self.setup_columns()
            self.apply_filters()

    def add_new_product(self):
        dialog = MalFormWidget(self)
        dialog.set_add_mode()
        if dialog.exec():
            self.load_data()
        
    def edit_product(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0: 
            QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, düzəliş etmək üçün bir mal seçin.")
            return
        # ID-ni birbaşa məhsul siyahısından alırıq, çünki cədvəl filtrlənmiş ola bilər
        visible_products = self._get_visible_products()
        if selected_row >= len(visible_products): return
        product_id = visible_products[selected_row]['id']
        
        dialog = MalFormWidget(self)
        dialog.set_edit_mode(product_id)
        if dialog.exec():
            self.load_data()
    
    def _get_visible_products(self):
        # Axtarış və filtr nəticəsində görünən məhsulların siyahısını qaytarır
        # Bu, bir növ apply_filters-in təkrarlanmasıdır, ancaq yalnız data qaytarır
        current_item = self.category_tree.currentItem()
        if not current_item:
            filtered_by_cat = self.all_products
        else:
            category_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            if category_id == "all":
                filtered_by_cat = self.all_products
            else:
                filtered_by_cat = [p for p in self.all_products if p.get('category_id') == category_id]
        
        search_text = self.search_box.text().lower()
        if not search_text:
            return filtered_by_cat
        else:
            final_filtered_list = []
            for product in filtered_by_cat:
                match = False
                if self._search_target_column_key:
                    value = product.get(self._search_target_column_key)
                    if value and search_text in str(value).lower():
                        match = True
                else:
                    for key in self.column_map.keys():
                        value = product.get(key)
                        if key.startswith('custom_'):
                            if product.get('custom_attributes'):
                                c_value = product['custom_attributes'].get(key.replace('custom_', ''))
                                if c_value and search_text in str(c_value).lower():
                                    match = True
                                    break
                        elif value and search_text in str(value).lower():
                            match = True
                            break
                if match:
                    final_filtered_list.append(product)
            return final_filtered_list
            
    def delete_product(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0: 
            QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, silmək üçün bir mal seçin.")
            return

        visible_products = self._get_visible_products()
        if selected_row >= len(visible_products): return
        product_to_delete = visible_products[selected_row]
        product_id = product_to_delete['id']
        product_name = product_to_delete['name']

        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', f"'{product_name}' adlı malı silməyə əminsinizmi?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_product(product_id): 
                self.load_data()
                QMessageBox.information(self, "Uğurlu", "Mal silindi.")
            else: 
                QMessageBox.critical(self, "Xəta", "Malı silmək mümkün olmadı. Bu məhsul qaimələrdə istifadə oluna bilər.")
    # kateqoriya ilə bağlı metodlar (add_new_category və s.) olduğu kimi qalır...
    def add_new_category(self):
        parent_item = self.category_tree.currentItem()
        parent_id = parent_item.data(0, Qt.ItemDataRole.UserRole) if parent_item and parent_item.data(0, Qt.ItemDataRole.UserRole) != "all" else None
        text, ok = QInputDialog.getText(self, 'Yeni Qovluq', 'Qovluğun adını daxil edin:')
        if ok and text:
            if database.add_category(text, parent_id): self.load_data()
            else: QMessageBox.critical(self, "Xəta", "Qovluq yaradılarkən xəta baş verdi.")
    def show_category_context_menu(self, position):
        item = self.category_tree.itemAt(position)
        if item and item.data(0, Qt.ItemDataRole.UserRole) != "all":
            menu = QMenu(); rename_action = menu.addAction("Adını dəyiş"); delete_action = menu.addAction("Sil")
            action = menu.exec(self.category_tree.mapToGlobal(position))
            if action == rename_action: self.rename_category(item)
            elif action == delete_action: self.delete_category(item)
    def rename_category(self, item):
        category_id = item.data(0, Qt.ItemDataRole.UserRole); old_name = item.text(0)
        text, ok = QInputDialog.getText(self, 'Adını Dəyiş', 'Yeni adı daxil edin:', text=old_name)
        if ok and text and text != old_name:
            if database.update_category_name(category_id, text): self.load_data()
            else: QMessageBox.critical(self, "Xəta", "Ad dəyişdirilərkən xəta baş verdi.")
    def delete_category(self, item):
        category_id = item.data(0, Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', f"'{item.text(0)}' qovluğunu silməyə əminsinizmi?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_category(category_id): self.load_data()
            else: QMessageBox.critical(self, "Xəta", "Silmə zamanı xəta baş verdi.")
    def populate_category_tree(self):
        current_selection = self.category_tree.currentItem().data(0, Qt.ItemDataRole.UserRole) if self.category_tree.currentItem() else None
        self.category_tree.clear()
        self.categories = database.get_all_categories()
        all_items_node = QTreeWidgetItem(self.category_tree, ["Bütün Mallar"])
        all_items_node.setData(0, Qt.ItemDataRole.UserRole, "all")
        self.build_tree(all_items_node, None)
        self.category_tree.expandAll()
        if current_selection:
            items = self.category_tree.findItems(str(current_selection), Qt.MatchFlag.Recursive | Qt.MatchFlag.MatchExactly, column=0)
            if items: self.category_tree.setCurrentItem(items[0])
    def build_tree(self, parent_item, parent_id):
        children = [cat for cat in self.categories if cat['parent_id'] == parent_id]
        for child_cat in sorted(children, key=lambda x: x['name']):
            child_item = QTreeWidgetItem(parent_item, [child_cat['name']])
            child_item.setData(0, Qt.ItemDataRole.UserRole, child_cat['id'])
            self.build_tree(child_item, child_cat['id'])

# MalManagerWidget sinfi olduğu kimi qalır
class MalManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        self.list_widget = MalListWidget()
        main_layout.addWidget(self.list_widget)