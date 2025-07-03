# database/schema.py

from .config import get_db_connection
from app_logger import logger

def _add_column_safely(table, column_name, column_type):
    """(Daxili istifadə üçün) Hər bir sütunu təhlükəsiz şəkildə əlavə edir."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column_name} {column_type};")
        cur.close()
    except Exception as e:
        logger.log(f"Sütun əlavə edilərkən xəta ({table}.{column_name}): {e}")
    finally:
        if conn: conn.close()

def create_tables():
    """Proqram üçün lazım olan bütün cədvəlləri yaradır və mövcud cədvəlləri yeniləyir."""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None: 
            logger.log("Cədvəl yaratma prosesi dayandırıldı: Baza bağlantısı yoxdur.")
            return

        cur = conn.cursor()
        
        # Bütün cədvəllər üçün CREATE IF NOT EXISTS əmrləri
        commands = (
            """
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY, 
                name VARCHAR(255) NOT NULL, 
                phone VARCHAR(50), 
                address TEXT, 
                is_active BOOLEAN DEFAULT TRUE, 
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS suppliers (
                id SERIAL PRIMARY KEY, 
                name VARCHAR(255) NOT NULL, 
                contact_person VARCHAR(255), 
                phone VARCHAR(50), 
                address TEXT, 
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY, 
                name VARCHAR(255) NOT NULL, 
                parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY, 
                name VARCHAR(255) NOT NULL, 
                product_code VARCHAR(100), 
                article VARCHAR(100), 
                purchase_price NUMERIC(10, 2) DEFAULT 0, 
                sale_price NUMERIC(10, 2) DEFAULT 0, 
                stock INTEGER DEFAULT 0, 
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
                supplier_id INTEGER REFERENCES suppliers (id) ON DELETE SET NULL, 
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL, 
                custom_attributes JSONB
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS custom_product_fields (
                id SERIAL PRIMARY KEY, 
                field_key VARCHAR(100) NOT NULL UNIQUE, 
                field_name VARCHAR(255) NOT NULL, 
                field_type VARCHAR(50) DEFAULT 'text', 
                is_active BOOLEAN DEFAULT TRUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS sales_invoices (
                id SERIAL PRIMARY KEY, 
                customer_id INTEGER NOT NULL REFERENCES customers (id) ON DELETE CASCADE, 
                invoice_number VARCHAR(100), 
                invoice_date DATE NOT NULL DEFAULT CURRENT_DATE, 
                total_amount NUMERIC(10, 2) NOT NULL, 
                is_paid BOOLEAN DEFAULT FALSE, 
                is_active BOOLEAN DEFAULT TRUE, 
                due_date DATE, 
                notes TEXT, 
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
                paid_amount NUMERIC(10, 2) DEFAULT 0
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS sales_invoice_items (
                id SERIAL PRIMARY KEY, 
                invoice_id INTEGER NOT NULL REFERENCES sales_invoices (id) ON DELETE CASCADE, 
                product_id INTEGER NOT NULL REFERENCES products (id) ON DELETE RESTRICT, 
                quantity INTEGER NOT NULL, 
                unit_price NUMERIC(10, 2) NOT NULL, 
                discount_percent NUMERIC(5, 2) DEFAULT 0, 
                total_price NUMERIC(10, 2) NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS purchase_invoices (
                id SERIAL PRIMARY KEY, 
                supplier_id INTEGER NOT NULL REFERENCES suppliers (id) ON DELETE RESTRICT, 
                invoice_number VARCHAR(100), 
                invoice_date DATE NOT NULL DEFAULT CURRENT_DATE, 
                total_amount NUMERIC(10, 2) NOT NULL, 
                is_paid BOOLEAN DEFAULT FALSE, 
                is_active BOOLEAN DEFAULT TRUE, 
                due_date DATE, 
                notes TEXT, 
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
                paid_amount NUMERIC(10, 2) DEFAULT 0
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS purchase_invoice_items (
                id SERIAL PRIMARY KEY, 
                purchase_invoice_id INTEGER NOT NULL REFERENCES purchase_invoices (id) ON DELETE CASCADE, 
                product_id INTEGER NOT NULL REFERENCES products (id) ON DELETE RESTRICT, 
                quantity INTEGER NOT NULL, 
                unit_price NUMERIC(10, 2) NOT NULL, 
                discount_percent NUMERIC(5, 2) DEFAULT 0, 
                line_total NUMERIC(10, 2) NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS customer_payments (
                id SERIAL PRIMARY KEY, 
                customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, 
                sales_invoice_id INTEGER REFERENCES sales_invoices(id) ON DELETE SET NULL, 
                payment_date DATE NOT NULL, 
                amount NUMERIC(10, 2) NOT NULL, 
                notes TEXT, 
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
                is_active BOOLEAN DEFAULT TRUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS cash_expenses (
                id SERIAL PRIMARY KEY, 
                expense_date DATE NOT NULL, 
                amount NUMERIC(10, 2) NOT NULL, 
                description TEXT NOT NULL, 
                supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL, 
                purchase_invoice_id INTEGER REFERENCES purchase_invoices(id) ON DELETE SET NULL, 
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
                is_active BOOLEAN DEFAULT TRUE
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

    # --- Mövcud cədvəllərə yeni sütunların əlavə edilməsi ---
    logger.log("Verilənlər bazası sütunları yenilənir...")

    # Products cədvəli üçün bütün yeni və köhnə sütunların yoxlanması
    _add_column_safely("products", "barcode_unit", "VARCHAR(100)") # Köhnə 'barcode' əvəzinə
    _add_column_safely("products", "is_food_product", "BOOLEAN DEFAULT TRUE")
    _add_column_safely("products", "pieces_in_box", "INTEGER DEFAULT 0")
    _add_column_safely("products", "pieces_in_block", "INTEGER DEFAULT 0")
    _add_column_safely("products", "barcode_box", "VARCHAR(100)")
    _add_column_safely("products", "barcode_block", "VARCHAR(100)")
    _add_column_safely("products", "unit_of_measure", "VARCHAR(50)")
    _add_column_safely("products", "production_date", "DATE")
    _add_column_safely("products", "expiry_date", "DATE")
    _add_column_safely("products", "warehouse_location", "VARCHAR(100)")
    _add_column_safely("products", "shelf_location", "VARCHAR(100)")
    _add_column_safely("products", "row_location", "VARCHAR(100)")

    # Digər cədvəllər üçün yoxlamalar
    _add_column_safely("custom_product_fields", "is_active", "BOOLEAN DEFAULT TRUE")
    _add_column_safely("sales_invoices", "paid_amount", "NUMERIC(10, 2) DEFAULT 0")
    _add_column_safely("purchase_invoices", "paid_amount", "NUMERIC(10, 2) DEFAULT 0")
    _add_column_safely("customer_payments", "is_active", "BOOLEAN DEFAULT TRUE")
    _add_column_safely("cash_expenses", "is_active", "BOOLEAN DEFAULT TRUE")
    
    logger.log("Sütunların yenilənməsi tamamlandı.")


def create_indexes():
    """Verilənlər bazasında axtarış sürətini artırmaq üçün indekslər yaradır."""
    conn = None
    commands = [
        "CREATE INDEX IF NOT EXISTS idx_prod_name ON products (name);",
        "CREATE INDEX IF NOT EXISTS idx_prod_barcode_unit ON products (barcode_unit);", # İndeks adı da yeniləndi
        "CREATE INDEX IF NOT EXISTS idx_sales_inv_customer_id ON sales_invoices (customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_sales_inv_date ON sales_invoices (invoice_date);",
        "CREATE INDEX IF NOT EXISTS idx_purch_inv_supplier_id ON purchase_invoices (supplier_id);",
        "CREATE INDEX IF NOT EXISTS idx_purch_inv_date ON purchase_invoices (invoice_date);",
        "CREATE INDEX IF NOT EXISTS idx_cust_pay_customer_id ON customer_payments (customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_cash_exp_supplier_id ON cash_expenses (supplier_id);"
    ]
    try:
        conn = get_db_connection()
        if not conn: return
        with conn.cursor() as cur:
            for command in commands:
                cur.execute(command)
        conn.commit()
        logger.log("Verilənlər bazası indeksləri uğurla yoxlanıldı/yaradıldı.")
    except Exception as e:
        logger.log(f"XƏTA: İndekslər yaradılarkən xəta: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()