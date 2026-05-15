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
    ["Add Invoice", "View Invoices", "Update Invoice Status", "Dashboard"]
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

elif menu == "Update Invoice Status":

    st.header("Update Invoice Status")

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM invoices ORDER BY created_at DESC",
        conn
    )

    if df.empty:
        st.info("No invoices available to update.")
        conn.close()
    else:
        df["invoice_label"] = (
            df["id"].astype(str)
            + " | "
            + df["vendor_name"]
            + " | "
            + df["invoice_number"]
            + " | $"
            + df["amount"].astype(str)
            + " | "
            + df["status"]
        )

        selected_invoice = st.selectbox(
            "Select Invoice",
            df["invoice_label"]
        )

        selected_id = int(selected_invoice.split(" | ")[0])

        selected_row = df[df["id"] == selected_id].iloc[0]

        st.write("Current Status:", selected_row["status"])

        new_status = st.selectbox(
            "New Status",
            ["Unpaid", "Paid", "Needs Review", "Approved", "Rejected"]
        )

        update_note = st.text_area("Update Notes")

        if st.button("Update Invoice"):

            cursor = conn.cursor()

            cursor.execute("""
                UPDATE invoices
                SET status = ?,
                    notes = ?
                WHERE id = ?
            """, (
                new_status,
                update_note,
                selected_id
            ))

            conn.commit()
            conn.close()

            st.success("Invoice updated successfully.")

elif menu == "Dashboard":

    st.header("Invoice Dashboard")

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM invoices",
        conn
    )

    conn.close()

    if df.empty:
        st.info("No invoice data available yet.")
    else:
        total_invoices = len(df)
        total_amount = df["amount"].sum()
        unpaid_amount = df[df["status"] == "Unpaid"]["amount"].sum()
        paid_amount = df[df["status"] == "Paid"]["amount"].sum()
        needs_review_count = len(df[df["status"] == "Needs Review"])

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Invoices", total_invoices)
        col2.metric("Total Amount", f"${total_amount:,.2f}")
        col3.metric("Unpaid Amount", f"${unpaid_amount:,.2f}")
        col4.metric("Needs Review", needs_review_count)

        st.subheader("Invoices by Status")
        status_counts = df["status"].value_counts()
        st.bar_chart(status_counts)

        st.subheader("Amount by Vendor")
        vendor_totals = df.groupby("vendor_name")["amount"].sum()
        st.bar_chart(vendor_totals)
