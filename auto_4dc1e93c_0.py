```python
#!/usr/bin/env python3
"""
CSV Transaction Parser and Categorizer

This script parses CSV files containing financial transactions, categorizes them
using keyword matching, and generates expense category summaries. It reads transaction
data from CSV files, applies predefined categorization rules based on description
keywords, and outputs summary statistics by category.

Features:
- Parses CSV files with transaction data (date, description, amount)
- Categorizes transactions using keyword matching
- Generates expense summaries by category
- Handles various CSV formats and encodings
- Provides detailed error handling and validation

Usage: python script.py [csv_file_path]
If no file path provided, uses sample data for demonstration.
"""

import csv
import re
import sys
from decimal import Decimal, InvalidOperation
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes transactions based on description keywords."""
    
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'pizza', 'burger', 'starbucks', 'dunkin',
                'mcdonalds', 'kfc', 'subway', 'chipotle', 'dominos', 'food',
                'dining', 'grocery', 'safeway', 'walmart', 'kroger', 'trader'
            ],
            'Transportation': [
                'gas', 'fuel', 'shell', 'exxon', 'bp', 'chevron', 'uber', 'lyft',
                'taxi', 'metro', 'bus', 'train', 'parking', 'toll', 'car wash'
            ],
            'Shopping': [
                'amazon', 'target', 'costco', 'ebay', 'walmart', 'bestbuy',
                'mall', 'store', 'shop', 'retail', 'purchase', 'clothing'
            ],
            'Entertainment': [
                'movie', 'cinema', 'theater', 'netflix', 'spotify', 'hulu',
                'disney', 'game', 'entertainment', 'concert', 'show'
            ],
            'Utilities': [
                'electric', 'gas bill', 'water', 'internet', 'cable', 'phone',
                'utility', 'verizon', 'att', 'comcast', 'power'
            ],
            'Healthcare': [
                'doctor', 'hospital', 'pharmacy', 'medical', 'dental',
                'health', 'cvs', 'walgreens', 'prescription'
            ],
            'Banking & Finance': [
                'bank', 'atm', 'fee', 'interest', 'transfer', 'payment',
                'finance', 'loan', 'credit'
            ]
        }
    
    def categorize(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'


class CSVTransactionParser:
    """Parses CSV files containing transaction data."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string to Decimal, handling various formats."""
        try:
            # Remove common currency symbols and whitespace
            cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string, trying common formats."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def detect_csv_format(self, file_path: str) -> Dict[str, int]:
        """Detect CSV column indices by examining headers."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try to detect dialect
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader, [])
                
                # Convert headers to lowercase for matching
                headers_lower = [h.lower().strip() for h in headers]
                
                column_map = {}
                
                # Find date column
                for i, header in enumerate(headers_lower):
                    if any(word in header for word in ['date', 'time', 'when']):
                        column_map['date'] = i
                        break
                
                # Find description column
                for i, header in enumerate(headers_lower):
                    if any(word in header for word in ['description', 'desc', 'memo', 'details', 'transaction']):
                        column_map['description'] = i
                        break
                
                # Find amount column
                for i, header in enumerate(headers_lower):
                    if any(word in header for word in ['amount', 'value', 'total', 'sum', 'debit', 'credit']):
                        column_map['amount'] = i
                        break
                
                return column_map
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return {}
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """Parse CSV file and return list of transaction dictionaries."""
        transactions = []
        
        try:
            column_map = self.detect_csv_format(file_path)
            
            if not all(key in column_map for key in ['date', 'description', 'amount']):
                print("Warning: Could not auto-detect all required columns. Using default indices.")
                column_map = {'date': 0, 'description': 1, 'amount': 2}
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header row
                
                for row_num, row in enumerate(reader, 2):
                    try:
                        if len(row) < max(column_map.values()) + 1:
                            print(f"Warning: Row {row_num} has insufficient columns, skipping")
                            continue
                        
                        date_str = row[column_map['date']]
                        description = row[column_map['description']]
                        amount_str = row[column_map['amount']]
                        
                        # Parse date
                        parsed_date = self.parse_date(date_str)
                        if not parsed_date:
                            print(f"Warning: Could not parse date '{date_str}' in row {row_num}")
                            continue
                        
                        # Parse amount
                        amount = self.parse_amount(amount_str)
                        if amount is None:
                            print(f"Warning: Could not parse amount '{amount_str}' in row {row_num}")
                            continue
                        
                        # Categorize transaction
                        category = self.categorizer.categorize(description)
                        
                        transactions.append({
                            'date': parsed_date,
                            'description': description.strip(),
                            'amount': amount,
                            'category': category
                        })
                    
                    except Exception as e: