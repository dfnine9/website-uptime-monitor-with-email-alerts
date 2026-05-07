```python
"""
Bank Transaction Categorizer

A self-contained Python script that reads bank CSV files and categorizes transactions
based on configurable keyword matching. Supports multiple CSV formats through
configurable column mapping.

Features:
- Reads CSV files with flexible column mapping
- Categorizes transactions using keyword-based rules
- Handles multiple bank CSV formats
- Comprehensive error handling
- Configurable category rules
- Summary statistics and reporting

Usage: python script.py
"""

import csv
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'kroger', 'safeway', 'target', 'costco', 'grocery',
                'supermarket', 'food lion', 'publix', 'whole foods', 'trader joe',
                'aldi', 'wegmans', 'harris teeter', 'giant', 'shoprite'
            ],
            'dining': [
                'restaurant', 'mcdonald', 'burger', 'pizza', 'starbucks', 'dunkin',
                'subway', 'taco bell', 'kfc', 'chipotle', 'panera', 'cafe',
                'diner', 'bistro', 'grill', 'bar', 'pub', 'doordash', 'ubereats',
                'grubhub', 'seamless', 'takeout'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'internet', 'cable', 'phone',
                'verizon', 'at&t', 'comcast', 'xfinity', 'cox', 'spectrum',
                'utility', 'power', 'energy'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'metro', 'transit', 'parking',
                'toll', 'auto', 'car wash', 'repair', 'mechanic'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'hulu', 'disney',
                'movie', 'cinema', 'theater', 'concert', 'game', 'steam',
                'xbox', 'playstation', 'itunes', 'youtube'
            ],
            'shopping': [
                'amazon', 'ebay', 'paypal', 'shopping', 'mall', 'department',
                'clothing', 'fashion', 'electronics', 'best buy', 'home depot',
                'lowes', 'ikea'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'doctor', 'dentist', 'hospital',
                'medical', 'health', 'clinic', 'urgent care'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'interest', 'overdraft', 'transfer',
                'check', 'deposit', 'withdrawal'
            ]
        }
        
        self.column_mappings = {
            'chase': {
                'date': 'Transaction Date',
                'description': 'Description',
                'amount': 'Amount'
            },
            'bofa': {
                'date': 'Date',
                'description': 'Description',
                'amount': 'Amount'
            },
            'wells_fargo': {
                'date': 'Date',
                'description': 'Description',
                'amount': 'Amount'
            },
            'generic': {
                'date': 'date',
                'description': 'description',
                'amount': 'amount'
            }
        }

    def detect_csv_format(self, headers: List[str]) -> str:
        """Detect which bank format the CSV uses based on headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        for format_name, mapping in self.column_mappings.items():
            required_cols = set(mapping.values())
            if all(col.lower() in headers_lower for col in required_cols):
                return format_name
        
        # Try partial matches
        for format_name, mapping in self.column_mappings.items():
            matches = sum(1 for col in mapping.values() 
                         if any(col.lower() in h for h in headers_lower))
            if matches >= 2:  # At least 2 columns match
                return format_name
        
        return 'generic'

    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'other'

    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols and spaces
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0

    def read_csv_file(self, file_path: str) -> List[Dict]:
        """Read and parse CSV file with automatic format detection."""
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first line to detect format
                first_line = file.readline().strip()
                file.seek(0)
                
                # Try different delimiters
                delimiter = ','
                if '\t' in first_line:
                    delimiter = '\t'
                elif ';' in first_line:
                    delimiter = ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    raise ValueError("No headers found in CSV file")
                
                format_type = self.detect_csv_format(headers)
                print(f"Detected format: {format_type}")
                print(f"Headers: {headers}")
                
                mapping = self.column_mappings[format_type]
                
                # Find actual column names (case-insensitive)
                actual_columns = {}
                for field, expected_col in mapping.items():
                    for header in headers:
                        if expected_col.lower() in header.lower():
                            actual_columns[field] = header
                            break
                    
                    if field not in actual_columns:
                        # Try common alternatives
                        alternatives = {
                            'date': ['transaction date', 'trans date', 'posting date'],
                            'description': ['memo', 'payee', 'merchant', 'details'],
                            'amount': ['debit', 'credit', 'transaction amount']
                        }
                        
                        for alt in alternatives.get(field, []):
                            for header in headers:
                                if alt in header.lower():
                                    actual_columns[field] = header
                                    break
                            if field in actual_columns:
                                break
                
                print(f"Mapped columns: {actual_columns}")
                
                for row in reader:
                    try:
                        transaction = {
                            'date': row.get(actual_columns.get('date', ''), ''),
                            'description': row.get(actual_columns.get('description', ''), ''),
                            'amount': self.parse_amount(row.get(actual_columns.get('amount', ''), 0))
                        }
                        
                        if transaction['description']:  # Skip empty rows
                            transaction['category'] = self.categorize_transaction(transaction['description'])
                            transactions.append(transaction)
                            
                    except Exception as e:
                        print(