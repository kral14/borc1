# database/__init__.py

from .config import get_db_connection
from .schema import create_tables

from .product_queries import (
    add_product,
    update_product,
    get_all_products,
    get_product_by_id,
    delete_product,
    add_category,
    get_all_categories,
    update_category_name,
    delete_category,
    get_custom_field_definitions,
    add_custom_field_definition,
    delete_custom_field_definition
)

from .contact_queries import (
    add_customer,
    update_customer,
    delete_customer,
    get_customer_by_id,
    get_all_customers_with_debt,
    add_supplier,
    update_supplier,
    delete_supplier,
    get_supplier_by_id,
    get_all_suppliers
)

from .invoice_queries import (
    add_purchase_invoice,
    update_purchase_invoice,
    delete_purchase_invoice,
    get_all_purchase_invoices,
    get_purchase_invoice_details,
    toggle_purchase_invoice_status,
    get_next_purchase_invoice_number,
    add_sales_invoice,
    update_sales_invoice,
    delete_sales_invoice,
    get_all_sales_invoices,
    get_sales_invoice_details,
    toggle_sales_invoice_status,
    get_next_sales_invoice_number
)
# database/__init__.py faylına əlavə edin

# ... digər importların sonuna ...
from .payment_queries import (
    get_unpaid_invoices_for_customer,
    add_customer_payment,
    get_all_payments,
    # --- YENİ FUNKSİYALAR ---
    get_unpaid_purchase_invoices_for_supplier,
    add_supplier_payment,
    get_all_cash_expenses
)
