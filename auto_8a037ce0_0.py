```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements, validates transaction data formats,
and categorizes transactions using rule-based keyword matching. It supports
common banking CSV formats and provides automated expense categorization
for personal finance analysis.

Features:
- CSV parsing with multiple format detection
- Data validation (dates, amounts, descriptions)
- Rule-based categorization using keyword dictionaries
- Comprehensive error handling and reporting
- Self-contained with minimal dependencies

Usage:
    python script.py
"""

import csv
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple, Optional, Any
import io


class TransactionCategorizer:
    """Handles transaction categorization using keyword-based rules."""
    
    def __init__(self):
        self.category_keywords = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods',
                'trader joe', 'costco', 'sam\'s club', 'publix', 'wegmans',
                'aldi', 'food lion', 'giant', 'stop shop', 'king soopers',
                'grocery', 'supermarket', 'market', 'fresh'
            ],
            'utilities': [
                'electric', 'electricity', 'gas', 'water', 'sewer',
                'internet', 'cable', 'phone', 'cellular', 'verizon',
                'at&t', 'comcast', 'xfinity', 'spectrum', 'cox',
                'utility', 'power', 'energy'
            ],
            'entertainment': [
                'netflix', 'hulu', 'disney', 'spotify', 'apple music',
                'amazon prime', 'hbo', 'movie', 'cinema', 'theater',
                'concert', 'game', 'entertainment', 'streaming',
                'youtube', 'twitch', 'playstation', 'xbox', 'steam'
            ],
            'dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'dunkin',
                'mcdonald', 'burger king', 'subway', 'pizza', 'taco bell',
                'kfc', 'wendy', 'chipotle', 'panera', 'diner',
                'bistro', 'grill', 'bar', 'pub', 'food delivery',
                'uber eats', 'doordash', 'grubhub'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron',
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train',
                'parking', 'toll', 'dmv', 'auto', 'car wash',
                'mechanic', 'oil change', 'tire'
            ],
            'shopping': [
                'amazon', 'ebay', 'etsy', 'best buy', 'home depot',
                'lowes', 'macy', 'nordstrom', 'tj maxx', 'ross',
                'marshall', 'clothing', 'apparel', 'shoes', 'electronics'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital',
                'clinic', 'doctor', 'dentist', 'medical', 'health',
                'insurance', 'prescription', 'urgent care'
            ],
            'banking': [
                'atm', 'withdrawal', 'deposit', 'transfer', 'fee',
                'overdraft', 'interest', 'dividend', 'check',
                'wire transfer', 'ach', 'direct deposit'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: Decimal) -> str:
        """
        Categorize a transaction based on description keywords.
        
        Args:
            description: Transaction description text
            amount: Transaction amount
            
        Returns:
            Category string or 'other' if no match found
        """
        if not description:
            return 'other'
            
        description_lower = description.lower()
        
        # Special case for income (positive amounts)
        if amount > 0:
            income_keywords = ['salary', 'payroll', 'deposit', 'refund', 'dividend']
            if any(keyword in description_lower for keyword in income_keywords):
                return 'income'
        
        # Check each category for keyword matches
        for category, keywords in self.category_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
                
        return 'other'


class BankStatementParser:
    """Parses and validates CSV bank statement data."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.common_date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
    
    def detect_csv_format(self, csv_content: str) -> Dict[str, int]:
        """
        Detect the CSV format by analyzing headers.
        
        Args:
            csv_content: Raw CSV content as string
            
        Returns:
            Dictionary mapping field types to column indices
        """
        lines = csv_content.strip().split('\n')
        if not lines:
            raise ValueError("Empty CSV file")
            
        # Try to detect delimiter
        delimiter = ','
        if '\t' in lines[0]:
            delimiter = '\t'
        elif ';' in lines[0]:
            delimiter = ';'
            
        reader = csv.reader(lines, delimiter=delimiter)
        headers = next(reader)
        headers_lower = [h.lower().strip() for h in headers]
        
        # Common header patterns
        date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
        description_patterns = ['description', 'memo', 'details', 'transaction', 'payee']
        amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
        
        format_map = {}
        
        # Find date column
        for i, header in enumerate(headers_lower):
            if any(pattern in header for pattern in date_patterns):
                format_map['date'] = i
                break
        
        # Find description column
        for i, header in enumerate(headers_lower):
            if any(pattern in header for pattern in description_patterns):
                format_map['description'] = i
                break
                
        # Find amount column(s)
        debit_col = credit_col = amount_col = None
        for i, header in enumerate(headers_lower):
            if 'debit' in header:
                debit_col = i
            elif 'credit' in header:
                credit_col = i
            elif any(pattern in header for pattern in amount_patterns):
                amount_col = i
                
        if debit_col is not None and credit_col is not None:
            format_map['debit'] = debit_col
            format_map['credit'] = credit_col
        elif amount_col is not None:
            format_map['amount'] = amount_col
            
        return format_map, delimiter
    
    def validate_date(self, date_str: str) -> Optional[datetime]:
        """
        Validate and parse date string.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Parsed datetime object or None if invalid
        """
        if not date_str or not date_str.strip():
            return None
            
        date_str = date_str.strip()
        
        for fmt in self.common_date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        return None
    
    def validate_amount(self, amount_str: str) -> Optional[Decimal]:
        """
        Validate and parse amount string.