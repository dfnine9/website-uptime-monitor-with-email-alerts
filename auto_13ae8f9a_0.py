```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer and Data Validator

This module reads bank CSV exports and automatically categorizes transactions
based on configurable keyword matching. It performs data integrity validation
and outputs categorized results with summary statistics.

Features:
- Configurable keyword-based transaction categorization
- Data integrity validation (duplicate detection, format validation)
- Support for common CSV formats from major banks
- Comprehensive error handling and logging
- Summary statistics and category breakdown

Usage:
    python script.py [csv_file_path]
    
If no file path is provided, it will look for 'transactions.csv' in the current directory.
"""

import csv
import sys
import os
import re
from datetime import datetime
from collections import defaultdict, Counter
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple, Optional, Set


class TransactionCategorizer:
    """Handles transaction categorization and data validation."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'publix', 'whole foods',
                'trader joe', 'costco', 'sams club', 'grocery', 'supermarket',
                'food lion', 'wegmans', 'harris teeter', 'giant', 'stop shop'
            ],
            'dining': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'starbucks',
                'pizza', 'taco bell', 'kfc', 'wendy', 'chick-fil-a', 'chipotle',
                'dunkin', 'panera', 'olive garden', 'applebee', 'chili', 'cafe',
                'diner', 'bistro', 'grill', 'kitchen', 'bar & grill'
            ],
            'utilities': [
                'electric', 'gas company', 'water', 'internet', 'phone', 'cable',
                'verizon', 'att', 'comcast', 'spectrum', 'utilities', 'power',
                'energy', 'telecom', 'wireless'
            ],
            'entertainment': [
                'netflix', 'hulu', 'disney', 'amazon prime', 'spotify', 'movie',
                'theater', 'cinema', 'game', 'entertainment', 'streaming',
                'music', 'concert', 'event', 'ticket'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'uber', 'lyft',
                'taxi', 'parking', 'toll', 'metro', 'bus', 'train', 'airline',
                'car wash', 'auto', 'service station'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'store', 'shop', 'retail', 'department',
                'boutique', 'outlet', 'marketplace'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'medical', 'doctor',
                'clinic', 'dental', 'health', 'prescription'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'interest', 'transfer', 'deposit', 'withdrawal'
            ]
        }
        
        self.transactions = []
        self.errors = []
        self.duplicates = []
        
    def detect_csv_format(self, file_path: str) -> Optional[Dict]:
        """Detect CSV format by analyzing headers."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = [h.lower().strip() for h in reader.fieldnames or []]
                
                # Common header mappings
                header_mappings = {
                    'date': ['date', 'transaction date', 'posting date', 'trans date'],
                    'description': ['description', 'memo', 'payee', 'merchant', 'reference'],
                    'amount': ['amount', 'debit', 'credit', 'transaction amount'],
                    'balance': ['balance', 'running balance', 'account balance']
                }
                
                detected_format = {}
                for field, possible_names in header_mappings.items():
                    for header in headers:
                        if any(name in header for name in possible_names):
                            detected_format[field] = reader.fieldnames[headers.index(header)]
                            break
                
                if 'date' in detected_format and 'description' in detected_format and 'amount' in detected_format:
                    detected_format['delimiter'] = delimiter
                    return detected_format
                    
        except Exception as e:
            self.errors.append(f"Error detecting CSV format: {str(e)}")
            
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string to Decimal, handling various formats."""
        try:
            # Remove currency symbols, commas, and extra whitespace
            cleaned = re.sub(r'[$,\s]', '', str(amount_str).strip())
            
            # Handle parentheses as negative (accounting format)
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format attempts."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        return None
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def validate_transaction(self, row_num: int, transaction: Dict) -> List[str]:
        """Validate individual transaction data."""
        errors = []
        
        if not transaction.get('date'):
            errors.append(f"Row {row_num}: Missing date")
        
        if not transaction.get('description'):
            errors.append(f"Row {row_num}: Missing description")
        
        if transaction.get('amount') is None:
            errors.append(f"Row {row_num}: Invalid amount format")
        
        return errors
    
    def detect_duplicates(self) -> List[Tuple[int, int]]:
        """Detect potential duplicate transactions."""
        duplicates = []
        seen = {}
        
        for i, transaction in enumerate(self.transactions):
            key = (
                transaction.get('date', ''),
                transaction.get('description', ''),
                transaction.get('amount', 0)
            )
            
            if key in seen:
                duplicates.append((seen[key], i))
            else:
                seen[key] = i
        
        return duplicates
    
    def load_transactions(self, file_path: str) -> bool:
        """Load and parse transactions from CSV file."""
        if not os.path.exists(file_path):
            self.errors.append(f"File not found: {file_path}")
            return False
        
        csv_format = self.detect_csv_format(file_path)
        if not csv_format