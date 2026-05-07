```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

This module parses bank CSV files and automatically categorizes transactions
based on keyword matching rules. It identifies common transaction columns
(date, description, amount) and applies predefined rules to categorize
expenses into common categories like groceries, gas, restaurants, utilities, etc.

Usage: python script.py [csv_file_path]
If no file path is provided, it will look for 'transactions.csv' in the current directory.
"""

import csv
import re
import sys
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    def __init__(self):
        # Categorization rules - keywords mapped to categories
        self.category_rules = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sams club', 'grocery', 'supermarket', 'food lion',
                'publix', 'wegmans', 'giant', 'stop shop', 'market'
            ],
            'gas': [
                'shell', 'bp', 'exxon', 'mobil', 'chevron', 'texaco', 'citgo',
                'sunoco', 'marathon', 'speedway', 'gas station', 'fuel'
            ],
            'restaurants': [
                'mcdonalds', 'burger king', 'subway', 'starbucks', 'pizza hut',
                'dominos', 'taco bell', 'kfc', 'restaurant', 'cafe', 'diner',
                'bistro', 'grill', 'bar', 'kitchen', 'eatery'
            ],
            'utilities': [
                'electric', 'power', 'gas company', 'water', 'sewer', 'internet',
                'cable', 'phone', 'wireless', 'utility', 'energy', 'comcast',
                'verizon', 'att', 'spectrum'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'subway', 'metro',
                'parking', 'toll', 'transit'
            ],
            'shopping': [
                'amazon', 'ebay', 'store', 'shop', 'retail', 'mall', 'outlet'
            ],
            'healthcare': [
                'doctor', 'hospital', 'clinic', 'pharmacy', 'cvs', 'walgreens',
                'medical', 'dental', 'vision', 'health'
            ],
            'entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'gym', 'fitness',
                'recreation', 'entertainment', 'club', 'concert'
            ],
            'banking': [
                'fee', 'atm', 'overdraft', 'interest', 'transfer', 'deposit',
                'withdrawal', 'payment'
            ]
        }

    def detect_csv_format(self, file_path: str) -> Tuple[Dict[str, int], str]:
        """
        Detect the CSV format and identify column positions for date, description, and amount.
        Returns a dictionary mapping column types to indices and the delimiter used.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try different delimiters
                delimiters = [',', ';', '\t']
                sample = file.read(1024)
                file.seek(0)
                
                best_delimiter = ','
                max_columns = 0
                
                for delimiter in delimiters:
                    dialect = csv.Sniffer().sniff(sample, delimiters=delimiter)
                    reader = csv.reader(file, dialect)
                    try:
                        header = next(reader)
                        if len(header) > max_columns:
                            max_columns = len(header)
                            best_delimiter = delimiter
                    except:
                        continue
                    file.seek(0)
                
                # Read header with best delimiter
                reader = csv.reader(file, delimiter=best_delimiter)
                header = next(reader)
                
                column_mapping = {}
                
                # Look for date column
                for i, col in enumerate(header):
                    col_lower = col.lower().strip()
                    if any(keyword in col_lower for keyword in ['date', 'transaction date', 'posted date']):
                        column_mapping['date'] = i
                        break
                
                # Look for description column
                for i, col in enumerate(header):
                    col_lower = col.lower().strip()
                    if any(keyword in col_lower for keyword in ['description', 'memo', 'payee', 'merchant', 'detail']):
                        column_mapping['description'] = i
                        break
                
                # Look for amount column
                for i, col in enumerate(header):
                    col_lower = col.lower().strip()
                    if any(keyword in col_lower for keyword in ['amount', 'debit', 'credit', 'transaction amount']):
                        column_mapping['amount'] = i
                        break
                
                return column_mapping, best_delimiter
                
        except Exception as e:
            raise Exception(f"Error detecting CSV format: {str(e)}")

    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols, commas, and parentheses
            cleaned = re.sub(r'[\$,\(\)]', '', str(amount_str).strip())
            
            # Handle negative amounts (sometimes in parentheses)
            if '(' in str(amount_str) and ')' in str(amount_str):
                cleaned = '-' + cleaned
            
            return float(cleaned)
        except:
            return 0.0

    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower().strip()
        
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'

    def parse_csv_file(self, file_path: str) -> List[Dict]:
        """Parse CSV file and return list of categorized transactions."""
        try:
            column_mapping, delimiter = self.detect_csv_format(file_path)
            
            if not all(key in column_mapping for key in ['date', 'description', 'amount']):
                raise Exception("Could not identify required columns (date, description, amount)")
            
            transactions = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=delimiter)
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(column_mapping.values()):
                            continue
                        
                        transaction = {
                            'date': row[column_mapping['date']].strip(),
                            'description': row[column_mapping['description']].strip(),
                            'amount': self.parse_amount(row[column_mapping['amount']]),
                            'category': self.categorize_transaction(row[column_mapping['description']])
                        }
                        
                        # Skip empty transactions
                        if transaction['description'] and transaction['amount'] != 0:
                            transactions.append(transaction)
                    
                    except Exception as e:
                        print(f"Warning: Error parsing row {row_num}: {str(e)}")
                        continue
            
            return transactions
            
        except Exception as e:
            raise Exception(f"Error parsing CSV file: {str(e)}")

    def generate_summary(self, transactions: List[Dict]) -> Dict:
        """Generate summary statistics by category."""
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        
        for transaction in transactions:
            category = transaction['category']