# main_app_window.py (RuntimeError xətası həll edilmiş yekun versiya)

from PyQt6.QtWidgets import (QMainWindow, QMenu, QWidget, QMdiArea, QVBoxLayout,
                             QToolBar, QToolButton, QHBoxLayout, QSizePolicy, QStyle,
                             QMenuBar, QApplication, QLabel, QMdiSubWindow)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer

from app_logger import logger
# ... digər widget importları ...
from app_musteri_widget import MusteriManagerWidget
from app_satici_widget import SaticiManagerWidget
from app_mal_widget import MalManagerWidget
from app_alis_qaime_widget import AlisQaimeManagerWidget
from app_satis_qaime_widget import SatisQaimeManagerWidget
from logger_widget import LoggerWidget
from app_custom_fields_widget import CustomFieldsManagerWidget


class CustomSubWindow(QMdiSubWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_pinned = False
        self.is_fake_maximized = False
        self.saved_geometry = None
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)

    def set_content_widget(self, content_widget):
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        toolbar = QToolBar()
        toolbar.setStyleSheet("QToolBar { border-bottom: 1px solid #444; }")
        self.maximize_action = QAction("Maksimallaşdır", self)
        self.maximize_action.triggered.connect(self.toggle_fake_maximize)
        toolbar.addAction(self.maximize_action)
        self.pin_action = QAction("Bərkit", self, checkable=True)
        self.pin_action.triggered.connect(self.set_pinned_status)
        toolbar.addAction(self.pin_action)
        container_layout.addWidget(toolbar)
        container_layout.addWidget(content_widget)
        self.setWidget(container_widget)

    def toggle_fake_maximize(self):
        if self.is_fake_maximized:
            if self.saved_geometry:
                self.setGeometry(self.saved_geometry)
                logger.log(f"'{self.windowTitle()}' pəncərəsi normal ölçüsünə qaytarıldı: {self.saved_geometry}")
            self.is_fake_maximized = False
            self.maximize_action.setText("Maksimallaşdır")
        else:
            self.saved_geometry = self.geometry()
            viewport_rect = self.mdiArea().viewport().rect()
            self.setGeometry(viewport_rect)
            logger.log(f"'{self.windowTitle()}' pəncərəsi MDI sahəsinə maksimallaşdırıldı: {viewport_rect}")
            self.is_fake_maximized = True
            self.maximize_action.setText("Normal Ölçü")

    def set_pinned_status(self, pinned):
        self.is_pinned = pinned
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, pinned)
        self.show()
        logger.log(f"'{self.windowTitle()}' pəncərəsinin bərkidilmə statusu dəyişdi: {pinned}")


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
        super().__init__()
        logger.log("Əsas pəncərə (MainAppWindow) başladılır...")
        self.window_map = {}
        self.setup_main_layout()

    def setup_main_layout(self):
        logger.log("Əsas pəncərənin layout, menyu və naviqasiya paneli qurulur.")
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
        QTimer.singleShot(100, self.mdi_area.cascadeSubWindows)

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
        logger.log("Əsas pəncərənin qurulması tamamlandı.")

    def create_top_navbar(self):
        nav_bar = QToolBar("Naviqasiya"); nav_bar.setMovable(False); nav_bar.setFloatable(False); nav_bar.setStyleSheet("QToolBar { background-color: #2d2d30; border: none; padding: 5px; }"); button_style = """ QToolButton { padding: 8px 18px; border: 1px solid #3e3e42; background-color: #3e3e42; border-radius: 4px; color: #ccc; font-weight: bold; margin-right: 5px; } QToolButton:hover { background-color: #4f4f53; } QToolButton:pressed { background-color: #007acc; } QToolButton:checked { background-color: #007acc; } QToolButton::menu-indicator { image: none; } """; btn_musteriler = QToolButton(); btn_musteriler.setText("Müştərilər"); btn_musteriler.setStyleSheet(button_style); btn_musteriler.clicked.connect(lambda: self.open_section_window(MusteriManagerWidget, "Müştərilər")); btn_saticilar = QToolButton(); btn_saticilar.setText("Satıcılar"); btn_saticilar.setStyleSheet(button_style); btn_saticilar.clicked.connect(lambda: self.open_section_window(SaticiManagerWidget, "Satıcılar")); btn_mallar = QToolButton(); btn_mallar.setText("Mallar"); btn_mallar.setStyleSheet(button_style); btn_mallar.clicked.connect(lambda: self.open_section_window(MalManagerWidget, "Mallar")); nav_bar.addWidget(btn_musteriler); nav_bar.addWidget(btn_saticilar); nav_bar.addWidget(btn_mallar); btn_qaimeler = QToolButton(); btn_qaimeler.setText("Qaimələr"); btn_qaimeler.setStyleSheet(button_style); qaime_menu = QMenu(self); qaime_menu.setStyleSheet(self.menu_bar.styleSheet()); action_alis = qaime_menu.addAction("Alış Qaimələri"); action_satis = qaime_menu.addAction("Satış Qaimələri"); btn_qaimeler.setMenu(qaime_menu); btn_qaimeler.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup); nav_bar.addWidget(btn_qaimeler); action_alis.triggered.connect(lambda: self.open_section_window(AlisQaimeManagerWidget, "Alış Qaimələri")); action_satis.triggered.connect(lambda: self.open_section_window(SatisQaimeManagerWidget, "Satış Qaimələri"));
        logger.log("Üst naviqasiya paneli yaradıldı.")
        return nav_bar
        
    def setup_menus(self):
        view_menu = self.menu_bar.addMenu("Görünüş")
        show_log_action = QAction("Log Pəncərəsini Göstər", self)
        show_log_action.triggered.connect(lambda: self.open_section_window(LoggerWidget, "Log Pəncərəsi"))
        view_menu.addAction(show_log_action)
        
        window_menu = self.menu_bar.addMenu("Pəncərə")
        cascade_action = QAction("Kaskad düzülüş", self)
        cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        window_menu.addAction(cascade_action)
        tile_action = QAction("Plitə düzülüş", self)
        tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        window_menu.addAction(tile_action)
        window_menu.addSeparator()
        close_all_action = QAction("Bütün pəncərələri bağla", self)
        close_all_action.triggered.connect(self.mdi_area.closeAllSubWindows)
        window_menu.addAction(close_all_action)
        
        settings_menu = self.menu_bar.addMenu("Ayarlar")
        custom_fields_action = QAction("Məhsul üçün Xüsusi Sahələr", self)
        custom_fields_action.triggered.connect(lambda: self.open_section_window(CustomFieldsManagerWidget, "Xüsusi Sahə Ayarları"))
        settings_menu.addAction(custom_fields_action)
        logger.log("Menyular quruldu.")

    def open_section_window(self, widget_class, title):
        logger.log(f"Yeni '{title}' pəncərəsi yaradılır...")
        
        sub_window = CustomSubWindow()
        sub_window.setWindowTitle(title)
        sub_window.set_content_widget(widget_class())
        sub_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.mdi_area.addSubWindow(sub_window)
        
        sub_window.resize(1024, 768)
        sub_window.show()

        taskbar_button = TaskbarButton(title, self.windowIcon())
        taskbar_button.action = self.taskbar.addWidget(taskbar_button)
        self.window_map[sub_window] = taskbar_button
        taskbar_button.clicked.connect(lambda sw=sub_window: self.activate_subwindow(sw))
        taskbar_button.closed.connect(sub_window.close)
        sub_window.destroyed.connect(lambda obj=sub_window: self.on_window_destroyed(obj))
        self.update_taskbar_buttons(sub_window)

    def on_window_destroyed(self, destroyed_window):
        if destroyed_window in self.window_map:
            logger.log(f"'{destroyed_window.windowTitle()}' pəncərəsi məhv edildi. Taskbar düyməsi silinir.")
            taskbar_button = self.window_map.pop(destroyed_window)
            taskbar_button.deleteLater()
            # DƏYİŞİKLİK: Taskbarı yeniləyərkən aktiv pəncərəni yenidən yoxlayırıq
            self.update_taskbar_buttons()

    def activate_subwindow(self, sub_window):
        if sub_window:
            self.mdi_area.setActiveSubWindow(sub_window)

    def on_subwindow_activated(self, window):
        for sw in self.mdi_area.subWindowList():
            if hasattr(sw, 'is_pinned') and sw.is_pinned:
                sw.raise_()
        self.update_taskbar_buttons(window)

    def update_taskbar_buttons(self, active_window=None):
        if active_window is None: 
            active_window = self.mdi_area.activeSubWindow()
        
        # Mövcud alt-pəncərələrin siyahısını alırıq
        current_subwindows = self.mdi_area.subWindowList()

        if active_window: 
            logger.log(f"Aktiv pəncərə dəyişdi: '{active_window.windowTitle()}'.")
        
        for window, button in self.window_map.items():
            # DƏYİŞİKLİK: XƏTANIN HƏLLİ
            # Pəncərə ilə əməliyyat aparmazdan əvvəl onun hələ də MDI sahəsində mövcud olduğunu yoxlayırıq.
            if window in current_subwindows:
                 button.set_active_style(window == active_window)
            else:
                 # Əgər pəncərə MDI sahəsində yoxdursa, deməli bağlanıb.
                 # Düyməsini deaktiv edirik. on_window_destroyed onsuz da onu siləcək.
                 button.set_active_style(False)