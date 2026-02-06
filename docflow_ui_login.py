"""
ui/login.py - Login Window
DocFlow Pro - Enterprise Document Automation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from datetime import datetime

class LoginWindow:
    """Login window for user authentication"""
    
    def __init__(self, parent, db_manager, on_success_callback):
        self.parent = parent
        self.db = db_manager
        self.on_success = on_success_callback
        
        # Create login window
        self.window = tk.Toplevel(parent)
        self.window.title("DocFlow Pro - Login")
        self.window.geometry("400x500")
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"400x500+{x}+{y}")
        
        self.window.transient(parent)
        self.window.grab_set()
        
        # Ensure default user exists
        self._ensure_default_user()
        
        # Create UI
        self._create_ui()
    
    def _ensure_default_user(self):
        """Create default admin user if no users exist"""
        users = self.db.execute_query('SELECT COUNT(*) as count FROM users')
        
        if users[0]['count'] == 0:
            # Create default admin user
            password = 'admin'  # Default password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            self.db.execute_update('''
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, 'Administrator', 'admin'))
    
    def _create_ui(self):
        """Create login UI"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding=40)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Title
        ttk.Label(main_frame, text="📄 DocFlow Pro",
                 font=('Arial', 24, 'bold')).pack(pady=20)
        
        ttk.Label(main_frame, text="Enterprise Document Automation",
                 font=('Arial', 10)).pack(pady=5)
        
        # Login form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=40)
        
        # Username
        ttk.Label(form_frame, text="Username").grid(row=0, column=0, 
                                                     sticky='w', pady=10)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=10)
        self.username_entry.insert(0, 'admin')  # Default username
        
        # Password
        ttk.Label(form_frame, text="Password").grid(row=1, column=0,
                                                     sticky='w', pady=10)
        self.password_entry = ttk.Entry(form_frame, width=30, show='*')
        self.password_entry.grid(row=1, column=1, pady=10)
        self.password_entry.insert(0, 'admin')  # Default password
        
        # Login button
        self.login_btn = ttk.Button(main_frame, text="Login", 
                                     command=self._login)
        self.login_btn.pack(pady=20)
        
        # Info label
        info_text = "Default credentials:\nUsername: admin\nPassword: admin"
        ttk.Label(main_frame, text=info_text, 
                 font=('Arial', 9), foreground='gray').pack(pady=10)
        
        # Bind Enter key
        self.window.bind('<Return>', lambda e: self._login())
        
        # Focus on username
        self.username_entry.focus()
    
    def _login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Query user
        users = self.db.execute_query('''
            SELECT * FROM users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash))
        
        if not users:
            messagebox.showerror("Error", "Invalid username or password")
            return
        
        user = users[0]
        
        # Update last login
        self.db.execute_update('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        ''', (user['id'],))
        
        # Log audit
        self.db.log_audit(user['id'], "User logged in")
        
        # Close login window
        self.window.destroy()
        
        # Call success callback
        self.on_success(user)