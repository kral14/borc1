import tkinter as tk
from tkinter import messagebox
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Verilənlər bazasına qoşulmaq üçün funksiya (main.py-dan kopyalanıb)
def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        messagebox.showerror("Database Error", f"Bağlantı xətası: {e}")
        return None

# Müştərini bazaya əlavə edən funksiya
def musteri_elave_et():
    ad = entry_ad.get()
    soyad = entry_soyad.get()
    sirket = entry_sirket.get()
    telefon = entry_telefon.get()

    if not ad or not telefon:
        messagebox.showwarning("Xəbərdarlıq", "Ad və Telefon xanaları boş buraxıla bilməz!")
        return

    conn = get_db_connection()
    if conn is None: return

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Musteriler (ad, soyad, sirket_adi, telefon) VALUES (%s, %s, %s, %s)",
                (ad, soyad, sirket, telefon)
            )
            conn.commit()
        messagebox.showinfo("Uğurlu", f"Müştəri '{ad} {soyad}' uğurla əlavə edildi!")
        # Xanaları təmizlə
        entry_ad.delete(0, tk.END)
        entry_soyad.delete(0, tk.END)
        entry_sirket.delete(0, tk.END)
        entry_telefon.delete(0, tk.END)
    except psycopg2.Error as e:
        messagebox.showerror("Database Error", f"Məlumat yazılarkən xəta: {e}")
    finally:
        if conn:
            conn.close()


# --- GUI (Qrafik İnterfeys) Hissəsi ---
app = tk.Tk()
app.title("Müştəri Əlavə Etmə")

# Pəncərə elementlərinin yaradılması
tk.Label(app, text="Ad:").grid(row=0, column=0, padx=10, pady=5)
entry_ad = tk.Entry(app)
entry_ad.grid(row=0, column=1, padx=10, pady=5)

tk.Label(app, text="Soyad:").grid(row=1, column=0, padx=10, pady=5)
entry_soyad = tk.Entry(app)
entry_soyad.grid(row=1, column=1, padx=10, pady=5)

tk.Label(app, text="Şirkət Adı:").grid(row=2, column=0, padx=10, pady=5)
entry_sirket = tk.Entry(app)
entry_sirket.grid(row=2, column=1, padx=10, pady=5)

tk.Label(app, text="Telefon:").grid(row=3, column=0, padx=10, pady=5)
entry_telefon = tk.Entry(app)
entry_telefon.grid(row=3, column=1, padx=10, pady=5)

add_button = tk.Button(app, text="Müştəri Əlavə Et", command=musteri_elave_et)
add_button.grid(row=4, column=0, columnspan=2, pady=20)

# Pəncərəni göstər
app.mainloop()