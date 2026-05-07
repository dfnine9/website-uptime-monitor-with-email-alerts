```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statement files and automatically categorizes transactions
based on merchant names and description patterns. It uses predefined rules to classify
transactions into categories like groceries, gas, restaurants, utilities, etc.

Features:
- Supports common CSV formats from major banks
- Configurable categorization rules based on merchant patterns
- Handles various date formats automatically
- Provides transaction summaries by category
- Error handling for malformed data

Usage: python script.py [csv_file_path]
If no file is provided, it will look for 'bank_statement.csv' in current directory.
"""

import csv
import re
import sys
import os
from datetime import datetime
from collections import defaultdict
import argparse


class TransactionCategorizer:
    def __init__(self):
        # Define categorization rules - merchant patterns mapped to categories
        self.category_patterns = {
            'Groceries': [
                r'walmart', r'kroger', r'safeway', r'publix', r'whole foods',
                r'trader joe', r'aldi', r'costco', r'sam\'s club', r'grocery',
                r'food lion', r'harris teeter', r'wegmans', r'giant eagle'
            ],
            'Gas/Fuel': [
                r'shell', r'exxon', r'bp', r'chevron', r'mobil', r'sunoco',
                r'wawa', r'speedway', r'marathon', r'citgo', r'fuel', r'gas station'
            ],
            'Restaurants': [
                r'mcdonald', r'burger king', r'subway', r'starbucks', r'pizza',
                r'restaurant', r'cafe', r'diner', r'grill', r'bar & grill',
                r'taco bell', r'kfc', r'wendy', r'chick-fil-a', r'domino'
            ],
            'Utilities': [
                r'electric', r'power', r'water', r'gas company', r'utility',
                r'verizon', r'at&t', r'comcast', r'spectrum', r'internet',
                r'phone', r'cable', r'trash', r'waste management'
            ],
            'Transportation': [
                r'uber', r'lyft', r'taxi', r'metro', r'bus', r'train',
                r'parking', r'toll', r'car wash', r'auto repair'
            ],
            'Shopping': [
                r'amazon', r'target', r'best buy', r'home depot', r'lowes',
                r'macy', r'kohls', r'tj maxx', r'marshall', r'ross',
                r'walmart.com', r'ebay', r'etsy'
            ],
            'Healthcare': [
                r'pharmacy', r'cvs', r'walgreens', r'rite aid', r'hospital',
                r'medical', r'doctor', r'dental', r'clinic', r'health'
            ],
            'Banking/Finance': [
                r'bank fee', r'atm fee', r'interest', r'dividend', r'transfer',
                r'check fee', r'overdraft', r'maintenance fee'
            ],
            'Entertainment': [
                r'netflix', r'spotify', r'hulu', r'disney', r'movie',
                r'theater', r'cinema', r'gym', r'fitness', r'subscription'
            ]
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]

    def categorize_transaction(self, description, merchant=None):
        """Categorize a transaction based on description and merchant name."""
        text_to_check = f"{description} {merchant or ''}".lower()
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text_to_check):
                    return category
        
        return 'Other'

    def parse_date(self, date_string):
        """Parse various date formats commonly found in bank statements."""
        date_formats = [
            '%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y',
            '%m/%d/%y', '%y-%m-%d', '%d/%m/%y', '%m-%d-%y',
            '%B %d, %Y', '%b %d, %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue
        
        # If no format matches, return None
        return None

    def detect_csv_structure(self, file_path):
        """Detect the structure of the CSV file and identify relevant columns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first few lines to detect structure
                sample = file.read(1024)
                file.seek(0)
                
                # Try different delimiters
                delimiter = ','
                if sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                elif sample.count(';') > sample.count(','):
                    delimiter = ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = [h.lower().strip() for h in reader.fieldnames]
                
                # Map common header variations to standard names
                column_map = {
                    'date': ['date', 'transaction date', 'posted date', 'trans date'],
                    'description': ['description', 'merchant', 'payee', 'memo', 'reference'],
                    'amount': ['amount', 'debit', 'credit', 'transaction amount', 'charge amount'],
                    'balance': ['balance', 'running balance', 'account balance']
                }
                
                detected_columns = {}
                for standard_name, variations in column_map.items():
                    for variation in variations:
                        if variation in headers:
                            detected_columns[standard_name] = variation
                            break
                
                return delimiter, detected_columns
                
        except Exception as e:
            print(f"Error detecting CSV structure: {e}")
            return ',', {}

    def parse_csv_file(self, file_path):
        """Parse the CSV file and extract transactions."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        delimiter, columns = self.detect_csv_structure(file_path)
        
        if not columns:
            print("Warning: Could not auto-detect column structure. Using default mapping.")
            # Default column indices (common format)
            columns = {'date': 0, 'description': 1, 'amount': 2}
            use_indices = True
        else:
            use_indices = False
        
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                if use_indices:
                    reader = csv.reader(file, delimiter=delimiter)
                    next(reader)  # Skip header
                    
                    for row_num, row in enumerate(reader, start=2):
                        try:
                            if len(row) < 3:
                                continue
                                
                            date_str = row[0].strip()
                            description = row[1].strip()
                            amount_str = row[2].strip()
                            
                            # Parse amount
                            amount_clean = re.sub(r'[^\d\.\-\+]', '', amount_str)
                            if amount_clean:
                                amount = float(amount_clean)
                            else:
                                continue
                            
                            # Parse date
                            date_obj = self.parse_date(date_str)
                            if not date_obj:
                                print(f"Warning: Could not parse date '{date_str}' on row {row_num}")
                                continue
                            
                            transactions.append({