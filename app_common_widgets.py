# app_common_widgets.py

from PyQt6.QtWidgets import QToolBar, QToolButton, QStyle
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize, Qt  # <--- DÜZƏLİŞ: Qt bura əlavə edildi

# Bu import, ikonların ölçüsünü miqyasa görə təyin etmək üçün lazımdır
import style_manager 

class GeneralToolbar(QToolBar):
    """
    Proqramın müxtəlif yerlərində istifadə edilə bilən,
    "Yeni", "Düzəliş Et", "Sil" kimi standart əməliyyatları ehtiva edən ümumi toolbar.
    """
    def __init__(self, parent=None):
        super().__init__("Ümumi Əməliyyatlar", parent)
        
        # Stil və ölçüləri mərkəzi style_manager-dən götürürük
        self.setIconSize(style_manager.get_scaled_icon_size(base_size=22))
        self.setMovable(False)

        # Standart ikonları əldə edirik
        style = self.style()
        
        # === ACTIONS ===
        # Bütün action-ları 'self' ilə yaradırıq ki, xaricdən onlara çata bilək
        # Məsələn: toolbar.action_add.triggered.connect(...)
        self.action_add = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Yeni Yarat", self)
        self.action_edit = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Düzəliş Et", self)
        self.action_delete = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "Sil", self)
        self.action_refresh = QAction(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "Yenilə", self)
        
        # === BUTTONS ===
        # Hər action üçün bir düymə yaradıb toolbar-a əlavə edirik
        
        # Yeni düyməsi
        btn_add = QToolButton()
        btn_add.setDefaultAction(self.action_add)
        btn_add.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addWidget(btn_add)
        
        # Düzəliş düyməsi
        btn_edit = QToolButton()
        btn_edit.setDefaultAction(self.action_edit)
        btn_edit.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addWidget(btn_edit)

        # Sil düyməsi
        btn_delete = QToolButton()
        btn_delete.setDefaultAction(self.action_delete)
        btn_delete.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addWidget(btn_delete)
        
        self.addSeparator()

        # Yenilə düyməsi
        btn_refresh = QToolButton()
        btn_refresh.setDefaultAction(self.action_refresh)
        btn_refresh.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addWidget(btn_refresh)