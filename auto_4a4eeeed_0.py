```python
"""
Bank Statement CSV Parser and Transaction Categorizer

This module parses CSV bank statements and categorizes transactions based on
keyword matching and regex patterns. It extracts transaction data including
date, amount, description, and balance, then automatically categorizes
expenses into common categories like groceries, utilities, entertainment, etc.

The script assumes CSV format with columns: Date, Description, Amount, Balance
but includes flexible parsing to handle various CSV formats.

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class TransactionCategorizer:
    """Categorizes bank transactions using keyword matching and regex patterns."""
    
    def __init__(self):
        self.categories = {
            'groceries': {
                'keywords': ['grocery', 'supermarket', 'walmart', 'target', 'safeway', 
                           'kroger', 'whole foods', 'trader joe', 'costco', 'food'],
                'patterns': [r'.*food.*', r'.*market.*', r'.*grocery.*']
            },
            'utilities': {
                'keywords': ['electric', 'gas', 'water', 'internet', 'phone', 'cable',
                           'utility', 'power', 'energy', 'telecom'],
                'patterns': [r'.*electric.*', r'.*gas company.*', r'.*water.*']
            },
            'entertainment': {
                'keywords': ['netflix', 'spotify', 'cinema', 'movie', 'theater',
                           'gaming', 'entertainment', 'streaming', 'music'],
                'patterns': [r'.*streaming.*', r'.*entertainment.*', r'.*movie.*']
            },
            'transportation': {
                'keywords': ['gas station', 'fuel', 'uber', 'lyft', 'taxi', 'bus',
                           'metro', 'parking', 'toll', 'car wash'],
                'patterns': [r'.*gas.*station.*', r'.*fuel.*', r'.*parking.*']
            },
            'dining': {
                'keywords': ['restaurant', 'cafe', 'coffee', 'pizza', 'fast food',
                           'doordash', 'ubereats', 'grubhub', 'dining'],
                'patterns': [r'.*restaurant.*', r'.*cafe.*', r'.*pizza.*']
            },
            'shopping': {
                'keywords': ['amazon', 'ebay', 'retail', 'store', 'mall', 'shopping',
                           'purchase', 'buy'],
                'patterns': [r'.*amazon.*', r'.*retail.*', r'.*store.*']
            },
            'healthcare': {
                'keywords': ['pharmacy', 'doctor', 'medical', 'hospital', 'clinic',
                           'health', 'dental', 'vision'],
                'patterns': [r'.*medical.*', r'.*pharmacy.*', r'.*doctor.*']
            },
            'banking': {
                'keywords': ['atm', 'fee', 'interest', 'transfer', 'deposit',
                           'withdrawal', 'bank'],
                'patterns': [r'.*atm.*', r'.*fee.*', r'.*interest.*']
            }
        }
    
    def categorize(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, rules in self.categories.items():
            # Check keywords
            for keyword in rules['keywords']:
                if keyword in description_lower:
                    return category
            
            # Check regex patterns
            for pattern in rules['patterns']:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        return 'other'


class BankStatementParser:
    """Parses CSV bank statements and extracts transaction data."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def detect_csv_format(self, file_path: str) -> Optional[Dict]:
        """Detect CSV format and column mappings."""
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                # Try different delimiters
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                try:
                    dialect = sniffer.sniff(sample)
                    delimiter = dialect.delimiter
                except:
                    delimiter = ','
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                
                # Common header variations
                header_mappings = {
                    'date': ['date', 'transaction date', 'posted date', 'trans date'],
                    'description': ['description', 'memo', 'transaction', 'details', 'payee'],
                    'amount': ['amount', 'debit', 'credit', 'transaction amount'],
                    'balance': ['balance', 'running balance', 'account balance']
                }
                
                column_map = {}
                headers_lower = [h.lower().strip() for h in headers]
                
                for field, possible_names in header_mappings.items():
                    for i, header in enumerate(headers_lower):
                        if any(name in header for name in possible_names):
                            column_map[field] = i
                            break
                
                return {
                    'delimiter': delimiter,
                    'headers': headers,
                    'column_map': column_map
                }
        
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str:
            return 0.0
        
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$£€¥,\s]', '', str(amount_str))
        
        # Handle parentheses for negative amounts
        if '(' in cleaned and ')' in cleaned:
            cleaned = '-' + cleaned.replace('(', '').replace(')', '')
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        
        # Common date formats
        formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_csv(self, file_path: str) -> List[Dict]:
        """Parse CSV file and extract transaction data."""
        format_info = self.detect_csv_format(file_path)
        if not format_info:
            raise ValueError("Could not detect CSV format")
        
        transactions = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=format_info['delimiter'])
                next(reader)  # Skip headers
                
                for row_num, row in enumerate(reader, 2):
                    if len(row) < len(format_info['column_map']):
                        continue
                    
                    try:
                        transaction = {}
                        
                        # Extract date
                        if 'date' in format_info['column_map']:
                            date_idx = format_info['column_map']['date']
                            transaction['date'] = self.parse_date(row[date_idx])
                        
                        # Extract description
                        if 'description' in format_info['column_map']:
                            desc_idx = format_info['column_map']['description']
                            transaction['description'] =