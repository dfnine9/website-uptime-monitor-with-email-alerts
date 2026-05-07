```python
#!/usr/bin/env python3
"""
Transaction CSV Parser and Categorizer

This module parses CSV transaction files and automatically categorizes transactions
based on keyword matching rules. It generates JSON output showing spending categories
and monthly trends.

Features:
- Parses CSV files with transaction data
- Categorizes transactions using keyword-based rules
- Generates monthly spending trends
- Outputs results in JSON format
- Handles various CSV formats and edge cases

Usage:
    python script.py

The script expects a CSV file named 'transactions.csv' in the same directory.
CSV should have columns: date, description, amount (negative for expenses)
"""

import csv
import json
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import sys


class TransactionCategorizer:
    """Categorizes transactions based on keyword matching rules."""
    
    def __init__(self):
        self.category_rules = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'food',
                'dining', 'kitchen', 'meal', 'lunch', 'dinner', 'breakfast',
                'mcdonalds', 'subway', 'starbucks', 'grocery', 'supermarket',
                'safeway', 'kroger', 'walmart', 'trader joe', 'whole foods'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train',
                'metro', 'parking', 'toll', 'vehicle', 'car', 'auto',
                'shell', 'chevron', 'exxon', 'mobil', 'bp'
            ],
            'Shopping': [
                'amazon', 'target', 'costco', 'mall', 'store', 'retail',
                'shop', 'purchase', 'buy', 'clothing', 'apparel', 'shoes',
                'electronics', 'best buy', 'home depot', 'lowes'
            ],
            'Utilities': [
                'electric', 'electricity', 'gas bill', 'water', 'sewer',
                'internet', 'phone', 'mobile', 'cable', 'utility',
                'pge', 'comcast', 'verizon', 'at&t', 'sprint'
            ],
            'Healthcare': [
                'medical', 'doctor', 'hospital', 'pharmacy', 'dental',
                'health', 'clinic', 'medicine', 'prescription', 'cvs',
                'walgreens', 'rite aid'
            ],
            'Entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'hulu', 'disney',
                'entertainment', 'game', 'music', 'concert', 'event',
                'ticket', 'amusement', 'park'
            ],
            'Financial': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'credit',
                'payment', 'transfer', 'withdrawal', 'deposit'
            ],
            'Other': []  # Catch-all category
        }
    
    def categorize(self, description):
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.category_rules.items():
            if category == 'Other':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'


class TransactionParser:
    """Parses CSV transaction files and generates categorized analysis."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
    
    def parse_csv(self, filename):
        """Parse CSV file and extract transaction data."""
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Normalize column names (handle different formats)
                fieldnames = [field.lower().strip() for field in reader.fieldnames]
                
                for row in reader:
                    try:
                        # Normalize keys
                        normalized_row = {k.lower().strip(): v for k, v in row.items()}
                        
                        # Extract date (try multiple formats)
                        date_str = self._extract_date(normalized_row)
                        if not date_str:
                            continue
                        
                        transaction_date = self._parse_date(date_str)
                        if not transaction_date:
                            continue
                        
                        # Extract description
                        description = self._extract_description(normalized_row)
                        if not description:
                            continue
                        
                        # Extract amount
                        amount = self._extract_amount(normalized_row)
                        if amount is None:
                            continue
                        
                        transaction = {
                            'date': transaction_date,
                            'description': description,
                            'amount': amount,
                            'category': self.categorizer.categorize(description)
                        }
                        
                        self.transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Warning: Skipping invalid row: {e}", file=sys.stderr)
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Transaction file '{filename}' not found")
        except Exception as e:
            raise Exception(f"Error parsing CSV file: {e}")
    
    def _extract_date(self, row):
        """Extract date from row, trying multiple column names."""
        date_columns = ['date', 'transaction_date', 'posted_date', 'trans_date']
        for col in date_columns:
            if col in row and row[col]:
                return row[col].strip()
        return None
    
    def _extract_description(self, row):
        """Extract description from row, trying multiple column names."""
        desc_columns = ['description', 'memo', 'details', 'merchant', 'payee']
        for col in desc_columns:
            if col in row and row[col]:
                return row[col].strip()
        return None
    
    def _extract_amount(self, row):
        """Extract amount from row, trying multiple column names."""
        amount_columns = ['amount', 'debit', 'credit', 'transaction_amount']
        
        for col in amount_columns:
            if col in row and row[col]:
                try:
                    # Clean amount string
                    amount_str = re.sub(r'[,$\s]', '', row[col].strip())
                    if amount_str:
                        return float(amount_str)
                except ValueError:
                    continue
        
        # Try debit/credit columns separately
        debit = row.get('debit', '').strip()
        credit = row.get('credit', '').strip()
        
        if debit:
            try:
                return -abs(float(re.sub(r'[,$\s]', '', debit)))
            except ValueError:
                pass
        
        if credit:
            try:
                return abs(float(re.sub(r'[,$\s]', '', credit)))
            except ValueError:
                pass
        
        return None
    
    def _parse_date(self, date_str):
        """Parse date string in various formats."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d/%m/%y',
            '%Y/%m/%d', '%m-%d-%Y', '%m-%d-%y', '%d-%m-%Y', '%d-%m-%y'
        ]
        
        for fmt in date_formats:
            try:
                return