# ============================================================================
# DocFlow Pro - Production-Ready Enterprise Document Automation System
# ============================================================================
# Complete Implementation - All 9 Modules
# For Indian SMEs and Enterprises
# On-Premise Desktop Application
# ============================================================================

# FILE 1: requirements.txt
"""
tkinter (built-in)
tkinterdnd2==0.3.0
pytesseract==0.3.10
Pillow==10.1.0
PyMuPDF==1.23.8
pandas==2.1.4
openpyxl==3.1.2
matplotlib==3.8.2
scikit-learn==1.3.2
reportlab==4.0.7
pywhatkit==5.4
cryptography==41.0.7
pyinstaller==6.3.0
"""

# ============================================================================
# FOLDER STRUCTURE
# ============================================================================
"""
docflow_pro/
├── main.py                          # Application entry point
├── config.py                        # Configuration management
├── requirements.txt                 # Python dependencies
├── README.md                        # Installation & usage guide
├── build.spec                       # PyInstaller build configuration
│
├── core/
│   ├── __init__.py
│   ├── app.py                       # Main application class
│   ├── database.py                  # SQLite database manager
│   ├── license.py                   # License validation
│   └── auth.py                      # User authentication
│
├── modules/
│   ├── __init__.py
│   │
│   ├── ocr/
│   │   ├── __init__.py
│   │   ├── scanner.py               # Document scanning & OCR
│   │   ├── extractor.py             # Data extraction (GST, PAN, etc)
│   │   └── patterns.py              # Indian invoice patterns
│   │
│   ├── data_cleaning/
│   │   ├── __init__.py
│   │   ├── cleaner.py               # Data cleaning logic
│   │   ├── validators.py            # GST/PAN/Amount validators
│   │   └── normalizer.py            # Data normalization
│   │
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── builder.py               # Visual workflow builder
│   │   ├── engine.py                # Workflow execution engine
│   │   ├── nodes.py                 # Workflow node definitions
│   │   └── templates.py             # Pre-built workflows
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── categorizer.py           # Expense categorization
│   │   ├── classifier.py            # Vendor classification
│   │   ├── anomaly.py               # Anomaly detection
│   │   └── trends.py                # Trend analysis
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── connector.py             # AI API abstraction
│   │   ├── summarizer.py            # Document summarization
│   │   └── search.py                # Intelligent search
│   │
│   ├── billing/
│   │   ├── __init__.py
│   │   ├── invoice_generator.py    # Invoice generation
│   │   ├── gst_calculator.py       # GST calculations
│   │   ├── payment_handler.py      # Payment processing
│   │   └── reconciliation.py       # Bank reconciliation
│   │
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── dashboard.py             # Dashboard UI
│   │   ├── exporter.py              # Excel/PDF export
│   │   └── gst_reports.py           # GST-specific reports
│   │
│   └── audit/
│       ├── __init__.py
│       ├── logger.py                # Audit logging
│       └── viewer.py                # Audit log viewer
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py               # Main application window
│   ├── login.py                     # Login screen
│   ├── dashboard.py                 # Dashboard UI
│   ├── document_upload.py           # Document upload UI
│   ├── workflow_canvas.py           # Workflow builder UI
│   ├── settings.py                  # Settings UI
│   └── components/
│       ├── __init__.py
│       ├── forms.py                 # Reusable form components
│       ├── tables.py                # Data table components
│       └── dialogs.py               # Dialog boxes
│
├── utils/
│   ├── __init__.py
│   ├── file_handler.py              # File operations
│   ├── email_sender.py              # Email utilities
│   ├── whatsapp_sender.py           # WhatsApp integration
│   ├── encryption.py                # Data encryption
│   └── helpers.py                   # General utilities
│
├── data/
│   ├── database/
│   │   └── docflow.db               # SQLite database (created at runtime)
│   ├── workflows/
│   │   ├── gst_approval.json
│   │   ├── purchase_approval.json
│   │   ├── expense_claim.json
│   │   └── leave_request.json
│   ├── templates/
│   │   └── invoice_template.html
│   └── ml_models/
│       └── (pre-trained models if needed)
│
├── assets/
│   ├── icons/
│   ├── images/
│   └── fonts/
│
├── tesseract/
│   ├── tesseract.exe                # Bundled Tesseract
│   └── tessdata/
│       ├── eng.traineddata
│       └── hin.traineddata
│
├── licenses/
│   ├── license.json                 # License file
│   └── key_validator.py             # License key validation
│
└── logs/
    └── app.log                       # Application logs
"""