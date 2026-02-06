"""
main.py - DocFlow Pro Application Entry Point
Enterprise Document Automation System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from core.database import DatabaseManager
from core.license import LicenseManager
from ui.main_window import MainWindow
from ui.login import LoginWindow

class DocFlowApp:
    """Main Application Class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide initially
        
        # Initialize core components
        self.db_manager = DatabaseManager()
        self.license_manager = LicenseManager()
        
        # Check license
        self.license_status = self.license_manager.validate_license()
        
        # Show license info if needed
        if not self.license_status['valid']:
            self._show_license_dialog()
        
        # Initialize main window
        self.main_window = None
        
        # Show login
        self._show_login()
    
    def _show_license_dialog(self):
        """Show license information dialog"""
        dialog = tk.Toplevel()
        dialog.title("License Information")
        dialog.geometry("500x300")
        
        # Center window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # License info
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="DocFlow Pro", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        status_text = f"License Status: {self.license_status['plan'].upper()}"
        ttk.Label(frame, text=status_text, 
                 font=('Arial', 12)).pack(pady=5)
        
        if not self.license_status['valid']:
            ttk.Label(frame, text=self.license_status['reason'],
                     foreground='red').pack(pady=5)
            
            ttk.Label(frame, 
                     text="You are using the FREE plan with limited features.",
                     wraplength=450).pack(pady=10)
        
        # Features
        features = self.license_status['features']
        features_text = f"""
        Features:
        • Documents per month: {features['documents_per_month'] if features['documents_per_month'] != -1 else 'Unlimited'}
        • Users: {features['users'] if features['users'] != -1 else 'Unlimited'}
        • Workflows: {features['workflows'] if features['workflows'] != -1 else 'Unlimited'}
        • AI Features: {'Enabled' if features['ai_enabled'] else 'Disabled'}
        • Support: {features['support'].title()}
        """
        
        ttk.Label(frame, text=features_text, justify=tk.LEFT).pack(pady=10)
        
        ttk.Button(frame, text="Continue", 
                  command=dialog.destroy).pack(pady=10)
        
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.wait_window()
    
    def _show_login(self):
        """Show login window"""
        login_window = LoginWindow(self.root, self.db_manager, self.on_login_success)
    
    def on_login_success(self, user_data):
        """Callback when login successful"""
        # Close login window
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        
        # Show main window
        self.root.deiconify()
        self.main_window = MainWindow(
            self.root, 
            self.db_manager, 
            self.license_manager,
            user_data
        )
    
    def run(self):
        """Start application"""
        self.root.mainloop()

def main():
    """Application entry point"""
    try:
        app = DocFlowApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()