```python
"""
Bank Transaction CSV Parser and Categorizer

This module reads CSV files from multiple bank formats, parses transaction data
(date, amount, description, balance), and implements a rule-based categorization
system using keyword matching for common expense types.

Supported bank formats:
- Chase Bank
- Bank of America
- Wells Fargo
- Generic format (date, amount, description, balance)

Categories: groceries, gas, dining, utilities, entertainment, other

Usage: python script.py
"""

import csv
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import glob


class TransactionCategorizer:
    """Rule-based transaction categorizer using keyword matching."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'grocery', 'supermarket', 'food lion',
                'publix', 'wegmans', 'harris teeter', 'giant', 'stop & shop'
            ],
            'gas': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'texaco', 'citgo',
                'gas station', 'fuel', 'petroleum', 'marathon', 'speedway',
                'wawa', 'sheetz', '76', 'conoco'
            ],
            'dining': [
                'restaurant', 'mcdonalds', 'burger king', 'subway', 'starbucks',
                'pizza', 'taco bell', 'kfc', 'wendy\'s', 'chipotle', 'panera',
                'domino\'s', 'papa john\'s', 'dunkin', 'cafe', 'bistro', 'grill',
                'bar', 'pub', 'diner', 'food truck', 'takeout'
            ],
            'utilities': [
                'electric', 'electricity', 'power', 'gas bill', 'water',
                'sewer', 'internet', 'phone', 'cable', 'utility', 'verizon',
                'at&t', 'comcast', 'spectrum', 'time warner', 'cox', 'dish'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'hulu', 'disney',
                'movie', 'theater', 'cinema', 'concert', 'ticket', 'game',
                'youtube', 'twitch', 'steam', 'playstation', 'xbox', 'apple music'
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


class BankCSVParser:
    """Parser for multiple bank CSV formats."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.supported_formats = {
            'chase': self._parse_chase,
            'bofa': self._parse_bofa,
            'wells_fargo': self._parse_wells_fargo,
            'generic': self._parse_generic
        }
    
    def _detect_format(self, headers: List[str]) -> str:
        """Detect bank format based on CSV headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Chase format detection
        if 'transaction date' in headers_lower and 'post date' in headers_lower:
            return 'chase'
        
        # Bank of America format detection
        if 'posted date' in headers_lower and 'reference number' in headers_lower:
            return 'bofa'
        
        # Wells Fargo format detection
        if any('wells' in h for h in headers_lower) or 'memo' in headers_lower:
            return 'wells_fargo'
        
        # Generic format (date, amount, description, balance)
        if len(headers) >= 4:
            return 'generic'
        
        return 'unknown'
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string in various formats."""
        date_formats = [
            '%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y',
            '%m/%d/%y', '%Y/%m/%d', '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string, handling various formats."""
        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def _parse_chase(self, reader: csv.DictReader) -> List[Dict]:
        """Parse Chase bank CSV format."""
        transactions = []
        
        for row in reader:
            try:
                date = self._parse_date(row.get('Transaction Date', ''))
                amount = self._parse_amount(row.get('Amount', '0'))
                description = row.get('Description', '').strip()
                balance = self._parse_amount(row.get('Balance', '0'))
                
                if date and description:
                    transaction = {
                        'date': date,
                        'amount': amount,
                        'description': description,
                        'balance': balance,
                        'category': self.categorizer.categorize(description)
                    }
                    transactions.append(transaction)
            except Exception as e:
                print(f"Error parsing Chase row: {e}")
                continue
        
        return transactions
    
    def _parse_bofa(self, reader: csv.DictReader) -> List[Dict]:
        """Parse Bank of America CSV format."""
        transactions = []
        
        for row in reader:
            try:
                date = self._parse_date(row.get('Posted Date', ''))
                amount = self._parse_amount(row.get('Amount', '0'))
                description = row.get('Payee', '').strip()
                balance = self._parse_amount(row.get('Running Bal.', '0'))
                
                if date and description:
                    transaction = {
                        'date': date,
                        'amount': amount,
                        'description': description,
                        'balance': balance,
                        'category': self.categorizer.categorize(description)
                    }
                    transactions.append(transaction)
            except Exception as e:
                print(f"Error parsing BofA row: {e}")
                continue
        
        return transactions
    
    def _parse_wells_fargo(self, reader: csv.DictReader) -> List[Dict]:
        """Parse Wells Fargo CSV format."""
        transactions = []
        
        for row in reader:
            try:
                date = self._parse_date(row.get('Date', ''))
                amount = self._parse_amount(row.get('Amount', '0'))
                description = row.get('Description', '').strip() or row.get('Memo', '').strip()
                balance = self._parse_amount(row.get('Balance', '0'))
                
                if date and description:
                    transaction = {
                        'date': date,
                        'amount': amount,
                        'description': description,
                        'balance': balance,
                        'category': self.categorizer.categorize(description)