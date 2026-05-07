```python
#!/usr/bin/env python3
"""
Bank CSV Transaction Parser and Validator

This module provides functionality to parse and validate bank CSV exports with
common banking structures. It handles various date formats, validates transaction
data, and provides detailed error reporting for malformed entries.

Supported CSV structures:
- Standard banking format: Date, Description, Amount, Balance
- Alternative formats with different column orders
- Various date formats (MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD, etc.)
- Positive/negative amount representations

Features:
- Automatic CSV structure detection
- Robust date parsing with multiple format support
- Amount validation and normalization
- Balance consistency checking
- Comprehensive error handling and reporting

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Optional, Tuple
import io

class BankCSVParser:
    """Parser for bank CSV exports with validation and error handling."""
    
    def __init__(self):
        self.date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y',
            '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
            '%Y-%m-%d', '%Y/%m/%d',
            '%B %d, %Y', '%b %d, %Y',
            '%d %B %Y', '%d %b %Y'
        ]
        
        self.common_headers = {
            'date': ['date', 'transaction date', 'posting date', 'value date'],
            'description': ['description', 'memo', 'details', 'transaction details', 'payee'],
            'amount': ['amount', 'debit', 'credit', 'transaction amount'],
            'balance': ['balance', 'running balance', 'account balance', 'current balance']
        }
        
    def detect_csv_structure(self, csv_content: str) -> Dict[str, int]:
        """Detect the structure of the CSV by analyzing headers."""
        try:
            reader = csv.reader(io.StringIO(csv_content))
            headers = [header.lower().strip() for header in next(reader)]
            
            column_mapping = {}
            
            for field_type, possible_names in self.common_headers.items():
                for i, header in enumerate(headers):
                    if any(name in header for name in possible_names):
                        column_mapping[field_type] = i
                        break
            
            return column_mapping
        except Exception as e:
            raise ValueError(f"Failed to detect CSV structure: {e}")
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string using multiple format attempts."""
        date_str = date_str.strip()
        
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return None
            
        # Clean the amount string
        amount_str = amount_str.strip()
        
        # Remove currency symbols
        amount_str = re.sub(r'[$£€¥₹]', '', amount_str)
        
        # Handle parentheses for negative amounts
        is_negative = False
        if amount_str.startswith('(') and amount_str.endswith(')'):
            is_negative = True
            amount_str = amount_str[1:-1]
        
        # Remove commas used as thousand separators
        amount_str = amount_str.replace(',', '')
        
        # Handle explicit positive/negative signs
        if amount_str.startswith('-'):
            is_negative = True
            amount_str = amount_str[1:]
        elif amount_str.startswith('+'):
            amount_str = amount_str[1:]
        
        try:
            amount = Decimal(amount_str)
            return -amount if is_negative else amount
        except InvalidOperation:
            return None
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> List[str]:
        """Validate a single transaction and return list of errors."""
        errors = []
        
        if not transaction.get('date'):
            errors.append("Missing or invalid date")
        
        if not transaction.get('description') or not transaction['description'].strip():
            errors.append("Missing or empty description")
        
        if transaction.get('amount') is None:
            errors.append("Missing or invalid amount")
        
        if transaction.get('balance') is None:
            errors.append("Missing or invalid balance")
        
        return errors
    
    def parse_csv_content(self, csv_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Parse CSV content and return transactions with validation errors."""
        try:
            column_mapping = self.detect_csv_structure(csv_content)
            
            if not all(field in column_mapping for field in ['date', 'description', 'amount']):
                raise ValueError("Required columns (date, description, amount) not found")
            
            transactions = []
            errors = []
            
            reader = csv.reader(io.StringIO(csv_content))
            next(reader)  # Skip header row
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    if len(row) == 0 or all(cell.strip() == '' for cell in row):
                        continue  # Skip empty rows
                    
                    transaction = {}
                    
                    # Parse date
                    date_str = row[column_mapping['date']] if len(row) > column_mapping['date'] else ''
                    transaction['date'] = self.parse_date(date_str)
                    
                    # Parse description
                    desc_col = column_mapping['description']
                    transaction['description'] = row[desc_col] if len(row) > desc_col else ''
                    
                    # Parse amount
                    amount_col = column_mapping['amount']
                    amount_str = row[amount_col] if len(row) > amount_col else ''
                    transaction['amount'] = self.parse_amount(amount_str)
                    
                    # Parse balance if available
                    if 'balance' in column_mapping:
                        balance_col = column_mapping['balance']
                        balance_str = row[balance_col] if len(row) > balance_col else ''
                        transaction['balance'] = self.parse_amount(balance_str)
                    else:
                        transaction['balance'] = None
                    
                    # Add raw row data for debugging
                    transaction['raw_row'] = row
                    transaction['row_number'] = row_num
                    
                    # Validate transaction
                    validation_errors = self.validate_transaction(transaction)
                    if validation_errors:
                        errors.extend([f"Row {row_num}: {error}" for error in validation_errors])
                    
                    transactions.append(transaction)
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: Error parsing row - {e}")
            
            return transactions, errors
            
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {e}")
    
    def validate_balance_consistency(self, transactions: List[Dict[str, Any]]) -> List[str]:
        """Validate balance consistency across transactions."""
        errors = []
        
        # Filter out transactions with missing balance or amount data
        valid_transactions = [
            t for t in transactions 
            if t.get('balance') is not None and t.get('amount') is not None
        ]
        
        if len(valid_transactions) < 2:
            return errors
        
        # Sort by date if dates are available
        valid_transactions = [t for t in valid_transactions if t.get('date')]
        valid_transactions.sort(key=lambda x: x['date'])
        
        for i in range(1, len(valid_transactions)):
            prev