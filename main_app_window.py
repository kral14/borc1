# main_app_window.py (Yekun Həll)

from PyQt6.QtWidgets import (QMainWindow, QMenu, QWidget, QMdiArea, QVBoxLayout,
                             QToolBar, QToolButton, QHBoxLayout, QSizePolicy, QStyle,
                             QMenuBar, QMdiSubWindow)
from PyQt6.QtGui import QAction, QIcon, QFont, QKeySequence
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QEvent

from app_logger import logger
from ui_main_window import Ui_MainWindow
from app_musteri_widget import MusteriManagerWidget
from app_satici_widget import SaticiManagerWidget
from app_mal_widget import MalManagerWidget
from app_alis_qaime_widget import AlisQaimeManagerWidget
from app_satis_qaime_widget import SatisQaimeManagerWidget
from logger_widget import LoggerWidget
from app_custom_fields_widget import CustomFieldsManagerWidget

# Pəncərə davranışını tam idarə etmək üçün xüsusi sinif
class CustomSubWindow(QMdiSubWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_pinned = False
        self.pin_action = None

    def mouseDoubleClickEvent(self, event):
        if self.is_pinned:
            event.ignore(); return
        super().mouseDoubleClickEvent(event)

class TaskbarButton(QWidget):
    clicked = pyqtSignal()
    closed = pyqtSignal()
    def __init__(self, text, icon, parent=None):
        super().__init__(parent); layout = QHBoxLayout(self); layout.setContentsMargins(0, 0, 4, 0); layout.setSpacing(4)
        self.main_button = QToolButton(); self.main_button.setText(text); self.main_button.setIcon(icon); self.main_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon); self.main_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred); self.main_button.setCheckable(True)
        self.close_button = QToolButton(); close_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton); self.close_button.setIcon(close_icon); self.close_button.setStyleSheet("QToolButton { border: none; border-radius: 3px; } QToolButton:hover { background-color: #c42b1c; }")
        layout.addWidget(self.main_button); layout.addWidget(self.close_button)
        self.main_button.clicked.connect(self.clicked); self.close_button.clicked.connect(self.closed)
    def set_active_style(self, is_active):
        self.main_button.setChecked(is_active); font = self.main_button.font(); font.setBold(is_active); self.main_button.setFont(font); style = "background-color: #007acc;" if is_active else "background-color: #3e3e42;"
        self.main_button.setStyleSheet(f"QToolButton {{ border: 1px solid #3e3e42; {style} color: #ccc; }} QToolButton:hover {{ background-color: #4f4f53; }}")

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.ui = Ui_MainWindow(); self.ui.setupUi(self); self.setWindowTitle("Borc İzləmə Sistemi"); self.window_map = {}; self.setStyleSheet("QMainWindow { background-color: #3c3c3c; }"); self.setup_main_layout()

    def setup_main_layout(self):
        main_widget = QWidget(); self.main_layout = QVBoxLayout(main_widget); self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0); top_panel = QWidget(); top_panel.setStyleSheet("QWidget { background-color: #2d2d30; border-bottom: 1px solid #000; }"); top_panel_layout = QVBoxLayout(top_panel); top_panel_layout.setContentsMargins(0, 0, 0, 0); top_panel_layout.setSpacing(0); self.menu_bar = QMenuBar(); self.mdi_area = QMdiArea(); self.menu_bar.setStyleSheet(""" QMenuBar { background-color: #2d2d30; color: #ccc; } QMenuBar::item:selected { background-color: #3e3e42; } QMenu { background-color: #2d2d30; color: #ccc; border: 1px solid #000; } QMenu::item:selected { background-color: #007acc; } """); top_panel_layout.addWidget(self.menu_bar); self.setup_menus(); nav_bar = self.create_top_navbar(); top_panel_layout.addWidget(nav_bar); self.mdi_area.setStyleSheet("QMdiArea { background-color: #3c3c3c; }"); self.mdi_area.setViewMode(QMdiArea.ViewMode.SubWindowView)
        # DƏYİŞİKLİK: subWindowActivated siqnalını taskbar-ı yeniləmək üçün istifadə edirik
        self.mdi_area.subWindowActivated.connect(self.update_taskbar_buttons)
        self.taskbar = QToolBar("Açıq Pəncərələr"); self.taskbar.setStyleSheet("QToolBar { background-color: #2d2d30; border-top: 1px solid #000; padding: 2px; spacing: 2px; }"); self.taskbar.setIconSize(QSize(16,16)); self.main_layout.addWidget(top_panel); self.main_layout.addWidget(self.mdi_area, 1); self.main_layout.addWidget(self.taskbar); self.setCentralWidget(main_widget)

    def create_top_navbar(self):
        # Bu metodda dəyişiklik yoxdur
        nav_bar = QToolBar("Naviqasiya"); nav_bar.setMovable(False); nav_bar.setFloatable(False); nav_bar.setStyleSheet("QToolBar { background-color: #2d2d30; border: none; padding: 5px; }"); button_style = """ QToolButton { padding: 8px 18px; border: 1px solid #3e3e42; background-color: #3e3e42; border-radius: 4px; color: #ccc; font-weight: bold; margin-right: 5px; } QToolButton:hover { background-color: #4f4f53; } QToolButton:pressed { background-color: #007acc; } QToolButton:checked { background-color: #007acc; } QToolButton::menu-indicator { image: none; } """; btn_musteriler = QToolButton(); btn_musteriler.setText("Müştərilər"); btn_musteriler.setStyleSheet(button_style); btn_musteriler.clicked.connect(lambda: self.open_section_in_subwindow(MusteriManagerWidget, "Müştərilər")); btn_saticilar = QToolButton(); btn_saticilar.setText("Satıcılar"); btn_saticilar.setStyleSheet(button_style); btn_saticilar.clicked.connect(lambda: self.open_section_in_subwindow(SaticiManagerWidget, "Satıcılar")); btn_mallar = QToolButton(); btn_mallar.setText("Mallar"); btn_mallar.setStyleSheet(button_style); btn_mallar.clicked.connect(lambda: self.open_section_in_subwindow(MalManagerWidget, "Mallar")); nav_bar.addWidget(btn_musteriler); nav_bar.addWidget(btn_saticilar); nav_bar.addWidget(btn_mallar); btn_qaimeler = QToolButton(); btn_qaimeler.setText("Qaimələr"); btn_qaimeler.setStyleSheet(button_style); qaime_menu = QMenu(self); qaime_menu.setStyleSheet(self.menu_bar.styleSheet()); action_alis = qaime_menu.addAction("Alış Qaimələri"); action_satis = qaime_menu.addAction("Satış Qaimələri"); btn_qaimeler.setMenu(qaime_menu); btn_qaimeler.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup); nav_bar.addWidget(btn_qaimeler); action_alis.triggered.connect(lambda: self.open_section_in_subwindow(AlisQaimeManagerWidget, "Alış Qaimələri")); action_satis.triggered.connect(lambda: self.open_section_in_subwindow(SatisQaimeManagerWidget, "Satış Qaimələri")); return nav_bar

    def setup_menus(self):
        # Bu metodda dəyişiklik yoxdur
        view_menu = self.menu_bar.addMenu("Görünüş"); show_log_action = QAction("Log Pəncərəsini Göstər", self); show_log_action.triggered.connect(lambda: self.open_section_in_subwindow(LoggerWidget, "Log Pəncərəsi")); view_menu.addAction(show_log_action); window_menu = self.menu_bar.addMenu("Pəncərə"); cascade_action = QAction("Kaskad düzülüş", self); cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows); window_menu.addAction(cascade_action); tile_action = QAction("Plitə düzülüş", self); tile_action.triggered.connect(self.mdi_area.tileSubWindows); window_menu.addAction(tile_action); window_menu.addSeparator(); close_all_action = QAction("Bütün pəncərələri bağla", self); close_all_action.triggered.connect(self.mdi_area.closeAllSubWindows); window_menu.addAction(close_all_action); settings_menu = self.menu_bar.addMenu("Ayarlar"); custom_fields_action = QAction("Məhsul üçün Xüsusi Sahələr", self); custom_fields_action.triggered.connect(lambda: self.open_section_in_subwindow(CustomFieldsManagerWidget, "Xüsusi Sahə Ayarları")); settings_menu.addAction(custom_fields_action)

    def eventFilter(self, source, event):
        # Minimizasiya hadisəsini idarə edən son həll
        if event.type() == QEvent.Type.WindowStateChange and source in self.window_map:
            if source.windowState() & Qt.WindowState.WindowMinimized:
                # Pəncərə minimizasiya olunduqda, onu MDI sahəsindən gizlədirik
                # və vəziyyətini normala qaytarırıq ki, sonradan düzgün görünsün.
                source.setWindowState(Qt.WindowState.WindowNoState)
                source.hide()
                return True
        elif event.type() == QEvent.Type.Close and source in self.window_map:
            self.remove_taskbar_button(source); return True
        return super().eventFilter(source, event)

    def open_section_in_subwindow(self, widget_class, title):
        content_widget = widget_class(); sub_window = CustomSubWindow(); sub_window.setWidget(content_widget); self.mdi_area.addSubWindow(sub_window); sub_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose); sub_window.installEventFilter(self); sub_window.setWindowTitle(title); sub_window.setWindowIcon(self.windowIcon()); self.add_pin_action_to_window(sub_window); sub_window.showMaximized(); taskbar_button = TaskbarButton(title, self.windowIcon()); taskbar_button.action = self.taskbar.addWidget(taskbar_button); self.window_map[sub_window] = taskbar_button; taskbar_button.clicked.connect(lambda sw=sub_window: self.handle_taskbar_click(sw)); taskbar_button.closed.connect(sub_window.close); self.mdi_area.setActiveSubWindow(sub_window)

    def add_pin_action_to_window(self, sub_window):
        pin_action = QAction("Pəncərəni Bərkit", sub_window); pin_action.setCheckable(True); pin_action.triggered.connect(lambda checked, sw=sub_window: self.toggle_window_pinned_state(sw, checked)); sub_window.pin_action = pin_action; menu = sub_window.systemMenu(); menu.addSeparator(); menu.addAction(pin_action)

    def toggle_window_pinned_state(self, sub_window, is_pinned):
        sub_window.is_pinned = is_pinned; action = sub_window.pin_action;
        if is_pinned:
            action.setText("Bərkitməni ləğv et"); sub_window.setWindowFlags(sub_window.windowFlags() | Qt.WindowType.WindowStaysOnTopHint); sub_window.setFixedSize(sub_window.size()); sub_window.show()
        else:
            action.setText("Pəncərəni Bərkit"); sub_window.setWindowFlags(sub_window.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint); sub_window.setMinimumSize(200, 150); sub_window.setMaximumSize(16777215, 16777215); sub_window.show()
    
    # DƏYİŞİKLİK: Taskbar klikləri üçün xüsusi metod
    def handle_taskbar_click(self, sub_window):
        if not sub_window: return
        
        # Əgər pəncərə aktivdirsə və görünürsə, onu gizlət (minimizasiya et)
        if self.mdi_area.currentSubWindow() == sub_window and sub_window.isVisible():
            sub_window.hide()
        else:
            # Əks halda, göstər və aktiv et
            sub_window.show()
            self.mdi_area.setActiveSubWindow(sub_window)
        
    def remove_taskbar_button(self, sub_window_obj):
        if sub_window_obj in self.window_map:
            button = self.window_map.pop(sub_window_obj); self.taskbar.removeAction(button.action); button.deleteLater(); self.update_taskbar_buttons(None)

    def update_taskbar_buttons(self, active_window=None):
        # Bu metod sadəcə taskbar düymələrinin görünüşünü yeniləyir
        if active_window is None:
            active_window = self.mdi_area.currentSubWindow()

        for window, button in self.window_map.items():
            if window:
                is_active = (window == active_window and window.isVisible())
                button.set_active_style(is_active)