```python
"""
Bank Transaction Categorizer

A self-contained Python script that parses CSV bank transaction files and automatically
categorizes transactions using rule-based keyword matching. Supports common expense
categories including groceries, utilities, entertainment, transport, dining, and shopping.

Features:
- Automatic CSV format detection and parsing
- Rule-based categorization using keyword matching
- Comprehensive error handling
- Detailed transaction reporting
- Summary statistics by category

Usage:
    python script.py [csv_file_path]
    
If no file path is provided, the script will look for 'transactions.csv' in the current directory.
"""

import csv
import sys
import os
import re
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple, Optional


class TransactionCategorizer:
    """Main class for parsing and categorizing bank transactions."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway',
                'whole foods', 'trader joe', 'costco', 'sam\'s club', 'food lion',
                'publix', 'wegmans', 'aldi', 'fresh market', 'market', 'deli'
            ],
            'utilities': [
                'electric', 'electricity', 'gas', 'water', 'sewer', 'internet',
                'cable', 'phone', 'cellular', 'verizon', 'at&t', 'comcast',
                'utility', 'power', 'energy', 'trash', 'waste management'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'disney', 'hulu', 'movie',
                'theater', 'cinema', 'concert', 'spotify', 'apple music',
                'youtube', 'gaming', 'entertainment', 'streaming'
            ],
            'transport': [
                'gas station', 'fuel', 'shell', 'exxon', 'chevron', 'bp',
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'parking',
                'toll', 'car wash', 'auto', 'vehicle', 'dmv'
            ],
            'dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'dunkin', 'mcdonald',
                'burger', 'pizza', 'subway', 'chipotle', 'panera', 'dining',
                'bar', 'pub', 'food delivery', 'doordash', 'uber eats', 'grubhub'
            ],
            'shopping': [
                'amazon', 'ebay', 'shop', 'store', 'retail', 'clothing',
                'apparel', 'shoes', 'electronics', 'best buy', 'home depot',
                'lowes', 'department store', 'mall', 'boutique'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'medical', 'doctor',
                'dentist', 'clinic', 'health', 'prescription', 'medicine'
            ],
            'banking': [
                'atm', 'fee', 'interest', 'transfer', 'deposit', 'withdrawal',
                'overdraft', 'maintenance', 'service charge'
            ],
            'insurance': [
                'insurance', 'premium', 'policy', 'coverage', 'claim'
            ]
        }
    
    def detect_csv_format(self, file_path: str) -> Optional[Dict[str, int]]:
        """
        Detect the CSV format by analyzing the header row.
        Returns a mapping of field types to column indices.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try different delimiters
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.reader(file, delimiter=delimiter)
                header = next(reader, None)
                
                if not header:
                    return None
                
                # Normalize headers for matching
                normalized_headers = [h.lower().strip() for h in header]
                
                field_mapping = {}
                
                # Date field detection
                date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
                for i, h in enumerate(normalized_headers):
                    if any(pattern in h for pattern in date_patterns):
                        field_mapping['date'] = i
                        break
                
                # Description field detection
                desc_patterns = ['description', 'memo', 'payee', 'merchant', 'details']
                for i, h in enumerate(normalized_headers):
                    if any(pattern in h for pattern in desc_patterns):
                        field_mapping['description'] = i
                        break
                
                # Amount field detection
                amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
                for i, h in enumerate(normalized_headers):
                    if any(pattern in h for pattern in amount_patterns):
                        field_mapping['amount'] = i
                        break
                
                # If we found all three required fields, return the mapping
                if len(field_mapping) >= 3:
                    field_mapping['delimiter'] = delimiter
                    return field_mapping
                
                return None
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats."""
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y',
            '%m-%d-%y', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y'
        ]
        
        date_str = date_str.strip()
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string and return float value."""
        try:
            # Remove currency symbols, commas, and spaces
            cleaned = re.sub(r'[\$,\s]', '', amount_str.strip())
            
            # Handle parentheses for negative values
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'uncategorized'
    
    def parse_csv_file(self, file_path: str) -> List[Dict]:
        """Parse CSV file and extract transaction data."""
        transactions = []
        
        # Detect CSV format
        field_mapping = self.detect_csv_format(file_path)
        if not field_mapping:
            raise ValueError("Could not detect CSV format or missing required columns")
        
        delimiter = field_mapping.pop('delimiter', ',')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=delimiter)
                header = next(reader, None)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(field_mapping.values()):
                            continue
                        
                        # Extract fields
                        date_str = row[field_mapping['date