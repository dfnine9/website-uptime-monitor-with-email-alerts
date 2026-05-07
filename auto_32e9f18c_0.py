```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Parser and Categorizer

This module parses CSV bank statement files and categorizes transactions based on
keyword matching. It extracts transaction data (date, amount, description) and
assigns categories like groceries, utilities, entertainment, etc.

Usage:
    python script.py

The script looks for CSV files in the current directory and processes them automatically.
Results are printed to stdout showing categorized transactions and summary statistics.
"""

import csv
import re
import os
import glob
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class TransactionCategorizer:
    """Categorizes bank transactions based on description keywords."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'grocery', 'supermarket', 'food', 'safeway', 'kroger', 'walmart',
                'whole foods', 'trader joe', 'costco', 'target', 'market', 'deli'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'internet', 'phone', 'cable',
                'utility', 'power', 'energy', 'telecom', 'verizon', 'att', 'comcast'
            ],
            'entertainment': [
                'movie', 'theater', 'cinema', 'netflix', 'spotify', 'hulu',
                'entertainment', 'game', 'music', 'concert', 'show', 'streaming'
            ],
            'dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'pizza',
                'bar', 'pub', 'diner', 'fast food', 'takeout', 'delivery'
            ],
            'transportation': [
                'gas station', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train',
                'metro', 'parking', 'toll', 'shell', 'exxon', 'chevron'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'store', 'retail', 'clothing',
                'department', 'online', 'purchase', 'buy'
            ],
            'healthcare': [
                'medical', 'doctor', 'pharmacy', 'hospital', 'clinic',
                'dental', 'health', 'prescription', 'cvs', 'walgreens'
            ],
            'banking': [
                'fee', 'atm', 'transfer', 'interest', 'deposit', 'withdrawal',
                'maintenance', 'overdraft', 'service charge'
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


class BankStatementParser:
    """Parses CSV bank statement files and extracts transaction data."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
    
    def detect_csv_format(self, filepath: str) -> Optional[Dict[str, int]]:
        """Detect CSV format by examining headers."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect dialect
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                
                reader = csv.reader(file, dialect)
                headers = next(reader)
                
                # Common header variations
                date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
                amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
                description_patterns = ['description', 'memo', 'details', 'transaction details']
                
                column_map = {}
                headers_lower = [h.lower().strip() for h in headers]
                
                # Find date column
                for i, header in enumerate(headers_lower):
                    for pattern in date_patterns:
                        if pattern in header:
                            column_map['date'] = i
                            break
                    if 'date' in column_map:
                        break
                
                # Find amount column
                for i, header in enumerate(headers_lower):
                    for pattern in amount_patterns:
                        if pattern in header:
                            column_map['amount'] = i
                            break
                    if 'amount' in column_map:
                        break
                
                # Find description column
                for i, header in enumerate(headers_lower):
                    for pattern in description_patterns:
                        if pattern in header:
                            column_map['description'] = i
                            break
                    if 'description' in column_map:
                        break
                
                return column_map if len(column_map) >= 3 else None
                
        except Exception as e:
            print(f"Error detecting CSV format for {filepath}: {e}")
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format attempts."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d/%m/%y',
            '%Y/%m/%d', '%m-%d-%Y', '%m-%d-%y', '%d-%m-%Y', '%d-%m-%y'
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
            # Remove currency symbols and whitespace
            clean_amount = re.sub(r'[^\d.-]', '', amount_str.replace(',', ''))
            return float(clean_amount)
        except (ValueError, TypeError):
            return None
    
    def parse_csv_file(self, filepath: str) -> List[Dict]:
        """Parse a CSV file and extract transactions."""
        transactions = []
        column_map = self.detect_csv_format(filepath)
        
        if not column_map:
            print(f"Could not detect format for {filepath}")
            return transactions
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Re-detect dialect
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                
                reader = csv.reader(file, dialect)
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(column_map.values()):
                            continue
                        
                        date_str = row[column_map['date']]
                        amount_str = row[column_map['amount']]
                        description = row[column_map['description']]
                        
                        parsed_date = self.parse_date(date_str)
                        parsed_amount = self.parse_amount(amount_str)
                        
                        if parsed_date and parsed_amount is not None and description:
                            category = self.categorizer.categorize(description)
                            
                            transactions.append({
                                'date': parsed_date,
                                'amount': parsed_amount,
                                'description': description.strip(),
                                'category': category,
                                'file': os.path.basename(filepath)
                            })
                    
                    except (IndexError, ValueError) as e:
                        print(f"Error parsing row {row_num} in {filepath}: {e}")
                        continue
        
        except Exception as e:
            print(f"Error reading {filepath}: {e