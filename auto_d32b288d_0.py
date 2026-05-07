```python
"""
Transaction Categorization System

This module provides a CSV parser for transaction data with intelligent rule-based 
categorization using regex patterns. It automatically categorizes transactions based 
on merchant names, amounts, and transaction descriptions using predefined patterns 
for common spending categories like groceries, restaurants, gas stations, etc.

Features:
- CSV parsing with flexible column detection
- Regex-based merchant pattern matching
- Amount-based categorization rules
- Comprehensive error handling
- Configurable category rules
- Summary reporting

Usage: python script.py
"""

import csv
import re
import sys
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, InvalidOperation
import io

class TransactionCategorizer:
    def __init__(self):
        """Initialize the categorizer with predefined rules."""
        self.category_patterns = {
            'Groceries': [
                r'walmart.*super',
                r'kroger',
                r'safeway',
                r'whole foods',
                r'trader joe',
                r'publix',
                r'harris teeter',
                r'food lion',
                r'giant eagle',
                r'meijer',
                r'aldi',
                r'costco',
                r'sams club',
                r'target.*grocery',
                r'grocery.*store'
            ],
            'Restaurants': [
                r'mcdonalds?',
                r'burger king',
                r'subway',
                r'taco bell',
                r'kfc',
                r'pizza hut',
                r'dominos',
                r'starbucks',
                r'dunkin',
                r'chipotle',
                r'panera',
                r'olive garden',
                r'applebees',
                r'chilis',
                r'restaurant',
                r'cafe',
                r'bistro',
                r'grill',
                r'diner',
                r'bar & grill'
            ],
            'Gas': [
                r'shell',
                r'exxon',
                r'bp\b',
                r'chevron',
                r'mobil',
                r'texaco',
                r'citgo',
                r'marathon',
                r'sunoco',
                r'valero',
                r'gas station',
                r'fuel',
                r'pump \d+'
            ],
            'Shopping': [
                r'amazon',
                r'target',
                r'walmart(?!.*super)',
                r'best buy',
                r'home depot',
                r'lowes',
                r'macys',
                r'nordstrom',
                r'kohls',
                r'tj maxx',
                r'marshalls',
                r'ross',
                r'old navy',
                r'gap',
                r'cvs',
                r'walgreens',
                r'rite aid'
            ],
            'Entertainment': [
                r'netflix',
                r'hulu',
                r'spotify',
                r'apple music',
                r'amazon prime',
                r'disney\+?',
                r'hbo',
                r'movie',
                r'cinema',
                r'theater',
                r'theatre',
                r'amc',
                r'regal',
                r'ticket'
            ],
            'Transportation': [
                r'uber',
                r'lyft',
                r'taxi',
                r'metro',
                r'bus',
                r'train',
                r'parking',
                r'toll',
                r'transit'
            ],
            'Utilities': [
                r'electric',
                r'gas company',
                r'water',
                r'sewer',
                r'internet',
                r'cable',
                r'phone',
                r'cellular',
                r'verizon',
                r'att',
                r'tmobile',
                r'sprint',
                r'comcast',
                r'xfinity'
            ],
            'Healthcare': [
                r'pharmacy',
                r'cvs.*pharmacy',
                r'walgreens.*pharmacy',
                r'hospital',
                r'medical',
                r'doctor',
                r'dentist',
                r'dental',
                r'clinic',
                r'health'
            ],
            'Banking': [
                r'atm.*fee',
                r'overdraft',
                r'monthly.*fee',
                r'maintenance.*fee',
                r'transfer.*fee',
                r'wire.*fee',
                r'interest.*charge'
            ]
        }
        
        # Compile regex patterns for performance
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, description: str, amount: str) -> str:
        """
        Categorize a transaction based on description and amount.
        
        Args:
            description: Transaction description/merchant name
            amount: Transaction amount as string
            
        Returns:
            Category name or 'Other' if no match found
        """
        if not description:
            return 'Other'
        
        # Clean description for better matching
        clean_desc = description.strip().lower()
        
        # Try to match against patterns
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(clean_desc):
                    return category
        
        # Amount-based rules for edge cases
        try:
            amount_val = abs(float(amount.replace('$', '').replace(',', '')))
            
            # Small amounts at common merchants might be coffee/snacks
            if amount_val < 10 and any(word in clean_desc for word in ['store', 'mart', 'shop']):
                return 'Food & Beverages'
            
            # Large amounts might be rent/mortgage if no other category matched
            if amount_val > 1000:
                return 'Housing'
                
        except (ValueError, AttributeError):
            pass
        
        return 'Other'

class TransactionParser:
    def __init__(self):
        """Initialize the parser with a categorizer."""
        self.categorizer = TransactionCategorizer()
        self.transactions = []
        self.category_stats = {}
    
    def detect_csv_format(self, sample_lines: List[str]) -> Dict[str, int]:
        """
        Detect CSV column format by analyzing headers.
        
        Args:
            sample_lines: First few lines of CSV
            
        Returns:
            Dictionary mapping column types to indices
        """
        if not sample_lines:
            raise ValueError("No sample lines provided")
        
        # Try to parse header line
        try:
            reader = csv.reader([sample_lines[0]])
            headers = next(reader)
        except (csv.Error, StopIteration):
            raise ValueError("Could not parse CSV header")
        
        # Normalize headers for matching
        normalized_headers = [h.lower().strip() for h in headers]
        
        column_map = {}
        
        # Look for common column patterns
        for i, header in enumerate(normalized_headers):
            if any(keyword in header for keyword in ['date', 'transaction date', 'posted']):
                column_map['date'] = i
            elif any(keyword in header for keyword in ['description', 'merchant', 'payee', 'memo']):
                column_map['description'] = i
            elif any(keyword in header for keyword in ['amount', 'debit', 'credit', 'transaction amount']):
                if 'amount' not in column_map:  # Take first amount column
                    column_map['amount'] = i
        
        # Validate required columns
        required = ['description', 'amount']
        missing = [col for col in required if col not in column_map]
        if missing:
            print(f"Warning: Could not detect columns: {missing}")
            print(f"Available headers: {headers}")
            
            # Fallback: assume standard order
            if len(headers) >= 2:
                column_map['description'] = 0
                column_map['amount'] = 1
                if len(headers) >= 3:
                    column_map['date'] =