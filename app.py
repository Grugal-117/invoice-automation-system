import streamlit as st
import pandas as pd
from database import create_tables, get_connection

create_tables()

st.set_page_config(
    page_title="Invoice Automation System",
    layout="wide"
)

st.title("Invoice Automation System")

menu = st.sidebar.selectbox(
    "Menu",
    ["Add Invoice", "View Invoices"]
)

if menu == "Add Invoice":

    st.header("Add New Invoice")

    vendor_name = st.text_input("Vendor Name")
    invoice_number = st.text_input("Invoice Number")
    invoice_date = st.date_input("Invoice Date")
    due_date = st.date_input("Due Date")

    amount = st.number_input(
        "Invoice Amount",
        min_value=0.0,
        format="%.2f"
    )

    status = st.selectbox(
        "Status",
        ["Unpaid", "Paid", "Needs Review"]
    )

    notes = st.text_area("Notes")

    if st.button("Save Invoice"):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO invoices
            (
                vendor_name,
                invoice_number,
                invoice_date,
                due_date,
                amount,
                status,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            vendor_name,
            invoice_number,
            str(invoice_date),
            str(due_date),
            amount,
            status,
            notes
        ))

        conn.commit()
        conn.close()

        st.success("Invoice saved successfully.")

elif menu == "View Invoices":

    st.header("Invoice Records")

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM invoices ORDER BY created_at DESC",
        conn
    )

    conn.close()

    if df.empty:
        st.info("No invoices found.")
    else:
        st.dataframe(df, use_container_width=True)
