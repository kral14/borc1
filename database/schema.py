# database/schema.py (Kassa Məxaric üçün yenilənmiş)

from .config import get_db_connection
from app_logger import logger

def _add_column_safely(table, column_name, column_type):
    # ... (Bu funksiya dəyişmir) ...
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
    conn = None
    try:
        conn = get_db_connection()
        if conn is None: 
            logger.log("Cədvəl yaratma prosesi dayandırıldı: Baza bağlantısı yoxdur.")
            return

        cur = conn.cursor()
        
        commands = (
            # ... mövcud CREATE TABLE əmrləri olduğu kimi qalır ...
            "CREATE TABLE IF NOT EXISTS customers (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, phone VARCHAR(50), address TEXT, is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS suppliers (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, contact_person VARCHAR(255), phone VARCHAR(50), address TEXT, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS categories (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE);",
            "CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, barcode VARCHAR(100), product_code VARCHAR(100), article VARCHAR(100), purchase_price NUMERIC(10, 2) DEFAULT 0, sale_price NUMERIC(10, 2) DEFAULT 0, stock INTEGER DEFAULT 0, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, supplier_id INTEGER REFERENCES suppliers (id) ON DELETE SET NULL, category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL, custom_attributes JSONB);",
            "CREATE TABLE IF NOT EXISTS custom_product_fields (id SERIAL PRIMARY KEY, field_key VARCHAR(100) NOT NULL UNIQUE, field_name VARCHAR(255) NOT NULL, field_type VARCHAR(50) DEFAULT 'text');",
            "CREATE TABLE IF NOT EXISTS sales_invoices (id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL, invoice_number VARCHAR(100), invoice_date DATE NOT NULL DEFAULT CURRENT_DATE, total_amount NUMERIC(10, 2) NOT NULL, is_paid BOOLEAN DEFAULT FALSE, is_active BOOLEAN DEFAULT TRUE, due_date DATE, notes TEXT, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE);",
            "CREATE TABLE IF NOT EXISTS sales_invoice_items (id SERIAL PRIMARY KEY, invoice_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL, unit_price NUMERIC(10, 2) NOT NULL, discount_percent NUMERIC(5, 2) DEFAULT 0, total_price NUMERIC(10, 2) NOT NULL, FOREIGN KEY (invoice_id) REFERENCES sales_invoices (id) ON DELETE CASCADE, FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT);",
            "CREATE TABLE IF NOT EXISTS purchase_invoices (id SERIAL PRIMARY KEY, supplier_id INTEGER NOT NULL, invoice_number VARCHAR(100), invoice_date DATE NOT NULL DEFAULT CURRENT_DATE, total_amount NUMERIC(10, 2) NOT NULL, is_paid BOOLEAN DEFAULT FALSE, is_active BOOLEAN DEFAULT TRUE, due_date DATE, notes TEXT, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE RESTRICT);",
            "CREATE TABLE IF NOT EXISTS purchase_invoice_items (id SERIAL PRIMARY KEY, purchase_invoice_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL, unit_price NUMERIC(10, 2) NOT NULL, discount_percent NUMERIC(5, 2) DEFAULT 0, line_total NUMERIC(10, 2) NOT NULL, FOREIGN KEY (purchase_invoice_id) REFERENCES purchase_invoices (id) ON DELETE CASCADE, FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT);",
            "CREATE TABLE IF NOT EXISTS customer_payments (id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE, sales_invoice_id INTEGER REFERENCES sales_invoices(id) ON DELETE SET NULL, payment_date DATE NOT NULL, amount NUMERIC(10, 2) NOT NULL, notes TEXT, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP);",
            
            # --- YENİ MƏXARİC CƏDVƏLİ ---
            """
            CREATE TABLE IF NOT EXISTS cash_expenses (
                id SERIAL PRIMARY KEY,
                expense_date DATE NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                description TEXT NOT NULL,
                supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
                purchase_invoice_id INTEGER REFERENCES purchase_invoices(id) ON DELETE SET NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        for command in commands: cur.execute(command)
        cur.close()
        conn.commit()
    except Exception as e:
        logger.log(f"KRİTİK XƏTA: Əsas cədvəllər yaradılarkən xəta: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

    logger.log("Verilənlər bazası sütunları yenilənir...")
    _add_column_safely("products", "custom_attributes", "JSONB")
    _add_column_safely("custom_product_fields", "is_active", "BOOLEAN DEFAULT TRUE")
    _add_column_safely("sales_invoices", "paid_amount", "NUMERIC(10, 2) DEFAULT 0")
    # --- YENİ MƏXARİC ÜÇÜN SÜTUN ---
    _add_column_safely("purchase_invoices", "paid_amount", "NUMERIC(10, 2) DEFAULT 0")

    logger.log("Sütunların yenilənməsi tamamlandı.")