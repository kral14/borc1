# borc/themes.py

# Dəyişənlər: 
# @@FONT_SIZE@@: Yazı ölçüsü
# @@PADDING_V@@: Şaquli daxili boşluq
# @@PADDING_H@@: Üfüqi daxili boşluq
# @@RADIUS@@: Künclərin yumruqluğu
# @@MARGIN@@: Elementlər arası kiçik məsafə
# @@NAV_PADDING_V@@: Naviqasiya düymələrinin şaquli boşluğu
# @@NAV_PADDING_H@@: Naviqasiya düymələrinin üfüqi boşluğu

# --- QARA TEMA ŞABLONU ---
DARK_TEMPLATE = """
/* --- ÜMUMİ ELEMENTLƏR --- */
QWidget {
    color: #e0e0e0;
    background-color: #2c2c2c;
    font-size: @@FONT_SIZE@@pt;
    border: none;
}
QGroupBox {
    background-color: #383838;
    border: 1px solid #555555;
    border-radius: @@RADIUS@@px;
    margin-top: 1ex;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 @@PADDING_H@@px;
    background-color: #555555;
    border-radius: @@RADIUS@@px;
}
QLabel {
    background-color: transparent;
    font-weight: normal;
    padding: @@MARGIN@@px;
}
QLabel#label_total_amount { color: #28a745; font-weight: bold; }
QLabel#label_total_discount_amount { color: #ffc107; font-weight: bold; }
QLabel#label_total, QLabel#label_total_discount { font-weight: bold; }

/* Form Elementləri */
QLineEdit, QComboBox, QTextEdit, QDateEdit, QSpinBox, QDoubleSpinBox {
    padding: @@PADDING_V@@px;
    border: 1px solid #555555;
    border-radius: @@RADIUS@@px;
    background-color: #4a4a4a;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #007bff;
}
QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left-width: 1px;
    border-left-color: #555555;
    border-left-style: solid;
}

/* --- CƏDVƏLLƏR --- */
QTableWidget {
    background-color: #3C3C3C;
    alternate-background-color: #464646;
    gridline-color: #5A5A5A;
    border: 1px solid #5A5A5A;
}
QTableWidget::item {
    padding: @@PADDING_V@@px;
}
QTableWidget::item:selected {
    background-color: #007BFF;
    color: white;
}
QHeaderView::section {
    background-color: #555555;
    color: #e0e0e0;
    padding: @@PADDING_V@@px;
    border: 1px solid #666666;
    font-weight: bold;
}

/* --- DÜYMƏLƏR VƏ TOOLBAR --- */
QPushButton {
    background-color: #007BFF;
    color: white;
    border-radius: @@RADIUS@@px;
    padding: @@PADDING_V@@px @@PADDING_H@@px;
    font-weight: bold;
}
QPushButton:hover { background-color: #0056b3; }
QPushButton#btn_cancel { background-color: #6c757d; }
QPushButton#btn_cancel:hover { background-color: #5a6268; }

QToolBar {
    background-color: transparent;
    border: none;
}
/* Üst Naviqasiya Paneli */
QToolBar#MainNavBar QToolButton {
    padding: @@NAV_PADDING_V@@px @@NAV_PADDING_H@@px;
    border: 1px solid #3e3e42;
    background-color: #3e3e42;
    border-radius: @@RADIUS@@px;
    color: #ccc;
    font-weight: bold;
    margin-right: @@MARGIN@@px;
}
QToolBar#MainNavBar QToolButton:hover { background-color: #4f4f53; }
QToolBar#MainNavBar QToolButton:pressed { background-color: #007acc; }
QToolBar#MainNavBar QToolButton::menu-indicator { image: none; }

/* Cədvəl və Form daxilindəki kiçik düymələr */
QToolButton {
    padding: @@PADDING_V@@px;
    margin: @@MARGIN@@px;
    border: 1px solid #555555;
    border-radius: @@RADIUS@@px;
    background-color: #4a4a4a;
}
QToolButton:hover { background-color: #5a5a5a; }

/* --- PƏNCƏRƏ ELEMENTLƏRİ --- */
QTabWidget::pane { border-top: 2px solid #555555; }
QTabBar::tab {
    background: #383838;
    border: 1px solid #555555;
    border-bottom-color: #2c2c2c; /* Pane-nin borderi ilə birləşsin deyə */
    border-top-left-radius: @@RADIUS@@px;
    border-top-right-radius: @@RADIUS@@px;
    padding: @@PADDING_V@@px @@PADDING_H@@px;
}
QTabBar::tab:selected, QTabBar::tab:hover { background: #4a4a4a; }
QTabBar::tab:selected { border-bottom-color: #4a4a4a; } /* Seçilən tab pane ilə birləşik görünsün */

QMdiSubWindow {
    border: 1px solid #666666;
    border-radius: @@RADIUS@@px;
}
QMdiSubWindow::titleBar {
    background-color: #3e3e42;
    color: #e0e0e0;
    padding: @@MARGIN@@px;
}
QMdiArea { background-color: #252526; }
QMenuBar { background-color: #2d2d30; color: #ccc; }
QMenuBar::item:selected { background-color: #3e3e42; }
QMenu { background-color: #2d2d30; color: #ccc; border: 1px solid #000; }
QMenu::item:selected { background-color: #007acc; }
QStatusBar { color: #CCCCCC; }
QSplitter::handle { background-color: #555555; }
QSplitter::handle:hover { background-color: #666666; }
"""

# --- AĞ TEMA ŞABLONU ---
LIGHT_TEMPLATE = """
QWidget {
    color: #000000;
    background-color: #FDFDFD;
    font-size: @@FONT_SIZE@@pt;
    border: none;
}
QGroupBox {
    background-color: #F0F0F0;
    border: 1px solid #CCCCCC;
    border-radius: @@RADIUS@@px;
    margin-top: 1ex;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 @@PADDING_H@@px;
    background-color: #E0E0E0;
    border-radius: @@RADIUS@@px;
}
QLabel { background-color: transparent; padding: @@MARGIN@@px; }
QLabel#label_total_amount { color: #1E8449; font-weight: bold; }
QLabel#label_total_discount_amount { color: #D35400; font-weight: bold; }
QLabel#label_total, QLabel#label_total_discount { font-weight: bold; }

QLineEdit, QComboBox, QTextEdit, QDateEdit, QSpinBox, QDoubleSpinBox {
    padding: @@PADDING_V@@px;
    border: 1px solid #AAAAAA;
    border-radius: @@RADIUS@@px;
    background-color: #FFFFFF;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #0078d7;
}
QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left-width: 1px;
    border-left-color: #AAAAAA;
    border-left-style: solid;
}

QTableWidget {
    background-color: #FFFFFF;
    alternate-background-color: #F8F8F8;
    gridline-color: #E0E0E0;
    border: 1px solid #CCCCCC;
}
QTableWidget::item { padding: @@PADDING_V@@px; }
QTableWidget::item:selected { background-color: #0078d7; color: white; }

QHeaderView::section {
    background-color: #E8E8E8;
    color: #000000;
    padding: @@PADDING_V@@px;
    border: 1px solid #CCCCCC;
    font-weight: bold;
}

QPushButton {
    background-color: #0078d7;
    color: white;
    border-radius: @@RADIUS@@px;
    padding: @@PADDING_V@@px @@PADDING_H@@px;
    font-weight: bold;
}
QPushButton:hover { background-color: #005ecb; }
QPushButton#btn_cancel { background-color: #7f8c8d; }
QPushButton#btn_cancel:hover { background-color: #616A6B; }

QToolBar { background-color: #F0F0F0; border: none; }

QToolBar#MainNavBar QToolButton {
    padding: @@NAV_PADDING_V@@px @@NAV_PADDING_H@@px;
    border: 1px solid #c0c0c0;
    background-color: #f0f0f0;
    border-radius: @@RADIUS@@px;
    color: #000000;
    font-weight: bold;
    margin-right: @@MARGIN@@px;
}
QToolBar#MainNavBar QToolButton:hover { background-color: #e0e0e0; }
QToolBar#MainNavBar QToolButton:pressed { background-color: #0078d7; color: white; }
QToolBar#MainNavBar QToolButton::menu-indicator { image: none; }

QToolButton {
    padding: @@PADDING_V@@px;
    margin: @@MARGIN@@px;
    border: 1px solid #c0c0c0;
    border-radius: @@RADIUS@@px;
    background-color: #E8E8E8;
}
QToolButton:hover { background-color: #DDEEFF; }

QTabBar::tab {
    background: #E0E0E0;
    border: 1px solid #CCCCCC;
    border-bottom: none;
    padding: @@PADDING_V@@px @@PADDING_H@@px;
    border-top-left-radius: @@RADIUS@@px;
    border-top-right-radius: @@RADIUS@@px;
}
QTabBar::tab:selected, QTabBar::tab:hover { background: #FFFFFF; }

QMdiSubWindow { border: 1px solid #AAAAAA; border-radius: @@RADIUS@@px; }
QMdiSubWindow::titleBar { background-color: #E0E0E0; color: #000000; padding: @@MARGIN@@px; }
QMdiArea { background-color: #D6D6D6; }
QMenuBar { background-color: #F0F0F0; color: #000000; }
QMenuBar::item:selected { background-color: #DDEEFF; }
QMenu { background-color: #FFFFFF; color: #000000; border: 1px solid #CCCCCC; }
QMenu::item:selected { background-color: #0078d7; color: #FFFFFF; }
QStatusBar { color: #000000; }
QSplitter::handle { background-color: #D0D0D0; }
QSplitter::handle:hover { background-color: #B0B0B0; }
"""