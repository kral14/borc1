# database/payment_queries.py (Məxaric funksiyaları əlavə edilmiş)

import psycopg2.extras
from .config import get_db_connection
from app_logger import logger

# --- MƏDAXİL FUNKSİYALARI (Müştəri Ödənişləri) ---

def get_unpaid_invoices_for_customer(customer_id):
    # ... (Bu funksiya dəyişmir) ...
    sql = "SELECT id, invoice_number, invoice_date, total_amount, paid_amount, (total_amount - paid_amount) as remaining_debt FROM sales_invoices WHERE customer_id = %s AND is_paid = FALSE AND is_active = TRUE ORDER BY invoice_date;"
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (customer_id,))
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Müştərinin ({customer_id}) ödənilməmiş qaimələrini alarkən xəta: {e}")
        return []

def add_customer_payment(customer_id, invoice_id, amount, payment_date, notes):
    # ... (Bu funksiya dəyişmir) ...
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO customer_payments (customer_id, sales_invoice_id, amount, payment_date, notes) VALUES (%s, %s, %s, %s, %s)", (customer_id, invoice_id, amount, payment_date, notes))
            cur.execute("UPDATE sales_invoices SET paid_amount = paid_amount + %s WHERE id = %s", (amount, invoice_id))
            cur.execute("UPDATE sales_invoices SET is_paid = TRUE WHERE id = %s AND paid_amount >= total_amount", (invoice_id,))
            conn.commit()
        logger.log(f"Müştəri (ID: {customer_id}) tərəfindən {amount} AZN məbləğində ödəniş qəbul edildi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Müştəri ödənişi əlavə edilərkən tranzaksiya xətası: {e}")
        return False
    finally:
        if conn: conn.close()

def get_all_payments():
    # ... (Bu funksiya dəyişmir) ...
    sql = "SELECT p.id, p.payment_date, p.amount, p.notes, c.name as customer_name, si.invoice_number FROM customer_payments p JOIN customers c ON p.customer_id = c.id LEFT JOIN sales_invoices si ON p.sales_invoice_id = si.id ORDER BY p.payment_date DESC, p.id DESC;"
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Bütün ödənişləri alarkən xəta: {e}")
        return []

# --- YENİ: MƏXARİC FUNKSİYALARI (Tədarükçü Ödənişləri) ---

def get_unpaid_purchase_invoices_for_supplier(supplier_id):
    """Tədarükçünün ödənilməmiş alış qaimələrini qaytarır."""
    sql = """
        SELECT id, invoice_number, invoice_date, total_amount, paid_amount,
               (total_amount - paid_amount) as remaining_debt
        FROM purchase_invoices
        WHERE supplier_id = %s AND is_paid = FALSE AND is_active = TRUE
        ORDER BY invoice_date;
    """
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (supplier_id,))
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Tədarükçünün ({supplier_id}) ödənilməmiş qaimələrini alarkən xəta: {e}")
        return []

def add_supplier_payment(supplier_id, invoice_id, amount, expense_date, description):
    """Tədarükçüyə ödənişi (məxarici) əlavə edir və alış qaiməsini yeniləyir."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # 1. Ödənişi `cash_expenses` cədvəlinə əlavə et
            cur.execute(
                "INSERT INTO cash_expenses (supplier_id, purchase_invoice_id, amount, expense_date, description) VALUES (%s, %s, %s, %s, %s)",
                (supplier_id, invoice_id, amount, expense_date, description)
            )

            # 2. `purchase_invoices` cədvəlində ödənilən məbləği yenilə
            cur.execute(
                "UPDATE purchase_invoices SET paid_amount = paid_amount + %s WHERE id = %s",
                (amount, invoice_id)
            )
            
            # 3. Alış qaimənin tam ödənilib-ödənilmədiyini yoxla və statusunu yenilə
            cur.execute(
                "UPDATE purchase_invoices SET is_paid = TRUE WHERE id = %s AND paid_amount >= total_amount",
                (invoice_id,)
            )
            
            conn.commit()
        logger.log(f"Tədarükçüyə (ID: {supplier_id}) {amount} AZN məbləğində məxaric edildi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Tədarükçü ödənişi əlavə edilərkən tranzaksiya xətası: {e}")
        return False
    finally:
        if conn: conn.close()

def get_all_cash_expenses():
    """Bütün məxaricləri tədarükçü adları ilə birlikdə qaytarır."""
    sql = """
        SELECT 
            e.id, e.expense_date, e.amount, e.description,
            s.name as supplier_name,
            pi.invoice_number
        FROM cash_expenses e
        LEFT JOIN suppliers s ON e.supplier_id = s.id
        LEFT JOIN purchase_invoices pi ON e.purchase_invoice_id = pi.id
        ORDER BY e.expense_date DESC, e.id DESC;
    """
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Bütün məxaricləri alarkən xəta: {e}")
        return []