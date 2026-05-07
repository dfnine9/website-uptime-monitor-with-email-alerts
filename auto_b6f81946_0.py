```python
"""
Bank CSV Transaction Categorizer and Analyzer

This module parses bank CSV files, categorizes transactions using keyword matching,
calculates monthly spending totals by category, and exports summary statistics to JSON.

Features:
- Automatic transaction categorization based on description keywords
- Monthly spending analysis by category
- JSON export of summary statistics
- Error handling for file operations and data processing
- Support for common CSV formats with configurable columns

Usage:
    python script.py

The script will look for CSV files in the current directory and process them automatically.
Results are printed to stdout and saved to 'transaction_summary.json'.
"""

import csv
import json
import re
from datetime import datetime
from collections import defaultdict, Counter
import os
import sys
from typing import Dict, List, Tuple, Any


class TransactionCategorizer:
    """Handles transaction categorization using keyword matching."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sams club', 'grocery', 'supermarket', 'food lion',
                'publix', 'wegmans', 'harris teeter', 'giant', 'shoprite'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'internet', 'cable',
                'phone', 'utility', 'power', 'energy', 'comcast', 'verizon',
                'att', 'spectrum', 'xfinity', 'trash', 'waste'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'movie',
                'cinema', 'theater', 'concert', 'game', 'entertainment',
                'streaming', 'youtube', 'apple music', 'paramount'
            ],
            'restaurants': [
                'restaurant', 'mcdonald', 'burger', 'pizza', 'starbucks',
                'dunkin', 'subway', 'taco bell', 'kfc', 'wendys', 'chipotle',
                'panera', 'dominos', 'papa johns', 'dining', 'cafe'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'parking',
                'toll', 'auto', 'car wash', 'repair'
            ],
            'shopping': [
                'amazon', 'ebay', 'bestbuy', 'home depot', 'lowes', 'macys',
                'nordstrom', 'gap', 'old navy', 'tj maxx', 'marshalls',
                'clothing', 'apparel', 'shoes', 'electronics'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital',
                'clinic', 'doctor', 'medical', 'dental', 'vision',
                'health', 'prescription', 'medicare', 'insurance'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'interest', 'transfer', 'deposit',
                'withdrawal', 'overdraft', 'maintenance', 'service charge'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class BankCSVParser:
    """Parses bank CSV files and extracts transaction data."""
    
    def __init__(self):
        self.common_date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
        
        self.common_column_names = {
            'date': ['date', 'transaction date', 'posted date', 'trans date'],
            'description': ['description', 'memo', 'payee', 'merchant', 'details'],
            'amount': ['amount', 'debit', 'credit', 'transaction amount', 'value']
        }
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse date string using common formats."""
        date_str = date_str.strip()
        
        for fmt in self.common_date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string, handling various formats."""
        # Remove currency symbols and whitespace
        amount_str = re.sub(r'[$,\s]', '', amount_str.strip())
        
        # Handle negative amounts in parentheses
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            return float(amount_str)
        except ValueError:
            raise ValueError(f"Unable to parse amount: {amount_str}")
    
    def detect_columns(self, header: List[str]) -> Dict[str, int]:
        """Detect relevant columns in CSV header."""
        header_lower = [col.lower().strip() for col in header]
        columns = {}
        
        for field, possible_names in self.common_column_names.items():
            for i, col_name in enumerate(header_lower):
                if any(name in col_name for name in possible_names):
                    columns[field] = i
                    break
        
        required_fields = ['date', 'description', 'amount']
        missing_fields = [field for field in required_fields if field not in columns]
        
        if missing_fields:
            raise ValueError(f"Could not detect columns: {missing_fields}")
        
        return columns
    
    def parse_csv_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse a CSV file and return transaction data."""
        transactions = []
        
        with open(filepath, 'r', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            delimiter = ','
            if sample.count(';') > sample.count(','):
                delimiter = ';'
            elif sample.count('\t') > sample.count(','):
                delimiter = '\t'
            
            reader = csv.reader(file, delimiter=delimiter)
            header = next(reader)
            
            try:
                columns = self.detect_columns(header)
            except ValueError as e:
                print(f"Warning: {e} in file {filepath}")
                return transactions
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    if len(row) <= max(columns.values()):
                        continue
                    
                    date_obj = self.parse_date(row[columns['date']])
                    description = row[columns['description']].strip()
                    amount = self.parse_amount(row[columns['amount']])
                    
                    transactions.append({
                        'date': date_obj,
                        'description': description,
                        'amount': amount,
                        'source_file': filepath
                    })
                    
                except (ValueError, IndexError) as e:
                    print(f"Warning: Skipping row {row_num} in {filepath}: {e}")
                    continue
        
        return transactions


class TransactionAnalyzer:
    """Analyzes transaction data and generates reports."""
    
    def __init__(self, categorizer: TransactionCategorizer):