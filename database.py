<<<<<<< HEAD

=======
import sqlite3

DB_NAME = "invoices.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT NOT NULL,
            invoice_number TEXT NOT NULL,
            invoice_date TEXT,
            due_date TEXT,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'Unpaid',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
>>>>>>> ee4ac80 (Built initial invoice tracking system)
