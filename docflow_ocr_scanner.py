"""
modules/ocr/scanner.py - Document Scanning & OCR
DocFlow Pro - Enterprise Document Automation
"""

import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional, Dict, List
import config
import re

# Set Tesseract command
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

class DocumentScanner:
    def __init__(self):
        self.supported_formats = config.SUPPORTED_FORMATS
    
    def extract_text_from_image(self, image_path: Path, lang: str = config.TESSERACT_LANG) -> str:
        """Extract text from image file using OCR"""
        try:
            image = Image.open(image_path)
            
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang=lang)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_path: Path, lang: str = config.TESSERACT_LANG) -> str:
        """Extract text from PDF file"""
        try:
            full_text = []
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Try extracting text directly first (for text-based PDFs)
                text = page.get_text()
                
                # If no text found, perform OCR on page image
                if not text.strip():
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img = self._preprocess_image(img)
                    text = pytesseract.image_to_string(img, lang=lang)
                
                full_text.append(text)
            
            doc.close()
            return '\n\n'.join(full_text).strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        image = image.convert('L')
        
        # Resize if too small
        if image.width < 1000:
            scale_factor = 1000 / image.width
            new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def scan_document(self, file_path: Path) -> Dict:
        """Main method to scan document and extract text"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Extract text based on file type
        if file_ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        else:
            text = self.extract_text_from_image(file_path)
        
        return {
            'filename': file_path.name,
            'file_type': file_ext,
            'text': text,
            'length': len(text),
            'success': True
        }
    
    def batch_scan(self, file_paths: List[Path]) -> List[Dict]:
        """Scan multiple documents"""
        results = []
        for file_path in file_paths:
            try:
                result = self.scan_document(file_path)
                results.append(result)
            except Exception as e:
                results.append({
                    'filename': file_path.name,
                    'success': False,
                    'error': str(e)
                })
        return results


class InvoiceExtractor:
    """Extract structured data from invoice text"""
    
    def __init__(self):
        # Indian GST number pattern: 2 digits + PAN (10 chars) + entity code + checksum
        self.gst_pattern = r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b'
        
        # PAN pattern: 5 letters + 4 digits + 1 letter
        self.pan_pattern = r'\b[A-Z]{5}\d{4}[A-Z]{1}\b'
        
        # Invoice number patterns
        self.invoice_patterns = [
            r'(?:invoice|bill|inv|bill no|invoice no|invoice number|inv no|inv #|invoice #)[:\s#-]*([A-Z0-9/-]+)',
            r'(?:नंबर|संख्या|बिल)[:\s]*([A-Z0-9/-]+)'
        ]
        
        # Date patterns
        self.date_patterns = [
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
            r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b',
            r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b'
        ]
        
        # Amount patterns
        self.amount_patterns = [
            r'(?:total|amount|sum|₹|Rs\.?|INR)\s*[:\s]*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:only|/-)'
        ]
    
    def extract_gst_numbers(self, text: str) -> List[str]:
        """Extract GST numbers"""
        matches = re.findall(self.gst_pattern, text, re.IGNORECASE)
        return list(set(matches))
    
    def extract_pan_numbers(self, text: str) -> List[str]:
        """Extract PAN numbers"""
        matches = re.findall(self.pan_pattern, text, re.IGNORECASE)
        # Filter out GST numbers that contain PAN
        return list(set([m for m in matches if not re.search(self.gst_pattern, m)]))
    
    def extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number"""
        for pattern in self.invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract dates"""
        dates = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        return list(set(dates))
    
    def extract_amounts(self, text: str) -> List[float]:
        """Extract amounts"""
        amounts = []
        for pattern in self.amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Remove commas and convert to float
                    amount = float(match.replace(',', ''))
                    amounts.append(amount)
                except:
                    pass
        return sorted(set(amounts), reverse=True)
    
    def extract_vendor_name(self, text: str) -> Optional[str]:
        """Extract vendor/company name"""
        lines = text.split('\n')
        # Heuristic: vendor name is often in first few lines
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            # Look for lines with company keywords
            if any(kw in line.lower() for kw in ['pvt', 'ltd', 'limited', 'company', 'enterprises', 'corp']):
                return line
            # Or lines with all caps (company names often in caps)
            if len(line) > 10 and line.isupper():
                return line
        return None
    
    def extract_invoice_data(self, text: str) -> Dict:
        """Extract all invoice data"""
        gst_numbers = self.extract_gst_numbers(text)
        pan_numbers = self.extract_pan_numbers(text)
        invoice_number = self.extract_invoice_number(text)
        dates = self.extract_dates(text)
        amounts = self.extract_amounts(text)
        vendor_name = self.extract_vendor_name(text)
        
        # Determine vendor and customer GST
        vendor_gst = gst_numbers[0] if len(gst_numbers) > 0 else None
        customer_gst = gst_numbers[1] if len(gst_numbers) > 1 else None
        
        # Determine amounts (heuristic: largest is total, others are components)
        total_amount = amounts[0] if len(amounts) > 0 else None
        taxable_amount = amounts[-1] if len(amounts) > 2 else None
        
        return {
            'invoice_number': invoice_number,
            'invoice_date': dates[0] if dates else None,
            'vendor_name': vendor_name,
            'vendor_gst': vendor_gst,
            'vendor_pan': pan_numbers[0] if pan_numbers else None,
            'customer_gst': customer_gst,
            'taxable_amount': taxable_amount,
            'total_amount': total_amount,
            'gst_numbers_found': gst_numbers,
            'dates_found': dates,
            'amounts_found': amounts
        }