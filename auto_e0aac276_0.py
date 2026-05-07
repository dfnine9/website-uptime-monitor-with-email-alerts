```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statement files and categorizes transactions based on
keyword matching. It processes transaction data including dates, amounts, and
descriptions to automatically categorize expenses into predefined categories
such as groceries, gas, restaurants, utilities, etc.

The script supports multiple CSV formats and provides detailed categorization
results with transaction summaries by category.

Usage: python script.py
"""

import csv
import sys
import os
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions based on description keywords."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'publix', 'food lion', 'harris teeter',
                'giant', 'stop & shop', 'wegmans', 'aldi', 'target grocery',
                'grocery', 'supermarket', 'market', 'food store'
            ],
            'gas': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'texaco',
                'sunoco', 'valero', 'marathon', 'wawa', '7-eleven',
                'gas station', 'fuel', 'petrol'
            ],
            'restaurants': [
                'mcdonald', 'burger king', 'subway', 'starbucks', 'pizza',
                'restaurant', 'cafe', 'diner', 'bistro', 'grill',
                'kitchen', 'bar & grill', 'domino', 'taco bell',
                'kfc', 'wendy', 'chipotle', 'panera'
            ],
            'utilities': [
                'electric', 'electricity', 'gas company', 'water',
                'sewer', 'internet', 'cable', 'phone', 'verizon',
                'at&t', 'comcast', 'xfinity', 'utility', 'power company'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'disney+',
                'movie', 'theater', 'cinema', 'game', 'steam',
                'xbox', 'playstation', 'entertainment'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'metro',
                'parking', 'toll', 'dmv', 'car wash', 'auto repair'
            ],
            'shopping': [
                'amazon', 'ebay', 'target', 'best buy', 'home depot',
                'lowes', 'macy', 'nordstrom', 'mall', 'store'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'doctor', 'hospital',
                'medical', 'dental', 'vision', 'clinic'
            ],
            'banking': [
                'atm', 'fee', 'interest', 'transfer', 'deposit',
                'withdrawal', 'overdraft', 'maintenance'
            ]
        }
        
        self.transactions = []
        self.categorized_transactions = defaultdict(list)
        
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols, commas, and parentheses
            cleaned = re.sub(r'[$,()]', '', str(amount_str).strip())
            # Handle negative amounts in parentheses
            if amount_str.strip().startswith('(') and amount_str.strip().endswith(')'):
                cleaned = '-' + cleaned
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object, trying common formats."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y',
            '%Y/%m/%d', '%m/%d/%y', '%m-%d-%y', '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except (ValueError, AttributeError):
                continue
        return None
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords."""
        if not description:
            return 'uncategorized'
        
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
        
        return 'uncategorized'
    
    def read_csv_file(self, filepath: str) -> List[Dict]:
        """Read and parse CSV file, attempting to detect column structure."""
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = [h.lower().strip() for h in reader.fieldnames]
                
                # Map common column names
                date_cols = ['date', 'transaction date', 'posting date', 'trans date']
                amount_cols = ['amount', 'debit', 'credit', 'transaction amount']
                desc_cols = ['description', 'memo', 'transaction description', 'payee']
                
                date_col = next((col for col in headers if any(dc in col for dc in date_cols)), None)
                amount_col = next((col for col in headers if any(ac in col for ac in amount_cols)), None)
                desc_col = next((col for col in headers if any(dc in col for dc in desc_cols)), None)
                
                if not all([date_col, amount_col, desc_col]):
                    print(f"Warning: Could not identify all required columns in {filepath}")
                    print(f"Available columns: {headers}")
                    return transactions
                
                for row in reader:
                    try:
                        date_obj = self.parse_date(row[date_col]) if date_col else None
                        amount = self.parse_amount(row[amount_col]) if amount_col else 0.0
                        description = str(row[desc_col]).strip() if desc_col else ""
                        
                        if date_obj and description:
                            transaction = {
                                'date': date_obj,
                                'amount': amount,
                                'description': description,
                                'raw_row': row
                            }
                            transactions.append(transaction)
                    except Exception as e:
                        print(f"Error parsing row: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
        
        return transactions
    
    def process_files(self, file_paths: List[str]):
        """Process multiple CSV files and categorize all transactions."""
        all_transactions = []
        
        for filepath in file_paths:
            if os.path.exists(filepath):
                print(f"Processing {filepath}...")
                transactions = self.read_csv_file(filepath)
                all_transactions.extend(transactions)
                print(f"Loaded {len(transactions)} transactions from {filepath}")
            else:
                print(f"File not found: {filepath}")
        
        # Categorize all transactions
        for transaction in all_transactions:
            category = self.categorize_transaction(transaction['description'])
            transaction['category'] = category
            self.categorized_transactions[category].append(transaction)
        
        self.transactions = all_transactions