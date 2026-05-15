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
            file_name TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(invoices)")
    columns = [column[1] for column in cursor.fetchall()]

    if "file_name" not in columns:
        cursor.execute("ALTER TABLE invoices ADD COLUMN file_name TEXT")

    conn.commit()
    conn.close()