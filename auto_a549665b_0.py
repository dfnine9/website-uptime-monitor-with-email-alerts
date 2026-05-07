```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements and categorizes transactions based on keywords.
It provides comprehensive data validation, error handling, and supports multiple CSV formats.

Features:
- Automatic CSV format detection
- Keyword-based transaction categorization
- Data validation and cleaning
- Comprehensive error handling
- Summary statistics and reporting

Usage:
    python script.py

The script will look for CSV files in the current directory and process them automatically.
"""

import csv
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, InvalidOperation


class TransactionCategorizer:
    """Handles transaction categorization based on keywords and patterns."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'safeway', 'kroger', 'publix', 'whole foods',
                'trader joe', 'costco', 'sams club', 'grocery', 'supermarket',
                'food lion', 'harris teeter', 'wegmans', 'aldi', 'lidl'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'internet', 'cable',
                'phone', 'cellular', 'verizon', 'att', 'comcast', 'xfinity',
                'spectrum', 'duke energy', 'pge', 'utility', 'bill pay'
            ],
            'entertainment': [
                'netflix', 'hulu', 'disney', 'spotify', 'apple music',
                'youtube', 'movie', 'theater', 'cinema', 'concert',
                'gaming', 'steam', 'playstation', 'xbox', 'entertainment'
            ],
            'dining': [
                'restaurant', 'mcdonalds', 'burger king', 'subway', 'starbucks',
                'dunkin', 'pizza', 'kfc', 'taco bell', 'chipotle',
                'panera', 'cafe', 'bar', 'pub', 'diner', 'bistro'
            ],
            'transport': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train',
                'parking', 'toll', 'automotive', 'car wash'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'clothing', 'department store',
                'best buy', 'home depot', 'lowes', 'macys', 'nordstrom',
                'online', 'retail', 'store'
            ],
            'healthcare': [
                'hospital', 'doctor', 'dental', 'pharmacy', 'cvs',
                'walgreens', 'medical', 'clinic', 'urgent care',
                'insurance', 'copay'
            ],
            'finance': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'credit card',
                'transfer', 'payment', 'investment', 'brokerage'
            ],
            'income': [
                'salary', 'payroll', 'deposit', 'dividend', 'refund',
                'bonus', 'commission', 'freelance', 'contract'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: Decimal) -> str:
        """Categorize a transaction based on description and amount."""
        if not description:
            return 'uncategorized'
        
        description_lower = description.lower()
        
        # Special handling for income (positive amounts with income keywords)
        if amount > 0:
            for keyword in self.categories['income']:
                if keyword in description_lower:
                    return 'income'
        
        # Check each category for keyword matches
        for category, keywords in self.categories.items():
            if category == 'income':  # Skip income for negative amounts
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'uncategorized'


class BankStatementProcessor:
    """Main class for processing bank statement CSV files."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.processed_transactions = []
        self.errors = []
        self.statistics = {}
    
    def detect_csv_format(self, filepath: str) -> Optional[Dict[str, str]]:
        """Detect the CSV format and return column mappings."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                # Read first few lines to detect format
                sample_lines = [file.readline().strip() for _ in range(3)]
                file.seek(0)
                
                # Try to detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(''.join(sample_lines[:2])).delimiter
                
                # Read header
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader, [])
                
                if not headers:
                    return None
                
                # Normalize headers for mapping
                normalized_headers = [h.lower().strip() for h in headers]
                
                # Common column mappings
                mappings = {
                    'date': self._find_column(normalized_headers, ['date', 'transaction date', 'posted date']),
                    'description': self._find_column(normalized_headers, ['description', 'memo', 'details', 'transaction']),
                    'amount': self._find_column(normalized_headers, ['amount', 'transaction amount', 'debit', 'credit']),
                    'balance': self._find_column(normalized_headers, ['balance', 'running balance', 'account balance'])
                }
                
                # Ensure we have required fields
                if mappings['date'] is not None and mappings['description'] is not None and mappings['amount'] is not None:
                    return {
                        'delimiter': delimiter,
                        'headers': headers,
                        'mappings': mappings
                    }
                
        except Exception as e:
            self.errors.append(f"Error detecting CSV format for {filepath}: {str(e)}")
        
        return None
    
    def _find_column(self, headers: List[str], possible_names: List[str]) -> Optional[int]:
        """Find column index by matching possible column names."""
        for name in possible_names:
            for i, header in enumerate(headers):
                if name in header:
                    return i
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string to Decimal, handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return None
        
        try:
            # Clean the amount string
            cleaned = re.sub(r'[^\d.-]', '', amount_str.strip())
            
            # Handle parentheses as negative
            if amount_str.strip().startswith('(') and amount_str.strip().endswith(')'):
                cleaned = '-' + cleaned
            
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str or date_str.strip() == '':
            return None
        
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%d/%m/%Y',
            '%m/%d/%y', '%m-%d-%y', '%y-%m-%d', '%d/%m/%y',
            '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return