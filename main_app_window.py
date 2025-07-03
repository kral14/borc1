# main_app_window.py (Bütün girinti və təyin etmə xətaları üçün düzəlişlərlə)

from PyQt6.QtWidgets import (QMainWindow, QMenu, QWidget, QMdiArea, QVBoxLayout,
                             QToolBar, QToolButton, QHBoxLayout, QSizePolicy, QStyle,
                             QMenuBar, QApplication, QLabel, QMdiSubWindow)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QSettings, QRect

from app_logger import logger
from app_musteri_widget import MusteriManagerWidget
from app_satici_widget import SaticiManagerWidget
from app_mal_widget import MalManagerWidget
from app_alis_qaime_widget import AlisQaimeManagerWidget
from app_satis_qaime_widget import SatisQaimeManagerWidget
from logger_widget import LoggerWidget
from app_custom_fields_widget import CustomFieldsManagerWidget
# Kassa modulunu import edirik
from app_kassa_medaxil_widget import KassaMedaxilManagerWidget
from app_kassa_mexaric_widget import KassaMexaricManagerWidget

class UndockedWindow(QMainWindow):
    closing = pyqtSignal(object)

    def __init__(self, content_widget, title, original_class, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"[Kənarda] {title}")
        self.setCentralWidget(content_widget)
        self.original_class = original_class
        self.original_title = title
        self.resize(content_widget.size())

    def closeEvent(self, event):
        logger.log(f"'{self.windowTitle()}' pəncərəsi bağlanır, MDI sahəsinə geri qaytarılır.")
        self.closing.emit(self)
        super().closeEvent(event)


class CustomSubWindow(QMdiSubWindow):
    aboutToClose = pyqtSignal(QMdiSubWindow)
    undock_requested = pyqtSignal(QMdiSubWindow)

    def __init__(self, widget_class, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget_class = widget_class
        self.title = title
        
        self.is_pinned = False
        self.is_fake_maximized = False
        self.saved_geometry = None

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)

        system_menu = self.systemMenu()
        system_menu.addSeparator()

        self.maximize_action = QAction("Maksimallaşdır", self)
        self.maximize_action.triggered.connect(self.toggle_fake_maximize)
        system_menu.addAction(self.maximize_action)

        self.pin_action = QAction("Bərkit (Stay on Top)", self)
        self.pin_action.setCheckable(True)
        self.pin_action.triggered.connect(self.toggle_pinned_status)
        system_menu.addAction(self.pin_action)
        
        system_menu.addSeparator()
        self.undock_action = QAction("Kənarlaşdır (Undock)", self)
        self.undock_action.triggered.connect(lambda: self.undock_requested.emit(self))
        system_menu.addAction(self.undock_action)

    def set_content_widget(self, content_widget):
        self.setWidget(content_widget)

    def closeEvent(self, event):
        settings = QSettings("MySoft", "BorcIzlemeApp")
        key = f"WindowGeometry/{self.windowTitle()}"
        
        geometry_to_save = self.saved_geometry if self.is_fake_maximized else self.geometry()
        
        if geometry_to_save:
            settings.setValue(key, geometry_to_save)
            logger.log(f"'{self.windowTitle()}' pəncərəsinin vəziyyəti yadda saxlanıldı: {geometry_to_save}")
        
        self.aboutToClose.emit(self)
        super().closeEvent(event)

    def mouseDoubleClickEvent(self, event):
        title_bar_height = self.style().pixelMetric(QStyle.PixelMetric.PM_TitleBarHeight)
        if event.pos().y() <= title_bar_height:
            self.toggle_fake_maximize()
        super().mouseDoubleClickEvent(event)

    def toggle_fake_maximize(self):
        if self.is_fake_maximized:
            if self.saved_geometry: self.setGeometry(self.saved_geometry)
            self.is_fake_maximized = False
            self.maximize_action.setText("Maksimallaşdır")
        else:
            self.saved_geometry = self.geometry()
            self.setGeometry(self.mdiArea().viewport().rect())
            self.is_fake_maximized = True
            self.maximize_action.setText("Normal Ölçü")

    def toggle_pinned_status(self, pinned):
        self.is_pinned = pinned
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, pinned)
        self.show()


class TaskbarButton(QWidget):
    clicked = pyqtSignal(object)
    closed = pyqtSignal()
    def __init__(self, text, icon, parent=None):
        super().__init__(parent); layout = QHBoxLayout(self); layout.setContentsMargins(0, 0, 4, 0); layout.setSpacing(4)
        self.main_button = QToolButton(); self.main_button.setText(text); self.main_button.setIcon(icon); self.main_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon); self.main_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred); self.main_button.setCheckable(True)
        self.close_button = QToolButton(); close_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton); self.close_button.setIcon(close_icon); self.close_button.setStyleSheet("QToolButton { border: none; border-radius: 3px; } QToolButton:hover { background-color: #c42b1c; }")
        layout.addWidget(self.main_button); layout.addWidget(self.close_button)
        self.main_button.clicked.connect(lambda: self.clicked.emit(self))
        self.close_button.clicked.connect(self.closed.emit)
    def set_active_style(self, is_active):
        self.main_button.setChecked(is_active); font = self.main_button.font(); font.setBold(is_active); self.main_button.setFont(font); style = "background-color: #007acc;" if is_active else "background-color: #3e3e42;"
        self.main_button.setStyleSheet(f"QToolButton {{ border: 1px solid #3e3e42; {style} color: #ccc; }} QToolButton:hover {{ background-color: #4f4f53; }}")


class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_map = {}
        self.undocked_windows = {}
        self.setup_main_layout()

    def setup_main_layout(self):
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        top_panel = QWidget()
        top_panel.setStyleSheet("QWidget { background-color: #2d2d30; border-bottom: 1px solid #000; }")
        top_panel_layout = QVBoxLayout(top_panel)
        top_panel_layout.setContentsMargins(0, 0, 0, 0)
        top_panel_layout.setSpacing(0)
        self.menu_bar = QMenuBar()
        self.menu_bar.setStyleSheet(""" QMenuBar { background-color: #2d2d30; color: #ccc; } QMenuBar::item:selected { background-color: #3e3e42; } QMenu { background-color: #2d2d30; color: #ccc; border: 1px solid #000; } QMenu::item:selected { background-color: #007acc; } """)
        top_panel_layout.addWidget(self.menu_bar)

        self.mdi_area = QMdiArea()
        self.mdi_area.subWindowActivated.connect(self.on_subwindow_activated)
        self.mdi_area.setViewMode(QMdiArea.ViewMode.SubWindowView)

        self.setup_menus()
        nav_bar = self.create_top_navbar()
        top_panel_layout.addWidget(nav_bar)

        self.taskbar = QToolBar("Açıq Pəncərələr")
        self.taskbar.setStyleSheet("QToolBar { background-color: #2d2d30; border-top: 1px solid #000; padding: 2px; spacing: 2px; }")
        self.taskbar.setIconSize(QSize(16,16))

        self.main_layout.addWidget(top_panel)
        self.main_layout.addWidget(self.mdi_area, 1)
        self.main_layout.addWidget(self.taskbar)
        self.setCentralWidget(main_widget)

    def create_top_navbar(self):
        nav_bar = QToolBar("Naviqasiya")
        nav_bar.setMovable(False)
        nav_bar.setFloatable(False)
        nav_bar.setStyleSheet("QToolBar { background-color: #2d2d30; border: none; padding: 5px; }")
        
        button_style = """
            QToolButton { 
                padding: 8px 18px; 
                border: 1px solid #3e3e42; 
                background-color: #3e3e42; 
                border-radius: 4px; 
                color: #ccc; 
                font-weight: bold; 
                margin-right: 5px; 
            } 
            QToolButton:hover { background-color: #4f4f53; } 
            QToolButton:pressed { background-color: #007acc; } 
            QToolButton:checked { background-color: #007acc; } 
            QToolButton::menu-indicator { image: none; } 
        """

        btn_musteriler = QToolButton()
        btn_musteriler.setText("Müştərilər")
        btn_musteriler.setStyleSheet(button_style)
        btn_musteriler.clicked.connect(lambda: self.open_section_window(MusteriManagerWidget, "Müştərilər"))
        
        btn_saticilar = QToolButton()
        btn_saticilar.setText("Satıcılar")
        btn_saticilar.setStyleSheet(button_style)
        btn_saticilar.clicked.connect(lambda: self.open_section_window(SaticiManagerWidget, "Satıcılar"))
        
        btn_mallar = QToolButton()
        btn_mallar.setText("Mallar")
        btn_mallar.setStyleSheet(button_style)
        btn_mallar.clicked.connect(lambda: self.open_section_window(MalManagerWidget, "Mallar"))
        
        nav_bar.addWidget(btn_musteriler)
        nav_bar.addWidget(btn_saticilar)
        nav_bar.addWidget(btn_mallar)
        
        btn_qaimeler = QToolButton()
        btn_qaimeler.setText("Qaimələr")
        btn_qaimeler.setStyleSheet(button_style)
        qaime_menu = QMenu(self)
        qaime_menu.setStyleSheet(self.menu_bar.styleSheet())
        action_alis = qaime_menu.addAction("Alış Qaimələri")
        action_satis = qaime_menu.addAction("Satış Qaimələri")
        btn_qaimeler.setMenu(qaime_menu)
        btn_qaimeler.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        nav_bar.addWidget(btn_qaimeler)
        action_alis.triggered.connect(lambda: self.open_section_window(AlisQaimeManagerWidget, "Alış Qaimələri"))
        action_satis.triggered.connect(lambda: self.open_section_window(SatisQaimeManagerWidget, "Satış Qaimələri"))

        btn_kassa = QToolButton()
        btn_kassa.setText("Kassa")
        btn_kassa.setStyleSheet(button_style)
        kassa_menu = QMenu(self)
        kassa_menu.setStyleSheet(self.menu_bar.styleSheet())
        action_medaxil = kassa_menu.addAction("Kassa Mədaxil")
        action_mexaric = kassa_menu.addAction("Kassa Məxaric")
        action_mexaric.setEnabled(True) 
        btn_kassa.setMenu(kassa_menu)
        btn_kassa.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        nav_bar.addWidget(btn_kassa)
        action_medaxil.triggered.connect(lambda: self.open_section_window(KassaMedaxilManagerWidget, "Kassa Mədaxil"))
        action_mexaric.triggered.connect(lambda: self.open_section_window(KassaMexaricManagerWidget, "Kassa Məxaric"))
        
        logger.log("Üst naviqasiya paneli yaradıldı.")
        return nav_bar

    def setup_menus(self):
        view_menu = self.menu_bar.addMenu("Görünüş"); show_log_action = QAction("Log Pəncərəsini Göstər", self); show_log_action.triggered.connect(lambda: self.open_section_window(LoggerWidget, "Log Pəncərəsi")); view_menu.addAction(show_log_action)
        window_menu = self.menu_bar.addMenu("Pəncərə"); cascade_action = QAction("Kaskad düzülüş", self); cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows); window_menu.addAction(cascade_action); tile_action = QAction("Plitə düzülüş", self); tile_action.triggered.connect(self.mdi_area.tileSubWindows); window_menu.addAction(tile_action); window_menu.addSeparator(); close_all_action = QAction("Bütün pəncərələri bağla", self); close_all_action.triggered.connect(self.mdi_area.closeAllSubWindows); window_menu.addAction(close_all_action)
        settings_menu = self.menu_bar.addMenu("Ayarlar"); custom_fields_action = QAction("Məhsul üçün Xüsusi Sahələr", self); custom_fields_action.triggered.connect(lambda: self.open_section_window(CustomFieldsManagerWidget, "Xüsusi Sahə Ayarları")); settings_menu.addAction(custom_fields_action)

    def open_section_window(self, widget_class, title):
        sub_window = CustomSubWindow(widget_class, title)
        sub_window.setWindowTitle(title)
        sub_window.set_content_widget(widget_class())
        sub_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

        settings = QSettings("MySoft", "BorcIzlemeApp")
        key = f"WindowGeometry/{title}"
        saved_geometry = settings.value(key)

        if saved_geometry and isinstance(saved_geometry, QRect):
            sub_window.setGeometry(saved_geometry)
        else:
            sub_window.resize(1024, 768)
        
        taskbar_button = TaskbarButton(title, self.windowIcon())
        taskbar_button.action = self.taskbar.addWidget(taskbar_button)
        taskbar_button.clicked.connect(self.on_taskbar_button_clicked)
        taskbar_button.closed.connect(sub_window.close)
        self.window_map[sub_window] = taskbar_button
        
        sub_window.aboutToClose.connect(self.handle_sub_window_close)
        sub_window.undock_requested.connect(self.undock_sub_window)
        
        self.update_taskbar_buttons(sub_window)

    def undock_sub_window(self, sub_window):
        content_widget = sub_window.widget()
        if not content_widget: return
        
        logger.log(f"'{sub_window.title}' pəncərəsi kənarlaşdırılır.")
        
        sub_window.setWidget(None)
        content_widget.setParent(None)
        
        undocked = UndockedWindow(content_widget, sub_window.title, sub_window.widget_class, self)
        self.undocked_windows[sub_window.title] = undocked
        undocked.closing.connect(self.redock_sub_window)
        undocked.show()
        
        sub_window.close()

    def redock_sub_window(self, undocked_window):
        title = undocked_window.original_title
        widget_class = undocked_window.original_class
        logger.log(f"'{title}' pəncərəsi MDI sahəsinə geri qaytarılır.")
        
        self.open_section_window(widget_class, title)
        
        if title in self.undocked_windows:
            del self.undocked_windows[title]

    def on_taskbar_button_clicked(self, clicked_button):
        target_window = None
        for window, button in list(self.window_map.items()):
            if button == clicked_button:
                target_window = window
                break
        if target_window and target_window in self.mdi_area.subWindowList():
            self.mdi_area.setActiveSubWindow(target_window)

    def handle_sub_window_close(self, window_to_close):
        if window_to_close in self.window_map:
            taskbar_button = self.window_map.pop(window_to_close)
            try:
                taskbar_button.clicked.disconnect()
                taskbar_button.closed.disconnect()
            except TypeError: pass
            self.taskbar.removeAction(taskbar_button.action)
            taskbar_button.deleteLater()
            self.update_taskbar_buttons()

    def on_subwindow_activated(self, window):
        for sw in self.mdi_area.subWindowList():
            if hasattr(sw, 'is_pinned') and sw.is_pinned:
                sw.raise_()
        self.update_taskbar_buttons(window)

    def update_taskbar_buttons(self, active_window=None):
        if active_window is None:
            active_window = self.mdi_area.activeSubWindow()
        for window, button in list(self.window_map.items()):
            if window and window in self.window_map:
                 button.set_active_style(window == active_window)
            else:
                 button.set_active_style(False)