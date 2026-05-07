```python
#!/usr/bin/env python3
"""
Bank Statement Expense Categorizer

This module parses CSV bank statements and automatically categorizes expenses
using rule-based pattern matching. It identifies transactions across categories
including food, transport, utilities, entertainment, and shopping.

Features:
- Reads CSV files with transaction data
- Pattern-based categorization using merchant names and descriptions
- Handles various CSV formats commonly used by banks
- Provides summary statistics and uncategorized transaction reports
- Error handling for file operations and data parsing

Usage:
    python script.py [csv_file_path]

If no file path is provided, it will look for 'bank_statement.csv' in the current directory.
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional


class ExpenseCategorizer:
    """Rule-based expense categorizer for bank transactions."""
    
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                r'restaurant', r'cafe', r'pizza', r'burger', r'starbucks', r'subway',
                r'mcdonalds', r'kfc', r'taco bell', r'dominos', r'food', r'dining',
                r'bistro', r'grill', r'kitchen', r'eatery', r'deli', r'bakery',
                r'coffee', r'bar & grill', r'steakhouse', r'sushi', r'takeout',
                r'delivery', r'grubhub', r'doordash', r'uber eats', r'postmates'
            ],
            'Transport': [
                r'gas station', r'shell', r'bp', r'exxon', r'chevron', r'mobil',
                r'uber', r'lyft', r'taxi', r'metro', r'subway', r'bus', r'parking',
                r'toll', r'transport', r'airline', r'airport', r'car rental',
                r'hertz', r'enterprise', r'avis', r'budget', r'train', r'amtrak'
            ],
            'Utilities': [
                r'electric', r'electricity', r'power', r'gas company', r'water',
                r'sewer', r'trash', r'waste', r'internet', r'cable', r'phone',
                r'wireless', r'verizon', r'att', r'comcast', r'spectrum', r'utility',
                r'heating', r'cooling', r'energy', r'city of', r'municipal'
            ],
            'Entertainment': [
                r'netflix', r'spotify', r'hulu', r'disney', r'amazon prime',
                r'movie', r'theater', r'cinema', r'concert', r'music', r'game',
                r'steam', r'playstation', r'xbox', r'nintendo', r'entertainment',
                r'youtube', r'twitch', r'streaming', r'subscription', r'gym',
                r'fitness', r'club', r'spa', r'recreation'
            ],
            'Shopping': [
                r'amazon', r'walmart', r'target', r'costco', r'best buy',
                r'home depot', r'lowes', r'macys', r'nordstrom', r'kohls',
                r'store', r'shop', r'market', r'mall', r'retail', r'clothing',
                r'shoes', r'electronics', r'furniture', r'pharmacy', r'cvs',
                r'walgreens', r'rite aid', r'grocery', r'supermarket'
            ],
            'Healthcare': [
                r'hospital', r'clinic', r'doctor', r'medical', r'pharmacy',
                r'dental', r'vision', r'health', r'insurance', r'copay'
            ],
            'Financial': [
                r'bank', r'atm', r'fee', r'interest', r'transfer', r'payment',
                r'credit card', r'loan', r'mortgage', r'investment'
            ]
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.categories.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description or merchant name
            amount: Transaction amount (negative for expenses)
            
        Returns:
            Category name or 'Uncategorized'
        """
        if amount > 0:  # Income transactions
            return 'Income'
            
        description = description.lower().strip()
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(description):
                    return category
        
        return 'Uncategorized'


class BankStatementParser:
    """Parser for CSV bank statements with flexible column detection."""
    
    def __init__(self):
        self.categorizer = ExpenseCategorizer()
        
    def detect_csv_format(self, file_path: str) -> Tuple[List[str], Dict[str, int]]:
        """
        Detect CSV format and column mappings.
        
        Returns:
            Tuple of (headers, column_mapping)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                
                # Normalize headers for mapping
                headers_lower = [h.lower().strip() for h in headers]
                
                column_mapping = {}
                
                # Map common column variations
                for i, header in enumerate(headers_lower):
                    if any(word in header for word in ['date', 'transaction date', 'posted date']):
                        column_mapping['date'] = i
                    elif any(word in header for word in ['description', 'merchant', 'payee', 'memo']):
                        column_mapping['description'] = i
                    elif any(word in header for word in ['amount', 'debit', 'credit']):
                        if 'amount' not in column_mapping:
                            column_mapping['amount'] = i
                    elif 'debit' in header and header not in ['debit card']:
                        column_mapping['debit'] = i
                    elif 'credit' in header and header not in ['credit card']:
                        column_mapping['credit'] = i
                
                return headers, column_mapping
                
        except Exception as e:
            raise ValueError(f"Error detecting CSV format: {e}")
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return 0.0
            
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[^\d.,-]', '', amount_str.strip())
        
        # Handle negative amounts in parentheses
        if amount_str.strip().startswith('(') and amount_str.strip().endswith(')'):
            cleaned = '-' + cleaned
        
        # Handle comma as thousand separator
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace(',', '')
        elif cleaned.count(',') == 1 and len(cleaned.split(',')[1]) <= 2:
            # Comma as decimal separator
            cleaned = cleaned.replace(',', '.')
        else:
            # Comma as thousand separator
            cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date