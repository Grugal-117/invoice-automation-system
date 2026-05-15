import streamlit as st
import pandas as pd
import os
from database import create_tables, get_connection
from extractor import extract_invoice_data


create_tables()

UPLOAD_FOLDER = "uploaded_invoices"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

    uploaded_file = st.file_uploader(
        "Upload Invoice File",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    extracted_data = {
        "vendor_name": "",
        "invoice_number": "",
        "invoice_date": "",
        "due_date": "",
        "amount": 0.0
    }

    if uploaded_file is not None:

        temp_path = os.path.join(
            UPLOAD_FOLDER,
            uploaded_file.name
        )

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if uploaded_file.name.endswith(".pdf"):
            extracted_data = extract_invoice_data(temp_path)

            st.success("Invoice data extracted successfully.")

    vendor_name = st.text_input(
        "Vendor Name",
        value=extracted_data["vendor_name"]
    )

    invoice_number = st.text_input(
        "Invoice Number",
        value=extracted_data["invoice_number"]
    )

    invoice_date = st.text_input(
        "Invoice Date",
        value=extracted_data["invoice_date"]
    )

    due_date = st.text_input(
        "Due Date",
        value=extracted_data["due_date"]
    )

    amount = st.number_input(
        "Invoice Amount",
        min_value=0.0,
        value=float(extracted_data["amount"]),
        format="%.2f"
    )

    status = st.selectbox(
        "Status",
        ["Unpaid", "Paid", "Needs Review"]
    )

    notes = st.text_area("Notes")

    if st.button("Save Invoice"):

        file_name = None

        if uploaded_file is not None:
            file_name = uploaded_file.name

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM invoices
            WHERE vendor_name = ?
            AND invoice_number = ?
        """, (
            vendor_name,
            invoice_number
        ))

        duplicate = cursor.fetchone()

        if duplicate:
            st.error("Possible duplicate invoice detected. This vendor and invoice number already exist.")
            conn.close()
            st.stop()

        cursor.execute("""
            INSERT INTO invoices
            (
                vendor_name,
                invoice_number,
                invoice_date,
                due_date,
                amount,
                status,
                file_name,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vendor_name,
            invoice_number,
            str(invoice_date),
            str(due_date),
            amount,
            status,
            file_name,
            notes
        ))

        conn.commit()
        conn.close()

        st.success("Invoice saved successfully.")

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
