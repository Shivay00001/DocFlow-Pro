"""
modules/ml/categorizer.py - Expense Categorization using ML
DocFlow Pro - Enterprise Document Automation
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
from pathlib import Path
from typing import List, Dict
import config

class ExpenseCategorizer:
    """
    Generic expense categorization using pre-built ML
    NO custom training - uses predefined rules and patterns
    """
    
    def __init__(self):
        self.categories = config.ML_EXPENSE_CATEGORIES
        self._build_keyword_map()
        
        # Pre-built classifier (would be trained on generic data in production)
        self.model = self._build_generic_model()
    
    def _build_keyword_map(self):
        """Build keyword map for rule-based classification"""
        self.keyword_map = {
            'Office Supplies': [
                'stationery', 'paper', 'pen', 'pencil', 'notebook', 'folder',
                'printer', 'ink', 'toner', 'stapler', 'clip', 'desk'
            ],
            'Travel': [
                'flight', 'hotel', 'cab', 'taxi', 'uber', 'ola', 'train',
                'bus', 'ticket', 'booking', 'airfare', 'accommodation'
            ],
            'Utilities': [
                'electricity', 'water', 'gas', 'internet', 'phone', 'mobile',
                'broadband', 'wifi', 'telephone', 'utility', 'bill'
            ],
            'Salaries': [
                'salary', 'wages', 'payroll', 'compensation', 'bonus',
                'incentive', 'allowance', 'pf', 'esi', 'employee'
            ],
            'Marketing': [
                'advertisement', 'marketing', 'promotion', 'campaign', 'seo',
                'social media', 'facebook', 'google ads', 'branding', 'pr'
            ],
            'IT Services': [
                'software', 'saas', 'cloud', 'hosting', 'domain', 'server',
                'aws', 'azure', 'license', 'subscription', 'api', 'database'
            ],
            'Professional Fees': [
                'consultant', 'legal', 'audit', 'lawyer', 'ca', 'accountant',
                'advisor', 'consulting', 'professional', 'attorney'
            ],
            'Rent': [
                'rent', 'lease', 'property', 'office space', 'premises',
                'building', 'facility', 'maintenance'
            ],
            'Insurance': [
                'insurance', 'policy', 'premium', 'coverage', 'liability',
                'health insurance', 'vehicle insurance'
            ],
            'Taxes': [
                'tax', 'gst', 'tds', 'income tax', 'service tax', 'vat',
                'professional tax', 'property tax'
            ],
            'Miscellaneous': [
                'misc', 'miscellaneous', 'other', 'general', 'various'
            ]
        }
    
    def _build_generic_model(self):
        """Build generic ML model using predefined training data"""
        # Create synthetic training data based on keywords
        training_texts = []
        training_labels = []
        
        for category, keywords in self.keyword_map.items():
            for keyword in keywords:
                # Create sample descriptions
                training_texts.append(f"Payment for {keyword}")
                training_texts.append(f"{keyword} expense")
                training_texts.append(f"Bill for {keyword}")
                training_labels.extend([category] * 3)
        
        # Build pipeline
        model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=100, ngram_range=(1, 2))),
            ('clf', MultinomialNB())
        ])
        
        # Train on synthetic data
        model.fit(training_texts, training_labels)
        
        return model
    
    def predict(self, description: str) -> str:
        """Predict expense category"""
        if not description:
            return 'Miscellaneous'
        
        description_lower = description.lower()
        
        # First try rule-based matching
        for category, keywords in self.keyword_map.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        # Fall back to ML model
        try:
            prediction = self.model.predict([description])[0]
            return prediction
        except:
            return 'Miscellaneous'
    
    def predict_batch(self, descriptions: List[str]) -> List[str]:
        """Predict categories for multiple descriptions"""
        return [self.predict(desc) for desc in descriptions]
    
    def get_category_stats(self, expenses: List[Dict]) -> Dict:
        """Get category-wise statistics"""
        category_totals = {cat: 0 for cat in self.categories}
        category_counts = {cat: 0 for cat in self.categories}
        
        for expense in expenses:
            category = self.predict(expense.get('description', ''))
            amount = expense.get('amount', 0)
            
            category_totals[category] += amount
            category_counts[category] += 1
        
        return {
            'totals': category_totals,
            'counts': category_counts,
            'average': {
                cat: (category_totals[cat] / category_counts[cat] if category_counts[cat] > 0 else 0)
                for cat in self.categories
            }
        }


class VendorClassifier:
    """Classify and standardize vendor names"""
    
    def __init__(self):
        self.vendor_patterns = self._build_vendor_patterns()
    
    def _build_vendor_patterns(self):
        """Build common vendor name patterns"""
        return {
            'Amazon': ['amazon', 'amzn', 'amazon.in', 'amazon india'],
            'Flipkart': ['flipkart', 'flipkart.com'],
            'Microsoft': ['microsoft', 'msft', 'microsoft corp'],
            'Google': ['google', 'google inc', 'google india'],
            'Reliance': ['reliance', 'ril', 'reliance industries'],
            'Tata': ['tata', 'tcs', 'tata consultancy'],
            'Airtel': ['airtel', 'bharti airtel'],
            'BSNL': ['bsnl', 'bharat sanchar'],
        }
    
    def standardize_vendor(self, vendor_name: str) -> str:
        """Standardize vendor name"""
        if not vendor_name:
            return ''
        
        vendor_lower = vendor_name.lower()
        
        # Check against known patterns
        for standard_name, patterns in self.vendor_patterns.items():
            for pattern in patterns:
                if pattern in vendor_lower:
                    return standard_name
        
        # Return cleaned original name
        return vendor_name.strip().title()
    
    def classify_vendor_type(self, vendor_name: str) -> str:
        """Classify vendor by type"""
        vendor_lower = vendor_name.lower()
        
        if any(kw in vendor_lower for kw in ['pvt', 'ltd', 'limited', 'llp', 'inc']):
            return 'Company'
        elif any(kw in vendor_lower for kw in ['shop', 'store', 'mart', 'retail']):
            return 'Retailer'
        elif any(kw in vendor_lower for kw in ['consultant', 'services', 'solutions']):
            return 'Service Provider'
        else:
            return 'Other'


class AnomalyDetector:
    """Detect anomalous transactions"""
    
    def __init__(self):
        self.thresholds = {
            'Office Supplies': 50000,
            'Travel': 100000,
            'Utilities': 25000,
            'Salaries': 500000,
            'Marketing': 200000,
            'IT Services': 150000,
            'Professional Fees': 100000,
            'Rent': 200000,
            'Insurance': 100000,
            'Taxes': 1000000,
            'Miscellaneous': 50000
        }
    
    def detect(self, amount: float, category: str, 
               historical_amounts: List[float] = None) -> Dict:
        """Detect if transaction is anomalous"""
        result = {
            'is_anomaly': False,
            'reasons': [],
            'severity': 'normal'
        }
        
        # Check against category threshold
        threshold = self.thresholds.get(category, 50000)
        if amount > threshold:
            result['is_anomaly'] = True
            result['reasons'].append(f'Amount exceeds category threshold of ₹{threshold:,.2f}')
            result['severity'] = 'high' if amount > threshold * 2 else 'medium'
        
        # Check against historical average
        if historical_amounts and len(historical_amounts) >= 3:
            avg_amount = sum(historical_amounts) / len(historical_amounts)
            std_dev = (sum((x - avg_amount) ** 2 for x in historical_amounts) / len(historical_amounts)) ** 0.5
            
            # If amount is more than 3 standard deviations from mean
            if abs(amount - avg_amount) > 3 * std_dev:
                result['is_anomaly'] = True
                result['reasons'].append(f'Significantly different from historical average of ₹{avg_amount:,.2f}')
                result['severity'] = 'high'
        
        return result
    
    def detect_duplicate(self, transaction: Dict, 
                        existing_transactions: List[Dict],
                        days_window: int = 30) -> bool:
        """Detect potential duplicate transactions"""
        from datetime import datetime, timedelta
        
        trans_amount = transaction.get('amount', 0)
        trans_date = datetime.fromisoformat(transaction.get('date', datetime.now().isoformat()))
        trans_vendor = transaction.get('vendor', '').lower()
        
        for existing in existing_transactions:
            exist_amount = existing.get('amount', 0)
            exist_date = datetime.fromisoformat(existing.get('date', datetime.now().isoformat()))
            exist_vendor = existing.get('vendor', '').lower()
            
            # Check if amounts match
            if abs(trans_amount - exist_amount) < 0.01:
                # Check if dates are within window
                if abs((trans_date - exist_date).days) <= days_window:
                    # Check if vendors match
                    if trans_vendor and exist_vendor and trans_vendor == exist_vendor:
                        return True
        
        return False


class TrendAnalyzer:
    """Analyze spending trends"""
    
    def analyze_monthly_trends(self, expenses: List[Dict]) -> Dict:
        """Analyze month-over-month trends"""
        from datetime import datetime
        from collections import defaultdict
        
        monthly_totals = defaultdict(float)
        monthly_counts = defaultdict(int)
        
        for expense in expenses:
            date_str = expense.get('date', '')
            amount = expense.get('amount', 0)
            
            try:
                date = datetime.fromisoformat(date_str)
                month_key = f"{date.year}-{date.month:02d}"
                monthly_totals[month_key] += amount
                monthly_counts[month_key] += 1
            except:
                continue
        
        # Calculate trends
        sorted_months = sorted(monthly_totals.keys())
        trends = []
        
        for i in range(1, len(sorted_months)):
            prev_month = sorted_months[i-1]
            curr_month = sorted_months[i]
            
            prev_total = monthly_totals[prev_month]
            curr_total = monthly_totals[curr_month]
            
            if prev_total > 0:
                change_pct = ((curr_total - prev_total) / prev_total) * 100
                trends.append({
                    'month': curr_month,
                    'total': curr_total,
                    'change_pct': round(change_pct, 2),
                    'direction': 'increase' if change_pct > 0 else 'decrease'
                })
        
        return {
            'monthly_totals': dict(monthly_totals),
            'monthly_counts': dict(monthly_counts),
            'trends': trends
        }
    
    def identify_seasonal_patterns(self, expenses: List[Dict]) -> Dict:
        """Identify seasonal spending patterns"""
        from collections import defaultdict
        from datetime import datetime
        
        quarter_totals = defaultdict(float)
        
        for expense in expenses:
            date_str = expense.get('date', '')
            amount = expense.get('amount', 0)
            
            try:
                date = datetime.fromisoformat(date_str)
                quarter = (date.month - 1) // 3 + 1
                quarter_key = f"Q{quarter}"
                quarter_totals[quarter_key] += amount
            except:
                continue
        
        return {
            'quarterly_totals': dict(quarter_totals),
            'highest_quarter': max(quarter_totals.items(), key=lambda x: x[1])[0] if quarter_totals else None
        }