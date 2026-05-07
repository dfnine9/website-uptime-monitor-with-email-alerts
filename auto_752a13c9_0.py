```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statement files and categorizes transactions based on keywords.
It validates data integrity and handles malformed entries with comprehensive error reporting.

Features:
- Automatic transaction categorization using predefined keyword mappings
- Data validation with detailed error reporting
- Flexible CSV format detection
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
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Handles transaction categorization based on keyword matching."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'grocery', 'market', 'food', 'supermarket'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'internet', 'phone', 'cable',
                'utility', 'power', 'energy', 'comcast', 'verizon', 'at&t'
            ],
            'entertainment': [
                'netflix', 'spotify', 'movie', 'theater', 'cinema', 'game', 'entertainment',
                'streaming', 'music', 'concert', 'ticket', 'amazon prime', 'disney'
            ],
            'transportation': [
                'gas station', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'transit',
                'parking', 'toll', 'car', 'auto', 'shell', 'chevron', 'exxon'
            ],
            'dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'pizza',
                'burger', 'diner', 'bistro', 'bar', 'pub', 'takeout', 'delivery'
            ],
            'shopping': [
                'amazon', 'ebay', 'store', 'mall', 'shop', 'retail', 'clothing',
                'apparel', 'shoes', 'electronics', 'best buy', 'macy'
            ],
            'healthcare': [
                'hospital', 'clinic', 'doctor', 'pharmacy', 'medical', 'health',
                'dental', 'vision', 'insurance', 'cvs', 'walgreens'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'transfer', 'deposit', 'withdrawal', 'interest',
                'overdraft', 'maintenance', 'service charge'
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


class CSVBankStatementProcessor:
    """Processes CSV bank statement files with data validation and categorization."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.valid_transactions = []
        self.errors = []
        self.stats = {
            'total_processed': 0,
            'valid_transactions': 0,
            'errors': 0,
            'categories': {}
        }
    
    def detect_csv_format(self, filepath: str) -> Optional[Dict]:
        """Detect CSV format and return column mapping."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Read first few lines to detect format
                sample = file.read(1024)
                file.seek(0)
                
                # Try to detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = [h.lower().strip() for h in reader.fieldnames or []]
                
                # Common column name variations
                date_cols = ['date', 'transaction date', 'posted date', 'effective date']
                desc_cols = ['description', 'memo', 'details', 'transaction details']
                amount_cols = ['amount', 'debit', 'credit', 'transaction amount']
                
                mapping = {}
                
                for header in headers:
                    if any(col in header for col in date_cols):
                        mapping['date'] = header
                    elif any(col in header for col in desc_cols):
                        mapping['description'] = header
                    elif any(col in header for col in amount_cols):
                        mapping['amount'] = header
                
                return mapping if len(mapping) >= 2 else None
                
        except Exception as e:
            print(f"Error detecting CSV format for {filepath}: {e}")
            return None
    
    def validate_date(self, date_str: str) -> Optional[datetime]:
        """Validate and parse date string."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%b %d, %Y', '%B %d, %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def validate_amount(self, amount_str: str) -> Optional[Decimal]:
        """Validate and parse amount string."""
        try:
            # Clean the amount string
            cleaned = re.sub(r'[^\d.-]', '', amount_str.strip())
            if not cleaned:
                return None
            
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
    
    def process_transaction(self, row: Dict, mapping: Dict, row_num: int) -> bool:
        """Process a single transaction row."""
        try:
            # Extract required fields
            date_field = mapping.get('date', '')
            desc_field = mapping.get('description', '')
            amount_field = mapping.get('amount', '')
            
            if not all([date_field, desc_field, amount_field]):
                self.errors.append(f"Row {row_num}: Missing required field mapping")
                return False
            
            raw_date = row.get(date_field, '').strip()
            raw_description = row.get(desc_field, '').strip()
            raw_amount = row.get(amount_field, '').strip()
            
            if not all([raw_date, raw_description, raw_amount]):
                self.errors.append(f"Row {row_num}: Empty required fields")
                return False
            
            # Validate date
            parsed_date = self.validate_date(raw_date)
            if not parsed_date:
                self.errors.append(f"Row {row_num}: Invalid date format '{raw_date}'")
                return False
            
            # Validate amount
            parsed_amount = self.validate_amount(raw_amount)
            if parsed_amount is None:
                self.errors.append(f"Row {row_num}: Invalid amount format '{raw_amount}'")
                return False
            
            # Categorize transaction
            category = self.categorizer.categorize(raw_description)
            
            # Store valid transaction
            transaction = {
                'date': parsed_date,
                'description': raw_description,
                'amount': parsed_amount,
                'category': category,
                'raw_row': row_num
            }
            
            self.valid_transactions.append(transaction)
            
            # Update category stats
            if category not in self.stats['categories']:
                self.stats['categories'][category] = {'count': 0, 'total': Decimal('0')}
            
            self.stats['categories'][category]['