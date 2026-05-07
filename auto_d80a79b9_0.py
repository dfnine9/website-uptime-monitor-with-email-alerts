```python
#!/usr/bin/env python3
"""
Bank CSV Transaction Categorizer

This module parses bank CSV files from various formats, applies keyword-based
categorization rules to transactions, and validates data structure consistency.
Supports multiple bank formats and provides detailed categorization reporting.

Features:
- Auto-detects common bank CSV formats (Chase, Bank of America, Wells Fargo, etc.)
- Keyword-based transaction categorization (groceries, gas, restaurants, utilities)
- Data validation and format consistency checking
- Error handling for malformed files
- Detailed reporting and statistics

Usage: python script.py [csv_file_path]
If no file provided, uses sample data for demonstration.
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional, Tuple


class BankCSVParser:
    """Parses and categorizes bank CSV transactions with format validation."""
    
    def __init__(self):
        self.category_keywords = {
            'groceries': [
                'grocery', 'supermarket', 'kroger', 'safeway', 'whole foods',
                'trader joe', 'walmart', 'target', 'costco', 'sams club',
                'food lion', 'publix', 'wegmans', 'aldi', 'fresh market'
            ],
            'gas': [
                'gas', 'fuel', 'exxon', 'shell', 'chevron', 'bp', 'mobil',
                'texaco', 'citgo', 'speedway', 'wawa', 'sheetz', '76'
            ],
            'restaurants': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'pizza',
                'starbucks', 'dunkin', 'kfc', 'taco bell', 'chipotle',
                'panera', 'olive garden', 'applebee', 'chili', 'diner'
            ],
            'utilities': [
                'electric', 'gas company', 'water', 'sewer', 'internet',
                'cable', 'phone', 'verizon', 'att', 'comcast', 'xfinity',
                'duke energy', 'pge', 'con edison', 'national grid'
            ],
            'shopping': [
                'amazon', 'ebay', 'etsy', 'best buy', 'home depot', 'lowes',
                'macy', 'nordstrom', 'tj maxx', 'marshall', 'ross'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'movie', 'theater',
                'cinema', 'concert', 'ticket', 'entertainment'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'airline',
                'parking', 'toll', 'car rental'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital',
                'medical', 'dental', 'doctor', 'clinic'
            ],
            'banking': [
                'atm fee', 'overdraft', 'interest', 'transfer', 'check',
                'deposit', 'withdrawal', 'service charge'
            ]
        }
        
        self.bank_formats = {
            'chase': ['Date', 'Description', 'Amount', 'Balance'],
            'bofa': ['Date', 'Description', 'Amount', 'Running Bal.'],
            'wells_fargo': ['Date', 'Amount', 'Description', 'Balance'],
            'citi': ['Date', 'Description', 'Debit', 'Credit', 'Balance'],
            'generic': ['date', 'description', 'amount', 'balance']
        }
    
    def detect_format(self, headers: List[str]) -> str:
        """Detect bank format based on CSV headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        for bank, expected_headers in self.bank_formats.items():
            expected_lower = [h.lower() for h in expected_headers]
            if all(any(exp in header for header in headers_lower) 
                   for exp in expected_lower):
                return bank
        
        # Check for common variations
        if any('date' in h for h in headers_lower) and \
           any('description' in h or 'memo' in h for h in headers_lower) and \
           any('amount' in h or 'debit' in h or 'credit' in h for h in headers_lower):
            return 'generic'
        
        return 'unknown'
    
    def normalize_headers(self, headers: List[str], bank_format: str) -> Dict[str, int]:
        """Map headers to standard field names."""
        headers_lower = [h.lower().strip() for h in headers]
        field_mapping = {}
        
        # Date field
        for i, header in enumerate(headers_lower):
            if 'date' in header:
                field_mapping['date'] = i
                break
        
        # Description field
        for i, header in enumerate(headers_lower):
            if any(term in header for term in ['description', 'memo', 'payee']):
                field_mapping['description'] = i
                break
        
        # Amount fields
        for i, header in enumerate(headers_lower):
            if header in ['amount', 'debit', 'credit']:
                if 'debit' in header:
                    field_mapping['debit'] = i
                elif 'credit' in header:
                    field_mapping['credit'] = i
                else:
                    field_mapping['amount'] = i
        
        # Balance field
        for i, header in enumerate(headers_lower):
            if 'balance' in header or 'bal' in header:
                field_mapping['balance'] = i
                break
        
        return field_mapping
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return 0.0
        
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
        
        # Handle parentheses (negative amounts)
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format support."""
        if not date_str:
            return None
        
        date_formats = [
            '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y',
            '%m-%d-%Y', '%Y/%m/%d', '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords."""
        if not description:
            return 'uncategorized'
        
        description_lower = description.lower()
        
        for category, keywords in self.category_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'uncategorized'
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> List[str]:
        """Validate transaction data and return list of errors."""
        errors = []
        
        if not transaction.get('date'):
            errors.append("Missing or invalid date")
        
        if not transaction.get('description'):
            errors.append("Missing description")
        
        amount = transaction.get('amount', 0)
        if amount == 0 and not transaction.get('debit') and not transaction.get('credit