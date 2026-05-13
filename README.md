# Invoice Automation System

Automated Accounts Payable (AP) invoice processing and tracking system built with Python, Streamlit, SQLite, and future Sage 100 integration support.

---

# Overview

This project was created to modernize and optimize traditional invoice processing workflows commonly handled through paper tracking, spreadsheets, and manual accounting procedures.

The system is designed to:

- Track unpaid and paid invoices
- Store invoice records digitally
- Upload and organize invoice files
- Reduce duplicate payments and manual errors
- Improve invoice visibility and workflow efficiency
- Prepare invoice data for ERP integration workflows such as Sage 100

This project is being developed as a real-world financial systems automation portfolio project focused on accounting operations, analytics, and business process optimization.

---

# Current Features (MVP)

- Invoice tracking dashboard
- Vendor invoice management
- Invoice status tracking
  - Unpaid
  - Paid
  - Needs Review
- File upload support
- SQLite database storage
- Streamlit web application interface

---

# Planned Features

## OCR Invoice Processing
Automatic extraction of:
- Vendor names
- Invoice numbers
- Due dates
- Invoice totals
- Purchase order references

## AI Invoice Classification
- Duplicate invoice detection
- Fraud/error flagging
- Vendor matching validation
- Confidence scoring

## Analytics & Reporting
- AP aging dashboards
- Vendor spend analytics
- Payment trend analysis
- Power BI integration

## ERP Integration
Future support for:
- Sage 100 import/export workflows
- CSV export formatting
- Visual Integrator compatibility

## Workflow Automation
- Approval queues
- Invoice review workflow
- Automated reminders
- Payment scheduling support

---

# Tech Stack

## Backend
- Python
- SQLite
- Pandas

## Frontend
- Streamlit

## Future Technologies
- FastAPI
- PostgreSQL
- OCR services
- Power BI
- Cloud deployment

---

# Project Structure

```text
invoice-automation-system/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/invoice-automation-system.git
```

## Install Requirements

```bash
pip install -r requirements.txt
```

## Run Application

```bash
streamlit run app.py
```

---

# Goals of This Project

This project is intended to demonstrate practical skills in:

- Financial systems automation
- Business process optimization
- Software engineering
- Database management
- Data analytics
- Workflow design
- ERP-related integrations
- Real-world accounting operations

---

# Disclaimer

This project uses sample and demonstration data only.

No confidential company data, vendor information, accounting records, or proprietary workflows are included in this repository.

---

# License

© 2026 Felipe Restrepo. All rights reserved.

This project is shared for portfolio and demonstration purposes only.

Unauthorized copying, redistribution, modification, or commercial use is prohibited.