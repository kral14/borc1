# database/invoice_queries.py

import datetime
import psycopg2.extras
from .config import get_db_connection
from app_logger import logger

# --- ALIŞ QAİMƏSİ FUNKSİYALARI ---
def add_purchase_invoice(supplier_id, invoice_number, invoice_date, due_date, notes, total_amount, items):
    invoice_sql = "INSERT INTO purchase_invoices (supplier_id, invoice_number, invoice_date, due_date, notes, total_amount) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
    items_sql = "INSERT INTO purchase_invoice_items (purchase_invoice_id, product_id, quantity, unit_price, discount_percent, line_total) VALUES (%s, %s, %s, %s, %s, %s);"
    stock_sql = "UPDATE products SET stock = stock + %s WHERE id = %s;"
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(invoice_sql, (supplier_id, invoice_number, invoice_date, due_date, notes, total_amount))
            invoice_id = cur.fetchone()[0]
            for item in items:
                cur.execute(items_sql, (invoice_id, item['product_id'], item['quantity'], item['unit_price'], item['discount'], item['line_total']))
                cur.execute(stock_sql, (item['quantity'], item['product_id']))
        conn.commit()
        logger.log(f"Yeni Alış Qaiməsi (№{invoice_number}) uğurla əlavə edildi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Alış qaiməsi əlavə edilmədi (№{invoice_number}): {e}")
        return False
    finally:
        if conn: conn.close()

def update_purchase_invoice(invoice_id, supplier_id, invoice_number, invoice_date, due_date, notes, total_amount, items):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("UPDATE products p SET stock = p.stock - pi.quantity FROM purchase_invoice_items pi WHERE p.id = pi.product_id AND pi.purchase_invoice_id = %s;", (invoice_id,))
            cur.execute("DELETE FROM purchase_invoice_items WHERE purchase_invoice_id = %s;", (invoice_id,))
            cur.execute("UPDATE purchase_invoices SET supplier_id = %s, invoice_number = %s, invoice_date = %s, due_date = %s, notes = %s, total_amount = %s WHERE id = %s;", (supplier_id, invoice_number, invoice_date, due_date, notes, total_amount, invoice_id))
            items_sql = "INSERT INTO purchase_invoice_items (purchase_invoice_id, product_id, quantity, unit_price, discount_percent, line_total) VALUES (%s, %s, %s, %s, %s, %s);"
            stock_sql = "UPDATE products SET stock = stock + %s WHERE id = %s;"
            for item in items:
                cur.execute(items_sql, (invoice_id, item['product_id'], item['quantity'], item['unit_price'], item['discount'], item['line_total']))
                cur.execute(stock_sql, (item['quantity'], item['product_id']))
        conn.commit()
        logger.log(f"Alış Qaiməsi (ID: {invoice_id}, №{invoice_number}) uğurla yeniləndi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Alış qaiməsi yenilənmədi (ID: {invoice_id}): {e}")
        return False
    finally:
        if conn: conn.close()

def delete_purchase_invoice(invoice_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("UPDATE products p SET stock = p.stock - pi.quantity FROM purchase_invoice_items pi WHERE p.id = pi.product_id AND pi.purchase_invoice_id = %s;", (invoice_id,))
            cur.execute("DELETE FROM purchase_invoices WHERE id = %s;", (invoice_id,))
        conn.commit()
        logger.log(f"Alış Qaiməsi (ID: {invoice_id}) və bağlı stoklar uğurla silindi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Alış qaiməsi silinmədi (ID: {invoice_id}): {e}")
        return False
    finally:
        if conn: conn.close()

def get_all_purchase_invoices():
    sql = "SELECT pi.id, pi.invoice_number, s.name as supplier_name, pi.invoice_date, pi.due_date, pi.notes, pi.total_amount, pi.is_paid, pi.is_active FROM purchase_invoices pi LEFT JOIN suppliers s ON pi.supplier_id = s.id ORDER BY pi.invoice_date DESC, pi.id DESC;"
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Bütün alış qaimələrini alarkən xəta: {e}")
        return []

def get_purchase_invoice_details(invoice_id):
    details = {}
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM purchase_invoices WHERE id = %s", (invoice_id,))
            details['invoice'] = cur.fetchone()
            cur.execute("SELECT pi.*, p.name as product_name, p.barcode, p.article FROM purchase_invoice_items pi JOIN products p ON pi.product_id = p.id WHERE pi.purchase_invoice_id = %s", (invoice_id,))
            details['items'] = cur.fetchall()
            return details
    except Exception as e:
        logger.log(f"XƏTA: Alış qaiməsi detallarını alarkən xəta (ID: {invoice_id}): {e}")
        return None

def toggle_purchase_invoice_status(invoice_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT is_active FROM purchase_invoices WHERE id = %s;", (invoice_id,))
            is_currently_active = cur.fetchone()[0]
            cur.execute("SELECT product_id, quantity FROM purchase_invoice_items WHERE purchase_invoice_id = %s;", (invoice_id,))
            items = cur.fetchall()
            operator = "-" if is_currently_active else "+"
            log_action = "deaktiv edildi, stoklar geri alındı" if is_currently_active else "aktiv edildi, stoklar artırıldı"
            for product_id, quantity in items:
                cur.execute(f"UPDATE products SET stock = stock {operator} %s WHERE id = %s;", (quantity, product_id))
            cur.execute("UPDATE purchase_invoices SET is_active = NOT is_active WHERE id = %s;", (invoice_id,))
        conn.commit()
        logger.log(f"Alış qaiməsi (ID: {invoice_id}) {log_action}.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Alış qaiməsi statusunu dəyişmək mümkün olmadı (ID: {invoice_id}): {e}")
        return False
    finally:
        if conn: conn.close()

def get_next_purchase_invoice_number():
    sql = "SELECT last_value FROM purchase_invoices_id_seq;"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql)
            last_id = cur.fetchone()[0]
            next_id = last_id + 1
            year = datetime.date.today().year
            return f"AQ-{year}-{next_id}"
    except Exception:
        year = datetime.date.today().year
        return f"AQ-{year}-1"

# --- SATIŞ QAİMƏSİ FUNKSİYALARI ---
def add_sales_invoice(customer_id, invoice_number, invoice_date, due_date, notes, total_amount, items):
    conn = None
    invoice_sql = "INSERT INTO sales_invoices (customer_id, invoice_number, invoice_date, due_date, notes, total_amount) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
    items_sql = "INSERT INTO sales_invoice_items (invoice_id, product_id, quantity, unit_price, discount_percent, total_price) VALUES (%s, %s, %s, %s, %s, %s);"
    stock_sql = "UPDATE products SET stock = stock - %s WHERE id = %s;"
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(invoice_sql, (customer_id, invoice_number, invoice_date, due_date, notes, total_amount))
            invoice_id = cur.fetchone()[0]
            for item in items:
                cur.execute(items_sql, (invoice_id, item['product_id'], item['quantity'], item['unit_price'], item['discount'], item['line_total']))
                cur.execute(stock_sql, (item['quantity'], item['product_id']))
        conn.commit()
        logger.log(f"Yeni Satış Qaiməsi (№{invoice_number}) uğurla əlavə edildi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Satış qaiməsi əlavə edilmədi (№{invoice_number}): {e}")
        return False
    finally:
        if conn: conn.close()

def update_sales_invoice(invoice_id, customer_id, invoice_number, invoice_date, due_date, notes, total_amount, items):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("UPDATE products p SET stock = p.stock + si.quantity FROM sales_invoice_items si WHERE p.id = si.product_id AND si.invoice_id = %s;", (invoice_id,))
            cur.execute("DELETE FROM sales_invoice_items WHERE invoice_id = %s;", (invoice_id,))
            cur.execute("UPDATE sales_invoices SET customer_id = %s, invoice_number = %s, invoice_date = %s, due_date = %s, notes = %s, total_amount = %s WHERE id = %s;",(customer_id, invoice_number, invoice_date, due_date, notes, total_amount, invoice_id))
            items_sql = "INSERT INTO sales_invoice_items (invoice_id, product_id, quantity, unit_price, discount_percent, total_price) VALUES (%s, %s, %s, %s, %s, %s);"
            stock_sql = "UPDATE products SET stock = stock - %s WHERE id = %s;"
            for item in items:
                cur.execute(items_sql, (invoice_id, item['product_id'], item['quantity'], item['unit_price'], item['discount'], item['line_total']))
                cur.execute(stock_sql, (item['quantity'], item['product_id']))
        conn.commit()
        logger.log(f"Satış Qaiməsi (ID: {invoice_id}, №{invoice_number}) uğurla yeniləndi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Satış qaiməsi yenilənmədi (ID: {invoice_id}): {e}")
        return False
    finally:
        if conn: conn.close()

def delete_sales_invoice(invoice_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("UPDATE products p SET stock = p.stock + si.quantity FROM sales_invoice_items si WHERE p.id = si.product_id AND si.invoice_id = %s;", (invoice_id,))
            cur.execute("DELETE FROM sales_invoices WHERE id = %s;", (invoice_id,))
        conn.commit()
        logger.log(f"Satış Qaiməsi (ID: {invoice_id}) və bağlı stoklar uğurla silindi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Satış qaiməsi silinmədi (ID: {invoice_id}): {e}")
        return False
    finally:
        if conn: conn.close()

def get_all_sales_invoices():
    sql = "SELECT si.id, si.invoice_number, c.name as customer_name, si.invoice_date, si.due_date, si.notes, si.total_amount, si.is_paid, si.is_active FROM sales_invoices si LEFT JOIN customers c ON si.customer_id = c.id ORDER BY si.invoice_date DESC, si.id DESC;"
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Bütün satış qaimələrini alarkən xəta: {e}")
        return []

def get_sales_invoice_details(invoice_id):
    details = {}
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM sales_invoices WHERE id = %s", (invoice_id,))
            details['invoice'] = cur.fetchone()
            cur.execute("SELECT sii.*, p.name as product_name FROM sales_invoice_items sii JOIN products p ON sii.product_id = p.id WHERE sii.invoice_id = %s", (invoice_id,))
            details['items'] = cur.fetchall()
            return details
    except Exception as e:
        logger.log(f"XƏTA: Satış qaiməsi detallarını alarkən xəta (ID: {invoice_id}): {e}")
        return None

def toggle_sales_invoice_status(invoice_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT is_active FROM sales_invoices WHERE id = %s;", (invoice_id,))
            is_currently_active = cur.fetchone()[0]
            cur.execute("SELECT product_id, quantity FROM sales_invoice_items WHERE invoice_id = %s;", (invoice_id,))
            items = cur.fetchall()
            operator = "+" if is_currently_active else "-"
            log_action = "deaktiv edildi, stoklar geri artırıldı" if is_currently_active else "aktiv edildi, stoklar azaldıldı"
            for product_id, quantity in items:
                cur.execute(f"UPDATE products SET stock = stock {operator} %s WHERE id = %s;", (quantity, product_id))
            cur.execute("UPDATE sales_invoices SET is_active = NOT is_active WHERE id = %s;", (invoice_id,))
        conn.commit()
        logger.log(f"Satış qaiməsi (ID: {invoice_id}) {log_action}.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Satış qaiməsi statusunu dəyişmək mümkün olmadı (ID: {invoice_id}): {e}")
        return False
    finally:
        if conn: conn.close()

def get_next_sales_invoice_number():
    sql = "SELECT last_value FROM sales_invoices_id_seq;"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql)
            last_id = cur.fetchone()[0]
            next_id = last_id + 1
            year = datetime.date.today().year
            return f"SQ-{year}-{next_id}"
    except Exception:
        year = datetime.date.today().year
        return f"SQ-{year}-1"