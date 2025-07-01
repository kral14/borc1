# main_app_window.py (Çoxlu pəncərə dəstəyi ilə)

from PyQt6.QtWidgets import (QMainWindow, QMenu, QWidget, QMdiArea, QVBoxLayout, 
                             QToolBar, QToolButton, QHBoxLayout, QSizePolicy, QStyle)
from PyQt6.QtGui import QAction, QIcon, QFont, QKeySequence
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QEvent

from ui_main_window import Ui_MainWindow
from app_musteri_widget import MusteriManagerWidget
from app_satici_widget import SaticiManagerWidget
from app_mal_widget import MalManagerWidget
from app_alis_qaime_widget import AlisQaimeManagerWidget
from app_satis_qaime_widget import SatisQaimeManagerWidget

class TaskbarButton(QWidget):
    clicked = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, text, icon, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(4)

        self.main_button = QToolButton()
        self.main_button.setText(text)
        self.main_button.setIcon(icon)
        self.main_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.main_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.main_button.setCheckable(True)

        self.close_button = QToolButton()
        close_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        self.close_button.setIcon(close_icon)
        self.close_button.setStyleSheet("QToolButton { border: none; border-radius: 3px; } QToolButton:hover { background-color: #c42b1c; }")
        
        layout.addWidget(self.main_button)
        layout.addWidget(self.close_button)

        self.main_button.clicked.connect(self.clicked)
        self.close_button.clicked.connect(self.closed)

    def set_active_style(self, is_active):
        self.main_button.setChecked(is_active)
        font = self.main_button.font()
        font.setBold(is_active)
        self.main_button.setFont(font)
        style = "background-color: #555555;" if is_active else "background-color: #3C3C3C;"
        self.main_button.setStyleSheet(f"QToolButton {{ border: 1px solid #666; {style} }} QToolButton:hover {{ background-color: #6E6E6E; }}")

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.window_map = {}
        
        self.setup_mdi_interface()

        self.ui.btn_musteriler.clicked.connect(lambda: self.open_section_in_subwindow(MusteriManagerWidget, "Müştərilər"))
        self.ui.btn_saticilar.clicked.connect(lambda: self.open_section_in_subwindow(SaticiManagerWidget, "Satıcılar"))
        self.ui.btn_mallar.clicked.connect(lambda: self.open_section_in_subwindow(MalManagerWidget, "Mallar"))
        
        self.setup_qaimeler_menu()
        self.setup_window_menu()

    def setup_mdi_interface(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.mdi_area = QMdiArea()
        self.mdi_area.subWindowActivated.connect(self.update_taskbar_buttons)
        
        self.taskbar = QToolBar("Açıq Pəncərələr")
        self.taskbar.setStyleSheet("QToolBar { border-top: 1px solid #555; background-color: #2E2E2E; padding: 2px; }")
        
        main_layout.addWidget(self.mdi_area)
        main_layout.addWidget(self.taskbar)

        old_content_frame = self.ui.mainContentFrame
        self.ui.gridLayout.removeWidget(old_content_frame)
        old_content_frame.deleteLater()
        
        self.ui.gridLayout.addWidget(central_widget, 0, 1, 1, 1)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Close and source in self.window_map:
            self.remove_taskbar_button(source)
        return super().eventFilter(source, event)

    def open_section_in_subwindow(self, widget_class, title):
        # DƏYİŞİKLİK: Eyni adda pəncərənin təkrar açılmasını məhdudlaşdıran kod silindi
        # Artıq hər dəfə yeni pəncərə açılacaq
        
        content_widget = widget_class()
        sub_window = self.mdi_area.addSubWindow(content_widget)
        
        sub_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        sub_window.installEventFilter(self)
        
        sub_window.setWindowTitle(title)
        sub_window.setWindowIcon(self.windowIcon())
        sub_window.resize(900, 700)
        sub_window.show()

        close_action = QAction(sub_window)
        close_action.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        close_action.triggered.connect(sub_window.close)
        sub_window.addAction(close_action)

        taskbar_button = TaskbarButton(title, self.windowIcon())
        taskbar_button.action = self.taskbar.addWidget(taskbar_button)
        
        self.window_map[sub_window] = taskbar_button
        
        taskbar_button.clicked.connect(lambda sw=sub_window: self.activate_sub_window(sw))
        taskbar_button.closed.connect(sub_window.close)
        
        self.update_taskbar_buttons(sub_window)

    def activate_sub_window(self, sub_window):
        if sub_window and sub_window.isMinimized():
            sub_window.showNormal()
        self.mdi_area.setActiveSubWindow(sub_window)
        
    def remove_taskbar_button(self, sub_window_obj):
        if sub_window_obj in self.window_map:
            button = self.window_map.pop(sub_window_obj)
            self.taskbar.removeAction(button.action)
            button.deleteLater()

    def update_taskbar_buttons(self, sub_window):
        if not sub_window and self.mdi_area.currentSubWindow():
            sub_window = self.mdi_area.currentSubWindow()

        for window, button in self.window_map.items():
            if window:
                is_active = (window == sub_window) and not window.isMinimized()
                button.set_active_style(is_active)

    def setup_window_menu(self):
        if not self.menuBar().findChildren(QMenu, "Pəncərə"):
            window_menu = self.menuBar().addMenu("Pəncərə")
            cascade_action = QAction("Kaskad düzülüş", self); cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
            window_menu.addAction(cascade_action)
            tile_action = QAction("Plitə düzülüş", self); tile_action.triggered.connect(self.mdi_area.tileSubWindows)
            window_menu.addAction(tile_action)
            window_menu.addSeparator()
            close_all_action = QAction("Bütün pəncərələri bağla", self); close_all_action.triggered.connect(self.mdi_area.closeAllSubWindows)
            window_menu.addAction(close_all_action)
        
    def setup_qaimeler_menu(self):
        self.qaime_menu = QMenu(self)
        self.action_alis_qaimesi = QAction("Alış Qaimələri", self)
        self.action_satis_qaimesi = QAction("Satış Qaimələri", self)
        self.qaime_menu.addAction(self.action_alis_qaimesi); self.qaime_menu.addAction(self.action_satis_qaimesi)
        self.action_alis_qaimesi.triggered.connect(lambda: self.open_section_in_subwindow(AlisQaimeManagerWidget, "Alış Qaimələri"))
        self.action_satis_qaimesi.triggered.connect(lambda: self.open_section_in_subwindow(SatisQaimeManagerWidget, "Satış Qaimələri"))
        self.ui.btn_qaimeler.setMenu(self.qaime_menu)
        self.ui.btn_qaimeler.setStyleSheet(self.ui.btn_qaimeler.styleSheet() + "QPushButton::menu-indicator { image: none; }")