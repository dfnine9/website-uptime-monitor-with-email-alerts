```python
#!/usr/bin/env python3
"""
Bank Transaction CSV Parser and Categorizer

This module provides functionality to parse bank transaction CSV files,
validate data formats, and categorize transactions based on keyword matching.
It supports common expense categories like groceries, transportation, utilities,
and entertainment.

Features:
- CSV parsing with flexible column detection
- Data validation (date formats, amount parsing)
- Keyword-based transaction categorization
- Comprehensive error handling
- Summary statistics and reporting

Usage:
    python script.py [csv_file_path]
    
If no file path is provided, it will look for 'transactions.csv' in the current directory.
"""

import csv
import re
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, InvalidOperation


class TransactionCategorizer:
    """Handles categorization of transactions based on description keywords."""
    
    def __init__(self):
        self.category_keywords = {
            'groceries': [
                'supermarket', 'grocery', 'safeway', 'kroger', 'walmart', 'target',
                'whole foods', 'trader joe', 'costco', 'sam\'s club', 'publix',
                'wegmans', 'harris teeter', 'food lion', 'giant', 'stop shop',
                'aldi', 'lidl', 'fresh market', 'market', 'food'
            ],
            'transportation': [
                'gas', 'fuel', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'metro', 'subway', 'bus', 'train',
                'parking', 'toll', 'dmv', 'registration', 'insurance auto',
                'car wash', 'auto repair', 'mechanic', 'tire', 'oil change'
            ],
            'utilities': [
                'electric', 'electricity', 'gas bill', 'water', 'sewer',
                'internet', 'cable', 'phone', 'wireless', 'verizon', 'att',
                'comcast', 'spectrum', 'xfinity', 'utility', 'power company',
                'energy', 'heating', 'cooling'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'hulu', 'disney',
                'movie', 'cinema', 'theater', 'concert', 'music', 'game',
                'steam', 'playstation', 'xbox', 'nintendo', 'bar', 'pub',
                'restaurant', 'dining', 'coffee', 'starbucks', 'dunkin'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'doctor', 'medical',
                'hospital', 'clinic', 'dentist', 'vision', 'prescription',
                'health insurance', 'co-pay', 'copay'
            ],
            'shopping': [
                'amazon', 'ebay', 'walmart online', 'target online', 'best buy',
                'home depot', 'lowes', 'macy', 'nordstrom', 'gap', 'clothing',
                'shoes', 'electronics', 'furniture', 'appliance'
            ],
            'banking': [
                'fee', 'atm', 'overdraft', 'interest', 'transfer', 'deposit',
                'withdrawal', 'maintenance', 'service charge'
            ],
            'income': [
                'salary', 'payroll', 'direct deposit', 'wages', 'bonus',
                'refund', 'dividend', 'interest earned', 'cashback'
            ]
        }
    
    def categorize(self, description: str, amount: Decimal) -> str:
        """Categorize a transaction based on its description and amount."""
        if not description:
            return 'uncategorized'
        
        description_lower = description.lower()
        
        # Special case for income (positive amounts)
        if amount > 0:
            for keyword in self.category_keywords['income']:
                if keyword in description_lower:
                    return 'income'
        
        # Check all other categories
        for category, keywords in self.category_keywords.items():
            if category == 'income':  # Skip income for negative amounts
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'uncategorized'


class TransactionParser:
    """Parses and validates bank transaction CSV files."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
        self.errors = []
    
    def detect_csv_format(self, file_path: str) -> Dict[str, int]:
        """Detect the column indices for common transaction CSV formats."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sample_lines = [file.readline() for _ in range(3)]
                
            # Reset file pointer and read header
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)
                
            header_lower = [col.lower().strip() for col in header]
            
            column_mapping = {}
            
            # Common date column names
            date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
            for i, col in enumerate(header_lower):
                if any(pattern in col for pattern in date_patterns):
                    column_mapping['date'] = i
                    break
            
            # Common description column names
            desc_patterns = ['description', 'memo', 'payee', 'merchant', 'details']
            for i, col in enumerate(header_lower):
                if any(pattern in col for pattern in desc_patterns):
                    column_mapping['description'] = i
                    break
            
            # Common amount column names
            amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
            for i, col in enumerate(header_lower):
                if any(pattern in col for pattern in amount_patterns):
                    column_mapping['amount'] = i
                    break
            
            # If we have separate debit/credit columns
            if 'amount' not in column_mapping:
                for i, col in enumerate(header_lower):
                    if 'debit' in col:
                        column_mapping['debit'] = i
                    elif 'credit' in col:
                        column_mapping['credit'] = i
            
            return column_mapping
            
        except Exception as e:
            raise Exception(f"Error detecting CSV format: {str(e)}")
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various common formats."""
        if not date_str or date_str.strip() == '':
            return None
        
        date_formats = [
            '%Y-%m-%d',      # 2023-12-31
            '%m/%d/%Y',      # 12/31/2023
            '%m/%d/%y',      # 12/31/23
            '%d/%m/%Y',      # 31/12/2023
            '%Y%m%d',        # 20231231
            '%m-%d-%Y',      # 12-31-2023
            '%d-%m-%Y',      # 31-12-2023
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string, handling various formats and currency symbols."""
        if not amount_str or amount_str.strip() == '':
            return None
        
        # Clean the amount string
        cleaned = amount_str.strip()
        cleaned = re.sub(r'[$€£¥,]', '', cleaned)  # Remove currency symbols and commas
        cleaned = cleaned.replace('(', '-