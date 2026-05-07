```python
"""
Bank Transaction Parser and Categorizer

This module parses bank CSV exports and automatically categorizes transactions
using keyword-based rules. It extracts transaction data (date, description, amount)
and assigns categories like groceries, gas, utilities, dining, and entertainment.

Usage: python script.py

The script will look for CSV files in the current directory and process them.
Results are printed to stdout showing categorized transactions and summaries.
"""

import csv
import os
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions using keyword-based rules."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'publix', 'whole foods',
                'trader joe', 'costco', 'sams club', 'aldi', 'food lion',
                'grocery', 'market', 'supermarket', 'food store'
            ],
            'gas': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'texaco', 'citgo',
                'marathon', 'sunoco', 'gas station', 'fuel', 'petro'
            ],
            'utilities': [
                'electric', 'electricity', 'power', 'gas company', 'water',
                'sewer', 'internet', 'cable', 'phone', 'wireless', 'verizon',
                'att', 'comcast', 'xfinity', 'utility', 'pge', 'con ed'
            ],
            'dining': [
                'restaurant', 'mcdonalds', 'burger king', 'subway', 'pizza',
                'starbucks', 'dunkin', 'kfc', 'taco bell', 'chipotle',
                'panera', 'olive garden', 'applebees', 'chilis', 'dining',
                'cafe', 'bistro', 'grill', 'bar', 'pub'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime',
                'movie', 'theater', 'cinema', 'concert', 'show', 'ticket',
                'gaming', 'steam', 'xbox', 'playstation', 'entertainment'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes',
                'macy', 'nordstrom', 'gap', 'old navy', 'tj maxx',
                'marshall', 'store', 'shop', 'retail'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital',
                'medical', 'doctor', 'dentist', 'clinic', 'health'
            ],
            'transport': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'transit',
                'parking', 'toll', 'airline', 'flight'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'interest', 'transfer', 'deposit',
                'withdrawal', 'overdraft', 'maintenance'
            ]
        }
    
    def categorize(self, description: str) -> str:
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
        self.categorizer = TransactionCategorizer()
    
    def detect_csv_format(self, file_path: str) -> Optional[Dict[str, int]]:
        """Detect the CSV format by analyzing headers."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                # Common delimiters
                delimiters = [',', ';', '\t']
                delimiter = ','
                
                for delim in delimiters:
                    if sample.count(delim) > sample.count(delimiter):
                        delimiter = delim
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                
                # Normalize headers for matching
                normalized_headers = [h.lower().strip() for h in headers]
                
                # Map common header variations to our expected fields
                field_mapping = {}
                
                # Date field variations
                date_patterns = ['date', 'transaction date', 'posted date', 'effective date']
                for i, header in enumerate(normalized_headers):
                    for pattern in date_patterns:
                        if pattern in header:
                            field_mapping['date'] = i
                            break
                
                # Description field variations
                desc_patterns = ['description', 'memo', 'detail', 'transaction', 'merchant']
                for i, header in enumerate(normalized_headers):
                    for pattern in desc_patterns:
                        if pattern in header:
                            field_mapping['description'] = i
                            break
                
                # Amount field variations
                amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
                for i, header in enumerate(normalized_headers):
                    for pattern in amount_patterns:
                        if pattern in header:
                            field_mapping['amount'] = i
                            break
                
                return field_mapping if len(field_mapping) >= 3 else None
                
        except Exception as e:
            print(f"Error detecting CSV format for {file_path}: {e}")
            return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[^\d.-]', '', str(amount_str))
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d/%m/%y',
            '%Y/%m/%d', '%m-%d-%Y', '%m-%d-%y', '%d-%m-%Y', '%d-%m-%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_csv_file(self, file_path: str) -> List[Tuple[datetime, str, float, str]]:
        """Parse a CSV file and return list of transactions."""
        transactions = []
        
        try:
            field_mapping = self.detect_csv_format(file_path)
            if not field_mapping:
                print(f"Could not detect format for {file_path}")
                return transactions
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(field_mapping.values()):
                            continue
                        
                        # Extract fields based on mapping
                        date_str = row[field_mapping['date']]
                        description = row[field_mapping['description']]
                        amount_str = row[field_mapping['amount']]
                        
                        # Parse data
                        transaction_date = self.parse_date(date_str)
                        if not transaction_date:
                            continue