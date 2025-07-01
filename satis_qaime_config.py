# satis_qaime_config.py

# Satış qaiməsi cədvəlində istifadə oluna biləcək bütün mümkün sütunların siyahısı
MASTER_COLUMN_LIST = [
    {'key': 'product_id', 'header': 'Məhsul ID', 'default_visible': False, 'default_width': 80},
    {'key': 'product_name', 'header': 'Məhsul Adı', 'default_visible': True, 'default_width': 250},
    {'key': 'quantity', 'header': 'Miqdar', 'default_visible': True, 'default_width': 100},
    {'key': 'unit_price', 'header': 'Satış Qiyməti', 'default_visible': True, 'default_width': 120},
    {'key': 'discount_percent', 'header': 'Endirim %', 'default_visible': True, 'default_width': 100},
    {'key': 'final_price', 'header': 'Son Qiymət', 'default_visible': True, 'default_width': 120},
    {'key': 'line_total', 'header': 'Cəm', 'default_visible': True, 'default_width': 120},
    {'key': 'stock', 'header': 'Anbar Qalığı', 'default_visible': False, 'default_width': 100},
]