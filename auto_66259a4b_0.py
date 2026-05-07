```python
#!/usr/bin/env python3
"""
Bank Statement Categorizer

This script reads CSV bank statement files and categorizes transactions based on keywords.
It parses transaction data including date, description, and amount, then applies predefined
rules to categorize expenses into common categories like groceries, gas, restaurants, utilities, etc.

The script is self-contained and only requires Python's standard library.
Results are printed to stdout showing categorized transactions and summary statistics.

Usage: python script.py
"""

import csv
import re
import os
from datetime import datetime
from collections import defaultdict
from pathlib import Path


class BankStatementCategorizer:
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joes',
                'costco', 'sams club', 'grocery', 'market', 'food store', 'supermarket',
                'publix', 'wegmans', 'harris teeter', 'giant', 'stop shop', 'aldi'
            ],
            'gas': [
                'shell', 'exxon', 'mobil', 'chevron', 'bp', 'citgo', 'sunoco',
                'texaco', 'marathon', 'speedway', 'gas station', 'fuel', 'petrol'
            ],
            'restaurants': [
                'restaurant', 'mcdonalds', 'burger king', 'subway', 'starbucks',
                'pizza', 'taco bell', 'kfc', 'wendys', 'chipotle', 'panera',
                'dominos', 'papa johns', 'dunkin', 'cafe', 'diner', 'bistro'
            ],
            'utilities': [
                'electric', 'electricity', 'gas company', 'water', 'sewer',
                'internet', 'cable', 'phone', 'cellular', 'verizon', 'att',
                'comcast', 'xfinity', 'spectrum', 'utility', 'power company'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'hulu', 'disney',
                'movie', 'theater', 'cinema', 'concert', 'show', 'entertainment'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'medical', 'doctor',
                'dentist', 'clinic', 'health', 'prescription'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'parking',
                'toll', 'transit', 'transportation'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes', 'macy',
                'nordstrom', 'shopping', 'retail', 'store'
            ],
            'banking': [
                'atm fee', 'bank fee', 'overdraft', 'interest', 'transfer',
                'service charge', 'monthly fee'
            ]
        }
        
        self.transactions = []
        self.categorized_transactions = defaultdict(list)
        self.totals_by_category = defaultdict(float)

    def find_csv_files(self, directory='.'):
        """Find all CSV files in the specified directory."""
        try:
            csv_files = list(Path(directory).glob('*.csv'))
            return csv_files
        except Exception as e:
            print(f"Error finding CSV files: {e}")
            return []

    def parse_csv_file(self, filepath):
        """Parse a CSV file and extract transaction data."""
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect the CSV format by examining the first few lines
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader, None)
                
                if not headers:
                    print(f"Warning: No headers found in {filepath}")
                    return transactions
                
                # Convert headers to lowercase for easier matching
                headers = [h.lower().strip() for h in headers]
                
                # Find column indices
                date_col = self.find_column_index(headers, ['date', 'transaction date', 'posted date'])
                desc_col = self.find_column_index(headers, ['description', 'desc', 'merchant', 'payee'])
                amount_col = self.find_column_index(headers, ['amount', 'debit', 'credit', 'transaction amount'])
                
                if date_col is None or desc_col is None or amount_col is None:
                    print(f"Warning: Could not find required columns in {filepath}")
                    print(f"Headers found: {headers}")
                    return transactions
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) <= max(date_col, desc_col, amount_col):
                        continue
                    
                    try:
                        date_str = row[date_col].strip()
                        description = row[desc_col].strip()
                        amount_str = row[amount_col].strip()
                        
                        # Parse date
                        transaction_date = self.parse_date(date_str)
                        if not transaction_date:
                            continue
                        
                        # Parse amount
                        amount = self.parse_amount(amount_str)
                        if amount is None:
                            continue
                        
                        transactions.append({
                            'date': transaction_date,
                            'description': description,
                            'amount': amount,
                            'source_file': filepath.name
                        })
                        
                    except Exception as e:
                        print(f"Error parsing row {row_num} in {filepath}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            
        return transactions

    def find_column_index(self, headers, possible_names):
        """Find the index of a column based on possible names."""
        for name in possible_names:
            for i, header in enumerate(headers):
                if name in header:
                    return i
        return None

    def parse_date(self, date_str):
        """Parse date string into datetime object."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d/%m/%y',
            '%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        print(f"Warning: Could not parse date: {date_str}")
        return None

    def parse_amount(self, amount_str):
        """Parse amount string into float."""
        try:
            # Remove currency symbols, commas, and spaces
            cleaned = re.sub(r'[$,\s]', '', amount_str)
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            print(f"Warning: Could not parse amount: {amount_str}")
            return None

    def categorize_transaction(self, description):
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'

    def process_transactions(self):
        """Categorize all transactions and calculate totals."""
        for transaction in self.transactions:
            category = self.categor