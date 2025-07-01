# app_mal_widget.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, 
                             QStackedWidget, QMessageBox, QAbstractItemView, QHeaderView, QStyle, QToolButton,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, QSize, Qt

import database
from ui_mal_form import Ui_MalForm

class MalFormWidget(QWidget):
    form_closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.ui = Ui_MalForm(); self.ui.setupUi(self)
        self.current_product_id = None
        
        self.ui.btn_save.clicked.connect(self.save_product)
        self.ui.btn_cancel.clicked.connect(self.close_form)
        self.load_suppliers_to_combobox()
        self.load_categories_to_combobox()

    def load_suppliers_to_combobox(self):
        self.ui.combo_supplier.clear()
        self.ui.combo_supplier.addItem("Satıcı seçin...", None)
        suppliers = database.get_all_suppliers()
        for supplier in suppliers:
            self.ui.combo_supplier.addItem(supplier['name'], supplier['id'])

    def load_categories_to_combobox(self):
        self.ui.combo_category.clear()
        self.ui.combo_category.addItem("Kateqoriya/Qovluq seçin...", None)
        categories = database.get_all_categories()
        
        root_categories = [c for c in categories if c['parent_id'] is None]
        for category in sorted(root_categories, key=lambda x: x['name']):
            self.ui.combo_category.addItem(category['name'], category['id'])
            sub_categories = [c for c in categories if c['parent_id'] == category['id']]
            for sub_category in sorted(sub_categories, key=lambda x: x['name']):
                self.ui.combo_category.addItem(f"  - {sub_category['name']}", sub_category['id'])

    def set_edit_mode(self, product_id):
        self.load_suppliers_to_combobox()
        self.load_categories_to_combobox()
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

    def set_add_mode(self):
        self.load_suppliers_to_combobox()
        self.load_categories_to_combobox()
        self.current_product_id = None
        for w in [self.ui.edit_name, self.ui.edit_barcode, self.ui.edit_code, self.ui.edit_article]: w.clear()
        self.ui.spin_purchase_price.setValue(0); self.ui.spin_sale_price.setValue(0); self.ui.spin_stock.setValue(0)
        self.ui.combo_supplier.setCurrentIndex(0); self.ui.combo_category.setCurrentIndex(0)

    def save_product(self):
        name = self.ui.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Xəta", "Mal adı boş ola bilməz."); return

        args = (
            name, self.ui.edit_barcode.text().strip(), self.ui.edit_code.text().strip(),
            self.ui.edit_article.text().strip(), self.ui.combo_category.currentData(),
            self.ui.combo_supplier.currentData(), self.ui.spin_purchase_price.value(),
            self.ui.spin_sale_price.value(), self.ui.spin_stock.value()
        )
        if self.current_product_id is None:
            success = database.add_product(*args)
        else:
            success = database.update_product(self.current_product_id, *args)
        
        if success:
            QMessageBox.information(self, "Uğurlu", "Məlumatlar yadda saxlanıldı."); self.close_form()
        else:
            QMessageBox.critical(self, "Xəta", "Əməliyyat zamanı xəta baş verdi.")

    def close_form(self): self.form_closed.emit()


class MalListWidget(QWidget):
    def __init__(self, stacked_widget, form_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.form_widget = form_widget
        self.all_products = []
        self.categories = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5); main_layout.setSpacing(10)
        
        toolbar = QToolBar("Mal Əməliyyatları")
        toolbar.setIconSize(QSize(24, 24)); toolbar.setStyleSheet("QToolBar { border: none; }")
        
        style = self.style()
        self.action_add_category = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DirIcon), "Yeni Qovluq", self)
        self.action_add = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Yeni Mal", self)
        self.action_edit = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Düzəliş Et", self)
        self.action_delete = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "Sil", self)

        for action in [self.action_add_category, self.action_add, self.action_edit, self.action_delete]:
            toolbar.addAction(action)
        main_layout.addWidget(toolbar)
        
        self.action_add_category.triggered.connect(self.add_new_category)
        self.action_add.triggered.connect(self.add_new_product)
        self.action_edit.triggered.connect(self.edit_product)
        self.action_delete.triggered.connect(self.delete_product)

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
        self.table_widget.itemDoubleClicked.connect(lambda: self.edit_product())
        self.splitter.addWidget(self.table_widget)
        self.splitter.setSizes([250, 750])

        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Adı", "Barkod", "Kateqoriya", "Alındığı Yer", "Alış Qiyməti", "Satış Qiyməti", "Stok"])
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_widget.hideColumn(0)
        
        self.table_widget.setStyleSheet("QTableWidget{background-color:#3C3C3C;alternate-background-color:#464646;gridline-color:#5A5A5A;color:#FFFFFF;border:1px solid #5A5A5A;font-size:11pt} QTableWidget::item{padding:5px} QHeaderView::section{background-color:#555555;color:#FFFFFF;padding:5px;border:1px solid #666666;font-weight:bold} QTableWidget::item:selected{background-color:#007BFF;color:white}")
        self.load_data()

    def build_tree(self, parent_item, parent_id):
        children = [cat for cat in self.categories if cat['parent_id'] == parent_id]
        for child_cat in children:
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
        if not current: return
        category_id = current.data(0, Qt.ItemDataRole.UserRole)
        
        if category_id == "all":
            self.display_products(self.all_products)
        else:
            filtered_products = [p for p in self.all_products if p.get('category_id') == category_id]
            self.display_products(filtered_products)

    def display_products(self, products):
        self.table_widget.setRowCount(0)
        if not products: return

        for row, p in enumerate(products):
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(p['id'])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(p.get('name', '')))
            self.table_widget.setItem(row, 2, QTableWidgetItem(p.get('barcode', '')))
            self.table_widget.setItem(row, 3, QTableWidgetItem(p.get('category_name', '')))
            self.table_widget.setItem(row, 4, QTableWidgetItem(p.get('supplier_name', '')))
            self.table_widget.setItem(row, 5, QTableWidgetItem(f"{p.get('purchase_price', 0):.2f} AZN"))
            self.table_widget.setItem(row, 6, QTableWidgetItem(f"{p.get('sale_price', 0):.2f} AZN"))
            self.table_widget.setItem(row, 7, QTableWidgetItem(str(p.get('stock', 0))))

    def load_data(self):
        self.populate_category_tree()
        self.all_products = database.get_all_products()
        
        current_item = self.category_tree.currentItem()
        if not current_item:
            self.category_tree.setCurrentItem(self.category_tree.topLevelItem(0))
        else:
            self.on_category_selected(current_item, None)

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
            if database.update_category_name(category_id, text): self.load_data()
            else: QMessageBox.critical(self, "Xəta", "Ad dəyişdirilərkən xəta baş verdi.")

    def delete_category(self, item):
        category_id = item.data(0, Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', f"'{item.text(0)}' qovluğunu silməyə əminsinizmi? Bu qovluqdakı məhsullar kateqoriyasız qalacaq.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_category(category_id): self.load_data()
            else: QMessageBox.critical(self, "Xəta", "Silmə zamanı xəta baş verdi. İçində alt-qovluqlar ola bilər.")

    def add_new_product(self):
        self.form_widget.set_add_mode()
        self.stacked_widget.setCurrentWidget(self.form_widget)
        
    def edit_product(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0: QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, düzəliş etmək üçün bir mal seçin."); return
        product_id = int(self.table_widget.item(selected_row, 0).text())
        self.form_widget.set_edit_mode(product_id)
        self.stacked_widget.setCurrentWidget(self.form_widget)
        
    def delete_product(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0: QMessageBox.warning(self, "Xəbərdarlıq", "Zəhmət olmasa, silmək üçün bir mal seçin."); return
        product_id = int(self.table_widget.item(selected_row, 0).text())
        product_name = self.table_widget.item(selected_row, 1).text()
        reply = QMessageBox.question(self, 'Silməni Təsdiqlə', f"'{product_name}' adlı malı silməyə əminsinizmi?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if database.delete_product(product_id): self.load_data(); QMessageBox.information(self, "Uğurlu", "Mal silindi.")
            else: QMessageBox.critical(self, "Xəta", "Malı silmək mümkün olmadı.")

class MalManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.form_widget = MalFormWidget()
        self.list_widget = MalListWidget(self.stacked_widget, self.form_widget)
        self.stacked_widget.addWidget(self.list_widget); self.stacked_widget.addWidget(self.form_widget)
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0,0,0,0); main_layout.addWidget(self.stacked_widget)
        self.form_widget.form_closed.connect(self.show_list_and_refresh)
        
    def show_list_and_refresh(self):
        self.list_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.list_widget)