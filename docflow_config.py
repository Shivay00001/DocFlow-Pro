"""
config.py - Configuration Management
DocFlow Pro - Enterprise Document Automation
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "database"
WORKFLOW_DIR = DATA_DIR / "workflows"
TEMPLATE_DIR = DATA_DIR / "templates"
ML_MODELS_DIR = DATA_DIR / "ml_models"
ASSETS_DIR = BASE_DIR / "assets"
TESSERACT_DIR = BASE_DIR / "tesseract"
LOGS_DIR = BASE_DIR / "logs"
LICENSE_DIR = BASE_DIR / "licenses"

# Create directories
for dir_path in [DATA_DIR, DB_DIR, WORKFLOW_DIR, TEMPLATE_DIR, 
                  ML_MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_PATH = DB_DIR / "docflow.db"

# Tesseract OCR
TESSERACT_CMD = str(TESSERACT_DIR / "tesseract.exe") if os.name == 'nt' else 'tesseract'
TESSERACT_LANG = 'eng+hin'

# Application
APP_NAME = "DocFlow Pro"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "1400x900"

# Supported file formats
SUPPORTED_FORMATS = ['.pdf', '.jpg', '.jpeg', '.png', '.tif', '.tiff']

# GST & Tax
GST_RATES = [0, 5, 12, 18, 28]
STATE_CODES = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
    "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana",
    "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
    "16": "Tripura", "17": "Meghalaya", "18": "Assam",
    "19": "West Bengal", "20": "Jharkhand", "21": "Odisha",
    "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "25": "Daman & Diu", "26": "Dadra & Nagar Haveli", "27": "Maharashtra",
    "28": "Andhra Pradesh", "29": "Karnataka", "30": "Goa",
    "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu",
    "34": "Puducherry", "35": "Andaman & Nicobar", "36": "Telangana",
    "37": "Andhra Pradesh", "38": "Ladakh"
}

# Licensing
LICENSE_PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "documents_per_month": 50,
        "users": 1,
        "workflows": 2,
        "ai_enabled": False,
        "support": "community"
    },
    "basic": {
        "name": "Basic",
        "price": 5000,
        "documents_per_month": 500,
        "users": 3,
        "workflows": 10,
        "ai_enabled": False,
        "support": "email"
    },
    "pro": {
        "name": "Pro",
        "price": 10000,
        "documents_per_month": 2000,
        "users": 10,
        "workflows": -1,  # unlimited
        "ai_enabled": True,
        "support": "priority"
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 25000,
        "documents_per_month": -1,  # unlimited
        "users": -1,  # unlimited
        "workflows": -1,  # unlimited
        "ai_enabled": True,
        "support": "dedicated"
    }
}

# ML Models
ML_EXPENSE_CATEGORIES = [
    "Office Supplies", "Travel", "Utilities", "Salaries",
    "Marketing", "IT Services", "Professional Fees", "Rent",
    "Insurance", "Taxes", "Miscellaneous"
]

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Audit Log Retention
AUDIT_RETENTION_YEARS = 5

# UI Colors
COLORS = {
    "primary": "#2563eb",
    "secondary": "#64748b",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "background": "#f8fafc",
    "text": "#1e293b"
}

# Export formats
EXPORT_FORMATS = ["Excel (.xlsx)", "PDF (.pdf)", "CSV (.csv)"]