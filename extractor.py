import pdfplumber
import re

def extract_money(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(",", ""))
    return 0.0

def extract_invoice_data(file_path):
    extracted_data = {
        "vendor_name": "",
        "vendor_number": "",
        "po_number": "",
        "invoice_number": "",
        "invoice_date": "",
        "due_date": "",
        "subtotal": 0.0,
        "tax": 0.0,
        "freight": 0.0,
        "other_charges": 0.0,
        "amount": 0.0,
        "raw_text": ""
    }

    with pdfplumber.open(file_path) as pdf:
        text = ""

        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    extracted_data["raw_text"] = text

    patterns = {
        "vendor_name": r"Vendor Name:?\s*(.+)",
        "vendor_number": r"Vendor Number:?\s*(\S+)",
        "po_number": r"PO Number:?\s*(\S+)",
        "invoice_number": r"Invoice Number:?\s*(\S+)",
        "invoice_date": r"Invoice Date:?\s*([0-9\-\/]+)",
        "due_date": r"Due Date:?\s*([0-9\-\/]+)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted_data[field] = match.group(1).strip()

    extracted_data["subtotal"] = extract_money(r"Subtotal:?\s*\$?([0-9,]+\.\d{2})", text)
    extracted_data["tax"] = extract_money(r"Tax:?\s*\$?([0-9,]+\.\d{2})", text)
    extracted_data["freight"] = extract_money(r"Freight:?\s*\$?([0-9,]+\.\d{2})", text)
    extracted_data["other_charges"] = extract_money(r"Other Charges:?\s*\$?([0-9,]+\.\d{2})", text)
    extracted_data["amount"] = extract_money(r"Total Amount:?\s*\$?([0-9,]+\.\d{2})", text)

    return extracted_data