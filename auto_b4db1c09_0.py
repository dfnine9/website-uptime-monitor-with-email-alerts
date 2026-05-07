```python
"""
Bank Transaction Categorizer and Analyzer

This module reads bank CSV files, categorizes transactions based on keywords,
and calculates monthly spending totals by category. It includes comprehensive
data validation and error handling.

Usage: python script.py

The script expects CSV files with columns: date, description, amount
Date format: YYYY-MM-DD or MM/DD/YYYY or DD/MM/YYYY
Amount format: numeric (negative for expenses, positive for income)
"""

import csv
import re
import os
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import glob


class TransactionCategorizer:
    """Categorizes bank transactions based on keyword matching."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'publix', 'aldi', 'food lion', 'giant',
                'market', 'grocery', 'supermarket', 'food', 'fresh'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'internet', 'cable', 'phone',
                'utility', 'power', 'energy', 'telecom', 'verizon', 'at&t', 
                'comcast', 'xfinity', 'spectrum'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'youtube',
                'movie', 'theater', 'cinema', 'concert', 'game', 'steam',
                'entertainment', 'subscription', 'streaming'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'parking', 'metro', 'transit',
                'car payment', 'auto', 'insurance'
            ],
            'dining': [
                'restaurant', 'mcdonald', 'burger king', 'starbucks', 'pizza',
                'cafe', 'bar', 'grill', 'kitchen', 'diner', 'fast food',
                'doordash', 'ubereats', 'grubhub'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'store', 'shop', 'retail',
                'clothing', 'shoes', 'electronics', 'home depot', 'lowes'
            ],
            'healthcare': [
                'doctor', 'hospital', 'pharmacy', 'medical', 'dental',
                'vision', 'health', 'clinic', 'cvs', 'walgreens'
            ],
            'finance': [
                'bank', 'credit card', 'loan', 'mortgage', 'interest',
                'fee', 'charge', 'payment', 'transfer', 'atm'
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


class BankCSVProcessor:
    """Processes bank CSV files and analyzes spending patterns."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
        
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats."""
        date_formats = [
            '%Y-%m-%d',      # 2023-12-31
            '%m/%d/%Y',      # 12/31/2023
            '%d/%m/%Y',      # 31/12/2023
            '%Y/%m/%d',      # 2023/12/31
            '%m-%d-%Y',      # 12-31-2023
            '%d-%m-%Y'       # 31-12-2023
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string, handling various formats."""
        try:
            # Remove common currency symbols and whitespace
            clean_amount = re.sub(r'[$,\s]', '', amount_str.strip())
            
            # Handle parentheses as negative (common in accounting)
            if clean_amount.startswith('(') and clean_amount.endswith(')'):
                clean_amount = '-' + clean_amount[1:-1]
            
            return float(clean_amount)
        except (ValueError, TypeError):
            return None
    
    def detect_csv_format(self, filepath: str) -> Optional[Tuple[int, int, int]]:
        """Detect CSV column indices for date, description, amount."""
        try:
            with open(filepath, 'r', newline='', encoding='utf-8-sig') as file:
                # Try to read first few rows to detect format
                sample_lines = [file.readline().strip() for _ in range(min(5, sum(1 for _ in file) + 1))]
                file.seek(0)
                
                reader = csv.reader(file)
                header = next(reader, None)
                
                if not header:
                    return None
                
                # Look for common column names
                date_col = description_col = amount_col = None
                
                for i, col_name in enumerate(header):
                    col_lower = col_name.lower().strip()
                    
                    if any(keyword in col_lower for keyword in ['date', 'trans date', 'posting date']):
                        date_col = i
                    elif any(keyword in col_lower for keyword in ['description', 'memo', 'payee', 'merchant']):
                        description_col = i
                    elif any(keyword in col_lower for keyword in ['amount', 'debit', 'credit', 'value']):
                        amount_col = i
                
                # If header detection failed, try positional detection
                if None in (date_col, description_col, amount_col):
                    # Common formats: date, description, amount OR date, amount, description
                    if len(header) >= 3:
                        date_col = 0
                        description_col = 1
                        amount_col = 2
                
                return (date_col, description_col, amount_col) if None not in (date_col, description_col, amount_col) else None
                
        except Exception:
            return None
    
    def load_csv(self, filepath: str) -> bool:
        """Load transactions from CSV file."""
        try:
            format_info = self.detect_csv_format(filepath)
            if not format_info:
                print(f"Error: Could not detect CSV format for {filepath}")
                return False
            
            date_col, desc_col, amount_col = format_info
            
            with open(filepath, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                header = next(reader, None)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(date_col, desc_col, amount_col):
                            continue
                        
                        date_obj = self.parse_date(row[date_col])
                        if not date_obj:
                            print(f"Warning: Invalid date in row {row_num}: {row[date_col]}")
                            continue
                        
                        description = row[desc_col].strip()
                        if not description:
                            description = "Unknown Transaction"
                        
                        amount = self.parse_amount(row[amount_col])
                        if amount is None: