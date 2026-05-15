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
        "vendor_number": "",
        "po_number": "",
        "invoice_number": "",
        "invoice_date": "",
        "due_date": "",
        "amount": 0.0,
        "raw_text": ""
    }

    if uploaded_file is not None:
        temp_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if uploaded_file.name.endswith(".pdf"):
            extracted_data = extract_invoice_data(temp_path)

            extracted_data.setdefault("vendor_name", "")
            extracted_data.setdefault("vendor_number", "")
            extracted_data.setdefault("po_number", "")
            extracted_data.setdefault("invoice_number", "")
            extracted_data.setdefault("invoice_date", "")
            extracted_data.setdefault("due_date", "")
            extracted_data.setdefault("amount", 0.0)

            st.success("Invoice data extracted successfully.")

    vendor_name = st.text_input("Vendor Name", value=extracted_data["vendor_name"])
    vendor_number = st.text_input("Vendor Number", value=extracted_data["vendor_number"])
    po_number = st.text_input("PO Number", value=extracted_data["po_number"])
    invoice_number = st.text_input("Invoice Number", value=extracted_data["invoice_number"])
    invoice_date = st.text_input("Invoice Date", value=extracted_data["invoice_date"])
    due_date = st.text_input("Due Date", value=extracted_data["due_date"])

    subtotal = st.number_input("Subtotal", min_value=0.0, value=float(extracted_data.get("subtotal", 0.0)), format="%.2f")
    tax = st.number_input("Tax", min_value=0.0, value=float(extracted_data.get("tax", 0.0)), format="%.2f")
    freight = st.number_input("Freight", min_value=0.0, value=float(extracted_data.get("freight", 0.0)), format="%.2f")
    other_charges = st.number_input("Other Charges", min_value=0.0, value=float(extracted_data.get("other_charges", 0.0)), format="%.2f")

    amount = subtotal + tax + freight + other_charges
    st.write(f"Calculated Total: ${amount:,.2f}")

    status = st.selectbox("Status", ["Unpaid", "Paid", "Needs Review"])

    discount_eligible = st.selectbox("Discount Eligible?", ["No", "Yes"])

    discount_percent = 0.0
    discount_due_date = ""

    if discount_eligible == "Yes":
        discount_percent = st.number_input(
            "Discount Percent",
            min_value=0.0,
            max_value=100.0,
            format="%.2f"
        )

        discount_due_date = st.text_input("Discount Due Date")

    notes = st.text_area("Notes")

    if st.button("Save Invoice"):

        if not invoice_number.strip():
            st.warning("Invoice number is blank. Please enter an invoice number before saving.")
            st.stop()

        file_name = None

        if uploaded_file is not None:
            file_name = uploaded_file.name

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM invoices
            WHERE invoice_number = ?
        """, (
            invoice_number.strip(),
        ))

        duplicate = cursor.fetchone()

        if duplicate:
            st.error("Possible duplicate invoice detected. This invoice number already exists.")
            conn.close()
            st.stop()

        cursor.execute("""
            INSERT INTO invoices
            (
                vendor_name,
                vendor_number,
                po_number,
                invoice_number,
                invoice_date,
                due_date,
                subtotal,
                tax,
                freight,
                other_charges,
                amount,
                status,
                file_name,
                discount_eligible,
                discount_percent,
                discount_due_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vendor_name,
            vendor_number,
            po_number,
            invoice_number.strip(),
            invoice_date,
            due_date,
            subtotal,
            tax,
            freight,
            other_charges,
            amount,
            status,
            file_name,
            discount_eligible,
            discount_percent,
            discount_due_date,
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

        selected_invoice = st.selectbox("Select Invoice", df["invoice_label"])

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

    df = pd.read_sql_query("SELECT * FROM invoices", conn)

    conn.close()

    if df.empty:
        st.info("No invoice data available yet.")
    else:
        total_invoices = len(df)
        total_amount = df["amount"].sum()
        unpaid_amount = df[df["status"] == "Unpaid"]["amount"].sum()
        paid_amount = df[df["status"] == "Paid"]["amount"].sum()
        needs_review_count = len(df[df["status"] == "Needs Review"])

        discount_available = df[
            (df["discount_eligible"] == "Yes")
            & (df["status"] != "Paid")
        ]

        estimated_discount_savings = (
            discount_available["amount"]
            * (discount_available["discount_percent"] / 100)
        ).sum()

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Total Invoices", total_invoices)
        col2.metric("Total Amount", f"${total_amount:,.2f}")
        col3.metric("Unpaid Amount", f"${unpaid_amount:,.2f}")
        col4.metric("Needs Review", needs_review_count)
        col5.metric("Potential Discount Savings", f"${estimated_discount_savings:,.2f}")

        st.subheader("Invoices by Status")
        status_counts = df["status"].value_counts()
        st.bar_chart(status_counts)

        st.subheader("Amount by Vendor")
        vendor_totals = df.groupby("vendor_name")["amount"].sum()
        st.bar_chart(vendor_totals)

        st.subheader("Invoices Eligible for Discount")
        st.dataframe(discount_available, use_container_width=True)