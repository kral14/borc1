# database/payment_queries.py (Tam və Düzəliş Edilmiş Versiya)

import psycopg2.extras
from .config import get_db_connection
from app_logger import logger

# --- MƏDAXİL FUNKSİYALARI (Müştəri Ödənişləri) ---

def get_unpaid_invoices_for_customer(customer_id):
    """Müştərinin ödənilməmiş qaimələrini qaytarır."""
    sql = """
        SELECT id, invoice_number, invoice_date, total_amount, paid_amount,
               (total_amount - paid_amount) as remaining_debt
        FROM sales_invoices
        WHERE customer_id = %s AND is_paid = FALSE AND is_active = TRUE
        ORDER BY invoice_date;
    """
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (customer_id,))
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Müştərinin ({customer_id}) ödənilməmiş qaimələrini alarkən xəta: {e}")
        return []

def add_customer_payment(customer_id, invoice_id, amount, payment_date, notes):
    """Müştəri ödənişini əlavə edir və qaiməni yeniləyir (Tranzaksiya ilə)."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO customer_payments (customer_id, sales_invoice_id, amount, payment_date, notes) VALUES (%s, %s, %s, %s, %s)",
                (customer_id, invoice_id, amount, payment_date, notes)
            )
            cur.execute(
                "UPDATE sales_invoices SET paid_amount = paid_amount + %s WHERE id = %s",
                (amount, invoice_id)
            )
            cur.execute(
                "UPDATE sales_invoices SET is_paid = TRUE WHERE id = %s AND paid_amount >= total_amount",
                (invoice_id,)
            )
        conn.commit()
        logger.log(f"Müştəri (ID: {customer_id}) tərəfindən {amount} AZN məbləğində ödəniş qəbul edildi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Müştəri ödənişi əlavə edilərkən tranzaksiya xətası: {e}")
        return False
    finally:
        if conn: conn.close()

def get_all_payments(customer_id=None):
    """Bütün və ya seçilmiş müştərinin ödənişlərini qaytarır."""
    sql = """
        SELECT 
            p.id, p.payment_date, p.amount, p.notes, p.is_active,
            p.sales_invoice_id, c.name as customer_name,
            si.invoice_number
        FROM customer_payments p
        JOIN customers c ON p.customer_id = c.id
        LEFT JOIN sales_invoices si ON p.sales_invoice_id = si.id
    """
    params = []
    if customer_id:
        sql += " WHERE p.customer_id = %s"
        params.append(customer_id)
    
    sql += " ORDER BY p.payment_date DESC, p.id DESC;"

    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Ödənişləri alarkən xəta: {e}")
        return []

def delete_customer_payment(payment_id):
    """Ödənişi silir və qaimədəki məbləği geri qaytarır."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT amount, sales_invoice_id, is_active FROM customer_payments WHERE id = %s", (payment_id,))
            payment = cur.fetchone()
            if not payment:
                logger.log(f"XƏTA: Silinəcək ödəniş (ID: {payment_id}) tapılmadı.")
                return False

            if payment['is_active'] and payment['sales_invoice_id']:
                cur.execute(
                    "UPDATE sales_invoices SET paid_amount = paid_amount - %s, is_paid = FALSE WHERE id = %s",
                    (payment['amount'], payment['sales_invoice_id'])
                )
            
            cur.execute("DELETE FROM customer_payments WHERE id = %s", (payment_id,))
        
        conn.commit()
        logger.log(f"Ödəniş (ID: {payment_id}) uğurla silindi və qaimə yeniləndi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Ödəniş silinərkən (ID: {payment_id}): {e}")
        return False
    finally:
        if conn: conn.close()

# --- MƏXARİC FUNKSİYALARI (Tədarükçü Ödənişləri) ---

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
            cur.execute(
                "INSERT INTO cash_expenses (supplier_id, purchase_invoice_id, amount, expense_date, description) VALUES (%s, %s, %s, %s, %s)",
                (supplier_id, invoice_id, amount, expense_date, description)
            )
            cur.execute(
                "UPDATE purchase_invoices SET paid_amount = paid_amount + %s WHERE id = %s",
                (amount, invoice_id)
            )
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

def get_all_cash_expenses(supplier_id=None):
    """Bütün və ya seçilmiş tədarükçünün məxariclərini qaytarır."""
    sql = """
        SELECT 
            e.id, e.expense_date, e.amount, e.description, e.is_active,
            e.purchase_invoice_id, s.name as supplier_name,
            pi.invoice_number
        FROM cash_expenses e
        LEFT JOIN suppliers s ON e.supplier_id = s.id
        LEFT JOIN purchase_invoices pi ON e.purchase_invoice_id = pi.id
    """
    params = []
    if supplier_id:
        sql += " WHERE e.supplier_id = %s"
        params.append(supplier_id)
    
    sql += " ORDER BY e.expense_date DESC, e.id DESC;"
    try:
        with get_db_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Bütün məxaricləri alarkən xəta: {e}")
        return []

def delete_supplier_payment(expense_id):
    """Məxarici silir və alış qaiməsindəki məbləği geri qaytarır."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT amount, purchase_invoice_id, is_active FROM cash_expenses WHERE id = %s", (expense_id,))
            expense = cur.fetchone()
            if not expense:
                logger.log(f"XƏTA: Silinəcək məxaric (ID: {expense_id}) tapılmadı.")
                return False

            if expense['is_active'] and expense['purchase_invoice_id']:
                cur.execute(
                    "UPDATE purchase_invoices SET paid_amount = paid_amount - %s, is_paid = FALSE WHERE id = %s",
                    (expense['amount'], expense['purchase_invoice_id'])
                )
            
            cur.execute("DELETE FROM cash_expenses WHERE id = %s", (expense_id,))
        
        conn.commit()
        logger.log(f"Məxaric (ID: {expense_id}) uğurla silindi və alış qaiməsi yeniləndi.")
        return True
    except Exception as e:
        if conn: conn.rollback()
        logger.log(f"XƏTA: Məxaric silinərkən (ID: {expense_id}): {e}")
        return False
    finally:
        if conn: conn.close()
        # borc/database/payment_queries.py faylının sonuna əlavə edin

def check_payments_for_sales_invoice(sales_invoice_id):
    """
    Müəyyən bir satış qaiməsi ilə bağlı ödənişləri yoxlayır.
    Ödənilmiş ümumi məbləği qaytarır.
    """
    sql = "SELECT COALESCE(SUM(amount), 0) FROM customer_payments WHERE sales_invoice_id = %s AND is_active = TRUE;"
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (sales_invoice_id,))
            total_paid = cur.fetchone()[0]
            return total_paid or 0
    except Exception as e:
        logger.log(f"XƏTA: Satış qaiməsi üçün ödənişləri yoxlayarkən xəta: {e}")
        return 0 # Xəta baş verərsə, 0 qaytar