```python
#!/usr/bin/env python3
"""
CSV Bank Statement Parser

This module parses CSV bank statement files and extracts transaction data including:
- Transaction date
- Amount (debit/credit)
- Description
- Balance

The parser uses regex patterns to handle various CSV formats commonly used by banks.
It automatically detects column headers and maps them to standard transaction fields.

Usage:
    python script.py [csv_file_path]

If no file path is provided, the script will look for 'bank_statement.csv' in the current directory.
"""

import csv
import re
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class BankStatementParser:
    """Parser for CSV bank statement files with flexible format detection."""
    
    def __init__(self):
        # Common date patterns
        self.date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',      # MM/DD/YYYY or M/D/YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',      # YYYY-MM-DD
            r'\d{1,2}-\d{1,2}-\d{4}',      # MM-DD-YYYY
            r'\d{1,2}\.\d{1,2}\.\d{4}',    # MM.DD.YYYY
        ]
        
        # Amount patterns (handles negatives, parentheses, currency symbols)
        self.amount_patterns = [
            r'[-+]?\$?[\d,]+\.?\d*',       # $1,234.56 or -1234.56
            r'\(\$?[\d,]+\.?\d*\)',        # ($1,234.56) for negatives
        ]
        
        # Common column header mappings
        self.column_mappings = {
            'date': ['date', 'transaction_date', 'trans_date', 'posting_date'],
            'amount': ['amount', 'transaction_amount', 'debit', 'credit'],
            'description': ['description', 'memo', 'reference', 'details', 'payee'],
            'balance': ['balance', 'running_balance', 'account_balance']
        }

    def detect_delimiter(self, file_path: str) -> str:
        """Detect the CSV delimiter by examining the first few lines."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                
            # Count occurrences of common delimiters
            delimiters = [',', ';', '\t', '|']
            delimiter_counts = {}
            
            for delimiter in delimiters:
                delimiter_counts[delimiter] = sample.count(delimiter)
            
            # Return the delimiter with the highest count
            return max(delimiter_counts, key=delimiter_counts.get)
            
        except Exception as e:
            print(f"Error detecting delimiter: {e}")
            return ','  # Default to comma

    def map_columns(self, headers: List[str]) -> Dict[str, int]:
        """Map CSV headers to standard field names."""
        column_indices = {}
        headers_lower = [h.lower().strip() for h in headers]
        
        for field, possible_names in self.column_mappings.items():
            for i, header in enumerate(headers_lower):
                if any(name in header for name in possible_names):
                    column_indices[field] = i
                    break
        
        return column_indices

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string using various patterns."""
        date_str = date_str.strip()
        
        for pattern in self.date_patterns:
            match = re.search(pattern, date_str)
            if match:
                date_match = match.group()
                
                # Try different date formats
                formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%m.%d.%Y']
                for fmt in formats:
                    try:
                        return datetime.strptime(date_match, fmt)
                    except ValueError:
                        continue
        
        return None

    def parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string, handling various formats."""
        if not amount_str:
            return None
            
        amount_str = amount_str.strip()
        
        # Check if amount is in parentheses (negative)
        is_negative = False
        if amount_str.startswith('(') and amount_str.endswith(')'):
            is_negative = True
            amount_str = amount_str[1:-1]
        
        # Remove currency symbols and commas
        amount_str = re.sub(r'[$,]', '', amount_str)
        
        # Extract numeric value
        match = re.search(r'[-+]?[\d.]+', amount_str)
        if match:
            try:
                value = float(match.group())
                return -value if is_negative else value
            except ValueError:
                pass
        
        return None

    def parse_csv_file(self, file_path: str) -> List[Dict]:
        """Parse the CSV file and extract transaction data."""
        transactions = []
        
        try:
            delimiter = self.detect_delimiter(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first line to detect headers
                first_line = file.readline().strip()
                file.seek(0)
                
                reader = csv.reader(file, delimiter=delimiter)
                
                # Get headers
                headers = next(reader)
                column_indices = self.map_columns(headers)
                
                if not column_indices:
                    print("Warning: Could not map any columns. Using positional parsing.")
                    # Assume standard order: date, description, amount, balance
                    column_indices = {
                        'date': 0,
                        'description': 1,
                        'amount': 2,
                        'balance': 3 if len(headers) > 3 else None
                    }
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) < 2:  # Skip empty or incomplete rows
                        continue
                    
                    transaction = {}
                    
                    # Parse date
                    if 'date' in column_indices and column_indices['date'] < len(row):
                        date_obj = self.parse_date(row[column_indices['date']])
                        transaction['date'] = date_obj.strftime('%Y-%m-%d') if date_obj else 'Unknown'
                    else:
                        transaction['date'] = 'Unknown'
                    
                    # Parse description
                    if 'description' in column_indices and column_indices['description'] < len(row):
                        transaction['description'] = row[column_indices['description']].strip()
                    else:
                        transaction['description'] = 'No description'
                    
                    # Parse amount
                    amount = None
                    if 'amount' in column_indices and column_indices['amount'] < len(row):
                        amount = self.parse_amount(row[column_indices['amount']])
                    
                    transaction['amount'] = amount if amount is not None else 0.0
                    
                    # Parse balance
                    if 'balance' in column_indices and column_indices['balance'] and column_indices['balance'] < len(row):
                        balance = self.parse_amount(row[column_indices['balance']])
                        transaction['balance'] = balance if balance is not None else 0.0
                    else:
                        transaction['balance'] = 0.0
                    
                    transactions.append(transaction)
                    
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
        except Exception as e:
            print(f"Error parsing CSV file: {e}")
        
        return transactions

    def print_transactions(self, transactions: List[Dict]) -> None:
        """Print transactions in a formatted table."""
        if not transactions:
            print("No transactions found.")