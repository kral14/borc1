# ui_satis_qaime_form.py

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_SatisQaimeForm(object):
    def setupUi(self, SatisQaimeForm):
        SatisQaimeForm.setObjectName("SatisQaimeForm")
        SatisQaimeForm.resize(900, 750)
        # Stil kodu Alış Qaiməsi ilə eyniləşdirildi
        SatisQaimeForm.setStyleSheet("""
            QWidget {
                color: #e0e0e0;
                background-color: #2c2c2c;
                font-size: 11pt;
            }
            QGroupBox {
                background-color: #383838;
                border: 1px solid #555555;
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #555555;
                border-radius: 4px;
            }
            QLabel {
                background-color: transparent;
                font-weight: normal;
            }
            QLabel#label_total, QLabel#label_total_discount, QLabel#label_total_amount, QLabel#label_total_discount_amount {
                font-weight: bold;
            }
            QLineEdit, QComboBox, QTextEdit, QDateEdit {
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #4a4a4a;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 22px;
                border-left-width: 1px;
                border-left-color: #555555;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QDateEdit::down-arrow {
                image: url(./icons/down-arrow.png);
            }
            QDateEdit::drop-down:hover {
                background-color: #5a5a5a;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 1px solid #007bff;
            }
            QTableWidget {
                background-color: #3C3C3C;
                alternate-background-color: #464646;
                gridline-color: #5A5A5A;
                border: 1px solid #5A5A5A;
            }
            QHeaderView::section {
                background-color: #555555;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #666666;
                font-weight: bold;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0056b3; }
            QToolBar { background-color: transparent; border: none; }
            QToolButton {
                background-color: #4a4a4a;
                border: 1px solid #555555;
                border-radius: 4px; padding: 4px;
            }
            QToolButton:hover { background-color: #5a5a5a; }
        """)
        
        # Əsas layout Alış Qaiməsi ilə eyniləşdirildi
        self.verticalLayout = QtWidgets.QVBoxLayout(SatisQaimeForm)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName("verticalLayout")

        # Ümumi məlumatlar üçün GroupBox
        self.group_info = QtWidgets.QGroupBox(parent=SatisQaimeForm)
        self.group_info.setObjectName("group_info")
        self.gridLayout = QtWidgets.QGridLayout(self.group_info)
        
        # Elementlər QGridLayout içinə yerləşdirildi
        self.label_date = QtWidgets.QLabel(parent=self.group_info)
        self.gridLayout.addWidget(self.label_date, 0, 0, 1, 1)
        self.date_edit = QtWidgets.QDateEdit(parent=self.group_info)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.gridLayout.addWidget(self.date_edit, 0, 1, 1, 1)

        self.label_customer = QtWidgets.QLabel(parent=self.group_info)
        self.gridLayout.addWidget(self.label_customer, 1, 0, 1, 1)
        self.combo_customer = QtWidgets.QComboBox(parent=self.group_info)
        self.gridLayout.addWidget(self.combo_customer, 1, 1, 1, 1)
        
        self.label_invoice_no = QtWidgets.QLabel(parent=self.group_info)
        self.gridLayout.addWidget(self.label_invoice_no, 2, 0, 1, 1)
        self.edit_invoice_no = QtWidgets.QLineEdit(parent=self.group_info)
        self.gridLayout.addWidget(self.edit_invoice_no, 2, 1, 1, 1)

        # Son ödəmə tarixi əlavə edildi
        self.label_due_date = QtWidgets.QLabel(parent=self.group_info)
        self.gridLayout.addWidget(self.label_due_date, 3, 0, 1, 1)
        self.date_due = QtWidgets.QDateEdit(parent=self.group_info)
        self.date_due.setCalendarPopup(True)
        self.gridLayout.addWidget(self.date_due, 3, 1, 1, 1)
        
        # Qeyd sahəsi əlavə edildi
        self.label_notes = QtWidgets.QLabel(parent=self.group_info)
        self.gridLayout.addWidget(self.label_notes, 0, 2, 1, 1, QtCore.Qt.AlignmentFlag.AlignBottom)
        self.edit_notes = QtWidgets.QTextEdit(parent=self.group_info)
        self.gridLayout.addWidget(self.edit_notes, 1, 2, 3, 1)

        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 2)
        self.verticalLayout.addWidget(self.group_info)
        
        # Məhsullar üçün GroupBox
        self.group_items = QtWidgets.QGroupBox(parent=SatisQaimeForm)
        self.group_items.setObjectName("group_items")
        self.items_v_layout = QtWidgets.QVBoxLayout(self.group_items)
        
        self.table_toolbar = QtWidgets.QToolBar(parent=self.group_items)
        self.table_toolbar.setIconSize(QtCore.QSize(20, 20))
        self.items_v_layout.addWidget(self.table_toolbar)

        self.table_items = QtWidgets.QTableWidget(parent=self.group_items)
        self.table_items.setObjectName("table_items")
        self.table_items.setColumnCount(7)
        self.table_items.setHorizontalHeaderLabels(["Mal ID", "Malın Adı", "Sayı", "Satış Qiyməti", "Endirim %", "Son Qiymət", "Yekun Məbləğ"])
        self.table_items.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table_items.verticalHeader().setVisible(False)
        self.items_v_layout.addWidget(self.table_items)
        self.verticalLayout.addWidget(self.group_items)
        self.verticalLayout.setStretch(1, 1)

        # Alt bar (footer) Alış Qaiməsi ilə eyniləşdirildi
        self.bottom_bar_layout = QtWidgets.QHBoxLayout()
        
        self.label_total_discount = QtWidgets.QLabel(parent=SatisQaimeForm)
        self.bottom_bar_layout.addWidget(self.label_total_discount)
        self.label_total_discount_amount = QtWidgets.QLabel(parent=SatisQaimeForm)
        self.label_total_discount_amount.setStyleSheet("color: #ffc107;")
        self.bottom_bar_layout.addWidget(self.label_total_discount_amount)
        
        spacerItem_middle = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.bottom_bar_layout.addItem(spacerItem_middle)

        self.label_total = QtWidgets.QLabel(parent=SatisQaimeForm)
        self.bottom_bar_layout.addWidget(self.label_total)
        self.label_total_amount = QtWidgets.QLabel(parent=SatisQaimeForm)
        font = QtGui.QFont(); font.setPointSize(14); font.setBold(True)
        self.label_total_amount.setFont(font)
        self.label_total_amount.setStyleSheet("color: #28a745;")
        self.bottom_bar_layout.addWidget(self.label_total_amount)

        spacerItem_end = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.bottom_bar_layout.addItem(spacerItem_end)
        
        self.btn_save = QtWidgets.QPushButton(parent=SatisQaimeForm)
        self.bottom_bar_layout.addWidget(self.btn_save)
        self.btn_cancel = QtWidgets.QPushButton(parent=SatisQaimeForm)
        self.btn_cancel.setStyleSheet("background-color: #6c757d;")
        self.bottom_bar_layout.addWidget(self.btn_cancel)
        
        self.verticalLayout.addLayout(self.bottom_bar_layout)
        
        # Toolbar düymələri
        self.action_add_row = QtGui.QAction(parent=SatisQaimeForm)
        self.action_delete_row = QtGui.QAction(parent=SatisQaimeForm)
        self.table_toolbar.addAction(self.action_add_row)
        self.table_toolbar.addAction(self.action_delete_row)

        self.retranslateUi(SatisQaimeForm)
        QtCore.QMetaObject.connectSlotsByName(SatisQaimeForm)

    def retranslateUi(self, SatisQaimeForm):
        _translate = QtCore.QCoreApplication.translate
        SatisQaimeForm.setWindowTitle(_translate("SatisQaimeForm", "Satış Qaiməsi"))
        self.group_info.setTitle(_translate("SatisQaimeForm", "Ümumi Məlumatlar"))
        self.label_date.setText(_translate("SatisQaimeForm", "Qaimə Tarixi:"))
        self.label_customer.setText(_translate("SatisQaimeForm", "Müştəri:"))
        self.label_invoice_no.setText(_translate("SatisQaimeForm", "Qaimə №:"))
        self.label_due_date.setText(_translate("SatisQaimeForm", "Son Ödəmə:"))
        self.label_notes.setText(_translate("SatisQaimeForm", "Qeyd:"))
        self.group_items.setTitle(_translate("SatisQaimeForm", "Məhsullar"))
        self.label_total_discount.setText(_translate("SatisQaimeForm", "Ümumi Endirim:"))
        self.label_total_discount_amount.setText(_translate("SatisQaimeForm", "0.00 AZN"))
        self.label_total.setText(_translate("SatisQaimeForm", "Yekun Məbləğ:"))
        self.label_total_amount.setText(_translate("SatisQaimeForm", "0.00 AZN"))
        self.btn_save.setText(_translate("SatisQaimeForm", "Yadda Saxla"))
        self.btn_cancel.setText(_translate("SatisQaimeForm", "Ləğv Et"))
        self.action_add_row.setText(_translate("SatisQaimeForm", "Sətir Əlavə Et"))
        self.action_delete_row.setText(_translate("SatisQaimeForm", "Sətiri Sil"))