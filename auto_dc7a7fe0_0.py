```python
"""
Bank Transaction Categorizer and Analyzer

This module parses CSV files containing bank transactions and automatically categorizes them
based on keyword matching and amount patterns. It calculates total spending by category
with comprehensive data validation.

Features:
- Automatic transaction categorization using merchant keywords
- Amount pattern recognition for recurring payments
- Data validation and error handling
- Summary statistics by category
- Support for common CSV formats from major banks

Usage:
    python script.py

The script will look for CSV files in the current directory or prompt for a file path.
Expected CSV format: Date, Description, Amount (or similar column names)
"""

import csv
import re
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, InvalidOperation


class TransactionCategorizer:
    """Categorizes bank transactions based on keywords and patterns."""
    
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'pizza', 'burger', 'food', 'dining', 'starbucks',
                'mcdonalds', 'subway', 'dominos', 'uber eats', 'doordash', 'grubhub',
                'chipotle', 'panera', 'dunkin', 'kfc', 'taco bell'
            ],
            'Groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'costco', 'kroger',
                'safeway', 'whole foods', 'trader joe', 'aldi', 'publix', 'meijer'
            ],
            'Transportation': [
                'gas', 'fuel', 'shell', 'exxon', 'bp', 'chevron', 'mobil', 'uber',
                'lyft', 'taxi', 'parking', 'metro', 'bus', 'train', 'subway'
            ],
            'Shopping': [
                'amazon', 'ebay', 'store', 'retail', 'mall', 'shop', 'purchase',
                'best buy', 'home depot', 'lowes', 'macys', 'nordstrom'
            ],
            'Utilities': [
                'electric', 'power', 'gas company', 'water', 'internet', 'phone',
                'cable', 'utility', 'verizon', 'att', 'comcast', 'xfinity'
            ],
            'Entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'movie', 'theater',
                'concert', 'game', 'entertainment', 'subscription'
            ],
            'Healthcare': [
                'pharmacy', 'doctor', 'hospital', 'medical', 'cvs', 'walgreens',
                'clinic', 'dental', 'vision'
            ],
            'Banking': [
                'atm fee', 'bank fee', 'overdraft', 'transfer', 'interest',
                'maintenance fee'
            ]
        }
        
        # Recurring payment patterns (amounts that appear regularly)
        self.recurring_patterns = {}
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """Categorize a transaction based on description and amount."""
        description_lower = description.lower()
        
        # Check for keyword matches
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        # Check for recurring payment patterns
        amount_str = f"{amount:.2f}"
        if amount_str in self.recurring_patterns:
            if self.recurring_patterns[amount_str] >= 2:  # Seen at least twice
                return 'Recurring Payments'
        else:
            self.recurring_patterns[amount_str] = 0
        
        self.recurring_patterns[amount_str] += 1
        
        # Default category
        return 'Other'


class BankCSVParser:
    """Parses bank CSV files and extracts transaction data."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
    
    def detect_csv_format(self, file_path: str) -> Optional[Tuple[str, str, str]]:
        """Detect CSV format and return column names for date, description, amount."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try different encodings if utf-8 fails
                try:
                    sample = file.read(1024)
                    file.seek(0)
                except UnicodeDecodeError:
                    file.close()
                    with open(file_path, 'r', encoding='latin-1') as file:
                        sample = file.read(1024)
                        file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                file.seek(0)
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                headers_lower = [h.lower().strip() for h in headers]
                
                # Find relevant columns
                date_col = None
                desc_col = None
                amount_col = None
                
                # Look for date column
                for i, header in enumerate(headers_lower):
                    if any(word in header for word in ['date', 'transaction date', 'posted date']):
                        date_col = headers[i]
                        break
                
                # Look for description column
                for i, header in enumerate(headers_lower):
                    if any(word in header for word in ['description', 'memo', 'merchant', 'payee']):
                        desc_col = headers[i]
                        break
                
                # Look for amount column
                for i, header in enumerate(headers_lower):
                    if any(word in header for word in ['amount', 'debit', 'withdrawal', 'charge']):
                        amount_col = headers[i]
                        break
                
                if not all([date_col, desc_col, amount_col]):
                    return None
                
                return (date_col, desc_col, amount_col)
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return 0.0
        
        # Remove currency symbols and extra spaces
        amount_str = re.sub(r'[$,\s]', '', amount_str.strip())
        
        # Handle negative amounts in parentheses
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            return float(amount_str)
        except ValueError:
            try:
                return float(Decimal(amount_str))
            except (InvalidOperation, ValueError):
                return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y',
            '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_csv_file(self, file_path: str) -> List[Dict]:
        """Parse CSV file and return list of transaction dictionaries."""
        format_info = self.detect_csv_format(file_path)
        if not format_info:
            raise ValueError("Could not detect CSV format or find required columns")
        
        date_col, desc_col, amount_col = format_info
        transactions = []
        
        try:
            # Try UTF-8 first, then fall back to latin-1