# database.py (Tam, düzəliş edilmiş və loglama əlavə edilmiş versiya)

import os
import psycopg2
import psycopg2.extras
import datetime
from app_logger import logger # Log sistemini import edirik

# Verilənlər bazası bağlantı məlumatı
DATABASE_URL = "postgresql://takib_owner:npg_98btwuhVScvy@ep-rough-mountain-a9izj47k-pooler.gwc.azure.neon.tech/takib?sslmode=require"

def get_db_connection():
    """Verilənlər bazasına qoşulmaq üçün funksiya"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.log("Verilənlər bazasına uğurla qoşulma baş tutdu.")
        return conn
    except psycopg2.OperationalError as e:
        logger.log(f"KRİTİK XƏTA: Verilənlər bazasına qoşulmaq mümkün olmadı: {e}")
        print(f"Verilənlər bazasına qoşulma xətası: {e}")
        return None

def add_column_safely(table, column_name, column_type):
    """Hər bir sütunu ayrı bir tranzaksiyada, təhlükəsiz şəkildə əlavə edir."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column_name} {column_type};")
        logger.log(f"Sütun yoxlanıldı/əlavə edildi: '{table}' cədvəlində '{column_name}'.")
        cur.close()
    except Exception as e:
        logger.log(f"Sütun əlavə edilərkən xəta ({table}.{column_name}): {e}")
        print(f"Sütun əlavə edilərkən xəta baş verdi ({table}.{column_name}): {e}")
    finally:
        if conn: conn.close()

def create_tables():
    """Proqram üçün lazım olan bütün cədvəlləri yaradır və mövcud cədvəlləri yeniləyir"""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None: return
        cur = conn.cursor()
        
        commands = (
            """
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, phone VARCHAR(50), address TEXT,
                is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS suppliers (
                id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, contact_person VARCHAR(255),
                phone VARCHAR(50), address TEXT, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL,
                parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, barcode VARCHAR(100), product_code VARCHAR(100),
                article VARCHAR(100), 
                purchase_price NUMERIC(10, 2) DEFAULT 0, sale_price NUMERIC(10, 2) DEFAULT 0,
                stock INTEGER DEFAULT 0, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                supplier_id INTEGER REFERENCES suppliers (id) ON DELETE SET NULL,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS sales_invoices (
                id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL, invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
                total_amount NUMERIC(10, 2) NOT NULL, is_paid BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS sales_invoice_items (
                id SERIAL PRIMARY KEY, invoice_id INTEGER NOT NULL, product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL, unit_price NUMERIC(10, 2) NOT NULL, total_price NUMERIC(10, 2) NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES sales_invoices (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS purchase_invoices (
                id SERIAL PRIMARY KEY, supplier_id INTEGER NOT NULL, invoice_number VARCHAR(100),
                invoice_date DATE NOT NULL DEFAULT CURRENT_DATE, total_amount NUMERIC(10, 2) NOT NULL,
                is_paid BOOLEAN DEFAULT FALSE, is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE RESTRICT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS purchase_invoice_items (
                id SERIAL PRIMARY KEY, purchase_invoice_id INTEGER NOT NULL, product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL, unit_price NUMERIC(10, 2) NOT NULL,
                discount_percent NUMERIC(5, 2) DEFAULT 0, line_total NUMERIC(10, 2) NOT NULL,
                FOREIGN KEY (purchase_invoice_id) REFERENCES purchase_invoices (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT
            );
            """
        )
        for command in commands:
            cur.execute(command)
        
        cur.close()
        conn.commit()
        logger.log("Verilənlər bazası cədvəlləri uğurla yoxlanıldı/yaradıldı.")
    except Exception as e:
        logger.log(f"KRİTİK XƏTA: Əsas cədvəllər yaradılarkən xəta: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

    logger.log("Əlavə sütunlar yoxlanılır...")
    add_column_safely("products", "category_id", "INTEGER REFERENCES categories(id) ON DELETE SET NULL")
    add_column_safely("sales_invoices", "invoice_number", "VARCHAR(100)")
    add_column_safely("sales_invoices", "is_active", "BOOLEAN DEFAULT TRUE")
    add_column_safely("sales_invoices", "due_date", "DATE")
    add_column_safely("sales_invoices", "notes", "TEXT")
    add_column_safely("purchase_invoices", "due_date", "DATE")
    add_column_safely("purchase_invoices", "notes", "TEXT")
    add_column_safely("sales_invoice_items", "discount_percent", "NUMERIC(5, 2) DEFAULT 0")
    logger.log("Sütunların yoxlanması tamamlandı.")

# --- KATEQORIYA FUNKSİYALARI ---
def add_category(name, parent_id=None):
    sql = "INSERT INTO categories (name, parent_id) VALUES (%s, %s);"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name, parent_id))
        logger.log(f"Yeni kateqoriya yaradıldı: {name}")
        return True
    except Exception as e: 
        logger.log(f"XƏTA: Kateqoriya əlavə etmək mümkün olmadı: {e}")
        return False

def get_all_categories():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT * FROM categories ORDER BY name")
                return cur.fetchall()
    except Exception as e: 
        logger.log(f"XƏTA: Kateqoriyaları alarkən xəta: {e}")
        return []

def update_category_name(category_id, new_name):
    sql = "UPDATE categories SET name = %s WHERE id = %s;"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (new_name, category_id))
        logger.log(f"Kateqoriya adı dəyişdirildi (ID: {category_id}) -> Yeni ad: {new_name}")
        return True
    except Exception as e: 
        logger.log(f"XƏTA: Kateqoriya adını yeniləmək mümkün olmadı: {e}")
        return False

def delete_category(category_id):
    sql = "DELETE FROM categories WHERE id = %s;"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (category_id,))
        logger.log(f"Kateqoriya silindi (ID: {category_id})")
        return True
    except Exception as e: 
        logger.log(f"XƏTA: Kateqoriyanı silmək mümkün olmadı: {e}")
        return False

# --- MƏHSUL FUNKSİYALARI ---
def add_product(name, barcode, product_code, article, category_id, supplier_id, purchase_price, sale_price, stock):
    sql = "INSERT INTO products (name, barcode, product_code, article, category_id, supplier_id, purchase_price, sale_price, stock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name, barcode, product_code, article, category_id, supplier_id, purchase_price, sale_price, stock))
        logger.log(f"Yeni məhsul əlavə edildi: {name}")
        return True
    except Exception as e: 
        logger.log(f"XƏTA: Məhsul əlavə edilmədi: {e}")
        return False

def update_product(product_id, name, barcode, product_code, article, category_id, supplier_id, purchase_price, sale_price, stock):
    sql = "UPDATE products SET name=%s, barcode=%s, product_code=%s, article=%s, category_id=%s, supplier_id=%s, purchase_price=%s, sale_price=%s, stock=%s WHERE id=%s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name, barcode, product_code, article, category_id, supplier_id, purchase_price, sale_price, stock, product_id))
        logger.log(f"Məhsul məlumatları yeniləndi (ID: {product_id}): {name}")
        return True
    except Exception as e: 
        logger.log(f"XƏTA: Məhsul yenilənmədi (ID: {product_id}): {e}")
        return False

def delete_product(product_id):
    sql = "DELETE FROM products WHERE id = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (product_id,))
        logger.log(f"Məhsul silindi (ID: {product_id})")
        return True
    except psycopg2.Error as e:
        logger.log(f"XƏTA: Məhsul silinmədi (ID: {product_id}). Səbəb: Qaimələrdə istifadə oluna bilər. Detal: {e}")
        return False

def get_product_by_id(product_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                return cur.fetchone()
    except Exception as e:
        logger.log(f"XƏTA: ID {product_id} olan məhsulu alarkən xəta: {e}")
        return None

def get_all_products():
    sql = "SELECT p.*, s.name as supplier_name, c.name as category_name FROM products p LEFT JOIN suppliers s ON p.supplier_id = s.id LEFT JOIN categories c ON p.category_id = c.id ORDER BY p.name;"
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Bütün məhsulları alarkən xəta: {e}")
        return []

# --- MÜŞTƏRİ FUNKSİYALARI ---
def add_customer(name, phone, address):
    sql = "INSERT INTO customers(name, phone, address) VALUES(%s, %s, %s)"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name, phone, address))
        logger.log(f"Yeni müştəri əlavə edildi: {name}")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Müştəri əlavə etmək mümkün olmadı: {e}")
        return False

def update_customer(customer_id, name, phone, address):
    sql = "UPDATE customers SET name = %s, phone = %s, address = %s WHERE id = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name, phone, address, customer_id))
        logger.log(f"Müştəri məlumatları yeniləndi (ID: {customer_id}): {name}")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Müştəri yeniləmək mümkün olmadı (ID: {customer_id}): {e}")
        return False

def delete_customer(customer_id):
    sql = "DELETE FROM customers WHERE id = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (customer_id,))
        logger.log(f"Müştəri silindi (ID: {customer_id})")
        return True
    except psycopg2.Error as e:
        logger.log(f"XƏTA: Müştəri silinmədi (ID: {customer_id}). Səbəb: Satış qaimələri mövcuddur. Detal: {e}")
        return False

def get_customer_by_id(customer_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
                return cur.fetchone()
    except Exception as e:
        logger.log(f"XƏTA: ID {customer_id} olan müştərini alarkən xəta: {e}")
        return None

def get_all_customers_with_debt():
    sql = "SELECT c.id, c.name, c.phone, c.address, c.is_active, COALESCE(SUM(i.total_amount) FILTER (WHERE i.is_paid = FALSE AND i.is_active = TRUE), 0) as total_debt FROM customers c LEFT JOIN sales_invoices i ON c.id = i.customer_id GROUP BY c.id ORDER BY c.name;"
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Müştəriləri borcları ilə birgə alarkən xəta: {e}")
        return []

# --- SATICI FUNKSİYALARI ---
def add_supplier(name, contact_person, phone, address):
    sql = "INSERT INTO suppliers(name, contact_person, phone, address) VALUES(%s, %s, %s, %s)"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name, contact_person, phone, address))
        logger.log(f"Yeni satıcı əlavə edildi: {name}")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Satıcı əlavə etmək mümkün olmadı: {e}")
        return False

def update_supplier(supplier_id, name, contact_person, phone, address):
    sql = "UPDATE suppliers SET name = %s, contact_person = %s, phone = %s, address = %s WHERE id = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name, contact_person, phone, address, supplier_id))
        logger.log(f"Satıcı məlumatları yeniləndi (ID: {supplier_id}): {name}")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Satıcı yeniləmək mümkün olmadı (ID: {supplier_id}): {e}")
        return False

def delete_supplier(supplier_id):
    sql = "DELETE FROM suppliers WHERE id = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (supplier_id,))
        logger.log(f"Satıcı silindi (ID: {supplier_id})")
        return True
    except psycopg2.Error as e:
        logger.log(f"XƏTA: Satıcı silinmədi (ID: {supplier_id}). Səbəb: Alış qaimələri mövcuddur. Detal: {e}")
        return False

def get_supplier_by_id(supplier_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT * FROM suppliers WHERE id = %s", (supplier_id,))
                return cur.fetchone()
    except Exception as e:
        logger.log(f"XƏTA: ID {supplier_id} olan satıcını alarkən xəta: {e}")
        return None
        
def get_all_suppliers():
    sql = """
        SELECT s.id, s.name, s.contact_person, s.phone, s.address, 
               COALESCE(SUM(pi.total_amount) FILTER (WHERE pi.is_paid = FALSE AND pi.is_active = TRUE), 0) as total_debt 
        FROM suppliers s 
        LEFT JOIN purchase_invoices pi ON s.id = pi.supplier_id 
        GROUP BY s.id 
        ORDER BY s.name;
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Satıcıları borcları ilə birgə alarkən xəta: {e}")
        return []

# --- ALIŞ QAİMƏSİ FUNKSİYALARI ---
def add_purchase_invoice(supplier_id, invoice_number, invoice_date, due_date, notes, total_amount, items):
    invoice_sql = "INSERT INTO purchase_invoices (supplier_id, invoice_number, invoice_date, due_date, notes, total_amount) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
    items_sql = "INSERT INTO purchase_invoice_items (purchase_invoice_id, product_id, quantity, unit_price, discount_percent, line_total) VALUES (%s, %s, %s, %s, %s, %s);"
    stock_sql = "UPDATE products SET stock = stock + %s WHERE id = %s;"
    conn = None
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute(invoice_sql, (supplier_id, invoice_number, invoice_date, due_date, notes, total_amount)); invoice_id = cur.fetchone()[0]
        for item in items:
            cur.execute(items_sql, (invoice_id, item['product_id'], item['quantity'], item['unit_price'], item['discount'], item['line_total']))
            cur.execute(stock_sql, (item['quantity'], item['product_id']))
        conn.commit(); cur.close()
        logger.log(f"Yeni Alış Qaiməsi (№{invoice_number}) uğurla əlavə edildi.")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Alış qaiməsi əlavə edilmədi (№{invoice_number}): {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()

def update_purchase_invoice(invoice_id, supplier_id, invoice_number, invoice_date, due_date, notes, total_amount, items):
    conn = None
    try:
        conn = get_db_connection(); cur = conn.cursor()
        # Köhnə stokları geri qaytar
        cur.execute("UPDATE products p SET stock = p.stock - pi.quantity FROM purchase_invoice_items pi WHERE p.id = pi.product_id AND pi.purchase_invoice_id = %s;", (invoice_id,))
        # Köhnə qaimə detallarını sil
        cur.execute("DELETE FROM purchase_invoice_items WHERE purchase_invoice_id = %s;", (invoice_id,))
        # Əsas qaiməni yenilə
        cur.execute("UPDATE purchase_invoices SET supplier_id = %s, invoice_number = %s, invoice_date = %s, due_date = %s, notes = %s, total_amount = %s WHERE id = %s;",
                    (supplier_id, invoice_number, invoice_date, due_date, notes, total_amount, invoice_id))
        # Yeni detalları və stokları əlavə et
        items_sql = "INSERT INTO purchase_invoice_items (purchase_invoice_id, product_id, quantity, unit_price, discount_percent, line_total) VALUES (%s, %s, %s, %s, %s, %s);"
        stock_sql = "UPDATE products SET stock = stock + %s WHERE id = %s;"
        for item in items:
            cur.execute(items_sql, (invoice_id, item['product_id'], item['quantity'], item['unit_price'], item['discount'], item['line_total']))
            cur.execute(stock_sql, (item['quantity'], item['product_id']))
        conn.commit(); cur.close()
        logger.log(f"Alış Qaiməsi (ID: {invoice_id}, №{invoice_number}) uğurla yeniləndi.")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Alış qaiməsi yenilənmədi (ID: {invoice_id}): {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()

def delete_purchase_invoice(invoice_id):
    conn = None
    try:
        conn = get_db_connection(); cur = conn.cursor()
        # Stokları geri qaytar
        cur.execute("UPDATE products p SET stock = p.stock - pi.quantity FROM purchase_invoice_items pi WHERE p.id = pi.product_id AND pi.purchase_invoice_id = %s;", (invoice_id,))
        # Qaiməni sil
        cur.execute("DELETE FROM purchase_invoices WHERE id = %s;", (invoice_id,))
        conn.commit(); cur.close()
        logger.log(f"Alış Qaiməsi (ID: {invoice_id}) və bağlı stoklar uğurla silindi.")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Alış qaiməsi silinmədi (ID: {invoice_id}): {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()

def get_all_purchase_invoices():
    sql = "SELECT pi.id, pi.invoice_number, s.name as supplier_name, pi.invoice_date, pi.due_date, pi.notes, pi.total_amount, pi.is_paid, pi.is_active FROM purchase_invoices pi LEFT JOIN suppliers s ON pi.supplier_id = s.id ORDER BY pi.invoice_date DESC, pi.id DESC;"
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Bütün alış qaimələrini alarkən xəta: {e}")
        return []

def get_purchase_invoice_details(invoice_id):
    details = {}
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT * FROM purchase_invoices WHERE id = %s", (invoice_id,)); details['invoice'] = cur.fetchone()
                cur.execute("SELECT pi.*, p.name as product_name, p.barcode, p.article FROM purchase_invoice_items pi JOIN products p ON pi.product_id = p.id WHERE pi.purchase_invoice_id = %s", (invoice_id,)); details['items'] = cur.fetchall()
                return details
    except Exception as e:
        logger.log(f"XƏTA: Alış qaiməsi detallarını alarkən xəta (ID: {invoice_id}): {e}")
        return None

def toggle_purchase_invoice_status(invoice_id):
    # Bu funksiya stokları dəyişdiyi üçün diqqətli istifadə olunmalıdır
    # Tranzaksiya daxilində bütün əməliyyatların edilməsi vacibdir.
    conn = None
    try:
        conn = get_db_connection(); cur = conn.cursor()
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
        logger.log(f"XƏTA: Alış qaiməsi statusunu dəyişmək mümkün olmadı (ID: {invoice_id}): {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()

def get_next_purchase_invoice_number():
    sql = "SELECT last_value FROM purchase_invoices_id_seq;"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql); last_id = cur.fetchone()[0]
                next_id = last_id + 1; year = datetime.date.today().year; return f"AQ-{year}-{next_id}"
    except Exception:
        year = datetime.date.today().year; return f"AQ-{year}-1"

# --- SATIŞ QAİMƏSİ FUNKSİYALARI ---
def add_sales_invoice(customer_id, invoice_number, invoice_date, due_date, notes, total_amount, items):
    conn = None
    invoice_sql = "INSERT INTO sales_invoices (customer_id, invoice_number, invoice_date, due_date, notes, total_amount) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
    items_sql = "INSERT INTO sales_invoice_items (invoice_id, product_id, quantity, unit_price, discount_percent, total_price) VALUES (%s, %s, %s, %s, %s, %s);"
    stock_sql = "UPDATE products SET stock = stock - %s WHERE id = %s;"
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute(invoice_sql, (customer_id, invoice_number, invoice_date, due_date, notes, total_amount)); invoice_id = cur.fetchone()[0]
        for item in items:
            cur.execute(items_sql, (invoice_id, item['product_id'], item['quantity'], item['unit_price'], item['discount'], item['line_total']))
            cur.execute(stock_sql, (item['quantity'], item['product_id']))
        conn.commit(); cur.close()
        logger.log(f"Yeni Satış Qaiməsi (№{invoice_number}) uğurla əlavə edildi.")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Satış qaiməsi əlavə edilmədi (№{invoice_number}): {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()

def update_sales_invoice(invoice_id, customer_id, invoice_number, invoice_date, due_date, notes, total_amount, items):
    conn = None
    try:
        conn = get_db_connection(); cur = conn.cursor()
        # Köhnə stokları geri qaytar
        cur.execute("UPDATE products p SET stock = p.stock + si.quantity FROM sales_invoice_items si WHERE p.id = si.product_id AND si.invoice_id = %s;", (invoice_id,))
        # Köhnə detalları sil
        cur.execute("DELETE FROM sales_invoice_items WHERE invoice_id = %s;", (invoice_id,))
        # Əsas qaiməni yenilə
        cur.execute("UPDATE sales_invoices SET customer_id = %s, invoice_number = %s, invoice_date = %s, due_date = %s, notes = %s, total_amount = %s WHERE id = %s;",
                    (customer_id, invoice_number, invoice_date, due_date, notes, total_amount, invoice_id))
        # Yeni detalları və stokları əlavə et
        items_sql = "INSERT INTO sales_invoice_items (invoice_id, product_id, quantity, unit_price, discount_percent, total_price) VALUES (%s, %s, %s, %s, %s, %s);"
        stock_sql = "UPDATE products SET stock = stock - %s WHERE id = %s;"
        for item in items:
            cur.execute(items_sql, (invoice_id, item['product_id'], item['quantity'], item['unit_price'], item['discount'], item['line_total']))
            cur.execute(stock_sql, (item['quantity'], item['product_id']))
        conn.commit(); cur.close()
        logger.log(f"Satış Qaiməsi (ID: {invoice_id}, №{invoice_number}) uğurla yeniləndi.")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Satış qaiməsi yenilənmədi (ID: {invoice_id}): {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()

def delete_sales_invoice(invoice_id):
    conn = None
    try:
        conn = get_db_connection(); cur = conn.cursor()
        # Stokları geri qaytar
        cur.execute("UPDATE products p SET stock = p.stock + si.quantity FROM sales_invoice_items si WHERE p.id = si.product_id AND si.invoice_id = %s;", (invoice_id,))
        # Qaiməni sil
        cur.execute("DELETE FROM sales_invoices WHERE id = %s;", (invoice_id,))
        conn.commit(); cur.close()
        logger.log(f"Satış Qaiməsi (ID: {invoice_id}) və bağlı stoklar uğurla silindi.")
        return True
    except Exception as e:
        logger.log(f"XƏTA: Satış qaiməsi silinmədi (ID: {invoice_id}): {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()

def get_all_sales_invoices():
    sql = "SELECT si.id, si.invoice_number, c.name as customer_name, si.invoice_date, si.due_date, si.notes, si.total_amount, si.is_paid, si.is_active FROM sales_invoices si LEFT JOIN customers c ON si.customer_id = c.id ORDER BY si.invoice_date DESC, si.id DESC;"
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()
    except Exception as e:
        logger.log(f"XƏTA: Bütün satış qaimələrini alarkən xəta: {e}")
        return []

def get_sales_invoice_details(invoice_id):
    details = {}
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT * FROM sales_invoices WHERE id = %s", (invoice_id,)); details['invoice'] = cur.fetchone()
                cur.execute("SELECT sii.*, p.name as product_name FROM sales_invoice_items sii JOIN products p ON sii.product_id = p.id WHERE sii.invoice_id = %s", (invoice_id,)); details['items'] = cur.fetchall()
                return details
    except Exception as e:
        logger.log(f"XƏTA: Satış qaiməsi detallarını alarkən xəta (ID: {invoice_id}): {e}")
        return None

def toggle_sales_invoice_status(invoice_id):
    conn = None
    try:
        conn = get_db_connection(); cur = conn.cursor()
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
        logger.log(f"XƏTA: Satış qaiməsi statusunu dəyişmək mümkün olmadı (ID: {invoice_id}): {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()

def get_next_sales_invoice_number():
    sql = "SELECT last_value FROM sales_invoices_id_seq;"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql); last_id = cur.fetchone()[0]
                next_id = last_id + 1; year = datetime.date.today().year; return f"SQ-{year}-{next_id}"
    except Exception:
        year = datetime.date.today().year; return f"SQ-{year}-1"

if __name__ == '__main__':
    print("Verilənlər bazası cədvəlləri yoxlanılır və yaradılır...")
    create_tables()
    print("Proses tamamlandı.")