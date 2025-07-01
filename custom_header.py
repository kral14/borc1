# custom_header.py
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtCore import Qt

class CustomHeaderView(QHeaderView):
    """
    Hər bir sütun üçün sıralamanı fərdi idarə etməyə imkan verən
    xüsusi cədvəl başlığı sinfi.
    """
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self._sortable_columns = set()
        self.setSectionsClickable(True)

    def set_sortable_columns(self, sortable_logical_indices):
        """Sıralanmasına icazə verilən sütunların məntiqi indekslərini təyin edir."""
        self._sortable_columns = set(sortable_logical_indices)
        
    def mousePressEvent(self, e):
        """
        Kliklənən sütunun sıralanmasına icazə verilibsə, standart əməliyyatı yerinə yetirir.
        Bu yanaşma, resize funksionallığını pozmur.
        """
        self.setSectionsClickable(True)
        
        logical_index = self.logicalIndexAt(e.pos())
        
        if logical_index not in self._sortable_columns:
            # Əgər kliklənən sütun sıralana bilməyənlərdəndirsə,
            # müvəqqəti olaraq bütün başlıqları qeyri-kliklənən edirik.
            self.setSectionsClickable(False)

        # Standart hadisəni (klikləmə, sıralama və s.) icra et
        super().mousePressEvent(e)
        
        # Əməliyyat bitdikdən sonra başlıqları yenidən kliklənən vəziyyətə gətiririk
        self.setSectionsClickable(True)