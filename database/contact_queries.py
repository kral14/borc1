# database/contact_queries.py

import psycopg2.extras
from .config import get_db_connection
from app_logger import logger

# --- MÜŞTƏRİ FUNKSİYALARI ---
def add_customer(name, phone, address):
    sql = "INSERT INTO customers(name, phone, address) VALUES(%s, %s, %s)"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (name, phone, address))
        logger.log(f"Yeni müştəri əlavə edildi: {name}")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Müştəri əlavə etmək mümkün olmadı: {e}")
        return False

def update_customer(customer_id, name, phone, address):
    sql = "UPDATE customers SET name = %s, phone = %s, address = %s WHERE id = %s"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (name, phone, address, customer_id))
        logger.log(f"Müştəri məlumatları yeniləndi (ID: {customer_id}): {name}")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Müştəri yeniləmək mümkün olmadı (ID: {customer_id}): {e}")
        return False

def delete_customer(customer_id):
    sql = "DELETE FROM customers WHERE id = %s"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (customer_id,))
        logger.log(f"Müştəri silindi (ID: {customer_id})")
        return True
    except psycopg2.Error as e:
        logger.log(f"XƏTA: Müştəri silinmədi (ID: {customer_id}). Səbəb: Satış qaimələri mövcuddur. Detal: {e}")
        return False

def get_customer_by_id(customer_id):
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
            return cur.fetchone()
    except Exception as e:
        logger.log(f"XƏTA: ID {customer_id} olan müştərini alarkən xəta: {e}")
        return None
def get_all_customers_with_debt():
    # DÜZƏLİŞ: Borc hesablanarkən total_amount-dan paid_amount çıxılır
    sql = """
        SELECT 
            c.id, c.name, c.phone, c.address, c.is_active, 
            COALESCE(SUM(i.total_amount - i.paid_amount), 0) as total_debt 
        FROM customers c 
        LEFT JOIN sales_invoices i ON c.id = i.customer_id AND i.is_paid = FALSE AND i.is_active = TRUE
        GROUP BY c.id 
        ORDER BY c.name;
    """
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Müştəriləri borcları ilə birgə alarkən xəta: {e}")
        return []
# --- SATICI FUNKSİYALARI ---
def add_supplier(name, contact_person, phone, address):
    sql = "INSERT INTO suppliers(name, contact_person, phone, address) VALUES(%s, %s, %s, %s)"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (name, contact_person, phone, address))
        logger.log(f"Yeni satıcı əlavə edildi: {name}")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Satıcı əlavə etmək mümkün olmadı: {e}")
        return False

def update_supplier(supplier_id, name, contact_person, phone, address):
    sql = "UPDATE suppliers SET name = %s, contact_person = %s, phone = %s, address = %s WHERE id = %s"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (name, contact_person, phone, address, supplier_id))
        logger.log(f"Satıcı məlumatları yeniləndi (ID: {supplier_id}): {name}")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Satıcı yeniləmək mümkün olmadı (ID: {supplier_id}): {e}")
        return False

def delete_supplier(supplier_id):
    sql = "DELETE FROM suppliers WHERE id = %s"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (supplier_id,))
        logger.log(f"Satıcı silindi (ID: {supplier_id})")
        return True
    except psycopg2.Error as e:
        logger.log(f"XƏTA: Satıcı silinmədi (ID: {supplier_id}). Səbəb: Alış qaimələri mövcuddur. Detal: {e}")
        return False

def get_supplier_by_id(supplier_id):
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM suppliers WHERE id = %s", (supplier_id,))
            return cur.fetchone()
    except Exception as e:
        logger.log(f"XƏTA: ID {supplier_id} olan satıcını alarkən xəta: {e}")
        return None
        
def get_all_suppliers():
    # DÜZƏLİŞ: Bizim borcumuz hesablanarkən total_amount-dan paid_amount çıxılır
    sql = """
        SELECT 
            s.id, s.name, s.contact_person, s.phone, s.address, 
            COALESCE(SUM(pi.total_amount - pi.paid_amount), 0) as total_debt 
        FROM suppliers s 
        LEFT JOIN purchase_invoices pi ON s.id = pi.supplier_id AND pi.is_paid = FALSE AND pi.is_active = TRUE
        GROUP BY s.id 
        ORDER BY s.name;
    """
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Satıcıları borcları ilə birgə alarkən xəta: {e}")
        return []