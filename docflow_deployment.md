# DocFlow Pro - Complete Deployment Guide

## Table of Contents
1. [Development Setup](#development-setup)
2. [Building Standalone Executable](#building-standalone-executable)
3. [Deployment Scenarios](#deployment-scenarios)
4. [Production Configuration](#production-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Development Setup

### Prerequisites

```bash
# Python 3.8+ required
python --version

# Git
git --version
```

### Step 1: Clone and Setup

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

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Install Tesseract OCR

#### Windows
```bash
# Download installer
# https://github.com/UB-Mannheim/tesseract/wiki

# Install to: C:\Program Files\Tesseract-OCR

# Add to PATH or update config.py:
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-hin  # Hindi
sudo apt-get install tesseract-ocr-eng  # English
```

#### macOS
```bash
brew install tesseract
brew install tesseract-lang  # All languages
```

### Step 3: Verify Installation

```python
# Test script
import pytesseract
from PIL import Image

print("Tesseract version:", pytesseract.get_tesseract_version())
```

### Step 4: Run Application

```bash
python main.py
```

**Default Login:**
- Username: `admin`
- Password: `admin`

---

## Building Standalone Executable

### Method 1: Using PyInstaller (Recommended)

#### Step 1: Install PyInstaller

```bash
pip install pyinstaller==6.3.0
```

#### Step 2: Prepare Build Directory

```bash
# Create build directory
mkdir build_dist
cd build_dist

# Copy necessary files
cp -r ../tesseract .
cp -r ../data .
cp -r ../assets .
```

#### Step 3: Create build.spec File

```python
# build.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Determine platform
is_windows = sys.platform.startswith('win')
is_macos = sys.platform == 'darwin'
is_linux = sys.platform.startswith('linux')

# Binary files
binaries = []

if is_windows:
    binaries.append(('tesseract/tesseract.exe', 'tesseract'))
    binaries.append(('tesseract/*.dll', 'tesseract'))
elif is_linux:
    # Tesseract should be installed system-wide on Linux
    pass
elif is_macos:
    # Include Tesseract from Homebrew
    binaries.append(('/usr/local/bin/tesseract', 'tesseract'))

# Add tessdata
binaries.append(('tesseract/tessdata/*', 'tesseract/tessdata'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('data/workflows/*.json', 'data/workflows'),
        ('data/templates/*', 'data/templates'),
        ('assets/*', 'assets'),
        ('config.py', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'pytesseract',
        'pandas',
        'sklearn',
        'sklearn.utils._cython_blas',
        'sklearn.neighbors.typedefs',
        'sklearn.neighbors.quad_tree',
        'sklearn.tree._utils',
        'reportlab',
        'reportlab.pdfbase._fontdata',
        'tkinterdnd2',
        'fitz',
        'cryptography',
        'openpyxl',
        'matplotlib',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', 'tests', 'unittest'],
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
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if is_windows else None,
)

# For macOS, create .app bundle
if is_macos:
    app = BUNDLE(
        exe,
        name='DocFlowPro.app',
        icon='assets/icon.icns',
        bundle_identifier='com.yourcompany.docflowpro',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
        },
    )
```

#### Step 4: Build Executable

```bash
# Clean previous builds
pyinstaller --clean build.spec

# Or full command
pyinstaller --onefile \
    --windowed \
    --name DocFlowPro \
    --icon assets/icon.ico \
    --add-data "tesseract/tessdata:tesseract/tessdata" \
    --add-data "data/workflows:data/workflows" \
    --hidden-import pytesseract \
    --hidden-import sklearn \
    main.py
```

#### Step 5: Test Executable

```bash
# Windows
dist\DocFlowPro.exe

# Linux
./dist/DocFlowPro

# macOS
open dist/DocFlowPro.app
```

### Method 2: Using cx_Freeze (Alternative)

```python
# setup.py
from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": [
        "tkinter", "pytesseract", "PIL", "pandas", 
        "sklearn", "reportlab", "cryptography"
    ],
    "include_files": [
        ("tesseract/", "tesseract/"),
        ("data/", "data/"),
        ("assets/", "assets/"),
    ],
    "excludes": ["test", "unittest"],
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="DocFlowPro",
    version="1.0.0",
    description="Enterprise Document Automation",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="assets/icon.ico")]
)
```

```bash
python setup.py build
```

---

## Deployment Scenarios

### Scenario 1: Single PC Installation

**Use Case:** Individual user or small office

**Steps:**
1. Copy `DocFlowPro.exe` to target PC
2. Run executable
3. Data stored in: `%APPDATA%\DocFlowPro\` (Windows) or `~/.docflowpro/` (Linux)

**Pros:**
- Simple setup
- No network configuration
- Full offline capability

**Cons:**
- Single user only
- No data sharing

### Scenario 2: Local Server (LAN Multi-User)

**Use Case:** Multiple users in same office

**Architecture:**
```
Server PC (Database Host)
    ↓
  Network Share
    ↓
Client PCs → Access shared database
```

**Steps:**

#### On Server PC:
```bash
# 1. Install DocFlow Pro
# 2. Share data directory
# Windows:
Right-click data/ → Properties → Sharing → Share

# 3. Set permissions (Read/Write for all users)
```

#### On Client PCs:
```bash
# 1. Install DocFlow Pro
# 2. Map network drive
# Windows:
net use Z: \\SERVER-PC\docflow_data

# 3. Update config.py:
DATABASE_PATH = Path("Z:/database/docflow.db")
```

**Pros:**
- Multi-user access
- Centralized data
- Still fully on-premise

**Cons:**
- Requires network setup
- Potential SQLite locking issues (use connection pooling)

### Scenario 3: Enterprise Deployment

**Use Case:** Large organization with 50+ users

**Architecture:**
```
PostgreSQL/MySQL Server
    ↓
Application Server (Python FastAPI)
    ↓
Load Balancer
    ↓
Desktop Clients → REST API
```

**Migration Steps:**

1. **Replace SQLite with PostgreSQL:**

```python
# database.py
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="db-server.local",
            database="docflow_prod",
            user="docflow_user",
            password=os.getenv("DB_PASSWORD"),
            cursor_factory=RealDictCursor
        )
```

2. **Create API Server:**

```python
# api_server.py
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile):
    # Handle upload
    pass

@app.get("/api/v1/workflows/{id}/instances")
async def get_workflow_instances(id: int):
    # Get instances
    pass
```

3. **Deploy with Docker:**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Tesseract
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-hin && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: docflow_prod
      POSTGRES_USER: docflow_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://docflow_user:${DB_PASSWORD}@postgres/docflow_prod
    volumes:
      - ./data:/app/data

volumes:
  postgres_data:
```

**Deployment:**
```bash
docker-compose up -d
```

---

## Production Configuration

### Security Hardening

#### 1. Strong Password Policy

```python
# core/auth.py
import re

def validate_password(password):
    """
    Enforce strong password:
    - Min 12 characters
    - Upper + lowercase
    - Numbers
    - Special characters
    """
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*()]', password):
        return False
    return True
```

#### 2. Database Encryption

```python
# config.py
import sqlite3

def get_encrypted_connection(db_path, password):
    conn = sqlite3.connect(db_path)
    conn.execute(f"PRAGMA key = '{password}'")
    return conn
```

#### 3. License Validation

```python
# core/license.py
def verify_license_signature(license_data, public_key):
    """Verify license with RSA signature"""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    
    # Verify signature
    try:
        public_key.verify(
            license_data['signature'],
            license_data['payload'].encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False
```

### Performance Optimization

#### 1. Database Indexing

```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_invoices_invoice_date ON invoices(invoice_date);
CREATE INDEX idx_workflow_instances_current_state ON workflow_instances(current_state);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
```

#### 2. Connection Pooling

```python
# core/database.py
from queue import Queue
import threading

class ConnectionPool:
    def __init__(self, db_path, pool_size=10):
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            self.pool.put(conn)
    
    def get_connection(self):
        return self.pool.get()
    
    def return_connection(self, conn):
        self.pool.put(conn)
```

#### 3. Async OCR Processing

```python
# modules/ocr/scanner.py
import concurrent.futures
from typing import List

class AsyncDocumentScanner:
    def __init__(self, max_workers=4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    def scan_batch_async(self, file_paths: List[Path]):
        """Scan multiple documents in parallel"""
        futures = [
            self.executor.submit(self.scan_document, path)
            for path in file_paths
        ]
        return [f.result() for f in concurrent.futures.as_completed(futures)]
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

# Configuration
BACKUP_DIR="/backups/docflow"
DB_PATH="/app/data/database/docflow.db"
RETENTION_DAYS=90

# Create backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/docflow_$TIMESTAMP.db"

# Backup database
sqlite3 $DB_PATH ".backup $BACKUP_FILE"

# Compress
gzip $BACKUP_FILE

# Clean old backups
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

**Cron job:**
```cron
# Backup every day at 2 AM
0 2 * * * /path/to/backup.sh
```

---

## Troubleshooting

### Issue: Application Won't Start

**Symptoms:** Double-click does nothing or immediate crash

**Solutions:**
```bash
# 1. Run from command line to see errors
DocFlowPro.exe

# 2. Check dependencies
python -c "import tkinter; import pytesseract; import PIL"

# 3. Verify Tesseract installation
tesseract --version

# 4. Check logs
cat logs/app.log
```

### Issue: OCR Not Working

**Symptoms:** "Tesseract not found" error

**Solutions:**
```python
# Option 1: Update config.py
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Option 2: Add to PATH
# Windows:
setx PATH "%PATH%;C:\Program Files\Tesseract-OCR"

# Linux:
export PATH=$PATH:/usr/bin/tesseract
```

### Issue: Database Locked

**Symptoms:** "database is locked" error

**Solutions:**
```python
# Option 1: Increase timeout
conn = sqlite3.connect(db_path, timeout=30)

# Option 2: Enable WAL mode
conn.execute("PRAGMA journal_mode=WAL")

# Option 3: Check for zombie processes
# Windows:
taskkill /F /IM DocFlowPro.exe

# Linux:
pkill -9 DocFlowPro
```

### Issue: Poor OCR Accuracy

**Solutions:**
1. **Improve Image Quality:**
   - Scan at 300 DPI minimum
   - Use black & white mode
   - Ensure good lighting

2. **Preprocess Images:**
```python
from PIL import Image, ImageEnhance

def preprocess_for_ocr(image_path):
    img = Image.open(image_path)
    
    # Convert to grayscale
    img = img.convert('L')
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    
    # Sharpen
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2)
    
    return img
```

3. **Use Correct Language:**
```python
# For Hindi + English
text = pytesseract.image_to_string(image, lang='hin+eng')
```

### Issue: Memory Usage High

**Solutions:**
```python
# 1. Implement pagination
def get_documents_paginated(page=1, per_page=50):
    offset = (page - 1) * per_page
    return db.execute_query(
        'SELECT * FROM documents LIMIT ? OFFSET ?',
        (per_page, offset)
    )

# 2. Clean up resources
import gc
gc.collect()

# 3. Use generators for large datasets
def process_documents_streaming(file_paths):
    for path in file_paths:
        yield process_single_document(path)
        gc.collect()
```

---

## Support & Maintenance

### Monitoring

```python
# utils/monitoring.py
import logging
import psutil
from datetime import datetime

def log_system_stats():
    """Log system resource usage"""
    stats = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }
    logging.info(f"System stats: {stats}")
```

### Updates

```bash
# Check for updates
curl -s https://api.docflowpro.com/version/latest

# Download update
wget https://releases.docflowpro.com/DocFlowPro_v1.1.0.exe

# Backup before update
cp -r data/ data_backup_$(date +%Y%m%d)/

# Install update
./DocFlowPro_v1.1.0.exe
```

---

## Conclusion

DocFlow Pro is now ready for production deployment. Choose the deployment scenario that best fits your organization's needs:

- **Single PC:** Simple, no configuration needed
- **LAN Multi-User:** Network share with SQLite
- **Enterprise:** PostgreSQL + API + Docker

For support: support@docflowpro.com

---

**Version:** 1.0.0  
**Last Updated:** December 2024  
**License:** Commercial