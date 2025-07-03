# database/product_queries.py

import json
import psycopg2.extras
from .config import get_db_connection
from app_logger import logger

# --- MƏHSUL FUNKSİYALARI ---
def add_product(name, product_code, article, category_id, supplier_id, purchase_price, sale_price, stock, custom_attributes,
                is_food_product, pieces_in_box, pieces_in_block, barcode_unit, barcode_box, barcode_block,
                unit_of_measure, production_date, expiry_date, warehouse_location, shelf_location, row_location):
    custom_attributes_json = json.dumps(custom_attributes) if custom_attributes else None
    sql = """
        INSERT INTO products 
        (name, product_code, article, category_id, supplier_id, purchase_price, sale_price, stock, custom_attributes,
         is_food_product, pieces_in_box, pieces_in_block, barcode_unit, barcode_box, barcode_block,
         unit_of_measure, production_date, expiry_date, warehouse_location, shelf_location, row_location) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (
                name, product_code, article, category_id, supplier_id, purchase_price, sale_price, stock, custom_attributes_json,
                is_food_product, pieces_in_box, pieces_in_block, barcode_unit, barcode_box, barcode_block,
                unit_of_measure, production_date, expiry_date, warehouse_location, shelf_location, row_location
            ))
        logger.log(f"Yeni məhsul əlavə edildi: {name}")
        return True
    except Exception as e: 
        logger.log(f"XƏTA: Məhsul əlavə edilmədi: {e}")
        return False

def update_product(product_id, name, product_code, article, category_id, supplier_id, purchase_price, sale_price, stock, custom_attributes,
                   is_food_product, pieces_in_box, pieces_in_block, barcode_unit, barcode_box, barcode_block,
                   unit_of_measure, production_date, expiry_date, warehouse_location, shelf_location, row_location):
    custom_attributes_json = json.dumps(custom_attributes) if custom_attributes else None
    sql = """
        UPDATE products SET 
        name=%s, product_code=%s, article=%s, category_id=%s, supplier_id=%s, 
        purchase_price=%s, sale_price=%s, stock=%s, custom_attributes=%s,
        is_food_product=%s, pieces_in_box=%s, pieces_in_block=%s, barcode_unit=%s, barcode_box=%s, barcode_block=%s,
        unit_of_measure=%s, production_date=%s, expiry_date=%s, warehouse_location=%s, shelf_location=%s, row_location=%s
        WHERE id=%s
    """
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (
                name, product_code, article, category_id, supplier_id, purchase_price, sale_price, stock, custom_attributes_json,
                is_food_product, pieces_in_box, pieces_in_block, barcode_unit, barcode_box, barcode_block,
                unit_of_measure, production_date, expiry_date, warehouse_location, shelf_location, row_location,
                product_id
            ))
        logger.log(f"Məhsul məlumatları yeniləndi (ID: {product_id}): {name}")
        return True
    except Exception as e: 
        logger.log(f"XƏTA: Məhsul yenilənmədi (ID: {product_id}): {e}")
        return False
def get_all_products():
    sql = "SELECT p.*, s.name as supplier_name, c.name as category_name FROM products p LEFT JOIN suppliers s ON p.supplier_id = s.id LEFT JOIN categories c ON p.category_id = c.id ORDER BY p.name;"
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Bütün məhsulları alarkən xəta: {e}")
        return []

def get_product_by_id(product_id):
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Bütün yeni sütunları da sorğuya əlavə edirik
            cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            return cur.fetchone()
    except Exception as e:
        logger.log(f"XƏTA: ID {product_id} olan məhsulu alarkən xəta: {e}")
        return None

def delete_product(product_id):
    sql = "DELETE FROM products WHERE id = %s"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (product_id,))
        logger.log(f"Məhsul silindi (ID: {product_id})")
        return True
    except psycopg2.Error as e:
        logger.log(f"XƏTA: Məhsul silinmədi (ID: {product_id}). Səbəb: Qaimələrdə istifadə oluna bilər. Detal: {e}")
        return False

# --- KATEQORİYA FUNKSİYALARI ---
def add_category(name, parent_id=None):
    sql = "INSERT INTO categories (name, parent_id) VALUES (%s, %s);"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (name, parent_id))
        logger.log(f"Yeni kateqoriya yaradıldı: {name}")
        return True
    except Exception as e: 
        logger.log(f"XƏTA: Kateqoriya əlavə etmək mümkün olmadı: {e}")
        return False

def get_all_categories():
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM categories ORDER BY name")
            return cur.fetchall()
    except Exception as e: 
        logger.log(f"XƏTA: Kateqoriyaları alarkən xəta: {e}")
        return []
        
def update_category_name(category_id, new_name):
    sql = "UPDATE categories SET name = %s WHERE id = %s;"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (new_name, category_id))
        logger.log(f"Kateqoriya adı dəyişdirildi (ID: {category_id}) -> Yeni ad: {new_name}")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Kateqoriya adını yeniləmək mümkün olmadı: {e}")
        return False

def delete_category(category_id):
    sql = "DELETE FROM categories WHERE id = %s;"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (category_id,))
        logger.log(f"Kateqoriya silindi (ID: {category_id})")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Kateqoriyanı silmək mümkün olmadı: {e}")
        return False

# --- XÜSUSİ SAHƏ (CUSTOM FIELD) FUNKSİYALARI ---
def get_custom_field_definitions(active_only=False):
    """Bütün və ya yalnız aktiv olan xüsusi sahə təriflərini qaytarır."""
    sql = "SELECT id, field_key, field_name, is_active FROM custom_product_fields ORDER BY field_name"
    if active_only:
        sql = "SELECT id, field_key, field_name, is_active FROM custom_product_fields WHERE is_active = TRUE ORDER BY field_name"
    
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Xüsusi sahə təriflərini alarkən xəta: {e}")
        return []

def add_custom_field_definition(field_key, field_name):
    """Yeni xüsusi sahə tərifi əlavə edir."""
    sql = "INSERT INTO custom_product_fields (field_key, field_name) VALUES (%s, %s);"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (field_key.lower().replace(" ", "_"), field_name))
        logger.log(f"Yeni xüsusi sahə yaradıldı: {field_name} ({field_key})")
        return True
    except psycopg2.IntegrityError:
        logger.log(f"XƏTA: '{field_key}' açar sözü ilə sahə artıq mövcuddur.")
        return False
    except Exception as e:
        logger.log(f"XƏTA: Xüsusi sahə əlavə etmək mümkün olmadı: {e}")
        return False

def update_custom_field_definition(field_id, new_key, new_name):
    """Mövcud xüsusi sahə tərifini yeniləyir."""
    sql = "UPDATE custom_product_fields SET field_key = %s, field_name = %s WHERE id = %s"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (new_key, new_name, field_id))
        logger.log(f"Xüsusi sahə yeniləndi (ID: {field_id})")
        return True
    except psycopg2.IntegrityError:
        logger.log(f"XƏTA: '{new_key}' açar sözü ilə başqa bir sahə artıq mövcuddur.")
        return False
    except Exception as e:
        logger.log(f"XƏTA: Xüsusi sahəni yeniləmək mümkün olmadı: {e}")
        return False

def toggle_custom_field_active_status(field_id):
    """Sahənin aktiv/passiv statusunu dəyişir."""
    sql = "UPDATE custom_product_fields SET is_active = NOT is_active WHERE id = %s"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (field_id,))
        logger.log(f"Xüsusi sahənin statusu dəyişdirildi (ID: {field_id})")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Xüsusi sahənin statusunu dəyişmək mümkün olmadı: {e}")
        return False

def delete_custom_field_definition(field_id):
    """Mövcud xüsusi sahə tərifini silir."""
    sql = "DELETE FROM custom_product_fields WHERE id = %s;"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (field_id,))
        logger.log(f"Xüsusi sahə tərifi silindi (ID: {field_id})")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Xüsusi sahə tərifini silmək mümkün olmadı: {e}")
        return False