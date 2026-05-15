import pdfplumber
import re

def extract_invoice_data(file_path):
    extracted_data = {
        "vendor_name": "",
        "invoice_number": "",
        "invoice_date": "",
        "due_date": "",
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

    invoice_number_match = re.search(r"Invoice Number:\s*(\S+)", text)
    invoice_date_match = re.search(r"Invoice Date:\s*([0-9\-\/]+)", text)
    due_date_match = re.search(r"Due Date:\s*([0-9\-\/]+)", text)
    vendor_match = re.search(r"Vendor:\s*(.+)", text)
    total_match = re.search(r"Total Due\s*\$?([0-9,]+\.\d{2})", text)

    if invoice_number_match:
        extracted_data["invoice_number"] = invoice_number_match.group(1)

    if invoice_date_match:
        extracted_data["invoice_date"] = invoice_date_match.group(1)

    if due_date_match:
        extracted_data["due_date"] = due_date_match.group(1)

    if vendor_match:
        extracted_data["vendor_name"] = vendor_match.group(1).strip()

    if total_match:
        extracted_data["amount"] = float(total_match.group(1).replace(",", ""))

    return extracted_data