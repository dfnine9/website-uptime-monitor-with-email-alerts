```python
"""
Bank Transaction Data Standardization Tool

This module reads CSV files from multiple bank formats and standardizes transaction data
into a common format. It handles various CSV structures by detecting column patterns
and parsing date, amount, description, and balance information.

The standardized output format includes:
- date: ISO format (YYYY-MM-DD)
- amount: float value
- description: string description
- balance: float balance (if available)
- source_file: original filename

Usage: python script.py
"""

import csv
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import glob


class BankTransactionParser:
    """Parses and standardizes bank transaction data from various CSV formats."""
    
    def __init__(self):
        self.standardized_data = []
        self.supported_formats = {
            'chase': ['Date', 'Description', 'Amount', 'Balance'],
            'bofa': ['Posted Date', 'Payee', 'Amount', 'Running Bal.'],
            'wells': ['Date', 'Amount', 'Description', 'Balance'],
            'citi': ['Date', 'Description', 'Debit', 'Credit', 'Balance'],
            'generic': ['date', 'amount', 'description', 'balance']
        }
    
    def detect_date_format(self, date_string: str) -> str:
        """Detect and return the date format of a string."""
        date_patterns = [
            (r'\d{4}-\d{2}-\d{2}', '%Y-%m-%d'),
            (r'\d{2}/\d{2}/\d{4}', '%m/%d/%Y'),
            (r'\d{2}-\d{2}-\d{4}', '%m-%d-%Y'),
            (r'\d{1,2}/\d{1,2}/\d{4}', '%m/%d/%Y'),
            (r'\d{4}/\d{2}/\d{2}', '%Y/%m/%d'),
        ]
        
        for pattern, fmt in date_patterns:
            if re.match(pattern, date_string.strip()):
                return fmt
        return '%m/%d/%Y'  # default
    
    def parse_date(self, date_string: str) -> str:
        """Parse date string and return ISO format."""
        try:
            date_format = self.detect_date_format(date_string)
            parsed_date = datetime.strptime(date_string.strip(), date_format)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            return date_string  # return original if parsing fails
    
    def parse_amount(self, amount_string: str) -> float:
        """Parse amount string and return float value."""
        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[$,\s]', '', amount_string.strip())
            # Handle parentheses as negative
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def detect_csv_format(self, headers: List[str]) -> str:
        """Detect which bank format the CSV uses based on headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Check for specific bank patterns
        if any('chase' in h for h in headers_lower):
            return 'chase'
        elif 'posted date' in headers_lower:
            return 'bofa'
        elif 'running bal.' in ' '.join(headers_lower):
            return 'bofa'
        elif any('wells' in h for h in headers_lower):
            return 'wells'
        elif 'debit' in headers_lower and 'credit' in headers_lower:
            return 'citi'
        else:
            return 'generic'
    
    def map_columns(self, headers: List[str], bank_format: str) -> Dict[str, int]:
        """Map standard fields to column indices based on detected format."""
        headers_lower = [h.lower().strip() for h in headers]
        column_map = {}
        
        # Date mapping
        date_keywords = ['date', 'posted date', 'transaction date']
        for i, header in enumerate(headers_lower):
            if any(keyword in header for keyword in date_keywords):
                column_map['date'] = i
                break
        
        # Description mapping
        desc_keywords = ['description', 'payee', 'memo', 'reference']
        for i, header in enumerate(headers_lower):
            if any(keyword in header for keyword in desc_keywords):
                column_map['description'] = i
                break
        
        # Amount mapping
        if bank_format == 'citi':
            # Handle debit/credit columns separately
            for i, header in enumerate(headers_lower):
                if 'debit' in header:
                    column_map['debit'] = i
                elif 'credit' in header:
                    column_map['credit'] = i
        else:
            amount_keywords = ['amount', 'transaction amount']
            for i, header in enumerate(headers_lower):
                if any(keyword in header for keyword in amount_keywords):
                    column_map['amount'] = i
                    break
        
        # Balance mapping
        balance_keywords = ['balance', 'running bal', 'account balance']
        for i, header in enumerate(headers_lower):
            if any(keyword in header for keyword in balance_keywords):
                column_map['balance'] = i
                break
        
        return column_map
    
    def parse_csv_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse a single CSV file and return standardized transaction data."""
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
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
                
                bank_format = self.detect_csv_format(headers)
                column_map = self.map_columns(headers, bank_format)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) < len(headers):
                            continue  # Skip incomplete rows
                        
                        transaction = {
                            'date': '',
                            'amount': 0.0,
                            'description': '',
                            'balance': None,
                            'source_file': os.path.basename(filepath)
                        }
                        
                        # Parse date
                        if 'date' in column_map:
                            transaction['date'] = self.parse_date(row[column_map['date']])
                        
                        # Parse amount
                        if bank_format == 'citi':
                            # Handle debit/credit separately
                            debit = 0.0
                            credit = 0.0
                            if 'debit' in column_map and row[column_map['debit']]:
                                debit = self.parse_amount(row[column_map['debit']])
                            if 'credit' in column_map and row[column_map['credit']]:
                                credit = self.parse_amount(row[column_map['credit']])
                            transaction['amount'] = credit - debit
                        elif 'amount' in column_map:
                            transaction['amount'] = self.parse_amount(row[column_map['amount']])
                        
                        # Parse description
                        if 'description' in column_map:
                            transaction['description'] = row[column_map['description']].strip()
                        
                        # Parse balance
                        if 'balance' in column_map and row[column_map['balance']]:
                            transaction['balance'] = self