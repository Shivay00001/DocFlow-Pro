"""
modules/ai/connector.py - Optional AI Integration
DocFlow Pro - Enterprise Document Automation

IMPORTANT: AI is completely optional
- App works fully without AI
- User must provide their own API key
- Supports OpenAI, Anthropic Claude, HuggingFace
"""

from typing import Dict, Optional, List
import json

class AIConnector:
    """
    Abstraction layer for multiple AI providers
    AI features are OPTIONAL and disabled by default
    """
    
    def __init__(self, api_key: str = None, provider: str = 'openai'):
        self.api_key = api_key
        self.provider = provider
        self.enabled = bool(api_key)
    
    def is_enabled(self) -> bool:
        """Check if AI is enabled"""
        return self.enabled and self.api_key is not None
    
    def summarize_document(self, text: str, max_length: int = 200) -> Optional[str]:
        """
        Summarize document text
        Returns None if AI is not enabled
        """
        if not self.is_enabled():
            return None
        
        try:
            if self.provider == 'openai':
                return self._summarize_openai(text, max_length)
            elif self.provider == 'claude':
                return self._summarize_claude(text, max_length)
            elif self.provider == 'huggingface':
                return self._summarize_huggingface(text, max_length)
            else:
                return None
        except Exception as e:
            print(f"AI summarization error: {e}")
            return None
    
    def _summarize_openai(self, text: str, max_length: int) -> str:
        """Summarize using OpenAI"""
        import requests
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'Summarize the following document concisely.'},
                {'role': 'user', 'content': text[:4000]}  # Limit input
            ],
            'max_tokens': max_length
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return None
    
    def _summarize_claude(self, text: str, max_length: int) -> str:
        """Summarize using Anthropic Claude"""
        import requests
        
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-3-haiku-20240307',
            'max_tokens': max_length,
            'messages': [
                {'role': 'user', 'content': f'Summarize this document: {text[:4000]}'}
            ]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            return None
    
    def _summarize_huggingface(self, text: str, max_length: int) -> str:
        """Summarize using HuggingFace"""
        import requests
        
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'inputs': text[:1000],  # HuggingFace has stricter limits
            'parameters': {
                'max_length': max_length,
                'min_length': 50
            }
        }
        
        response = requests.post(
            'https://api-inference.huggingface.co/models/facebook/bart-large-cnn',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result[0]['summary_text']
        else:
            return None
    
    def intelligent_search(self, query: str, documents: List[Dict]) -> List[Dict]:
        """
        AI-powered semantic search
        Returns None if AI is not enabled
        """
        if not self.is_enabled():
            # Fallback to simple keyword search
            return self._keyword_search(query, documents)
        
        # Implement semantic search using AI embeddings
        # This would use OpenAI embeddings or similar
        # For now, fallback to keyword search
        return self._keyword_search(query, documents)
    
    def _keyword_search(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Simple keyword-based search fallback"""
        query_lower = query.lower()
        results = []
        
        for doc in documents:
            text = doc.get('text', '').lower()
            filename = doc.get('filename', '').lower()
            
            if query_lower in text or query_lower in filename:
                results.append(doc)
        
        return results
    
    def explain_report(self, report_data: Dict) -> Optional[str]:
        """
        Generate natural language explanation of report
        Returns None if AI is not enabled
        """
        if not self.is_enabled():
            return None
        
        # Convert report data to text description
        description = self._format_report_data(report_data)
        
        prompt = f"Explain this financial report in simple terms: {description}"
        
        # Use AI to generate explanation
        return self.summarize_document(prompt, max_length=300)
    
    def _format_report_data(self, report_data: Dict) -> str:
        """Format report data for AI processing"""
        lines = []
        
        if 'total_amount' in report_data:
            lines.append(f"Total Amount: ₹{report_data['total_amount']:,.2f}")
        
        if 'category_breakdown' in report_data:
            lines.append("Category Breakdown:")
            for category, amount in report_data['category_breakdown'].items():
                lines.append(f"  - {category}: ₹{amount:,.2f}")
        
        return "\n".join(lines)
    
    def suggest_category(self, description: str, amount: float) -> Optional[str]:
        """
        AI-powered category suggestion
        Returns None if AI is not enabled
        """
        if not self.is_enabled():
            return None
        
        try:
            if self.provider == 'openai':
                import requests
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {'role': 'system', 'content': 'You are an expense categorization assistant. Respond with only the category name.'},
                        {'role': 'user', 'content': f'Categorize this expense: "{description}" (Amount: ₹{amount})'}
                    ],
                    'max_tokens': 20
                }
                
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
        except:
            pass
        
        return None


class AISettings:
    """Manage AI configuration and settings"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def save_api_key(self, provider: str, api_key: str, user_id: int):
        """Save encrypted API key"""
        from cryptography.fernet import Fernet
        import base64
        
        # Generate encryption key from user_id
        key = base64.urlsafe_b64encode(str(user_id).encode().ljust(32)[:32])
        cipher = Fernet(key)
        
        # Encrypt API key
        encrypted_key = cipher.encrypt(api_key.encode()).decode()
        
        # Save to database
        self.db.execute_update('''
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        ''', (f'ai_api_key_{provider}_{user_id}', encrypted_key))
        
        # Log audit
        self.db.log_audit(user_id, f"Configured AI provider: {provider}")
    
    def get_api_key(self, provider: str, user_id: int) -> Optional[str]:
        """Retrieve and decrypt API key"""
        from cryptography.fernet import Fernet
        import base64
        
        result = self.db.execute_query('''
            SELECT value FROM settings WHERE key = ?
        ''', (f'ai_api_key_{provider}_{user_id}',))
        
        if not result:
            return None
        
        encrypted_key = result[0]['value']
        
        try:
            # Generate decryption key
            key = base64.urlsafe_b64encode(str(user_id).encode().ljust(32)[:32])
            cipher = Fernet(key)
            
            # Decrypt
            api_key = cipher.decrypt(encrypted_key.encode()).decode()
            return api_key
        except:
            return None
    
    def is_ai_enabled(self, user_id: int) -> bool:
        """Check if AI is enabled for user"""
        providers = ['openai', 'claude', 'huggingface']
        
        for provider in providers:
            api_key = self.get_api_key(provider, user_id)
            if api_key:
                return True
        
        return False
    
    def get_ai_connector(self, user_id: int) -> AIConnector:
        """Get AI connector for user"""
        # Try each provider
        for provider in ['openai', 'claude', 'huggingface']:
            api_key = self.get_api_key(provider, user_id)
            if api_key:
                return AIConnector(api_key, provider)
        
        # Return disabled connector
        return AIConnector(None, 'openai')
    
    def delete_api_key(self, provider: str, user_id: int):
        """Delete API key"""
        self.db.execute_update('''
            DELETE FROM settings WHERE key = ?
        ''', (f'ai_api_key_{provider}_{user_id}',))
        
        self.db.log_audit(user_id, f"Removed AI provider: {provider}")