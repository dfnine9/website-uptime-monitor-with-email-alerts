```python
#!/usr/bin/env python3
"""
Bank CSV Transaction Parser and Categorizer

This module parses bank CSV files and categorizes transactions based on configurable keyword rules.
It extracts transaction data (date, amount, description, account) and applies intelligent
categorization for expense tracking and financial analysis.

Features:
- Flexible CSV parsing with multiple format detection
- Configurable keyword-based categorization system
- Comprehensive error handling and validation
- Support for multiple date formats
- Transaction amount normalization
- Summary statistics and reporting

Usage:
    python script.py [csv_file_path]

If no file path is provided, it will process 'transactions.csv' in the current directory.
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from decimal import Decimal, InvalidOperation
import os


class TransactionCategorizer:
    """Handles transaction categorization based on configurable keyword rules."""
    
    def __init__(self):
        self.category_rules = {
            'groceries': [
                'safeway', 'kroger', 'walmart', 'target', 'costco', 'whole foods',
                'trader joe', 'publix', 'aldi', 'food lion', 'wegmans', 'harris teeter',
                'giant', 'stop shop', 'acme', 'supermarket', 'grocery', 'food mart'
            ],
            'utilities': [
                'electric', 'electricity', 'gas company', 'water', 'sewer',
                'internet', 'phone', 'cable', 'verizon', 'at&t', 'comcast',
                'xfinity', 'spectrum', 'dish', 'directv', 'utility'
            ],
            'entertainment': [
                'netflix', 'hulu', 'disney', 'spotify', 'apple music', 'amazon prime',
                'movie', 'theater', 'cinema', 'concert', 'ticket', 'entertainment',
                'game', 'steam', 'xbox', 'playstation', 'youtube premium'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'dunkin', 'mcdonald',
                'burger', 'pizza', 'subway', 'chipotle', 'taco bell', 'kfc',
                'wendy', 'chick-fil-a', 'domino', 'papa', 'dining', 'bistro'
            ],
            'gas': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'texaco', 'sunoco',
                'gas station', 'fuel', 'gasoline', 'petro', '76', 'arco'
            ],
            'shopping': [
                'amazon', 'ebay', 'walmart.com', 'target.com', 'best buy',
                'home depot', 'lowes', 'macy', 'nordstrom', 'gap', 'old navy',
                'tj maxx', 'marshall', 'kohls', 'jcpenney', 'sears'
            ],
            'healthcare': [
                'hospital', 'clinic', 'doctor', 'pharmacy', 'cvs', 'walgreens',
                'rite aid', 'medical', 'dental', 'optometry', 'health', 'rx'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'metro', 'train', 'airline',
                'parking', 'toll', 'dmv', 'registration', 'insurance'
            ],
            'banking': [
                'atm fee', 'bank fee', 'overdraft', 'maintenance fee',
                'wire transfer', 'check fee', 'service charge'
            ],
            'income': [
                'payroll', 'salary', 'deposit', 'refund', 'dividend',
                'interest', 'bonus', 'commission'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: Decimal) -> str:
        """
        Categorize a transaction based on its description and amount.
        
        Args:
            description: Transaction description
            amount: Transaction amount (positive for credits, negative for debits)
            
        Returns:
            Category string
        """
        description_lower = description.lower()
        
        # Check for income (typically positive amounts)
        if amount > 0:
            for keyword in self.category_rules['income']:
                if keyword in description_lower:
                    return 'income'
        
        # Check other categories for expenses (negative amounts)
        for category, keywords in self.category_rules.items():
            if category == 'income':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class BankCSVParser:
    """Parses bank CSV files and extracts transaction data."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d/%m/%y',
            '%Y/%m/%d', '%m-%d-%Y', '%m-%d-%y', '%d-%m-%Y', '%d-%m-%y'
        ]
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string using multiple format attempts.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime object or None if parsing fails
        """
        date_str = date_str.strip()
        for date_format in self.date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        return None
    
    def parse_amount(self, amount_str: str) -> Decimal:
        """
        Parse amount string to Decimal, handling various formats.
        
        Args:
            amount_str: Amount string to parse
            
        Returns:
            Decimal amount
        """
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$€£¥,\s]', '', amount_str)
        
        # Handle parentheses as negative indicators
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            raise ValueError(f"Cannot parse amount: {amount_str}")
    
    def detect_csv_format(self, file_path: str) -> Tuple[List[str], str]:
        """
        Detect CSV format and column headers.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Tuple of (headers, delimiter)
        """
        with open(file_path, 'r', encoding='utf-8', newline='') as file:
            # Try different delimiters
            sample = file.read(1024)
            file.seek(0)
            
            sniffer = csv.Sniffer()
            try:
                delimiter = sniffer.sniff(sample).delimiter
            except csv.Error:
                delimiter = ','
            
            reader = csv.reader(file, delimiter=delimiter)
            headers = [header.strip().lower() for header in next(reader)]
            
            return headers, delimiter
    
    def map_columns(self, headers: List[str]) -> Dict[str, int]:
        """
        Map standard column names to actual column indices.
        
        Args:
            headers: List of column headers
            
        Returns:
            Dictionary mapping standard names to column indices
        """
        column_mapping = {
            'date': None,
            'amount': None,
            'description': None,
            'account': None
        }
        
        # Common variations for each field
        date_variants = ['date', 'transaction date', 'posted date', 'trans date']
        amount_variants = ['amount', 'debit', 'credit', 'transaction amount', 'value']
        description_variants