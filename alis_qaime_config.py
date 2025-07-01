# alis_qaime_config.py

# Alış qaiməsi cədvəlində istifadə oluna biləcək bütün mümkün sütunların siyahısı
# 'key': Məlumatı proqram daxilində tanımaq üçün unikal ad
# 'header': Cədvəlin başlığında görünəcək ad
# 'source': Məlumatın haradan gəldiyini göstərir ('item', 'product', 'calculated')
# 'default_visible': İlkin olaraq görünüb-görünməyəcəyi
# 'default_width': İlkin eni

MASTER_COLUMN_LIST = [
    {'key': 'product_id', 'header': 'Məhsul ID', 'source': 'item', 'default_visible': False, 'default_width': 80},
    {'key': 'product_name', 'header': 'Məhsul Adı', 'source': 'product', 'default_visible': True, 'default_width': 250},
    {'key': 'quantity', 'header': 'Miqdar', 'source': 'item', 'default_visible': True, 'default_width': 100},
    {'key': 'unit_price', 'header': 'Alış Qiyməti', 'source': 'item', 'default_visible': True, 'default_width': 120},
    {'key': 'discount_percent', 'header': 'Endirim %', 'source': 'item', 'default_visible': True, 'default_width': 100},
    {'key': 'final_price', 'header': 'Yekun Qiymət', 'source': 'calculated', 'default_visible': True, 'default_width': 120},
    {'key': 'line_total', 'header': 'Cəm', 'source': 'calculated', 'default_visible': True, 'default_width': 120},
    {'key': 'barcode', 'header': 'Barkod', 'source': 'product', 'default_visible': False, 'default_width': 120},
    {'key': 'article', 'header': 'Artikul', 'source': 'product', 'default_visible': False, 'default_width': 120},
    {'key': 'category', 'header': 'Kateqoriya', 'source': 'product', 'default_visible': False, 'default_width': 120},
]