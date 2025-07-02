# database/config.py

import psycopg2
from app_logger import logger

DATABASE_URL = "postgresql://takib_owner:npg_98btwuhVScvy@ep-rough-mountain-a9izj47k-pooler.gwc.azure.neon.tech/takib?sslmode=require"

def get_db_connection():
    """Verilənlər bazasına qoşulmaq üçün mərkəzi funksiya"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        logger.log(f"KRİTİK XƏTA: Verilənlər bazasına qoşulmaq mümkün olmadı: {e}")
        return None