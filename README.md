# DocFlow Pro - Enterprise Document Automation System

**Production-Ready On-Premise Desktop Application for Indian SMEs and Enterprises**

## 🎯 Overview

DocFlow Pro is a comprehensive document automation, workflow management, and data intelligence system designed specifically for Indian businesses. It runs completely offline on local PCs/servers with no mandatory cloud dependency.

### Key Features

- 📄 **OCR & Data Extraction**: Extract data from invoices with Hindi + English support
- ✅ **Workflow Automation**: Visual workflow builder with approval chains
- 🧹 **Data Cleaning**: Automatic validation and normalization
- 📊 **Reports & Analytics**: GST-ready reports with export to Excel/PDF
- 🤖 **Built-in ML**: Generic expense categorization and anomaly detection
- 🔒 **Audit Logs**: 5-year retention with complete trail
- 💰 **Billing & Payments**: Invoice generation with Razorpay integration
- 🔑 **Flexible Licensing**: Free, Basic, Pro, and Enterprise plans

## 📋 System Requirements

- **OS**: Windows 10/11, Linux, macOS
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 2GB free space
- **Python**: 3.8 or higher (for development)

## 🚀 Quick Start

### For End Users (Standalone Executable)

1. Download the latest `DocFlowPro.exe` from releases
2. Double-click to run
3. Login with default credentials:
   - Username: `admin`
   - Password: `admin`
4. Start uploading documents!

### For Developers (Source Installation)

#### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/yourcompany/docflow-pro.git
cd docflow-pro

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to: `C:\Program Files\Tesseract-OCR`
- Add to PATH or update `config.py`

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-hin  # Hindi language
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # All languages
```

#### 3. Run Application

```bash
python main.py
```

## 📦 Building Standalone Executable

### Using PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller build.spec

# Output will be in dist/ folder
```

### Build Specification (build.spec)

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('tesseract/tesseract.exe', 'tesseract'),
        ('tesseract/tessdata/*', 'tesseract/tessdata'),
    ],
    datas=[
        ('data/workflows/*.json', 'data/workflows'),
        ('data/templates/*', 'data/templates'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'pytesseract',
        'pandas',
        'sklearn',
        'reportlab',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DocFlowPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
```

## 📁 Project Structure

```
docflow_pro/
├── main.py                 # Application entry point
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── README.md             # This file
├── build.spec            # PyInstaller config
│
├── core/                 # Core modules
│   ├── database.py       # SQLite database
│   ├── license.py        # License management
│   └── auth.py          # Authentication
│
├── modules/              # Feature modules
│   ├── ocr/             # OCR & extraction
│   ├── data_cleaning/   # Data validation
│   ├── workflow/        # Workflow engine
│   ├── ml/             # Machine learning
│   ├── ai/             # AI integration
│   ├── billing/        # Invoice generation
│   ├── reports/        # Reporting
│   └── audit/          # Audit logging
│
├── ui/                  # User interface
│   ├── main_window.py   # Main UI
│   ├── login.py        # Login screen
│   └── components/     # Reusable components
│
├── data/               # Application data
│   ├── database/       # SQLite DB
│   ├── workflows/      # Workflow templates
│   └── templates/      # Document templates
│
└── tesseract/         # Bundled OCR
    └── tessdata/      # Language data
```

## 🔧 Configuration

### Database

SQLite database is automatically created at: `data/database/docflow.db`

### Tesseract OCR

Update `config.py` if Tesseract is installed at non-standard location:

```python
TESSERACT_CMD = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

### License Configuration

Edit `licenses/license.json` to activate features:

```json
{
  "plan": "pro",
  "company_name": "Your Company",
  "license_key": "XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX",
  "expiry_date": "2025-12-31"
}
```

## 💳 Licensing Plans

| Feature | Free | Basic | Pro | Enterprise |
|---------|------|-------|-----|------------|
| **Price** | ₹0 | ₹5,000/mo | ₹10,000/mo | ₹25,000+/mo |
| **Documents/month** | 50 | 500 | 2,000 | Unlimited |
| **Users** | 1 | 3 | 10 | Unlimited |
| **Workflows** | 2 | 10 | Unlimited | Unlimited |
| **AI Features** | ❌ | ❌ | ✅ | ✅ |
| **Support** | Community | Email | Priority | Dedicated |

### Generating License Keys

```python
from core.license import LicenseManager

license_mgr = LicenseManager()
license_mgr.create_license(
    plan='pro',
    company_name='Acme Corp',
    contact_email='admin@acme.com',
    duration_days=365
)
```

## 📚 Module Documentation

### Module 1: OCR & Data Extraction

```python
from modules.ocr.scanner import DocumentScanner, InvoiceExtractor

scanner = DocumentScanner()
extractor = InvoiceExtractor()

# Scan document
result = scanner.scan_document(Path('invoice.pdf'))

# Extract data
invoice_data = extractor.extract_invoice_data(result['text'])
```

**Extracted Fields:**
- GST Number (Vendor & Customer)
- PAN Number
- Invoice Number & Date
- Amounts (Taxable, GST, Total)
- Vendor/Customer Names

### Module 2: Data Cleaning

```python
from modules.data_cleaning.cleaner import DataCleaner, InvoiceValidator

cleaner = DataCleaner()
validator = InvoiceValidator()

# Normalize date
clean_date = cleaner.normalize_dates('15-03-2024')

# Validate GST
is_valid = cleaner.validate_gst('29ABCDE1234F1Z5')

# Validate invoice
validation = validator.validate_invoice(invoice_data)
```

### Module 3: Workflows

```python
from modules.workflow.engine import WorkflowEngine, WorkflowNode, NodeType

engine = WorkflowEngine(db_manager)

# Create workflow
nodes = [
    WorkflowNode('start', NodeType.START, {}),
    WorkflowNode('approval1', NodeType.APPROVAL, {'approver_id': 1}),
    WorkflowNode('end', NodeType.END, {})
]

workflow_id = engine.create_workflow(
    name='Invoice Approval',
    description='GST invoice approval workflow',
    workflow_type='invoice_approval',
    nodes=nodes,
    created_by=1
)

# Start workflow
instance_id = engine.start_workflow(workflow_id, document_id=1, initiated_by=1)

# Approve
engine.approve(instance_id, approver_id=1, comments='Approved')
```

### Module 4: Billing

```python
from modules.billing.invoice_generator import InvoiceGenerator, GSTCalculator

generator = InvoiceGenerator()
gst_calc = GSTCalculator()

# Calculate GST
gst_breakdown = gst_calc.calculate_gst(
    taxable_amount=10000,
    gst_rate=18,
    is_interstate=False
)

# Generate invoice
output_path = generator.generate_invoice(invoice_data, Path('invoice.pdf'))
```

### Module 5: ML Features

```python
from modules.ml.categorizer import ExpenseCategorizer
from modules.ml.anomaly import AnomalyDetector

# Categorize expenses
categorizer = ExpenseCategorizer()
category = categorizer.predict('Office supplies purchase')

# Detect anomalies
detector = AnomalyDetector()
is_anomaly = detector.detect(amount=50000, category='Office Supplies')
```

## 🔐 Security Features

- **Password Hashing**: SHA-256 with salt
- **License Encryption**: Fernet symmetric encryption
- **Audit Logging**: All actions logged with timestamps
- **Data Validation**: GST, PAN, amount validation
- **Access Control**: Role-based permissions

## 🐛 Troubleshooting

### Tesseract Not Found

**Error:** `TesseractNotFoundError`

**Solution:**
```python
# In config.py, set correct path
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### Database Locked

**Error:** `database is locked`

**Solution:**
- Close all application instances
- Delete `data/database/docflow.db-journal` if exists
- Restart application

### Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### OCR Poor Accuracy

**Solutions:**
- Ensure image is high resolution (min 300 DPI)
- Use PNG or PDF instead of JPG
- Preprocess images (contrast, brightness)
- Install Hindi language data: `sudo apt-get install tesseract-ocr-hin`

## 📞 Support

- **Community**: GitHub Issues
- **Email**: support@docflowpro.com
- **Documentation**: https://docs.docflowpro.com
- **Enterprise Support**: enterprise@docflowpro.com

## 🚦 Deployment Options

### Option 1: Single PC

- Install executable on local PC
- Use for single-user operations
- Data stored locally

### Option 2: Local Server (LAN)

1. Install on server PC
2. Share database folder on network
3. Install client on each workstation
4. Point clients to shared database

### Option 3: Multi-User Setup

- Use client-server architecture
- SQLite replaced with PostgreSQL/MySQL
- Add authentication layer
- Deploy with load balancer

## 🛣️ Roadmap

### Version 1.1 (Q1 2025)
- [ ] Advanced ML models
- [ ] Mobile app sync
- [ ] Cloud backup option
- [ ] Enhanced reporting

### Version 2.0 (Q2 2025)
- [ ] REST API
- [ ] Webhook support
- [ ] Advanced AI features
- [ ] Multi-language UI

## 📄 License

Commercial License - See LICENSE file for details

## 🤝 Contributing

This is a commercial product. For enterprise customization:
- Contact: enterprise@docflowpro.com
- Custom development available
- White-label options available

---

**Built with ❤️ for Indian Businesses**

*DocFlow Pro - Automate. Accelerate. Achieve.*