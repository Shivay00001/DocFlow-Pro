"""
ui/main_window.py - Main Application Window
DocFlow Pro - Enterprise Document Automation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from pathlib import Path
import threading

import config
from modules.ocr.scanner import DocumentScanner, InvoiceExtractor
from modules.data_cleaning.cleaner import DataCleaner, InvoiceValidator
from modules.workflow.engine import WorkflowEngine

class MainWindow:
    """Main application window"""
    
    def __init__(self, root, db_manager, license_manager, user_data):
        self.root = root
        self.db = db_manager
        self.license = license_manager
        self.user = user_data
        
        # Initialize modules
        self.scanner = DocumentScanner()
        self.extractor = InvoiceExtractor()
        self.cleaner = DataCleaner()
        self.validator = InvoiceValidator()
        self.workflow_engine = WorkflowEngine(db_manager)
        
        # Setup window
        self.root.title(f"{config.APP_NAME} - {user_data['full_name']}")
        self.root.geometry(config.WINDOW_SIZE)
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create UI
        self._create_menu()
        self._create_layout()
        
        # Load dashboard
        self._load_dashboard()
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Upload Document", command=self._upload_document)
        file_menu.add_command(label="Batch Upload", command=self._batch_upload)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Workflow menu
        workflow_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Workflow", menu=workflow_menu)
        workflow_menu.add_command(label="Create Workflow", command=self._create_workflow)
        workflow_menu.add_command(label="My Approvals", command=self._show_approvals)
        
        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Dashboard", command=self._load_dashboard)
        reports_menu.add_command(label="GST Reports", command=self._gst_reports)
        reports_menu.add_command(label="Export Data", command=self._export_data)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Data Cleaning", command=self._data_cleaning)
        tools_menu.add_command(label="Audit Logs", command=self._audit_logs)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="License Info", command=self._show_license_info)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_layout(self):
        """Create main layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left sidebar
        sidebar = ttk.Frame(main_frame, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(sidebar, text="Quick Actions", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        actions = [
            ("📄 Upload Document", self._upload_document),
            ("✅ My Approvals", self._show_approvals),
            ("📊 Dashboard", self._load_dashboard),
            ("🔄 Workflows", self._create_workflow),
            ("📈 Reports", self._gst_reports),
        ]
        
        for text, command in actions:
            btn = ttk.Button(sidebar, text=text, command=command, width=20)
            btn.pack(pady=5)
        
        # Content area
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _load_dashboard(self):
        """Load dashboard view"""
        self._clear_content()
        
        # Title
        ttk.Label(self.content_frame, text="Dashboard", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Get stats
        stats = self.db.get_dashboard_stats()
        
        # Stats cards
        stats_frame = ttk.Frame(self.content_frame)
        stats_frame.pack(fill=tk.X, pady=20)
        
        cards = [
            ("Total Documents", stats['total_documents'], "#3b82f6"),
            ("Pending Approvals", stats['pending_approvals'], "#f59e0b"),
            ("This Month", stats['documents_this_month'], "#10b981"),
            ("Total Value", f"₹{stats['total_invoices_value']:,.2f}", "#8b5cf6")
        ]
        
        for i, (title, value, color) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=color, relief=tk.RAISED, bd=2)
            card.grid(row=0, column=i, padx=10, sticky='ew')
            stats_frame.columnconfigure(i, weight=1)
            
            tk.Label(card, text=str(value), font=('Arial', 20, 'bold'),
                    bg=color, fg='white').pack(pady=10)
            tk.Label(card, text=title, font=('Arial', 10),
                    bg=color, fg='white').pack(pady=5)
        
        # Recent documents
        ttk.Label(self.content_frame, text="Recent Documents",
                 font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        
        # Treeview
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Filename', 'Type', 'Status', 'Uploaded')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Load recent documents
        docs = self.db.execute_query('''
            SELECT id, filename, document_type, status, 
                   strftime('%Y-%m-%d', uploaded_at) as uploaded
            FROM documents
            ORDER BY uploaded_at DESC
            LIMIT 20
        ''')
        
        for doc in docs:
            tree.insert('', tk.END, values=(
                doc['id'], doc['filename'], doc['document_type'] or 'Unknown',
                doc['status'], doc['uploaded']
            ))
    
    def _upload_document(self):
        """Upload single document"""
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[
                ("All Supported", "*.pdf *.jpg *.jpeg *.png"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.jpg *.jpeg *.png"),
            ]
        )
        
        if file_path:
            self._process_document(Path(file_path))
    
    def _batch_upload(self):
        """Upload multiple documents"""
        file_paths = filedialog.askopenfilenames(
            title="Select Documents",
            filetypes=[
                ("All Supported", "*.pdf *.jpg *.jpeg *.png"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.jpg *.jpeg *.png"),
            ]
        )
        
        if file_paths:
            for file_path in file_paths:
                self._process_document(Path(file_path))
    
    def _process_document(self, file_path: Path):
        """Process uploaded document"""
        self.status_bar.config(text=f"Processing {file_path.name}...")
        
        def process():
            try:
                # Scan document
                scan_result = self.scanner.scan_document(file_path)
                
                # Extract invoice data
                invoice_data = self.extractor.extract_invoice_data(scan_result['text'])
                
                # Save to database
                doc_id = self.db.execute_update('''
                    INSERT INTO documents 
                    (filename, file_path, file_type, file_size, uploaded_by, 
                     ocr_text, extracted_data, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_path.name,
                    str(file_path),
                    file_path.suffix,
                    file_path.stat().st_size,
                    self.user['id'],
                    scan_result['text'],
                    str(invoice_data),
                    'pending'
                ))
                
                # Show edit dialog
                self.root.after(0, lambda: self._show_edit_dialog(doc_id, invoice_data))
                
                self.status_bar.config(text="Document processed successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process document: {str(e)}")
                self.status_bar.config(text="Ready")
        
        # Process in background thread
        threading.Thread(target=process, daemon=True).start()
    
    def _show_edit_dialog(self, doc_id: int, invoice_data: Dict):
        """Show dialog to edit extracted data"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Review Extracted Data")
        dialog.geometry("600x700")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Review and Edit Extracted Data",
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Form fields
        fields = {}
        field_names = [
            ('invoice_number', 'Invoice Number'),
            ('invoice_date', 'Invoice Date'),
            ('vendor_name', 'Vendor Name'),
            ('vendor_gst', 'Vendor GST'),
            ('vendor_pan', 'Vendor PAN'),
            ('customer_gst', 'Customer GST'),
            ('taxable_amount', 'Taxable Amount'),
            ('total_amount', 'Total Amount')
        ]
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        for i, (key, label) in enumerate(field_names):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, sticky='ew', pady=5, padx=10)
            entry.insert(0, str(invoice_data.get(key, '')))
            fields[key] = entry
        
        form_frame.columnconfigure(1, weight=1)
        
        def save():
            # Validate
            data = {k: v.get() for k, v in fields.items()}
            validation = self.validator.validate_invoice(data)
            
            if validation['errors']:
                messagebox.showerror("Validation Errors", 
                                   "\n".join(validation['errors']))
                return
            
            # Save invoice
            self.db.execute_update('''
                INSERT INTO invoices 
                (document_id, invoice_number, invoice_date, vendor_name,
                 vendor_gst, vendor_pan, customer_gst, taxable_amount, total_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                data['invoice_number'],
                data['invoice_date'],
                data['vendor_name'],
                data['vendor_gst'],
                data['vendor_pan'],
                data['customer_gst'],
                float(data['taxable_amount'] or 0),
                float(data['total_amount'] or 0)
            ))
            
            messagebox.showinfo("Success", "Invoice saved successfully")
            dialog.destroy()
            self._load_dashboard()
        
        ttk.Button(frame, text="Save", command=save).pack(pady=10)
    
    def _show_approvals(self):
        """Show pending approvals"""
        self._clear_content()
        
        ttk.Label(self.content_frame, text="My Pending Approvals",
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Get pending approvals
        approvals = self.workflow_engine.get_pending_approvals(self.user['id'])
        
        if not approvals:
            ttk.Label(self.content_frame, text="No pending approvals",
                     font=('Arial', 12)).pack(pady=20)
            return
        
        # Approval cards
        for approval in approvals:
            self._create_approval_card(approval)
    
    def _create_approval_card(self, approval: Dict):
        """Create approval card"""
        card = ttk.LabelFrame(self.content_frame, text=approval['workflow_name'],
                             padding=10)
        card.pack(fill=tk.X, pady=5)
        
        ttk.Label(card, text=f"Document: {approval['filename']}").pack(anchor='w')
        ttk.Label(card, text=f"Started: {approval['started_at']}").pack(anchor='w')
        
        btn_frame = ttk.Frame(card)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="✅ Approve",
                  command=lambda: self._approve_workflow(approval['id'])).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Reject",
                  command=lambda: self._reject_workflow(approval['id'])).pack(side=tk.LEFT)
    
    def _approve_workflow(self, instance_id: int):
        """Approve workflow"""
        self.workflow_engine.approve(instance_id, self.user['id'])
        messagebox.showinfo("Success", "Workflow approved")
        self._show_approvals()
    
    def _reject_workflow(self, instance_id: int):
        """Reject workflow"""
        self.workflow_engine.reject(instance_id, self.user['id'])
        messagebox.showinfo("Success", "Workflow rejected")
        self._show_approvals()
    
    def _create_workflow(self):
        """Create new workflow (simplified)"""
        messagebox.showinfo("Workflow Builder", 
                          "Visual workflow builder - Coming in next update")
    
    def _gst_reports(self):
        """Generate GST reports"""
        messagebox.showinfo("GST Reports", 
                          "GST report generation - Coming in next update")
    
    def _export_data(self):
        """Export data"""
        messagebox.showinfo("Export", 
                          "Data export feature - Coming in next update")
    
    def _data_cleaning(self):
        """Data cleaning tools"""
        messagebox.showinfo("Data Cleaning", 
                          "Data cleaning tools - Coming in next update")
    
    def _audit_logs(self):
        """Show audit logs"""
        messagebox.showinfo("Audit Logs", 
                          "Audit log viewer - Coming in next update")
    
    def _show_license_info(self):
        """Show license information"""
        status = self.license.validate_license()
        info = f"""
        Plan: {status['plan'].upper()}
        Valid: {status['valid']}
        
        Features:
        Documents/month: {status['features']['documents_per_month']}
        Users: {status['features']['users']}
        Workflows: {status['features']['workflows']}
        AI: {'Enabled' if status['features']['ai_enabled'] else 'Disabled'}
        """
        
        if status.get('expiry_date'):
            info += f"\n\nExpires: {status['expiry_date']}"
            info += f"\nDays remaining: {status.get('days_remaining', 0)}"
        
        messagebox.showinfo("License Information", info)
    
    def _show_about(self):
        """Show about dialog"""
        about_text = f"""
        {config.APP_NAME}
        Version {config.APP_VERSION}
        
        Enterprise Document Automation System
        for Indian SMEs and Enterprises
        
        Features:
        • OCR & Data Extraction
        • Workflow Automation
        • GST Invoice Processing
        • Audit Logs
        • Reports & Analytics
        """
        messagebox.showinfo("About", about_text)