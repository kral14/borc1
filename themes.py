# borc/themes.py

# Dəyişənlər: 
# @@FONT_SIZE@@: Yazı ölçüsü
# @@PADDING_V@@: Şaquli daxili boşluq
# @@PADDING_H@@: Üfüqi daxili boşluq
# @@RADIUS@@: Künclərin yumruqluğu
# @@MARGIN@@: Elementlər arası kiçik məsafə
# @@NAV_PADDING_V@@: Naviqasiya düymələrinin şaquli boşluğu
# @@NAV_PADDING_H@@: Naviqasiya düymələrinin üfüqi boşluğu

# --- QARA TEMA ŞABLONU (Dəyişiklik yoxdur) ---
DARK_TEMPLATE = """
/* --- ÜMUMİ ELEMENTLƏR --- */
QWidget {
    color: #e0e0e0;
    background-color: #1e1e1e; 
    font-size: @@FONT_SIZE@@pt;
    border: none;
}
QGroupBox {
    background-color: #252526;
    border: 1px solid #333333;
    border-radius: @@RADIUS@@px;
    margin-top: 1ex;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 @@PADDING_H@@px;
    background-color: #3c3c3c;
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
QLineEdit, QComboBox, QTextEdit, QDateEdit, QSpinBox, QDoubleSpinBox {
    padding: @@PADDING_V@@px;
    border: 1px solid #3c3c3c;
    border-radius: @@RADIUS@@px;
    background-color: #333333;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #007acc;
}
QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left-width: 1px;
    border-left-color: #3c3c3c;
    border-left-style: solid;
}
QTableWidget {
    background-color: #252526;
    alternate-background-color: #2a2a2a;
    gridline-color: #333333;
    border: 1px solid #333333;
}
QTableWidget::item {
    padding: @@PADDING_V@@px;
    border-bottom: 1px solid #333333;
}
QTableWidget::item:selected {
    background-color: #094771;
    color: white;
}
QHeaderView::section {
    background-color: #333333;
    color: #e0e0e0;
    padding: @@PADDING_V@@px;
    border: 1px solid #3c3c3c;
    font-weight: bold;
}
QPushButton {
    background-color: #007acc;
    color: white;
    border-radius: @@RADIUS@@px;
    padding: @@PADDING_V@@px @@PADDING_H@@px;
    font-weight: bold;
    border: none;
}
QPushButton:hover { background-color: #008ae6; }
QPushButton:pressed { background-color: #006bb2; }
QPushButton#btn_cancel { background-color: #555555; }
QPushButton#btn_cancel:hover { background-color: #666666; }
QToolBar#MainNavBar {
    background-color: #252526; 
    border-bottom: 1px solid #333333; 
    padding: @@MARGIN@@px;
    spacing: @@MARGIN@@px;
}
QToolBar#MainNavBar QToolButton {
    background-color: transparent; 
    border: none;
    padding: @@NAV_PADDING_V@@px @@NAV_PADDING_H@@px;
    border-radius: @@RADIUS@@px;
    color: #d0d0d0;
    font-weight: bold;
}
QToolBar#MainNavBar QToolButton:hover {
    background-color: #3c3c3c; 
    color: #ffffff;
}
QToolBar#MainNavBar QToolButton:pressed, QToolBar#MainNavBar QToolButton:checked {
    background-color: #007acc; 
    color: white;
}
QToolBar#MainNavBar QToolButton::menu-indicator { image: none; }
QMdiSubWindow QToolButton {
    padding: @@PADDING_V@@px;
    margin: @@MARGIN@@px;
    border: 1px solid #555555;
    border-radius: @@RADIUS@@px;
    background-color: #4a4a4a;
}
QMdiSubWindow QToolButton:hover { background-color: #5a5a5a; }
QToolBar#TaskBar {
    background-color: #004c8c;
    border: none;
}
QToolBar#TaskBar QToolButton {
    background-color: transparent;
    border: none;
    color: #ffffff;
    padding: @@PADDING_V@@px @@PADDING_H@@px;
}
QToolBar#TaskBar QToolButton:checked, QToolBar#TaskBar QToolButton:hover {
    background-color: #006bb2;
}
QToolButton#TaskbarCloseButton {
    background-color: transparent;
    border: none;
    padding: @@PADDING_V@@px;
    border-radius: @@RADIUS@@px;
}
QToolButton#TaskbarCloseButton:hover {
    background-color: #c42b1c;
}
QTabWidget::pane { border-top: 2px solid #333333; }
QTabBar::tab {
    background: #252526;
    border: 1px solid #333333;
    border-bottom-color: #1e1e1e;
    border-top-left-radius: @@RADIUS@@px;
    border-top-right-radius: @@RADIUS@@px;
    padding: @@PADDING_V@@px @@PADDING_H@@px;
    color: #a0a0a0;
}
QTabBar::tab:hover { background: #3c3c3c; color: #ffffff; }
QTabBar::tab:selected {
    background: #1e1e1e; 
    color: #ffffff;
    font-weight: bold;
    border-bottom-color: #1e1e1e;
}
QMdiSubWindow {
    background-color: #22272e;
    border-radius: 8px;
    border: 1px solid #000000;
}
QMdiSubWindow::titleBar {
    background-color: #2a2a2a;
    color: #e0e0e0;
    padding: @@MARGIN@@px;
}
QMdiArea { background-color: #1a1a1a; }
QMenuBar { background-color: #252526; color: #ccc; }
QMenuBar::item:selected { background-color: #3c3c3c; }
QMenu { background-color: #252526; color: #ccc; border: 1px solid #3c3c3c; }
QMenu::item:selected { background-color: #007acc; }
QStatusBar { color: #CCCCCC; }
QSplitter::handle { background-color: #333333; width: 1px; }
QSplitter::handle:hover { background-color: #007acc; }
"""

# --- AĞ TEMA ŞABLONU (YENİ DƏYİŞİKLİKLƏR BURADADIR) ---
LIGHT_TEMPLATE = """
QWidget {
    color: #2d2d2d;
    background-color: #fdfdfd; 
    font-size: @@FONT_SIZE@@pt;
    border: none;
}

/* === DÜZƏLİŞ 1: Menyu və Pəncərə Başlıqları Boz Edilir === */
QMenuBar {
    background-color: #E0E0E0; /* Açıq boz */
    color: #2d2d2d;
}
QMdiSubWindow::titleBar {
    background-color: #E0E0E0; /* Açıq boz */
    color: #333333;
    padding: @@MARGIN@@px;
}
QMdiSubWindow {
    border: 1px solid #DCDCDC;
    background-color: #FFFFFF; /* Pəncərənin içi ağ qalır */
}

/* === DÜZƏLİŞ 2: Pəncərə Daxili Toolbar Stili === */
QMdiSubWindow QToolBar {
    background-color: #EAE8D9; /* İstədiyiniz tünd krem/bej rəngi */
    border-bottom: 1px solid #DCDCDC;
    padding-top: 1px;    /* Qalınlığı azaltmaq üçün */
    padding-bottom: 1px; /* Qalınlığı azaltmaq üçün */
}

/* === DÜZƏLİŞ 3: Toolbar Düymələri və İkon Rəngi === */
QMdiSubWindow QToolButton {
    background-color: transparent;
    color: #33373B; /* İkonların tünd rəngi */
    border: none;
    padding: 4px; /* Qalınlığı azaltmaq üçün */
    margin: @@MARGIN@@px;
    border-radius: @@RADIUS@@px;
}
QMdiSubWindow QToolButton:hover { 
    background-color: #DCDCDC; 
}
QMdiSubWindow QToolButton:pressed {
    background-color: #C0C0C0;
}

/* === ÜST NAVİQASİYA PANELİ === */
QToolBar#MainNavBar {
    background-color: #EAE8D9;
    border-bottom: 1px solid #DCDCDC;
    padding: @@MARGIN@@px;
}
QToolBar#MainNavBar QToolButton {
    background-color: transparent;
    border: none;
    padding: @@NAV_PADDING_V@@px @@NAV_PADDING_H@@px;
    border-radius: @@RADIUS@@px;
    color: #333333;
    font-weight: bold;
}
QToolBar#MainNavBar QToolButton:hover {
    background-color: #DCD8C8;
    color: #000000;
}
QToolBar#MainNavBar QToolButton:pressed, QToolBar#MainNavBar QToolButton:checked {
    background-color: #0078d7;
    color: white;
}

/* === ALT TASKBAR === */
QToolBar#TaskBar {
    background-color: #0078d7;
    border: none;
}
QToolBar#TaskBar QToolButton {
    background-color: transparent;
    border: none;
    color: #ffffff;
    padding: @@PADDING_V@@px @@PADDING_H@@px;
}
QToolBar#TaskBar QToolButton:checked, QToolBar#TaskBar QToolButton:hover {
    background-color: #005a9e;
}
QToolButton#TaskbarCloseButton {
    background-color: transparent;
    border: none;
    padding: @@PADDING_V@@px;
    border-radius: @@RADIUS@@px;
}
QToolButton#TaskbarCloseButton:hover {
    background-color: #E81123;
}
"""