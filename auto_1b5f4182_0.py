```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statement files and automatically categorizes transactions
based on keyword matching. It reads transaction data from CSV files, applies predefined
categorization rules based on transaction descriptions, and outputs categorized results.

Features:
- Parses standard CSV bank statement formats
- Categorizes transactions using keyword matching
- Handles multiple date formats
- Provides transaction summaries by category
- Robust error handling for malformed data

Usage:
    python script.py

The script will look for CSV files in the current directory and process them automatically.
"""

import csv
import re
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class TransactionCategorizer:
    """Categorizes bank transactions based on description keywords."""
    
    def __init__(self):
        """Initialize categorizer with predefined keyword mappings."""
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonalds', 'burger',
                'pizza', 'food', 'dining', 'kitchen', 'grill', 'bistro', 'deli',
                'grocery', 'market', 'supermarket', 'walmart', 'target', 'kroger'
            ],
            'Transportation': [
                'gas', 'fuel', 'shell', 'exxon', 'chevron', 'bp', 'uber', 'lyft',
                'taxi', 'transport', 'metro', 'bus', 'train', 'parking', 'toll'
            ],
            'Shopping': [
                'amazon', 'ebay', 'store', 'shop', 'retail', 'mall', 'outlet',
                'clothing', 'apparel', 'shoes', 'electronics', 'best buy'
            ],
            'Utilities': [
                'electric', 'electricity', 'gas bill', 'water', 'internet',
                'phone', 'mobile', 'cable', 'utility', 'power', 'energy'
            ],
            'Healthcare': [
                'medical', 'doctor', 'hospital', 'pharmacy', 'health',
                'dental', 'clinic', 'medicine', 'prescription'
            ],
            'Entertainment': [
                'movie', 'cinema', 'theater', 'netflix', 'spotify', 'gaming',
                'entertainment', 'music', 'streaming', 'concert', 'event'
            ],
            'Banking': [
                'fee', 'atm', 'bank', 'interest', 'transfer', 'withdrawal',
                'deposit', 'service charge', 'overdraft'
            ],
            'Income': [
                'salary', 'payroll', 'deposit', 'refund', 'dividend',
                'bonus', 'payment received', 'income'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description
            amount: Transaction amount (positive for credits, negative for debits)
            
        Returns:
            Category name or 'Other' if no match found
        """
        description_lower = description.lower()
        
        # Handle income transactions
        if amount > 0:
            for keyword in self.categories['Income']:
                if keyword in description_lower:
                    return 'Income'
        
        # Check other categories
        for category, keywords in self.categories.items():
            if category == 'Income':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'

class CSVParser:
    """Parses CSV bank statement files with various formats."""
    
    def __init__(self):
        """Initialize parser with common date formats."""
        self.date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%m-%d-%Y',
            '%d-%m-%Y',
            '%Y/%m/%d'
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
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string, handling various formats.
        
        Args:
            amount_str: Amount string to parse
            
        Returns:
            Float amount
        """
        # Remove currency symbols, commas, and whitespace
        cleaned = re.sub(r'[\$,\s]', '', amount_str.strip())
        
        # Handle parentheses for negative amounts
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        return float(cleaned)
    
    def detect_csv_format(self, filepath: str) -> Dict[str, int]:
        """
        Detect CSV format by analyzing headers.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Dictionary mapping field names to column indices
        """
        with open(filepath, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            headers = [h.lower().strip() for h in headers]
        
        field_mapping = {}
        
        # Common header variations
        date_headers = ['date', 'transaction date', 'posted date', 'trans date']
        desc_headers = ['description', 'desc', 'memo', 'transaction', 'details']
        amount_headers = ['amount', 'debit', 'credit', 'transaction amount']
        
        for i, header in enumerate(headers):
            if any(dh in header for dh in date_headers):
                field_mapping['date'] = i
            elif any(dh in header for dh in desc_headers):
                field_mapping['description'] = i
            elif any(ah in header for ah in amount_headers):
                if 'amount' not in field_mapping:
                    field_mapping['amount'] = i
                elif 'debit' in header:
                    field_mapping['debit'] = i
                elif 'credit' in header:
                    field_mapping['credit'] = i
        
        return field_mapping
    
    def parse_csv(self, filepath: str) -> List[Dict]:
        """
        Parse CSV file and return list of transactions.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of transaction dictionaries
        """
        try:
            field_mapping = self.detect_csv_format(filepath)
            
            if 'date' not in field_mapping or 'description' not in field_mapping:
                raise ValueError("Unable to identify required fields (date, description)")
            
            transactions = []
            
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(field_mapping.values()):
                            continue
                        
                        # Parse date
                        date_obj = self.parse_date(row[field_mapping['date']])
                        if not date_obj:
                            print(f"Warning: Invalid date format in row {row_num}")
                            continue
                        
                        # Parse description
                        description = row[field_mapping['description']].strip()
                        
                        # Parse amount
                        amount = 0.0
                        if 'amount' in field_mapping:
                            amount = self.parse_amount(row[field_mapping['amount']])