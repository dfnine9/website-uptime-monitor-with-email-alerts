```python
#!/usr/bin/env python3
"""
Bank Transaction Categorization System

This module reads CSV files from multiple bank formats, parses transaction data
(date, description, amount, balance), and automatically categorizes expenses
using keyword matching dictionaries and spending amount heuristics.

Supports common banking CSV formats and categorizes transactions into:
- Groceries, Utilities, Entertainment, Transportation, Shopping, Dining, etc.

Usage: python script.py
"""

import csv
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import glob

class TransactionCategorizer:
    """Categorizes bank transactions using keyword matching and amount heuristics."""
    
    def __init__(self):
        self.category_keywords = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'publix', 'whole foods',
                'trader joe', 'costco', 'sam\'s club', 'grocery', 'supermarket',
                'food lion', 'giant', 'wegmans', 'harris teeter', 'aldi'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'internet', 'phone',
                'verizon', 'at&t', 'comcast', 'xfinity', 'duke energy',
                'pge', 'utility', 'cable', 'trash', 'waste management'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime',
                'movie', 'theater', 'cinema', 'concert', 'ticket',
                'gaming', 'steam', 'xbox', 'playstation', 'entertainment'
            ],
            'transportation': [
                'gas station', 'shell', 'bp', 'exxon', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'parking', 'toll', 'metro',
                'bus', 'train', 'airline', 'car wash', 'auto repair'
            ],
            'dining': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'starbucks',
                'pizza', 'taco bell', 'kfc', 'wendy', 'chipotle',
                'panera', 'dunkin', 'cafe', 'bar', 'grill'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowe\'s',
                'macy', 'nordstrom', 'tj maxx', 'marshall', 'clothing',
                'department store', 'retail', 'mall'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'doctor',
                'medical', 'hospital', 'clinic', 'dentist', 'health'
            ],
            'banking': [
                'atm', 'fee', 'interest', 'transfer', 'deposit',
                'withdrawal', 'overdraft', 'maintenance'
            ]
        }
        
        self.amount_heuristics = {
            'groceries': (20, 300),
            'utilities': (50, 400),
            'dining': (5, 100),
            'transportation': (10, 150),
            'entertainment': (5, 200),
            'shopping': (20, 500)
        }

class BankCSVParser:
    """Parses CSV files from multiple bank formats."""
    
    def __init__(self):
        self.common_date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%d/%m/%Y',
            '%m/%d/%y', '%m-%d-%y', '%y-%m-%d', '%d-%m-%Y'
        ]
        
        self.common_headers = {
            'date': ['date', 'transaction date', 'posted date', 'trans date'],
            'description': ['description', 'memo', 'transaction', 'merchant'],
            'amount': ['amount', 'debit', 'credit', 'transaction amount'],
            'balance': ['balance', 'running balance', 'account balance']
        }

    def detect_csv_format(self, filepath: str) -> Dict:
        """Detect the CSV format and column mapping."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.DictReader(f, delimiter=delimiter)
                headers = [h.lower().strip() for h in reader.fieldnames or []]
                
                # Map headers to standard fields
                field_mapping = {}
                for standard_field, possible_names in self.common_headers.items():
                    for header in headers:
                        for possible_name in possible_names:
                            if possible_name in header:
                                field_mapping[standard_field] = reader.fieldnames[headers.index(header)]
                                break
                        if standard_field in field_mapping:
                            break
                
                return {
                    'delimiter': delimiter,
                    'headers': reader.fieldnames,
                    'mapping': field_mapping
                }
        except Exception as e:
            print(f"Error detecting CSV format for {filepath}: {e}")
            return {}

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string using common formats."""
        date_str = date_str.strip()
        for fmt in self.common_date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        try:
            # Remove currency symbols and spaces
            cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0

    def read_transactions(self, filepath: str) -> List[Dict]:
        """Read and parse transactions from CSV file."""
        transactions = []
        
        try:
            csv_format = self.detect_csv_format(filepath)
            if not csv_format or not csv_format.get('mapping'):
                print(f"Could not detect format for {filepath}")
                return transactions
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f, delimiter=csv_format['delimiter'])
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        transaction = {}
                        mapping = csv_format['mapping']
                        
                        # Extract date
                        if 'date' in mapping:
                            date_obj = self.parse_date(row[mapping['date']])
                            transaction['date'] = date_obj
                            transaction['date_str'] = row[mapping['date']]
                        
                        # Extract description
                        if 'description' in mapping:
                            transaction['description'] = row[mapping['description']].strip()
                        
                        # Extract amount
                        if 'amount' in mapping:
                            transaction['amount'] = self.parse_amount(row[mapping['amount']])
                        
                        # Extract balance
                        if 'balance' in mapping:
                            transaction['balance'] = self.parse_amount(row[mapping['balance']])
                        
                        transaction['source_file'] = os.path.basename(filepath)
                        
                        if transaction.get('date') and transaction.get('