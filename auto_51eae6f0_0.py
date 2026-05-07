```python
"""
Bank Transaction CSV Parser and Categorizer

This module parses bank CSV exports and categorizes transactions using rule-based
keyword matching. It extracts transaction data (date, amount, description, merchant)
and automatically categorizes transactions into common categories like groceries,
gas, restaurants, utilities, etc.

Usage: python script.py

The script expects CSV files with columns: Date, Amount, Description
Place your CSV files in the same directory as this script.
"""

import csv
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Rule-based transaction categorizer using keyword matching."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sams club', 'grocery', 'supermarket', 'food mart',
                'publix', 'wegmans', 'harris teeter', 'giant', 'stop shop'
            ],
            'gas': [
                'shell', 'bp', 'exxon', 'chevron', 'mobil', 'texaco', 'citgo',
                'speedway', 'wawa', 'gas station', 'fuel', '76 gas', 'marathon'
            ],
            'restaurants': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'starbucks',
                'kfc', 'taco bell', 'pizza', 'domino', 'chipotle', 'panera',
                'dunkin', 'wendy', 'chick-fil-a', 'olive garden', 'applebee'
            ],
            'utilities': [
                'electric', 'gas bill', 'water', 'sewer', 'internet', 'cable',
                'phone', 'verizon', 'att', 'comcast', 'utilities', 'power company'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes', 'macys',
                'nordstrom', 'tj maxx', 'marshall', 'ross', 'old navy', 'gap'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'medical', 'doctor',
                'dentist', 'clinic', 'urgent care', 'health', 'rx'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'parking',
                'toll', 'dmv', 'car wash', 'auto repair'
            ],
            'entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'gym', 'fitness',
                'park', 'museum', 'concert', 'game', 'entertainment'
            ],
            'banking': [
                'atm fee', 'bank fee', 'overdraft', 'interest', 'transfer',
                'deposit', 'withdrawal', 'check'
            ]
        }
    
    def categorize(self, description: str, merchant: str = "") -> str:
        """Categorize a transaction based on description and merchant."""
        text = f"{description.lower()} {merchant.lower()}"
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return 'other'


class BankCSVParser:
    """Parser for bank CSV exports with transaction categorization."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def extract_merchant(self, description: str) -> str:
        """Extract merchant name from transaction description."""
        # Remove common prefixes and suffixes
        cleaned = re.sub(r'^(debit|credit|pos|purchase|payment|transfer)\s*', '', description.lower())
        cleaned = re.sub(r'\s*(#\d+|xx\d+|\*\d+).*$', '', cleaned)
        cleaned = re.sub(r'\s+\d{2}/\d{2}.*$', '', cleaned)
        
        # Split and take first meaningful part
        parts = cleaned.split()
        if parts:
            return parts[0].strip()
        return ""
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format support."""
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string, handling various formats."""
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
        
        # Handle parentheses for negative amounts
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def detect_csv_format(self, filepath: str) -> Tuple[List[str], str]:
        """Detect CSV format and return headers and delimiter."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try different delimiters
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                return [h.lower().strip() for h in headers], delimiter
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return [], ','
    
    def parse_csv(self, filepath: str) -> List[Dict]:
        """Parse CSV file and extract transaction data."""
        try:
            headers, delimiter = self.detect_csv_format(filepath)
            
            if not headers:
                print(f"Could not detect headers for {filepath}")
                return []
            
            print(f"Detected headers: {headers}")
            
            # Map common header variations
            header_map = {}
            for i, header in enumerate(headers):
                if any(word in header for word in ['date', 'posted', 'trans']):
                    header_map['date'] = i
                elif any(word in header for word in ['amount', 'debit', 'credit']):
                    header_map['amount'] = i
                elif any(word in header for word in ['description', 'memo', 'detail']):
                    header_map['description'] = i
            
            if 'date' not in header_map or 'amount' not in header_map or 'description' not in header_map:
                print(f"Could not map required columns in {filepath}")
                print(f"Required: date, amount, description")
                return []
            
            transactions = []
            
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=delimiter)
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, 2):
                    try:
                        if len(row) <= max(header_map.values()):
                            continue
                        
                        date_str = row[header_map['date']]
                        amount_str = row[header_map['amount']]
                        description = row[header_map['description']]
                        
                        parsed_date = self.parse_date(date_str)
                        if not parsed_date:
                            print(f"Warning: Could not parse date '{date_str}