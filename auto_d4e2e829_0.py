```python
#!/usr/bin/env python3
"""
Bank Transaction Categorization Engine

This module reads CSV files from multiple bank formats, categorizes transactions
using keyword-based rules, and handles various data formats and errors gracefully.

Supports common bank CSV formats and provides robust categorization for:
- Groceries, Utilities, Entertainment, Transportation, Healthcare
- Dining, Shopping, Banking, Insurance, and more

Usage: python script.py
"""

import csv
import re
import os
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import glob


class TransactionCategorizer:
    """Keyword-based transaction categorization engine"""
    
    def __init__(self):
        self.categories = {
            'Groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sams club', 'grocery', 'supermarket', 'food lion', 'publix',
                'aldi', 'wegmans', 'giant', 'harris teeter', 'meijer', 'heb'
            ],
            'Utilities': [
                'electric', 'gas company', 'water', 'sewer', 'utility', 'power',
                'energy', 'pge', 'edison', 'duke energy', 'xcel', 'constellation',
                'waste management', 'republic services', 'internet', 'cable',
                'verizon', 'att', 'comcast', 'spectrum', 'cox'
            ],
            'Entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'apple music',
                'movie', 'theater', 'cinema', 'concert', 'ticketmaster', 'stubhub',
                'game', 'entertainment', 'streaming', 'youtube premium', 'hbo'
            ],
            'Transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil', 'citgo',
                'uber', 'lyft', 'taxi', 'metro', 'transit', 'parking', 'toll',
                'automotive', 'car wash', 'jiffy lube', 'valvoline', 'midas'
            ],
            'Dining': [
                'restaurant', 'mcdonalds', 'burger king', 'subway', 'starbucks',
                'pizza', 'taco bell', 'chipotle', 'panera', 'dunkin', 'kfc',
                'wendys', 'dominos', 'papa johns', 'olive garden', 'applebees',
                'chilis', 'outback', 'red lobster', 'ihop', 'dennys'
            ],
            'Healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital', 'clinic',
                'doctor', 'medical', 'dental', 'vision', 'prescription', 'medicine',
                'health', 'urgent care', 'lab', 'imaging', 'therapy'
            ],
            'Shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes', 'macys',
                'nordstrom', 'kohls', 'jcpenney', 'sears', 'barnes noble',
                'staples', 'office depot', 'petco', 'petsmart', 'bed bath beyond'
            ],
            'Banking': [
                'bank', 'atm', 'fee', 'interest', 'transfer', 'deposit', 'withdrawal',
                'overdraft', 'service charge', 'maintenance', 'check', 'wire'
            ],
            'Insurance': [
                'insurance', 'geico', 'state farm', 'allstate', 'progressive',
                'usaa', 'farmers', 'liberty mutual', 'auto insurance', 'home insurance'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on description keywords"""
        if not description:
            return 'Other'
        
        description_lower = description.lower()
        
        # Check each category for keyword matches
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'


class BankCSVReader:
    """Handles multiple bank CSV formats with robust error handling"""
    
    def __init__(self, categorizer: TransactionCategorizer):
        self.categorizer = categorizer
        self.supported_formats = {
            'chase': ['Date', 'Description', 'Amount', 'Balance'],
            'bofa': ['Date', 'Description', 'Amount', 'Running Bal.'],
            'wells_fargo': ['Date', 'Amount', 'Description', 'Balance'],
            'citi': ['Date', 'Description', 'Debit', 'Credit', 'Balance'],
            'generic': ['date', 'description', 'amount', 'balance']
        }
    
    def detect_format(self, headers: List[str]) -> Optional[str]:
        """Detect bank format based on CSV headers"""
        headers_lower = [h.lower().strip() for h in headers]
        
        for format_name, expected_headers in self.supported_formats.items():
            expected_lower = [h.lower() for h in expected_headers]
            if all(any(exp in header for header in headers_lower) for exp in expected_lower[:3]):
                return format_name
        
        return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string handling various formats"""
        if not amount_str:
            return 0.0
        
        # Remove currency symbols, commas, and extra spaces
        cleaned = re.sub(r'[$,\s]', '', str(amount_str))
        
        # Handle negative amounts in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string handling various formats"""
        if not date_str:
            return None
        
        date_formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_str).strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return str(date_str).strip()
    
    def read_csv_file(self, filepath: str) -> List[Dict]:
        """Read and parse a CSV file with error handling"""
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect encoding issues
                content = file.read()
                file.seek(0)
                
                # Use csv.Sniffer to detect delimiter
                try:
                    sample = file.read(1024)
                    file.seek(0)
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                except:
                    delimiter = ','
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    print(f"Warning: No headers found in {filepath}")
                    return transactions
                
                format_type = self.detect_format(headers)
                if not format_type:
                    print(f"Warning: Unknown format in {filepath}, attempting generic parsing")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        transaction = self.parse_transaction_row(row, format_type)
                        if transaction: