import sqlite3

DB_NAME = "invoices.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def add_column_if_missing(cursor, existing_columns, column_name, column_type):
    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE invoices ADD COLUMN {column_name} {column_type}")

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

    cursor.execute("PRAGMA table_info(invoices)")
    columns = [column[1] for column in cursor.fetchall()]

    add_column_if_missing(cursor, columns, "file_name", "TEXT")
    add_column_if_missing(cursor, columns, "vendor_number", "TEXT")
    add_column_if_missing(cursor, columns, "po_number", "TEXT")
    add_column_if_missing(cursor, columns, "subtotal", "REAL DEFAULT 0")
    add_column_if_missing(cursor, columns, "tax", "REAL DEFAULT 0")
    add_column_if_missing(cursor, columns, "freight", "REAL DEFAULT 0")
    add_column_if_missing(cursor, columns, "other_charges", "REAL DEFAULT 0")
    add_column_if_missing(cursor, columns, "discount_eligible", "TEXT DEFAULT 'No'")
    add_column_if_missing(cursor, columns, "discount_percent", "REAL DEFAULT 0")
    add_column_if_missing(cursor, columns, "discount_due_date", "TEXT")

    conn.commit()
    conn.close()