import re
from typing import List

class TextProcessor:
    """Component for text preprocessing"""
    
    def __init__(self):
        self.phone_pattern = r'\+\d{1,3}-\d{6,14}'
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize input text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize phone numbers
        text = self._normalize_phone_numbers(text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s\+\-]', '', text)
        
        return text.strip()
    
    def _normalize_phone_numbers(self, text: str) -> str:
        """Normalize phone numbers to standard format"""
        def replace_number(match):
            number = match.group(0)
            # Ensure format: +XX-XXXXXXXXXX
            return re.sub(r'[\s\-\(\)]', '-', number)
            
        return re.sub(self.phone_pattern, replace_number, text) 