```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements, parses transaction data, and implements
a keyword-based categorization system with predefined rules for common expense
categories such as groceries, utilities, entertainment, etc.

The script processes CSV files containing transaction data and automatically
categorizes transactions based on merchant names and descriptions using
predefined keyword matching rules.

Usage:
    python script.py

Requirements:
    - CSV file named 'bank_statement.csv' in the same directory
    - CSV should have columns: Date, Description, Amount
    - Python 3.6+ (uses only standard library)
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions based on keyword matching."""
    
    def __init__(self):
        """Initialize with predefined category rules."""
        self.category_rules = {
            'Groceries': [
                'walmart', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'publix', 'wegmans', 'harris teeter',
                'food lion', 'giant', 'stop shop', 'aldi', 'fresh market',
                'grocery', 'supermarket', 'market', 'food store'
            ],
            'Utilities': [
                'electric', 'electricity', 'power', 'gas company', 'water',
                'sewer', 'waste management', 'trash', 'internet', 'cable',
                'phone', 'wireless', 'verizon', 'at&t', 'comcast', 'xfinity',
                'spectrum', 't-mobile', 'sprint', 'utility', 'duke energy',
                'pge', 'con edison'
            ],
            'Entertainment': [
                'netflix', 'hulu', 'disney', 'spotify', 'apple music',
                'amazon prime', 'movie', 'theater', 'cinema', 'concert',
                'tickets', 'entertainment', 'games', 'steam', 'playstation',
                'xbox', 'nintendo', 'youtube', 'streaming'
            ],
            'Restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'dunkin',
                'mcdonald', 'burger king', 'subway', 'pizza', 'domino',
                'taco bell', 'kfc', 'wendy', 'chipotle', 'panera',
                'dining', 'bar', 'grill', 'bistro', 'diner'
            ],
            'Transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'parking',
                'toll', 'car wash', 'auto', 'repair', 'mechanic', 'oil change'
            ],
            'Shopping': [
                'amazon', 'target', 'best buy', 'home depot', 'lowes',
                'macy', 'nordstrom', 'tj maxx', 'marshall', 'ross',
                'department store', 'mall', 'shopping', 'retail'
            ],
            'Healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital',
                'medical', 'doctor', 'dentist', 'clinic', 'health',
                'insurance', 'copay', 'prescription'
            ],
            'Banking': [
                'bank', 'atm', 'fee', 'transfer', 'deposit', 'withdrawal',
                'interest', 'overdraft', 'maintenance', 'service charge'
            ],
            'Subscription': [
                'subscription', 'monthly', 'annual', 'membership', 'gym',
                'fitness', 'recurring', 'auto pay', 'autopay'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description string
            
        Returns:
            Category name or 'Other' if no match found
        """
        if not description:
            return 'Other'
        
        description_lower = description.lower()
        
        # Check each category's keywords
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
        
        return 'Other'


class BankStatementProcessor:
    """Processes bank statement CSV files and categorizes transactions."""
    
    def __init__(self, filename: str = 'bank_statement.csv'):
        """
        Initialize processor with CSV filename.
        
        Args:
            filename: Path to CSV file containing bank statement data
        """
        self.filename = filename
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def read_csv(self) -> List[Dict]:
        """
        Read and parse CSV file.
        
        Returns:
            List of transaction dictionaries
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid
        """
        transactions = []
        
        try:
            with open(self.filename, 'r', newline='', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ',' if ',' in sample else ';'
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Normalize column names (handle variations)
                        normalized_row = {}
                        for key, value in row.items():
                            key_lower = key.lower().strip()
                            if 'date' in key_lower:
                                normalized_row['Date'] = value.strip()
                            elif 'description' in key_lower or 'merchant' in key_lower or 'payee' in key_lower:
                                normalized_row['Description'] = value.strip()
                            elif 'amount' in key_lower or 'total' in key_lower:
                                normalized_row['Amount'] = value.strip()
                        
                        # Validate required fields
                        if not all(k in normalized_row for k in ['Date', 'Description', 'Amount']):
                            print(f"Warning: Row {row_num} missing required fields, skipping")
                            continue
                        
                        # Parse amount (handle negative values, currency symbols)
                        amount_str = normalized_row['Amount']
                        amount_clean = re.sub(r'[^\d.-]', '', amount_str)
                        if amount_clean:
                            normalized_row['Amount'] = float(amount_clean)
                        else:
                            print(f"Warning: Invalid amount '{amount_str}' in row {row_num}, skipping")
                            continue
                        
                        # Parse date
                        try:
                            # Try common date formats
                            date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
                            date_parsed = None
                            for fmt in date_formats:
                                try:
                                    date_parsed = datetime.strptime(normalized_row['Date'], fmt)
                                    break
                                except ValueError:
                                    continue
                            
                            if date_parsed:
                                normalized_row['Date'] = date_parsed
                            else:
                                print(f"Warning: Invalid date format '{normalized_row['Date']}' in row {row_num}")
                                continue
                                
                        except Exception as e:
                            print(f"Warning: Date parsing error in row {row_num}: {e}")
                            continue
                        
                        transactions.append(normalized_row)
                        
                    except Exception as e:
                        print(f