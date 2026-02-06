"""
modules/data_cleaning/cleaner.py - Data Cleaning & Normalization
DocFlow Pro - Enterprise Document Automation
"""

import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import config

class DataCleaner:
    """Generic data cleaning for business documents"""
    
    def __init__(self):
        self.date_formats = [
            '%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d',
            '%d-%m-%y', '%d/%m/%y', '%d %b %Y', '%d %B %Y'
        ]
    
    def remove_duplicates(self, df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """Remove duplicate records"""
        if subset:
            return df.drop_duplicates(subset=subset, keep='first')
        return df.drop_duplicates(keep='first')
    
    def normalize_dates(self, date_str: str) -> Optional[str]:
        """Normalize date to YYYY-MM-DD format"""
        if not date_str or pd.isna(date_str):
            return None
        
        date_str = str(date_str).strip()
        
        # Try each date format
        for fmt in self.date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except:
                continue
        
        return None
    
    def normalize_amount(self, amount_str: Any) -> Optional[float]:
        """Normalize amount string to float"""
        if pd.isna(amount_str):
            return None
        
        try:
            # Convert to string and clean
            amount_str = str(amount_str).strip()
            
            # Remove currency symbols
            amount_str = re.sub(r'[₹Rs\.INR]', '', amount_str, flags=re.IGNORECASE)
            
            # Remove commas
            amount_str = amount_str.replace(',', '')
            
            # Remove spaces
            amount_str = amount_str.replace(' ', '')
            
            # Convert to float
            return float(amount_str)
        except:
            return None
    
    def validate_gst(self, gst_number: str) -> bool:
        """Validate GST number format"""
        if not gst_number or pd.isna(gst_number):
            return False
        
        gst_number = str(gst_number).strip().upper()
        
        # GST format: 2 digits + 10 char PAN + entity code + Z + checksum
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}[Z]{1}[A-Z0-9]{1}$'
        
        if not re.match(pattern, gst_number):
            return False
        
        # Validate state code
        state_code = gst_number[:2]
        if state_code not in config.STATE_CODES:
            return False
        
        return True
    
    def validate_pan(self, pan_number: str) -> bool:
        """Validate PAN number format"""
        if not pan_number or pd.isna(pan_number):
            return False
        
        pan_number = str(pan_number).strip().upper()
        
        # PAN format: 5 letters + 4 digits + 1 letter
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        
        return bool(re.match(pattern, pan_number))
    
    def standardize_vendor_name(self, vendor_name: str) -> str:
        """Standardize vendor name"""
        if not vendor_name or pd.isna(vendor_name):
            return ""
        
        vendor_name = str(vendor_name).strip()
        
        # Convert to title case
        vendor_name = vendor_name.title()
        
        # Remove extra spaces
        vendor_name = re.sub(r'\s+', ' ', vendor_name)
        
        # Standardize common suffixes
        suffixes = {
            'Pvt. Ltd.': ['pvt ltd', 'pvt. ltd', 'private limited', 'pvt.ltd.'],
            'Ltd.': ['ltd', 'limited', 'ltd.'],
            'LLP': ['llp'],
            'Corp.': ['corp', 'corporation']
        }
        
        for standard, variations in suffixes.items():
            for var in variations:
                if vendor_name.lower().endswith(var):
                    vendor_name = vendor_name[:-(len(var))].strip() + ' ' + standard
                    break
        
        return vendor_name
    
    def clean_dataframe(self, df: pd.DataFrame, config: Dict = None) -> pd.DataFrame:
        """Clean entire dataframe based on configuration"""
        df_clean = df.copy()
        
        if config is None:
            config = {}
        
        # Remove duplicates
        if config.get('remove_duplicates', True):
            subset = config.get('duplicate_subset', None)
            df_clean = self.remove_duplicates(df_clean, subset)
        
        # Normalize dates
        date_columns = config.get('date_columns', [])
        for col in date_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].apply(self.normalize_dates)
        
        # Normalize amounts
        amount_columns = config.get('amount_columns', [])
        for col in amount_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].apply(self.normalize_amount)
        
        # Validate GST
        gst_columns = config.get('gst_columns', [])
        for col in gst_columns:
            if col in df_clean.columns:
                df_clean[f'{col}_valid'] = df_clean[col].apply(self.validate_gst)
        
        # Validate PAN
        pan_columns = config.get('pan_columns', [])
        for col in pan_columns:
            if col in df_clean.columns:
                df_clean[f'{col}_valid'] = df_clean[col].apply(self.validate_pan)
        
        # Standardize vendor names
        vendor_columns = config.get('vendor_columns', [])
        for col in vendor_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].apply(self.standardize_vendor_name)
        
        return df_clean
    
    def get_data_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data quality report"""
        report = {
            'total_records': len(df),
            'columns': len(df.columns),
            'missing_values': {},
            'duplicate_records': 0,
            'data_types': {}
        }
        
        # Missing values
        for col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                report['missing_values'][col] = {
                    'count': int(missing),
                    'percentage': round(missing / len(df) * 100, 2)
                }
        
        # Duplicates
        report['duplicate_records'] = df.duplicated().sum()
        
        # Data types
        for col in df.columns:
            report['data_types'][col] = str(df[col].dtype)
        
        return report


class InvoiceValidator:
    """Validate invoice data"""
    
    def validate_invoice(self, invoice_data: Dict) -> Dict[str, Any]:
        """Validate invoice data and return validation report"""
        errors = []
        warnings = []
        
        cleaner = DataCleaner()
        
        # Validate GST numbers
        if invoice_data.get('vendor_gst'):
            if not cleaner.validate_gst(invoice_data['vendor_gst']):
                errors.append("Invalid vendor GST number format")
        else:
            warnings.append("Vendor GST number missing")
        
        if invoice_data.get('customer_gst'):
            if not cleaner.validate_gst(invoice_data['customer_gst']):
                errors.append("Invalid customer GST number format")
        
        # Validate PAN
        if invoice_data.get('vendor_pan'):
            if not cleaner.validate_pan(invoice_data['vendor_pan']):
                errors.append("Invalid vendor PAN number format")
        
        # Validate amounts
        if not invoice_data.get('total_amount'):
            errors.append("Total amount is missing")
        elif invoice_data['total_amount'] <= 0:
            errors.append("Total amount must be positive")
        
        # Validate date
        if not invoice_data.get('invoice_date'):
            warnings.append("Invoice date is missing")
        else:
            normalized_date = cleaner.normalize_dates(invoice_data['invoice_date'])
            if not normalized_date:
                errors.append("Invalid invoice date format")
        
        # Validate invoice number
        if not invoice_data.get('invoice_number'):
            warnings.append("Invoice number is missing")
        
        # Validate GST calculation
        if all(k in invoice_data for k in ['taxable_amount', 'total_gst', 'total_amount']):
            expected_total = invoice_data['taxable_amount'] + invoice_data['total_gst']
            if abs(expected_total - invoice_data['total_amount']) > 0.01:
                warnings.append(f"GST calculation mismatch: {expected_total} vs {invoice_data['total_amount']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'error_count': len(errors),
            'warning_count': len(warnings)
        }