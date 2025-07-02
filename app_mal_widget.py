# app_mal_widget.py

# DÜZƏLİŞ: Unudulmuş importlar bura əlavə edildi
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem,
                             QStackedWidget, QMessageBox, QAbstractItemView, QHeaderView, QStyle, QToolButton,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog, QLabel, QLineEdit)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import pyqtSignal, QSize, Qt

import database
from ui_mal_form import Ui_MalForm

class MalFormWidget(QWidget):
    form_closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.ui = Ui_MalForm()
        self.ui.setupUi(self)
        self.current_product_id = None
        self.dynamic_widgets = []

        self.ui.btn_save.clicked.connect(self.save_product)
        self.ui.btn_cancel.clicked.connect(self.close_form)

    def _clear_dynamic_widgets(self):
        for widget_list in self.dynamic_widgets:
            if widget_list['label']:
                widget_list['label'].deleteLater()
            if widget_list['widget']:
                widget_list['widget'].deleteLater()
        self.dynamic_widgets = []

    def _create_dynamic_widgets(self, product_data=None):
        self._clear_dynamic_widgets()
        
        custom_fields = database.get_custom_field_definitions()
        if not custom_fields:
            return

        product_attributes = {}
        if product_data and product_data.get('custom_attributes'):
             product_attributes = product_data.get('custom_attributes')

        for field in custom_fields:
            label = QLabel(f"{field['field_name']}:", self)
            line_edit = QLineEdit(self)

            if field['field_key'] in product_attributes:
                line_edit.setText(str(product_attributes[field['field_key']]))

            line_edit.setProperty("field_key", field['field_key'])
            
            self.ui.formLayout.addRow(label, line_edit)
            self.dynamic_widgets.append({'label': label, 'widget': line_edit})

    def set_edit_mode(self, product_id):
        self.load_comboboxes()
        self.current_product_id = product_id
        product = database.get_product_by_id(product_id)
        if product:
            self.ui.edit_name.setText(product['name'])
            self.ui.edit_barcode.setText(product.get('barcode', ''))
            self.ui.edit_code.setText(product.get('product_code', ''))
            self.ui.edit_article.setText(product.get('article', ''))
            self.ui.spin_purchase_price.setValue(product.get('purchase_price', 0))
            self.ui.spin_sale_price.setValue(product.get('sale_price', 0))
            self.ui.spin_stock.setValue(product.get('stock', 0))
            
            supplier_id = product.get('supplier_id')
            if supplier_id:
                index = self.ui.combo_supplier.findData(supplier_id)
                if index != -1: self.ui.combo_supplier.setCurrentIndex(index)
            
            category_id = product.get('category_id')
            if category_id:
                index = self.ui.combo_category.findData(category_id)
                if index != -1: self.ui.combo_category.setCurrentIndex(index)
            
            self._create_dynamic_widgets(product)

    def set_add_mode(self):
        self.load_comboboxes()
        self.current_product_id = None
        for w in [self.ui.edit_name, self.ui.edit_barcode, self.ui.edit_code, self.ui.edit_article]: w.clear()
        self.ui.spin_purchase_price.setValue(0)
        self.ui.spin_sale_price.setValue(0)
        self.ui.spin_stock.setValue(0)
        self.ui.combo_supplier.setCurrentIndex(0)
        self.ui.combo_category.setCurrentIndex(0)
        self._create_dynamic_widgets()

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
            root_categories = [c for c in categories if c['parent_id'] is None]
            for category in sorted(root_categories, key=lambda x: x['name']):
                self.ui.combo_category.addItem(category['name'], category['id'])
                sub_categories = [c for c in categories if c['parent_id'] == category['id']]
                for sub_category in sorted(sub_categories, key=lambda x: x['name']):
                    self.ui.combo_category.addItem(f"  - {sub_category['name']}", sub_category['id'])

    def save_product(self):
        name = self.ui.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Xəta", "Mal adı boş ola bilməz.")
            return

        custom_attributes = {}
        for item in self.dynamic_widgets:
            line_edit = item['widget']
            field_key = line_edit.property("field_key")
            value = line_edit.text().strip()
            if field_key and value:
                custom_attributes[field_key] = value

        args = (
            name, self.ui.edit_barcode.text().strip(), self.ui.edit_code.text().strip(),
            self.ui.edit_article.text().strip(), self.ui.combo_category.currentData(),
            self.ui.combo_supplier.currentData(), self.ui.spin_purchase_price.value(),
            self.ui.spin_sale_price.value(), self.ui.spin_stock.value(),
            custom_attributes
        )

        if self.current_product_id is None:
            success = database.add_product(*args)
        else:
            success = database.update_product(self.current_product_id, *args)
        
        if success:
            QMessageBox.information(self, "Uğurlu", "Məlumatlar yadda saxlanıldı.")
            self.close_form()
        else:
            QMessageBox.critical(self, "Xəta", "Əməliyyat zamanı xəta baş verdi.")

    def close_form(self):
        self._clear_dynamic_widgets()
        self.form_closed.emit()


class MalListWidget(QWidget):
    def __init__(self, stacked_widget, form_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.form_widget = form_widget
        self.all_products = []
        self.categories = []
        self.column_map = {}
        self.master_column_list = []

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
        self.category_tree.currentItemChanged.connect(self.on_category_selected)

        self.table_widget = QTableWidget()
        self.table_widget.itemDoubleClicked.connect(self.edit_product)
        self.splitter.addWidget(self.table_widget)
        self.splitter.setSizes([250, 750])

        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet("QTableWidget { background-color: #3C3C3C; alternate-background-color: #464646; gridline-color: #5A5A5A; color: #FFFFFF; border: 1px solid #5A5A5A; font-size: 11pt; } QTableWidget::item { padding: 5px; } QHeaderView::section { background-color: #555555; color: #FFFFFF; padding: 5px; border: 1px solid #666666; font-weight: bold; } QTableWidget::item:selected { background-color: #007BFF; color: white; }")
        
        self.load_data()

    def setup_columns(self):
        from column_settings_dialog import load_table_settings
        
        standard_columns = [
            {'key': 'id', 'header': 'ID', 'default_visible': False},
            {'key': 'name', 'header': 'Adı', 'default_visible': True, 'default_width': 250},
            {'key': 'barcode', 'header': 'Barkod', 'default_visible': True, 'default_width': 120},
            {'key': 'category_name', 'header': 'Kateqoriya', 'default_visible': False},
            {'key': 'supplier_name', 'header': 'Alındığı Yer', 'default_visible': False},
            {'key': 'purchase_price', 'header': 'Alış Qiyməti', 'default_visible': True, 'default_width': 100},
            {'key': 'sale_price', 'header': 'Satış Qiyməti', 'default_visible': True, 'default_width': 100},
            {'key': 'stock', 'header': 'Stok', 'default_visible': True, 'default_width': 80},
        ]
        
        custom_fields = database.get_custom_field_definitions()
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

    def open_column_settings(self):
        from column_settings_dialog import ColumnSettingsDialog
        self.setup_columns() 
        dialog = ColumnSettingsDialog("MalListTable", self.master_column_list, self)
        if dialog.exec():
            self.setup_columns()
            self.display_products_for_current_category()

    def display_products_for_current_category(self):
        current_item = self.category_tree.currentItem()
        if current_item:
            self.on_category_selected(current_item, None)
        elif self.all_products:
            self.display_products(self.all_products)

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
        else:
            self.display_products_for_current_category()

    def build_tree(self, parent_item, parent_id):
        children = [cat for cat in self.categories if cat['parent_id'] == parent_id]
        for child_cat in sorted(children, key=lambda x: x['name']):
            child_item = QTreeWidgetItem(parent_item, [child_cat['name']])
            child_item.setData(0, Qt.ItemDataRole.UserRole, child_cat['id'])
            self.build_tree(child_item, child_cat['id'])

    def populate_category_tree(self):
        self.category_tree.clear()
        self.categories = database.get_all_categories()
        all_items_node = QTreeWidgetItem(self.category_tree, ["Bütün Mallar"])
        all_items_node.setData(0, Qt.ItemDataRole.UserRole, "all")
        self.build_tree(all_items_node, None)
        self.category_tree.expandAll()

    def on_category_selected(self, current, previous):
        if not current: 
            self.display_products(self.all_products)
            return
            
        category_id = current.data(0, Qt.ItemDataRole.UserRole)
        
        if category_id == "all":
            self.display_products(self.all_products)
        else:
            filtered_products = [p for p in self.all_products if p.get('category_id') == category_id]
            self.display_products(filtered_products)

    def add_new_category(self):
        parent_item = self.category_tree.currentItem()
        parent_id = parent_item.data(0, Qt.ItemDataRole.UserRole) if parent_item and parent_item.data(0, Qt.ItemDataRole.UserRole) != "all" else None
        
        text, ok = QInputDialog.getText(self, 'Yeni Qovluq', 'Qovluğun adını daxil edin:')
        if ok and text:
            if database.add_category(text, parent_id): 
                self.load_data()
            else: 
                QMessageBox.critical(self, "Xəta", "Qovluq yaradılarkən xəta baş verdi.")

    def show_category_context_menu(self, position):
        item = self.category_tree.itemAt(position)
        if item and item.data(0, Qt.ItemDataRole.UserRole) != "all":
            menu = QMenu()
            rename_action = menu.addAction("Adını dəyiş")
            delete_action = menu.addAction("Sil")
            action = menu.exec(self.category_tree.mapToGlobal(position))
            if action == rename_action: self.rename_category(item)
            elif action == delete_action: self.delete_category(item)

    def rename_category(self, item):
        category_id = item.data(0, Qt.ItemDataRole.UserRole)
        old_name = item.text(0)
        text, ok = QInputDialog.getText(self, 'Adını Dəyiş', 'Yeni adı daxil edin:', text=old_name)
        if ok and text and text != old_name:
            if database.update_category_name(category_id, text): 
                self.load_data()
            else: 
                QMessageBox.critical(self, "Xəta", "Ad dəyişdirilərkən xəta baş verdi.")

    def delete_category(self, item):
        category_id = item.data(0, Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', f"'{item.text(0)}' qovluğunu silməyə əminsinizmi?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_category(category_id): 
                self.load_data()
            else: 
                QMessageBox.critical(self, "Xəta", "Silmə zamanı xəta baş verdi.")

    def add_new_product(self):
        self.form_widget.set_add_mode()
        self.stacked_widget.setCurrentWidget(self.form_widget)
        
    def edit_product(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0: 
            QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, düzəliş etmək üçün bir mal seçin.")
            return
        
        id_col_index = self.column_map.get('id')
        if id_col_index is None:
            QMessageBox.critical(self, "Konfiqurasiya Xətası", "Cədvəldə 'ID' sütunu tapılmadı. Sütun ayarlarını yoxlayın.")
            return

        product_id_item = self.table_widget.item(selected_row, id_col_index)
        if product_id_item is None: return

        product_id = int(product_id_item.text())
        self.form_widget.set_edit_mode(product_id)
        self.stacked_widget.setCurrentWidget(self.form_widget)
        
    def delete_product(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0: 
            QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, silmək üçün bir mal seçin.")
            return

        id_col_index = self.column_map.get('id')
        name_col_index = self.column_map.get('name')
        if id_col_index is None or name_col_index is None:
            QMessageBox.critical(self, "Konfiqurasiya Xətası", "Cədvəldə 'ID' və ya 'Ad' sütunu tapılmadı.")
            return

        product_id_item = self.table_widget.item(selected_row, id_col_index)
        product_name_item = self.table_widget.item(selected_row, name_col_index)
        if product_id_item is None or product_name_item is None: return

        product_id = int(product_id_item.text())
        product_name = product_name_item.text()

        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', f"'{product_name}' adlı malı silməyə əminsinizmi?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_product(product_id): 
                self.load_data()
                QMessageBox.information(self, "Uğurlu", "Mal silindi.")
            else: 
                QMessageBox.critical(self, "Xəta", "Malı silmək mümkün olmadı.")

class MalManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.form_widget = MalFormWidget()
        self.list_widget = MalListWidget(self.stacked_widget, self.form_widget)
        self.stacked_widget.addWidget(self.list_widget)
        self.stacked_widget.addWidget(self.form_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.stacked_widget)
        self.form_widget.form_closed.connect(self.show_list_and_refresh)
        
    def show_list_and_refresh(self):
        self.list_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.list_widget)