```python
"""
CSV Transaction Categorizer

This module parses CSV files containing transaction data and categorizes each transaction
based on keyword matching. It reads transaction data from a CSV file, applies predefined
category rules using keyword matching, and outputs categorized results to stdout.

Features:
- Parses CSV files with transaction data (amount, description, date)
- Categorizes transactions using configurable keyword matching
- Handles various CSV formats and encoding issues
- Provides summary statistics and detailed transaction listings
- Self-contained with minimal dependencies

Usage:
    python script.py [csv_file_path]
    
If no file path is provided, it will look for 'transactions.csv' in the current directory.
"""

import csv
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import re


class TransactionCategorizer:
    """Categorizes financial transactions based on keyword matching."""
    
    def __init__(self):
        """Initialize the categorizer with predefined category keywords."""
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'lunch', 'dinner', 'breakfast',
                'food', 'pizza', 'burger', 'starbucks', 'mcdonald', 'subway',
                'grocery', 'supermarket', 'market', 'bakery', 'deli'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train', 'metro',
                'parking', 'toll', 'auto', 'car', 'vehicle', 'maintenance'
            ],
            'Shopping': [
                'amazon', 'target', 'walmart', 'store', 'shop', 'retail',
                'clothes', 'clothing', 'electronics', 'mall', 'purchase'
            ],
            'Entertainment': [
                'movie', 'theater', 'cinema', 'netflix', 'spotify', 'music',
                'game', 'entertainment', 'concert', 'show', 'streaming'
            ],
            'Bills & Utilities': [
                'electric', 'electricity', 'water', 'gas bill', 'internet',
                'phone', 'mobile', 'insurance', 'rent', 'mortgage', 'utility'
            ],
            'Healthcare': [
                'doctor', 'hospital', 'medical', 'pharmacy', 'dentist',
                'health', 'medicine', 'prescription', 'clinic'
            ],
            'Banking & Finance': [
                'bank', 'atm', 'fee', 'interest', 'transfer', 'payment',
                'credit', 'loan', 'investment'
            ]
        }
        
        self.transactions = []
        self.categorized_transactions = defaultdict(list)
        self.uncategorized = []
    
    def clean_description(self, description: str) -> str:
        """Clean and normalize transaction description."""
        if not description:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', description.lower().strip())
        
        # Remove common transaction prefixes/suffixes
        cleaned = re.sub(r'^(debit card|credit card|pos|purchase|payment)\s*', '', cleaned)
        cleaned = re.sub(r'\s*(#\d+|\d{2}/\d{2}|\*+)$', '', cleaned)
        
        return cleaned
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        cleaned_desc = self.clean_description(description)
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in cleaned_desc:
                    return category
        
        return 'Uncategorized'
    
    def parse_csv_file(self, file_path: str) -> bool:
        """
        Parse CSV file and extract transaction data.
        
        Expected columns: date, description, amount (or similar variations)
        """
        try:
            with open(file_path, 'r', encoding='utf-8-sig', newline='') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Map common column name variations
                column_mapping = self._map_columns(reader.fieldnames)
                
                if not all(column_mapping.values()):
                    print(f"Error: Could not find required columns in CSV file.")
                    print(f"Available columns: {list(reader.fieldnames)}")
                    print(f"Expected columns: date, description, amount")
                    return False
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        transaction = self._parse_transaction_row(row, column_mapping)
                        if transaction:
                            self.transactions.append(transaction)
                    except Exception as e:
                        print(f"Warning: Error parsing row {row_num}: {e}")
                        continue
                
                return True
                
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return False
        except PermissionError:
            print(f"Error: Permission denied accessing file '{file_path}'.")
            return False
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
    
    def _map_columns(self, fieldnames: List[str]) -> Dict[str, Optional[str]]:
        """Map CSV column names to standard field names."""
        if not fieldnames:
            return {'date': None, 'description': None, 'amount': None}
        
        fieldnames_lower = [name.lower() if name else '' for name in fieldnames]
        
        mapping = {'date': None, 'description': None, 'amount': None}
        
        # Map date column
        for i, name in enumerate(fieldnames_lower):
            if any(keyword in name for keyword in ['date', 'time', 'posted']):
                mapping['date'] = fieldnames[i]
                break
        
        # Map description column
        for i, name in enumerate(fieldnames_lower):
            if any(keyword in name for keyword in ['description', 'memo', 'detail', 'merchant', 'payee']):
                mapping['description'] = fieldnames[i]
                break
        
        # Map amount column
        for i, name in enumerate(fieldnames_lower):
            if any(keyword in name for keyword in ['amount', 'debit', 'credit', 'value']):
                mapping['amount'] = fieldnames[i]
                break
        
        return mapping
    
    def _parse_transaction_row(self, row: Dict[str, str], column_mapping: Dict[str, str]) -> Optional[Dict]:
        """Parse a single transaction row from CSV."""
        try:
            date_str = row.get(column_mapping['date'], '').strip()
            description = row.get(column_mapping['description'], '').strip()
            amount_str = row.get(column_mapping['amount'], '').strip()
            
            if not description or not amount_str:
                return None
            
            # Parse amount
            amount_clean = re.sub(r'[^\d.-]', '', amount_str)
            amount = float(amount_clean) if amount_clean else 0.0
            
            # Parse date (try multiple formats)
            parsed_date = self._parse_date(date_str)
            
            return {
                'date': parsed_date or date_str,
                'description': description,
                'amount': amount,
                'category': self.categorize_transaction(description)
            }
            
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse transaction row: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string into standardized format."""
        if not date_str: