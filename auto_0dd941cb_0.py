```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

This module reads bank CSV files, automatically categorizes transactions using 
keyword matching rules, and stores the processed data in a structured format.

Features:
- Reads CSV files with common bank transaction formats
- Categorizes transactions based on configurable keyword rules
- Handles various CSV formats automatically
- Outputs categorized data in JSON format
- Includes comprehensive error handling

Usage:
    python script.py

The script will look for CSV files in the current directory and process them.
"""

import csv
import json
import os
import sys
import re
from datetime import datetime
from typing import Dict, List, Any, Optional


class TransactionCategorizer:
    """Categorizes bank transactions based on keyword matching rules."""
    
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'mcdonalds',
                'starbucks', 'subway', 'food', 'dining', 'kitchen', 'bar',
                'pub', 'diner', 'bistro', 'bakery', 'grocery', 'supermarket',
                'walmart', 'target', 'safeway', 'kroger', 'whole foods'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus',
                'parking', 'toll', 'chevron', 'shell', 'exxon', 'bp',
                'mobil', 'car wash', 'automotive', 'repair'
            ],
            'Shopping': [
                'amazon', 'ebay', 'store', 'shop', 'retail', 'purchase',
                'buy', 'mall', 'outlet', 'clothing', 'electronics',
                'best buy', 'costco', 'home depot', 'lowes'
            ],
            'Bills & Utilities': [
                'electric', 'gas bill', 'water', 'internet', 'phone',
                'cable', 'utility', 'mortgage', 'rent', 'insurance',
                'comcast', 'verizon', 'att', 'tmobile', 'sprint'
            ],
            'Healthcare': [
                'hospital', 'doctor', 'medical', 'pharmacy', 'cvs',
                'walgreens', 'clinic', 'dental', 'health', 'medicine'
            ],
            'Entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'game',
                'entertainment', 'concert', 'show', 'ticket',
                'amusement', 'park', 'gym', 'fitness'
            ],
            'Banking': [
                'atm', 'fee', 'transfer', 'deposit', 'withdrawal',
                'interest', 'dividend', 'check', 'overdraft'
            ],
            'Income': [
                'salary', 'payroll', 'wage', 'income', 'deposit',
                'refund', 'cashback', 'bonus', 'payment received'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """Categorize a transaction based on its description and amount."""
        description_lower = description.lower()
        
        # Special handling for income (positive amounts from known sources)
        if amount > 0:
            income_keywords = ['salary', 'payroll', 'wage', 'deposit', 'refund']
            if any(keyword in description_lower for keyword in income_keywords):
                return 'Income'
        
        # Check each category for keyword matches
        for category, keywords in self.categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'Other'


class BankCSVProcessor:
    """Processes bank CSV files and categorizes transactions."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.processed_data = []
    
    def detect_csv_format(self, filepath: str) -> Dict[str, Any]:
        """Detect the CSV format and column mappings."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Read first few lines to detect format
                lines = [file.readline().strip() for _ in range(3)]
                file.seek(0)
                
                # Try to detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(lines[0]).delimiter
                
                # Parse header
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    raise ValueError("No headers found in CSV file")
                
                # Common column name mappings
                column_mappings = self._map_columns(headers)
                
                return {
                    'delimiter': delimiter,
                    'headers': headers,
                    'mappings': column_mappings
                }
        
        except Exception as e:
            raise ValueError(f"Failed to detect CSV format: {str(e)}")
    
    def _map_columns(self, headers: List[str]) -> Dict[str, str]:
        """Map CSV headers to standard column names."""
        mappings = {}
        headers_lower = [h.lower() for h in headers]
        
        # Date column mapping
        date_patterns = ['date', 'transaction date', 'posted date', 'effective date']
        for pattern in date_patterns:
            for i, header in enumerate(headers_lower):
                if pattern in header:
                    mappings['date'] = headers[i]
                    break
            if 'date' in mappings:
                break
        
        # Description column mapping
        desc_patterns = ['description', 'memo', 'transaction', 'details', 'merchant']
        for pattern in desc_patterns:
            for i, header in enumerate(headers_lower):
                if pattern in header:
                    mappings['description'] = headers[i]
                    break
            if 'description' in mappings:
                break
        
        # Amount column mapping
        amount_patterns = ['amount', 'debit', 'credit', 'withdrawal', 'deposit']
        for pattern in amount_patterns:
            for i, header in enumerate(headers_lower):
                if pattern in header:
                    mappings['amount'] = headers[i]
                    break
            if 'amount' in mappings:
                break
        
        return mappings
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return 0.0
        
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$,\s]', '', str(amount_str))
        
        # Handle negative amounts in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format."""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Common date formats
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',
            '%d/%m/%Y', '%d/%m/%y', '%Y/%m/%d',
            '%m-%d-%Y', '%m-%d-%y', '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If all formats fail, return current date
        return datetime.now().strftime('%Y-%m-%d')
    
    def process_csv_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Process