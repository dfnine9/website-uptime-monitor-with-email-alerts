```python
#!/usr/bin/env python3
"""
Bank CSV Parser

This module parses CSV exports from multiple bank formats and standardizes
transaction data into a consistent structure. Supports common formats from
major banks including Chase, Bank of America, Wells Fargo, and Citi.

The standardized output includes:
- date: Transaction date (YYYY-MM-DD format)
- amount: Transaction amount (float, negative for debits)
- description: Transaction description
- merchant: Extracted merchant name (when identifiable)

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from io import StringIO


class BankCSVParser:
    """Parser for standardizing bank CSV transaction exports."""
    
    def __init__(self):
        self.bank_formats = {
            'chase': {
                'date_col': ['Transaction Date', 'Date'],
                'amount_col': ['Amount'],
                'description_col': ['Description'],
                'date_format': ['%m/%d/%Y', '%Y-%m-%d']
            },
            'bofa': {
                'date_col': ['Date', 'Posted Date'],
                'amount_col': ['Amount'],
                'description_col': ['Description', 'Payee'],
                'date_format': ['%m/%d/%Y', '%Y-%m-%d']
            },
            'wells_fargo': {
                'date_col': ['Date'],
                'amount_col': ['Amount'],
                'description_col': ['Description', 'Memo'],
                'date_format': ['%m/%d/%Y', '%Y-%m-%d']
            },
            'citi': {
                'date_col': ['Date'],
                'amount_col': ['Debit', 'Credit'],
                'description_col': ['Description'],
                'date_format': ['%m/%d/%Y', '%Y-%m-%d']
            }
        }
    
    def detect_bank_format(self, headers: List[str]) -> Optional[str]:
        """Detect bank format based on CSV headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Chase detection
        if any('transaction date' in h for h in headers_lower):
            return 'chase'
        
        # Bank of America detection
        if any('posted date' in h for h in headers_lower):
            return 'bofa'
        
        # Wells Fargo detection
        if 'date' in headers_lower and 'memo' in headers_lower:
            return 'wells_fargo'
        
        # Citi detection
        if 'debit' in headers_lower and 'credit' in headers_lower:
            return 'citi'
        
        # Generic format fallback
        if 'date' in headers_lower and 'amount' in headers_lower:
            return 'generic'
        
        return None
    
    def find_column_index(self, headers: List[str], possible_names: List[str]) -> Optional[int]:
        """Find column index by matching possible column names."""
        headers_lower = [h.lower().strip() for h in headers]
        
        for name in possible_names:
            name_lower = name.lower()
            for i, header in enumerate(headers_lower):
                if name_lower == header or name_lower in header:
                    return i
        return None
    
    def parse_date(self, date_str: str, formats: List[str]) -> Optional[str]:
        """Parse date string using multiple format attempts."""
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Try additional common formats
        additional_formats = ['%m-%d-%Y', '%d/%m/%Y', '%Y/%m/%d']
        for fmt in additional_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def parse_amount(self, amount_str: str, is_debit: bool = False) -> Optional[float]:
        """Parse amount string to float."""
        if not amount_str or not str(amount_str).strip():
            return None
        
        amount_str = str(amount_str).strip()
        
        # Remove currency symbols and commas
        amount_str = re.sub(r'[\$,]', '', amount_str)
        
        # Handle parentheses as negative
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            amount = float(amount_str)
            # For debit columns, make positive amounts negative
            if is_debit and amount > 0:
                amount = -amount
            return amount
        except ValueError:
            return None
    
    def extract_merchant(self, description: str) -> Optional[str]:
        """Extract merchant name from transaction description."""
        if not description:
            return None
        
        description = description.strip()
        
        # Common patterns for merchant extraction
        patterns = [
            r'^([A-Z\s&]+)\s+\d+',  # Merchant name followed by numbers
            r'^([A-Z][A-Za-z\s&]+?)\s+[-#]',  # Merchant name followed by dash or hash
            r'^([A-Z][A-Za-z\s&]{3,})',  # Capitalized words at start
        ]
        
        for pattern in patterns:
            match = re.match(pattern, description)
            if match:
                merchant = match.group(1).strip()
                # Clean up common suffixes
                merchant = re.sub(r'\s+(INC|LLC|CORP|CO)$', '', merchant)
                if len(merchant) > 3:
                    return merchant
        
        # Fallback: return first few words if they look like a merchant
        words = description.split()[:3]
        if words and len(' '.join(words)) > 3:
            return ' '.join(words)
        
        return None
    
    def parse_csv_content(self, csv_content: str) -> List[Dict[str, Any]]:
        """Parse CSV content and return standardized transactions."""
        try:
            # Try to detect delimiter
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(csv_content[:1024]).delimiter
        except:
            delimiter = ','
        
        lines = csv_content.strip().split('\n')
        if not lines:
            return []
        
        reader = csv.reader(StringIO(csv_content), delimiter=delimiter)
        
        try:
            headers = next(reader)
            headers = [h.strip() for h in headers]
        except StopIteration:
            return []
        
        bank_format = self.detect_bank_format(headers)
        if not bank_format:
            print(f"Warning: Could not detect bank format. Headers: {headers}", file=sys.stderr)
            return []
        
        print(f"Detected bank format: {bank_format}")
        
        # Get format configuration
        if bank_format == 'generic':
            format_config = {
                'date_col': ['Date', 'Transaction Date'],
                'amount_col': ['Amount'],
                'description_col': ['Description', 'Memo', 'Payee'],
                'date_format': ['%m/%d/%Y', '%Y-%m-%d']
            }
        else:
            format_config = self.bank_formats[bank_format]
        
        # Find column indices
        date_idx = self.find_column_index(headers, format_config['date_col'])
        description_idx = self.find_column_index(headers, format_config['description_col'])
        
        # Handle amount columns (some banks have separate debit/credit)
        amount_idx = None