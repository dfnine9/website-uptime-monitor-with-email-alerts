```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements, extracts transaction data, and automatically
categorizes expenses by matching description keywords to predefined categories.

Features:
- Reads CSV files with transaction data
- Categorizes transactions based on description keywords
- Handles various CSV formats automatically
- Provides summary statistics by category
- Includes error handling for malformed data

Usage:
    python script.py

The script will look for CSV files in the current directory and process them.
"""

import csv
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions based on description keywords."""
    
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'food', 'dining',
                'mcdonalds', 'subway', 'starbucks', 'dominos', 'uber eats', 'doordash',
                'grubhub', 'takeout', 'delivery', 'bistro', 'grill', 'kitchen'
            ],
            'Groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'costco', 'safeway',
                'kroger', 'whole foods', 'trader joes', 'market', 'fresh', 'produce'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus', 'train',
                'parking', 'toll', 'car wash', 'auto', 'vehicle', 'transportation'
            ],
            'Shopping': [
                'amazon', 'ebay', 'store', 'retail', 'shopping', 'purchase',
                'clothing', 'apparel', 'shoes', 'electronics', 'home depot', 'lowes'
            ],
            'Bills & Utilities': [
                'electric', 'electricity', 'gas bill', 'water', 'internet', 'phone',
                'cable', 'utility', 'bill', 'payment', 'service', 'monthly'
            ],
            'Entertainment': [
                'movie', 'cinema', 'theater', 'netflix', 'spotify', 'gaming',
                'entertainment', 'concert', 'show', 'event', 'tickets'
            ],
            'Healthcare': [
                'pharmacy', 'doctor', 'medical', 'hospital', 'clinic', 'dentist',
                'health', 'prescription', 'insurance', 'copay'
            ],
            'Banking & Finance': [
                'bank', 'atm', 'fee', 'interest', 'transfer', 'withdrawal',
                'deposit', 'check', 'finance', 'loan', 'credit'
            ],
            'Income': [
                'salary', 'payroll', 'deposit', 'income', 'refund', 'cashback',
                'dividend', 'bonus', 'earnings'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        # Check each category for keyword matches
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'


class BankStatementParser:
    """Parses CSV bank statements and extracts transaction data."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def detect_csv_format(self, file_path: str) -> Dict[str, int]:
        """Detect the column indices for common CSV formats."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first few lines to detect format
                sample_lines = [file.readline().strip() for _ in range(3)]
                
            # Common column name patterns
            date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
            description_patterns = ['description', 'memo', 'details', 'transaction', 'payee']
            amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
            
            header = sample_lines[0].lower()
            columns = [col.strip().strip('"') for col in header.split(',')]
            
            format_map = {}
            
            # Find column indices
            for i, col in enumerate(columns):
                if any(pattern in col for pattern in date_patterns):
                    format_map['date'] = i
                elif any(pattern in col for pattern in description_patterns):
                    format_map['description'] = i
                elif any(pattern in col for pattern in amount_patterns):
                    if 'amount' not in format_map:
                        format_map['amount'] = i
            
            return format_map
            
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return {}
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols, commas, and extra spaces
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%m-%d-%Y', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_csv_file(self, file_path: str) -> List[Dict]:
        """Parse a CSV file and extract transactions."""
        transactions = []
        
        try:
            format_map = self.detect_csv_format(file_path)
            
            if not format_map:
                print(f"Could not detect format for {file_path}")
                return transactions
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Skip header
                
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        if len(row) <= max(format_map.values()):
                            continue
                        
                        # Extract data based on detected format
                        date_str = row[format_map.get('date', 0)]
                        description = row[format_map.get('description', 1)]
                        amount_str = row[format_map.get('amount', 2)]
                        
                        # Parse and validate data
                        transaction_date = self.parse_date(date_str)
                        if not transaction_date:
                            continue
                        
                        amount = self.parse_amount(amount_str)
                        if amount == 0.0 and amount_str.strip():
                            continue
                        
                        # Categorize transaction
                        category = self.categorizer.categorize_transaction(description)
                        
                        transaction = {
                            'date': transaction_date,
                            'description': description.strip(),
                            'amount': amount,
                            'category': category,
                            'file': os.path.basename(file_path)
                        }
                        
                        transactions.append(transaction)
                        
                    except (IndexError, ValueError