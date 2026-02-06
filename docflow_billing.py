"""
modules/billing/invoice_generator.py - Invoice Generation
DocFlow Pro - Enterprise Document Automation
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import config

class InvoiceGenerator:
    """Generate professional invoices"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2563eb'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=12
        ))
    
    def generate_invoice(self, invoice_data: Dict, output_path: Path) -> Path:
        """Generate invoice PDF"""
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        
        # Company header
        story.append(Paragraph(
            invoice_data.get('company_name', 'Company Name'),
            self.styles['CompanyName']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Invoice title
        story.append(Paragraph('TAX INVOICE', self.styles['InvoiceTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice details table
        details_data = [
            ['Invoice No:', invoice_data.get('invoice_number', '')],
            ['Date:', invoice_data.get('invoice_date', datetime.now().strftime('%Y-%m-%d'))],
            ['GST No:', invoice_data.get('company_gst', '')],
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Customer details
        story.append(Paragraph('Bill To:', self.styles['Heading3']))
        customer_data = [
            [invoice_data.get('customer_name', '')],
            [invoice_data.get('customer_address', '')],
            [f"GST: {invoice_data.get('customer_gst', '')}"],
        ]
        
        customer_table = Table(customer_data, colWidths=[6*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Line items
        items = invoice_data.get('items', [])
        if not items:
            items = [{
                'description': 'Service/Product',
                'quantity': 1,
                'rate': invoice_data.get('taxable_amount', 0),
                'amount': invoice_data.get('taxable_amount', 0)
            }]
        
        items_data = [['#', 'Description', 'Qty', 'Rate', 'Amount']]
        
        for i, item in enumerate(items, 1):
            items_data.append([
                str(i),
                item['description'],
                str(item['quantity']),
                f"₹{item['rate']:,.2f}",
                f"₹{item['amount']:,.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[0.5*inch, 3*inch, 0.75*inch, 1.25*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Totals
        taxable_amount = invoice_data.get('taxable_amount', 0)
        cgst_rate = invoice_data.get('cgst_rate', 9)
        sgst_rate = invoice_data.get('sgst_rate', 9)
        cgst_amount = taxable_amount * (cgst_rate / 100)
        sgst_amount = taxable_amount * (sgst_rate / 100)
        total_amount = taxable_amount + cgst_amount + sgst_amount
        
        totals_data = [
            ['', 'Taxable Amount:', f"₹{taxable_amount:,.2f}"],
            ['', f'CGST @ {cgst_rate}%:', f"₹{cgst_amount:,.2f}"],
            ['', f'SGST @ {sgst_rate}%:', f"₹{sgst_amount:,.2f}"],
            ['', 'Total Amount:', f"₹{total_amount:,.2f}"],
        ]
        
        totals_table = Table(totals_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LINEABOVE', (1, -1), (-1, -1), 2, colors.black),
            ('FONTSIZE', (1, -1), (-1, -1), 12),
            ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = "Thank you for your business!"
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def generate_receipt(self, payment_data: Dict, output_path: Path) -> Path:
        """Generate payment receipt"""
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        story = []
        
        # Header
        story.append(Paragraph('PAYMENT RECEIPT', self.styles['InvoiceTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Receipt details
        details_data = [
            ['Receipt No:', payment_data.get('receipt_number', '')],
            ['Date:', payment_data.get('payment_date', datetime.now().strftime('%Y-%m-%d'))],
            ['Invoice No:', payment_data.get('invoice_number', '')],
            ['Amount Paid:', f"₹{payment_data.get('amount', 0):,.2f}"],
            ['Payment Method:', payment_data.get('payment_method', '')],
            ['Reference:', payment_data.get('reference', '')],
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        story.append(details_table)
        
        doc.build(story)
        return output_path


class GSTCalculator:
    """GST calculation utilities"""
    
    @staticmethod
    def calculate_gst(taxable_amount: float, gst_rate: float, 
                     is_interstate: bool = False) -> Dict:
        """Calculate GST breakdown"""
        total_gst = taxable_amount * (gst_rate / 100)
        
        if is_interstate:
            # IGST (Interstate)
            return {
                'taxable_amount': taxable_amount,
                'igst_rate': gst_rate,
                'igst_amount': total_gst,
                'cgst_rate': 0,
                'cgst_amount': 0,
                'sgst_rate': 0,
                'sgst_amount': 0,
                'total_gst': total_gst,
                'total_amount': taxable_amount + total_gst
            }
        else:
            # CGST + SGST (Intrastate)
            half_rate = gst_rate / 2
            half_amount = total_gst / 2
            
            return {
                'taxable_amount': taxable_amount,
                'cgst_rate': half_rate,
                'cgst_amount': half_amount,
                'sgst_rate': half_rate,
                'sgst_amount': half_amount,
                'igst_rate': 0,
                'igst_amount': 0,
                'total_gst': total_gst,
                'total_amount': taxable_amount + total_gst
            }
    
    @staticmethod
    def reverse_calculate(total_amount: float, gst_rate: float) -> Dict:
        """Calculate taxable amount from total (reverse calculation)"""
        multiplier = 1 + (gst_rate / 100)
        taxable_amount = total_amount / multiplier
        gst_amount = total_amount - taxable_amount
        
        return {
            'total_amount': total_amount,
            'taxable_amount': taxable_amount,
            'gst_amount': gst_amount,
            'gst_rate': gst_rate
        }
    
    @staticmethod
    def validate_gst_state(gst1: str, gst2: str) -> bool:
        """Check if two GST numbers are from same state"""
        if not gst1 or not gst2 or len(gst1) < 2 or len(gst2) < 2:
            return False
        return gst1[:2] == gst2[:2]