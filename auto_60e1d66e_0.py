```python
"""
Bank Statement Transaction Parser and Expense Categorizer

This module parses CSV bank statements and categorizes transactions based on predefined
keyword dictionaries. It extracts transaction data (date, description, amount) and
assigns expense categories like groceries, utilities, entertainment, etc.

Features:
- Parses various CSV formats commonly used by banks
- Automatic expense categorization using keyword matching
- Handles different date formats and amount representations
- Provides summary statistics by category
- Robust error handling for malformed data

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Handles transaction categorization using keyword matching."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'safeway', 'kroger', 'whole foods', 'trader joe',
                'costco', 'sams club', 'grocery', 'supermarket', 'market', 'food lion',
                'publix', 'wegmans', 'stop shop', 'giant', 'harris teeter'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'trash', 'garbage', 'power',
                'utility', 'pge', 'edison', 'verizon', 'att', 'comcast', 'xfinity',
                'internet', 'cable', 'phone', 'cellular', 'mobile'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'youtube',
                'movie', 'theater', 'cinema', 'concert', 'ticketmaster', 'stubhub',
                'gaming', 'steam', 'playstation', 'xbox', 'nintendo'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'chevron', 'bp', 'mobil', 'uber',
                'lyft', 'taxi', 'metro', 'bus', 'train', 'parking', 'toll',
                'dmv', 'registration', 'insurance', 'auto'
            ],
            'dining': [
                'restaurant', 'mcdonalds', 'burger king', 'subway', 'starbucks',
                'pizza', 'cafe', 'coffee', 'diner', 'bistro', 'grill', 'bar',
                'fast food', 'takeout', 'delivery', 'doordash', 'grubhub'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital', 'clinic',
                'doctor', 'medical', 'dental', 'vision', 'prescription', 'medicine'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes', 'macys',
                'nordstrom', 'tj maxx', 'marshall', 'outlet', 'mall', 'store'
            ],
            'finance': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'mortgage', 'credit card',
                'payment', 'transfer', 'deposit', 'withdrawal'
            ]
        }
    
    def categorize(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'other'


class BankStatementParser:
    """Parses CSV bank statements and extracts transaction data."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats."""
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m-%d-%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m/%d/%y',
            '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string, handling various formats."""
        try:
            # Remove currency symbols, commas, and extra whitespace
            clean_amount = re.sub(r'[$,\s]', '', amount_str.strip())
            
            # Handle negative amounts in parentheses
            if clean_amount.startswith('(') and clean_amount.endswith(')'):
                clean_amount = '-' + clean_amount[1:-1]
            
            return float(clean_amount)
        except (ValueError, AttributeError):
            return None
    
    def detect_csv_format(self, header: List[str]) -> Dict[str, int]:
        """Detect CSV format and return column mappings."""
        header_lower = [col.lower().strip() for col in header]
        mapping = {}
        
        # Common column name variations
        date_variants = ['date', 'transaction date', 'posted date', 'effective date']
        desc_variants = ['description', 'memo', 'payee', 'transaction description']
        amount_variants = ['amount', 'debit', 'credit', 'transaction amount']
        
        for i, col in enumerate(header_lower):
            if any(variant in col for variant in date_variants):
                mapping['date'] = i
            elif any(variant in col for variant in desc_variants):
                mapping['description'] = i
            elif any(variant in col for variant in amount_variants):
                if 'amount' not in mapping:
                    mapping['amount'] = i
                elif col in ['debit', 'credit'] and 'amount2' not in mapping:
                    mapping['amount2'] = i
        
        return mapping
    
    def parse_csv(self, file_path: str) -> List[Dict]:
        """Parse CSV file and extract transactions."""
        transactions = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.reader(csvfile, delimiter=delimiter)
                
                # Read header
                header = next(reader)
                column_mapping = self.detect_csv_format(header)
                
                if not all(key in column_mapping for key in ['date', 'description']):
                    raise ValueError("Could not detect required columns (date, description)")
                
                print(f"Detected columns: {column_mapping}")
                print(f"Processing transactions...")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) < max(column_mapping.values()) + 1:
                            continue
                        
                        # Extract data
                        date_str = row[column_mapping['date']]
                        description = row[column_mapping['description']]
                        
                        # Handle amount (might be in one or two columns)
                        amount = None
                        if 'amount' in column_mapping:
                            amount = self.parse_amount(row[column_mapping['amount']])
                        elif 'amount2' in column_mapping:
                            # Handle debit/credit columns
                            debit = self.parse_amount(row[column_mapping['amount']]) or 0
                            credit = self.parse_amount(row[column_mapping['amount2']]) or