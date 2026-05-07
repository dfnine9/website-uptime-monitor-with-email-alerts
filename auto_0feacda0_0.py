```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

This module parses CSV bank transaction data and automatically categorizes transactions
by merchant patterns using regex matching. It assigns spending types such as groceries,
dining, utilities, entertainment, etc. based on merchant names and transaction descriptions.

The script reads CSV data from stdin or a file, applies pattern matching rules to categorize
each transaction, and outputs the results with assigned categories to stdout.

Usage: python script.py [csv_file]
If no file is provided, reads from stdin.
"""

import csv
import re
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class TransactionCategorizer:
    """Categorizes bank transactions based on merchant patterns."""
    
    def __init__(self):
        """Initialize categorizer with predefined merchant patterns."""
        self.category_patterns = {
            'groceries': [
                r'walmart', r'kroger', r'safeway', r'publix', r'whole foods',
                r'trader joe', r'costco', r'sam\'s club', r'food lion',
                r'wegmans', r'giant', r'harris teeter', r'market', r'grocery'
            ],
            'dining': [
                r'restaurant', r'mcdonald', r'burger king', r'kfc', r'taco bell',
                r'subway', r'pizza', r'cafe', r'coffee', r'starbucks',
                r'dunkin', r'chipotle', r'panera', r'chick-fil-a', r'domino'
            ],
            'utilities': [
                r'electric', r'gas company', r'water', r'internet', r'cable',
                r'phone', r'verizon', r'at&t', r'comcast', r'utility',
                r'power', r'energy'
            ],
            'entertainment': [
                r'netflix', r'spotify', r'hulu', r'disney', r'amazon prime',
                r'movie', r'theater', r'cinema', r'game', r'entertainment',
                r'youtube', r'apple music'
            ],
            'gas': [
                r'shell', r'exxon', r'bp', r'chevron', r'mobil', r'citgo',
                r'gas station', r'fuel', r'petroleum'
            ],
            'shopping': [
                r'amazon', r'target', r'best buy', r'home depot', r'lowes',
                r'macy', r'nordstrom', r'walmart', r'ebay', r'store'
            ],
            'healthcare': [
                r'hospital', r'pharmacy', r'cvs', r'walgreens', r'rite aid',
                r'medical', r'doctor', r'clinic', r'health'
            ],
            'transportation': [
                r'uber', r'lyft', r'taxi', r'metro', r'bus', r'train',
                r'parking', r'toll', r'transit'
            ],
            'banking': [
                r'bank', r'atm', r'fee', r'interest', r'transfer',
                r'withdrawal', r'deposit'
            ]
        }
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, description: str, merchant: str = "") -> str:
        """
        Categorize a transaction based on description and merchant name.
        
        Args:
            description: Transaction description
            merchant: Merchant name (optional)
            
        Returns:
            Category string or 'other' if no match found
        """
        text_to_search = f"{description} {merchant}".lower()
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text_to_search):
                    return category
        
        return 'other'


class CSVTransactionParser:
    """Parses CSV transaction data and applies categorization."""
    
    def __init__(self, categorizer: TransactionCategorizer):
        """Initialize parser with a categorizer instance."""
        self.categorizer = categorizer
    
    def parse_csv_data(self, csv_data: str) -> List[Dict]:
        """
        Parse CSV transaction data from string.
        
        Args:
            csv_data: CSV data as string
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        
        try:
            csv_reader = csv.DictReader(csv_data.strip().split('\n'))
            
            for row in csv_reader:
                # Normalize field names (handle different CSV formats)
                normalized_row = {}
                for key, value in row.items():
                    normalized_key = key.lower().strip()
                    normalized_row[normalized_key] = value.strip() if value else ""
                
                transactions.append(normalized_row)
                
        except Exception as e:
            raise ValueError(f"Error parsing CSV data: {str(e)}")
        
        return transactions
    
    def categorize_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """
        Apply categorization to list of transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of transactions with added category field
        """
        categorized = []
        
        for transaction in transactions:
            # Try different common field names for description/merchant
            description = (
                transaction.get('description', '') or
                transaction.get('desc', '') or
                transaction.get('memo', '') or
                transaction.get('transaction', '')
            )
            
            merchant = (
                transaction.get('merchant', '') or
                transaction.get('payee', '') or
                transaction.get('vendor', '') or
                ""
            )
            
            # Categorize the transaction
            category = self.categorizer.categorize_transaction(description, merchant)
            
            # Add category to transaction
            categorized_transaction = transaction.copy()
            categorized_transaction['category'] = category
            
            categorized.append(categorized_transaction)
        
        return categorized


def print_categorized_transactions(transactions: List[Dict]):
    """Print categorized transactions to stdout in a readable format."""
    if not transactions:
        print("No transactions found.")
        return
    
    # Print header
    print("=" * 80)
    print("CATEGORIZED BANK TRANSACTIONS")
    print("=" * 80)
    
    # Group by category for summary
    category_totals = {}
    category_counts = {}
    
    for transaction in transactions:
        category = transaction.get('category', 'unknown')
        amount_str = transaction.get('amount', '0')
        
        # Try to parse amount
        try:
            amount = float(amount_str.replace('$', '').replace(',', ''))
        except (ValueError, AttributeError):
            amount = 0.0
        
        if category not in category_totals:
            category_totals[category] = 0.0
            category_counts[category] = 0
        
        category_totals[category] += abs(amount)  # Use absolute value for spending
        category_counts[category] += 1
    
    # Print individual transactions
    print("\nTRANSACTION DETAILS:")
    print("-" * 80)
    
    for i, transaction in enumerate(transactions, 1):
        date = transaction.get('date', 'N/A')
        description = transaction.get('description', 
                     transaction.get('desc', 
                     transaction.get('memo', 'N/A')))
        amount = transaction.get('amount', 'N/A')
        category = transaction.get('category', 'unknown')
        
        print(f"{i:3d}. {date:12s} | {description:30s} | {amount:>10s} | {category.upper()}")
    
    # Print category summary
    print("\n" + "=" * 80)
    print("CATEGORY SUMMARY:")
    print("=" * 80)
    print(f"{'Category':<15}