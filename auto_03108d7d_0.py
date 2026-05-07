```python
#!/usr/bin/env python3
"""
Bank Transaction Categorization Script

This script reads bank CSV files and categorizes transactions using regex-based rules.
It processes transaction data, applies predefined categorization patterns for common
spending categories (groceries, utilities, entertainment, transport, etc.), and
outputs the categorized data in a structured JSON format.

Features:
- Reads CSV files with bank transaction data
- Applies regex-based categorization rules
- Handles multiple CSV formats with flexible column mapping
- Outputs structured JSON data to stdout
- Includes comprehensive error handling

Usage:
    python script.py

The script expects CSV files in the current directory with transaction data.
"""

import csv
import json
import re
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional


class TransactionCategorizer:
    """Categorizes bank transactions using regex-based rules."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                r'walmart', r'kroger', r'safeway', r'whole foods', r'trader joe',
                r'grocery', r'market', r'food lion', r'publix', r'wegmans',
                r'aldi', r'costco', r'sam\'s club', r'target.*grocery'
            ],
            'utilities': [
                r'electric', r'gas company', r'water', r'sewer', r'internet',
                r'comcast', r'verizon', r'at&t', r'spectrum', r'utility',
                r'power', r'energy', r'cable', r'phone'
            ],
            'entertainment': [
                r'netflix', r'hulu', r'disney', r'spotify', r'amazon prime',
                r'movie', r'theater', r'cinema', r'concert', r'game',
                r'entertainment', r'streaming', r'music', r'youtube'
            ],
            'transport': [
                r'gas station', r'shell', r'exxon', r'bp', r'chevron',
                r'uber', r'lyft', r'taxi', r'metro', r'transit',
                r'parking', r'toll', r'auto', r'car wash', r'fuel'
            ],
            'dining': [
                r'restaurant', r'mcdonald', r'burger king', r'starbucks',
                r'pizza', r'cafe', r'diner', r'food', r'kitchen',
                r'grill', r'bar', r'pub', r'dining'
            ],
            'shopping': [
                r'amazon', r'ebay', r'store', r'shop', r'retail',
                r'mall', r'boutique', r'clothing', r'apparel'
            ],
            'healthcare': [
                r'hospital', r'doctor', r'pharmacy', r'medical',
                r'health', r'dental', r'clinic', r'cvs', r'walgreens'
            ],
            'banking': [
                r'atm fee', r'bank fee', r'overdraft', r'interest',
                r'transfer', r'deposit', r'withdrawal'
            ]
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.categories.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description = description.lower().strip()
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(description):
                    return category
        
        return 'other'


class CSVProcessor:
    """Processes bank CSV files and extracts transaction data."""
    
    def __init__(self):
        self.possible_headers = {
            'date': ['date', 'transaction date', 'posted date', 'trans date'],
            'description': ['description', 'memo', 'payee', 'merchant', 'details'],
            'amount': ['amount', 'debit', 'credit', 'transaction amount', 'value'],
            'balance': ['balance', 'running balance', 'account balance']
        }
    
    def detect_csv_format(self, filepath: str) -> Optional[Dict[str, str]]:
        """Detect CSV format and return column mappings."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try different delimiters
                for delimiter in [',', ';', '\t']:
                    file.seek(0)
                    sample = file.read(1024)
                    if delimiter in sample:
                        file.seek(0)
                        reader = csv.reader(file, delimiter=delimiter)
                        headers = next(reader, [])
                        
                        if len(headers) >= 3:  # Minimum viable CSV
                            return self._map_headers(headers)
            
            return None
            
        except Exception as e:
            print(f"Error detecting CSV format for {filepath}: {e}", file=sys.stderr)
            return None
    
    def _map_headers(self, headers: List[str]) -> Dict[str, str]:
        """Map CSV headers to standard field names."""
        headers_lower = [h.lower().strip() for h in headers]
        mapping = {}
        
        for field, possible_names in self.possible_headers.items():
            for i, header in enumerate(headers_lower):
                if any(name in header for name in possible_names):
                    mapping[field] = headers[i]
                    break
        
        return mapping
    
    def read_csv_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Read and parse CSV file."""
        column_mapping = self.detect_csv_format(filepath)
        if not column_mapping:
            raise ValueError(f"Could not detect valid CSV format in {filepath}")
        
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                delimiter = ',' if ',' in sample else ';' if ';' in sample else '\t'
                
                file.seek(0)
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        transaction = self._parse_transaction_row(row, column_mapping)
                        if transaction:
                            transactions.append(transaction)
                    except Exception as e:
                        print(f"Warning: Error parsing row {row_num} in {filepath}: {e}", 
                              file=sys.stderr)
                        continue
        
        except Exception as e:
            raise Exception(f"Error reading CSV file {filepath}: {e}")
        
        return transactions
    
    def _parse_transaction_row(self, row: Dict[str, str], mapping: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Parse a single transaction row."""
        try:
            # Extract required fields
            date_str = row.get(mapping.get('date', ''), '').strip()
            description = row.get(mapping.get('description', ''), '').strip()
            amount_str = row.get(mapping.get('amount', ''), '').strip()
            
            if not all([date_str, description, amount_str]):
                return None
            
            # Parse date
            date = self._parse_date(date_str)
            
            # Parse amount
            amount = self._parse_amount(amount_str)
            
            # Extract balance if available
            balance = None
            if 'balance' in mapping:
                balance_str = row.get(mapping['balance'], '').strip()
                if balance_str:
                    balance = self._parse_amount(balance_str)
            
            return {
                'date': date.isoformat() if date else date_str,
                'description': description,
                'amount': amount,
                'balance': balance,
                'raw_row': dict(row)  # Keep original data for reference
            }
            
        except