```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

This module reads CSV bank transaction files and automatically categorizes transactions
based on configurable keyword matching rules. It supports common expense categories
like groceries, utilities, entertainment, etc.

Features:
- Configurable category mappings via dictionary
- Keyword-based transaction categorization
- CSV file processing with error handling
- Summary statistics and reporting
- Self-contained with minimal dependencies

Usage:
    python script.py

The script looks for a 'transactions.csv' file in the current directory with columns:
Date, Description, Amount (negative for expenses, positive for income)
"""

import csv
import sys
from collections import defaultdict
from datetime import datetime
import re


class TransactionCategorizer:
    """Categorizes bank transactions based on keyword matching rules."""
    
    def __init__(self):
        """Initialize with default category mappings."""
        self.category_mappings = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'publix', 'aldi', 'food lion', 'wegmans',
                'harris teeter', 'giant', 'stop shop', 'market', 'grocery'
            ],
            'utilities': [
                'electric', 'gas company', 'water', 'internet', 'phone', 'cellular',
                'verizon', 'att', 'comcast', 'xfinity', 'spectrum', 'utility',
                'power', 'energy', 'telecom'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'disney', 'hulu', 'apple music',
                'youtube', 'movies', 'theater', 'cinema', 'concert', 'event',
                'entertainment', 'streaming', 'subscription'
            ],
            'restaurants': [
                'restaurant', 'mcdonald', 'burger king', 'kfc', 'taco bell', 'subway',
                'pizza', 'starbucks', 'dunkin', 'cafe', 'diner', 'grill', 'bar',
                'food delivery', 'doordash', 'uber eats', 'grubhub'
            ],
            'transportation': [
                'gas', 'fuel', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'parking',
                'toll', 'dmv', 'auto', 'car wash'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes', 'macy',
                'nordstrom', 'tj maxx', 'ross', 'clothing', 'retail', 'store',
                'mall', 'outlet'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'medical', 'doctor',
                'hospital', 'clinic', 'dental', 'vision', 'insurance', 'health'
            ],
            'income': [
                'salary', 'payroll', 'deposit', 'refund', 'interest', 'dividend',
                'bonus', 'commission', 'freelance', 'payment received'
            ],
            'banking': [
                'fee', 'atm', 'overdraft', 'maintenance', 'wire', 'transfer',
                'check', 'deposit fee', 'service charge'
            ]
        }
        
        self.transactions = []
        self.categorized_transactions = []
        
    def add_category_mapping(self, category, keywords):
        """Add or update category mapping with new keywords."""
        if category in self.category_mappings:
            self.category_mappings[category].extend(keywords)
        else:
            self.category_mappings[category] = keywords
    
    def categorize_transaction(self, description, amount):
        """Categorize a single transaction based on description and amount."""
        description_lower = description.lower()
        
        # Special handling for income (positive amounts)
        if float(amount) > 0:
            for keyword in self.category_mappings.get('income', []):
                if keyword in description_lower:
                    return 'income'
            return 'income'  # Default positive amounts to income
        
        # Check each category for keyword matches
        for category, keywords in self.category_mappings.items():
            if category == 'income':  # Skip income for negative amounts
                continue
                
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'  # Default category for unmatched transactions
    
    def read_csv_file(self, filename):
        """Read and parse CSV transaction file."""
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Handle different possible column names
                fieldnames = reader.fieldnames
                date_col = None
                desc_col = None
                amount_col = None
                
                for field in fieldnames:
                    field_lower = field.lower()
                    if 'date' in field_lower:
                        date_col = field
                    elif 'desc' in field_lower or 'description' in field_lower:
                        desc_col = field
                    elif 'amount' in field_lower or 'value' in field_lower:
                        amount_col = field
                
                if not all([date_col, desc_col, amount_col]):
                    raise ValueError(f"Could not identify required columns. Found: {fieldnames}")
                
                for row in reader:
                    try:
                        transaction = {
                            'date': row[date_col],
                            'description': row[desc_col],
                            'amount': float(row[amount_col])
                        }
                        self.transactions.append(transaction)
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping invalid row: {row}. Error: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
            
        return True
    
    def process_transactions(self):
        """Process and categorize all transactions."""
        for transaction in self.transactions:
            category = self.categorize_transaction(
                transaction['description'], 
                transaction['amount']
            )
            
            categorized = transaction.copy()
            categorized['category'] = category
            self.categorized_transactions.append(categorized)
    
    def generate_summary(self):
        """Generate summary statistics by category."""
        summary = defaultdict(lambda: {'count': 0, 'total': 0.0})
        
        for transaction in self.categorized_transactions:
            category = transaction['category']
            amount = transaction['amount']
            
            summary[category]['count'] += 1
            summary[category]['total'] += amount
        
        return dict(summary)
    
    def print_results(self):
        """Print categorized transactions and summary to stdout."""
        print("=" * 80)
        print("BANK TRANSACTION CATEGORIZER RESULTS")
        print("=" * 80)
        print()
        
        print(f"Total transactions processed: {len(self.categorized_transactions)}")
        print()
        
        # Print categorized transactions
        print("CATEGORIZED TRANSACTIONS:")
        print("-" * 80)
        print(f"{'Date':<12} {'Category':<15} {'Amount':<12} {'Description':<30}")
        print("-" * 80)
        
        for transaction in self.