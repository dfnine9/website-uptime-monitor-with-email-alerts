```python
#!/usr/bin/env python3
"""
Transaction CSV Parser and Categorizer

This module provides functionality to parse CSV transaction data and automatically
categorize transactions based on merchant names and transaction amounts using
rule-based logic.

Features:
- Reads CSV files containing transaction data
- Categorizes transactions by merchant name patterns
- Applies amount-based rules for classification
- Handles various CSV formats and edge cases
- Provides detailed categorization statistics

Usage:
    python script.py

The script expects a CSV file with columns: date, merchant, amount, description (optional)
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Any
import io


class TransactionCategorizer:
    """Categorizes transactions based on merchant names and amounts."""
    
    def __init__(self):
        self.merchant_patterns = {
            'Grocery': [
                r'walmart', r'kroger', r'safeway', r'whole foods', r'trader joe',
                r'publix', r'food lion', r'harris teeter', r'giant', r'stop & shop',
                r'aldi', r'costco', r'sam\'s club', r'market', r'grocery'
            ],
            'Gas': [
                r'shell', r'exxon', r'bp', r'chevron', r'mobil', r'sunoco',
                r'citgo', r'marathon', r'speedway', r'wawa', r'gas', r'fuel'
            ],
            'Restaurant': [
                r'mcdonald', r'burger king', r'subway', r'taco bell', r'kfc',
                r'pizza', r'restaurant', r'cafe', r'bistro', r'diner', r'grill'
            ],
            'Shopping': [
                r'amazon', r'target', r'best buy', r'home depot', r'lowe\'s',
                r'macy\'s', r'nordstrom', r'tj maxx', r'marshall', r'store'
            ],
            'Entertainment': [
                r'netflix', r'spotify', r'hulu', r'disney', r'theater', r'cinema',
                r'movie', r'concert', r'tickets', r'entertainment'
            ],
            'Utilities': [
                r'electric', r'power', r'gas company', r'water', r'internet',
                r'cable', r'phone', r'utility', r'energy'
            ],
            'Banking': [
                r'bank', r'credit union', r'atm', r'fee', r'transfer', r'payment'
            ],
            'Healthcare': [
                r'pharmacy', r'cvs', r'walgreens', r'rite aid', r'hospital',
                r'clinic', r'doctor', r'medical', r'health'
            ]
        }
        
        self.amount_rules = [
            (lambda x: x < -500, 'Large Expense'),
            (lambda x: x > 1000, 'Large Deposit'),
            (lambda x: -50 <= x <= 50 and x != 0, 'Small Transaction'),
            (lambda x: x > 0, 'Income/Deposit'),
            (lambda x: x < 0, 'Expense')
        ]
    
    def categorize_by_merchant(self, merchant: str) -> str:
        """Categorize transaction based on merchant name patterns."""
        merchant_lower = merchant.lower()
        
        for category, patterns in self.merchant_patterns.items():
            for pattern in patterns:
                if re.search(pattern, merchant_lower):
                    return category
        
        return 'Other'
    
    def categorize_by_amount(self, amount: float) -> str:
        """Categorize transaction based on amount rules."""
        for rule, category in self.amount_rules:
            if rule(amount):
                return category
        
        return 'Unknown'
    
    def categorize_transaction(self, merchant: str, amount: float) -> Dict[str, str]:
        """Categorize a single transaction."""
        return {
            'merchant_category': self.categorize_by_merchant(merchant),
            'amount_category': self.categorize_by_amount(amount)
        }


class CSVTransactionParser:
    """Parses CSV transaction data and applies categorization rules."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
        self.categories = defaultdict(list)
        self.stats = {}
    
    def detect_csv_format(self, sample_lines: List[str]) -> Dict[str, int]:
        """Detect CSV format and column mapping."""
        if not sample_lines:
            raise ValueError("Empty CSV file")
        
        # Try to parse header
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample_lines[0]).delimiter
        
        header = sample_lines[0].split(delimiter)
        header = [col.strip().lower() for col in header]
        
        # Map common column variations
        column_map = {}
        for i, col in enumerate(header):
            if any(word in col for word in ['date', 'time']):
                column_map['date'] = i
            elif any(word in col for word in ['merchant', 'payee', 'description', 'vendor']):
                column_map['merchant'] = i
            elif any(word in col for word in ['amount', 'value', 'total']):
                column_map['amount'] = i
            elif any(word in col for word in ['desc', 'memo', 'note']):
                column_map['description'] = i
        
        if 'merchant' not in column_map or 'amount' not in column_map:
            # Try positional fallback
            if len(header) >= 3:
                column_map = {'date': 0, 'merchant': 1, 'amount': 2}
                if len(header) >= 4:
                    column_map['description'] = 3
        
        return column_map
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[^\d.-]', '', amount_str.strip())
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def parse_csv_file(self, filepath: str) -> bool:
        """Parse CSV file and categorize transactions."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                lines = content.strip().split('\n')
            
            if len(lines) < 2:
                print("Error: CSV file must have at least a header and one data row")
                return False
            
            # Detect format
            column_map = self.detect_csv_format(lines[:2])
            
            # Parse transactions
            csv_reader = csv.reader(lines[1:])  # Skip header
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    if len(row) < len(column_map):
                        continue
                    
                    merchant = row[column_map.get('merchant', 1)].strip()
                    amount = self.parse_amount(row[column_map.get('amount', 2)])
                    
                    date_str = row[column_map.get('date', 0)].strip() if 'date' in column_map else ''
                    description = row[column_map.get('description', -1)].strip() if 'description' in column_map else ''
                    
                    if not merchant:
                        continue
                    
                    # Categorize transaction
                    categories = self.categorizer.categorize_transaction(merchant, amount)
                    
                    transaction = {
                        'row': row_num,
                        'date': date_str,
                        'merchant': merchant,
                        'amount': amount,
                        'description': description,
                        'merchant_category': categories['merchant_category'],
                        'amount_category':