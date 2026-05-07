```python
"""
Bank Transaction Categorizer

A self-contained Python script that reads bank CSV files and automatically categorizes
transactions based on configurable keyword matching. Supports flexible column mapping
to accommodate different bank CSV formats.

Features:
- Configurable column mapping for different bank CSV formats
- Keyword-based categorization with predefined dictionaries
- Comprehensive error handling
- Transaction summary reporting
- No external dependencies beyond Python standard library

Usage: python script.py
"""

import csv
import re
import os
from collections import defaultdict
from typing import Dict, List, Tuple, Any


class TransactionCategorizer:
    """Categorizes bank transactions based on keyword matching."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'publix', 'wegmans', 'harris teeter',
                'food lion', 'giant', 'stop shop', 'aldi', 'grocery', 'supermarket',
                'market', 'fresh market', 'organic'
            ],
            'utilities': [
                'electric', 'electricity', 'gas company', 'water', 'sewer',
                'internet', 'cable', 'phone', 'cellular', 'verizon', 'at&t',
                'comcast', 'xfinity', 'spectrum', 'cox', 'utility', 'power',
                'energy', 'telecom'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'hbo',
                'movie', 'theater', 'cinema', 'concert', 'show', 'entertainment',
                'gaming', 'steam', 'playstation', 'xbox', 'nintendo', 'music',
                'streaming', 'subscription'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'bus', 'train', 'subway', 'metro',
                'parking', 'toll', 'car wash', 'auto', 'vehicle', 'transportation',
                'fuel', 'gasoline'
            ],
            'dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'dunkin', 'mcdonald',
                'burger king', 'subway', 'pizza', 'taco bell', 'kfc', 'wendy',
                'chipotle', 'panera', 'dining', 'food delivery', 'grubhub',
                'doordash', 'uber eats'
            ],
            'shopping': [
                'amazon', 'ebay', 'clothing', 'department store', 'mall',
                'retail', 'online', 'purchase', 'buy', 'shopping', 'store'
            ],
            'healthcare': [
                'doctor', 'hospital', 'pharmacy', 'medical', 'health',
                'dental', 'vision', 'insurance', 'cvs', 'walgreens', 'clinic'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'transfer', 'deposit', 'withdrawal',
                'interest', 'overdraft', 'maintenance'
            ]
        }
        
        self.column_mappings = {
            'standard': {
                'date': ['date', 'transaction_date', 'posting_date'],
                'description': ['description', 'memo', 'details', 'transaction_details'],
                'amount': ['amount', 'transaction_amount', 'value'],
                'balance': ['balance', 'running_balance', 'account_balance']
            },
            'chase': {
                'date': ['Transaction Date', 'Post Date'],
                'description': ['Description'],
                'amount': ['Amount'],
                'balance': ['Balance']
            },
            'bank_of_america': {
                'date': ['Date'],
                'description': ['Description'],
                'amount': ['Amount'],
                'balance': ['Running Bal.']
            },
            'wells_fargo': {
                'date': ['Date'],
                'description': ['Description'],
                'amount': ['Amount'],
                'balance': ['Balance']
            }
        }
    
    def detect_column_mapping(self, headers: List[str]) -> Dict[str, str]:
        """Auto-detect column mapping based on CSV headers."""
        mapping = {}
        headers_lower = [h.lower().strip() for h in headers]
        
        # Try each mapping configuration
        for config_name, config in self.column_mappings.items():
            score = 0
            temp_mapping = {}
            
            for field_type, possible_names in config.items():
                for possible_name in possible_names:
                    if possible_name.lower() in headers_lower:
                        temp_mapping[field_type] = headers[headers_lower.index(possible_name.lower())]
                        score += 1
                        break
                    elif possible_name in headers:
                        temp_mapping[field_type] = possible_name
                        score += 1
                        break
            
            if score >= 3:  # Need at least date, description, and amount
                mapping = temp_mapping
                break
        
        # If no predefined mapping works, try intelligent matching
        if not mapping:
            for header in headers:
                header_lower = header.lower()
                if any(date_word in header_lower for date_word in ['date', 'time']):
                    mapping['date'] = header
                elif any(desc_word in header_lower for desc_word in ['description', 'memo', 'detail', 'transaction']):
                    mapping['description'] = header
                elif any(amt_word in header_lower for amt_word in ['amount', 'value', 'total']):
                    mapping['amount'] = header
                elif any(bal_word in header_lower for bal_word in ['balance', 'bal']):
                    mapping['balance'] = header
        
        return mapping
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        if not description:
            return 'other'
        
        description_lower = description.lower()
        
        # Check each category for keyword matches
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return 0.0
        
        try:
            # Remove currency symbols, commas, and extra whitespace
            cleaned = re.sub(r'[^\d\.-]', '', str(amount_str))
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def read_csv_file(self, filepath: str) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Read CSV file and return transactions with detected column mapping."""
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    raise ValueError("No headers found in CSV file")
                
                # Detect column mapping
                column_mapping = self.detect_column_mapping(headers)
                
                if not column_mapping.get('date') or not column_mapping.get('description'):
                    raise ValueError