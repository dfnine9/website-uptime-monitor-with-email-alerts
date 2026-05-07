```python
#!/usr/bin/env python3
"""
CSV Bank Statement Parser

This module parses CSV bank statements and extracts transaction data into a structured format.
It automatically detects common CSV formats used by major banks and normalizes the data
into a consistent structure for further processing or analysis.

The script handles various CSV formats and provides robust error handling for malformed data.
Extracted transaction data includes date, description, amount, balance, and transaction type.

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Union
from decimal import Decimal, InvalidOperation
import io


class BankStatementParser:
    """Parser for CSV bank statements with format auto-detection."""
    
    def __init__(self):
        self.transactions = []
        self.detected_format = None
        
    def detect_csv_format(self, headers: List[str]) -> Optional[str]:
        """Detect the CSV format based on column headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Common bank CSV formats
        formats = {
            'chase': ['date', 'description', 'amount', 'balance'],
            'bofa': ['date', 'description', 'amount', 'running balance'],
            'wells': ['date', 'amount', 'description', 'balance'],
            'generic': ['date', 'description', 'debit', 'credit', 'balance'],
            'simple': ['date', 'description', 'amount']
        }
        
        for format_name, expected_cols in formats.items():
            if all(any(col in header for header in headers_lower) for col in expected_cols):
                return format_name
                
        return 'auto'  # Fallback to auto-detection
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string into ISO format."""
        if not date_str or date_str.strip() == '':
            return None
            
        date_str = date_str.strip()
        date_formats = [
            '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y',
            '%B %d, %Y', '%b %d, %Y', '%m-%d-%Y', '%Y%m%d'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        return date_str  # Return original if parsing fails
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string into Decimal."""
        if not amount_str or amount_str.strip() == '':
            return None
            
        # Clean the amount string
        amount_str = str(amount_str).strip()
        amount_str = re.sub(r'[,$\s]', '', amount_str)
        
        # Handle parentheses as negative
        is_negative = False
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = amount_str[1:-1]
            is_negative = True
        
        try:
            amount = Decimal(amount_str)
            return -amount if is_negative else amount
        except (InvalidOperation, ValueError):
            return None
    
    def normalize_transaction(self, row: Dict[str, str], format_type: str) -> Dict[str, Union[str, Decimal, None]]:
        """Normalize transaction data based on detected format."""
        transaction = {
            'date': None,
            'description': '',
            'amount': None,
            'balance': None,
            'type': 'unknown'
        }
        
        # Map fields based on format
        field_mappings = {
            'chase': {'date': 'date', 'description': 'description', 'amount': 'amount', 'balance': 'balance'},
            'bofa': {'date': 'date', 'description': 'description', 'amount': 'amount', 'balance': 'running balance'},
            'wells': {'date': 'date', 'description': 'description', 'amount': 'amount', 'balance': 'balance'},
            'generic': {'date': 'date', 'description': 'description', 'debit': 'debit', 'credit': 'credit', 'balance': 'balance'},
            'simple': {'date': 'date', 'description': 'description', 'amount': 'amount'}
        }
        
        mapping = field_mappings.get(format_type, {})
        
        # Find matching columns (case-insensitive)
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        
        # Parse date
        for key in ['date', 'transaction date', 'posting date']:
            if key in row_lower:
                transaction['date'] = self.parse_date(row_lower[key])
                break
        
        # Parse description
        for key in ['description', 'memo', 'details', 'transaction']:
            if key in row_lower:
                transaction['description'] = row_lower[key].strip()
                break
        
        # Parse amount (handle debit/credit or single amount)
        amount = None
        if format_type == 'generic':
            debit = self.parse_amount(row_lower.get('debit', ''))
            credit = self.parse_amount(row_lower.get('credit', ''))
            if debit:
                amount = -abs(debit)
                transaction['type'] = 'debit'
            elif credit:
                amount = abs(credit)
                transaction['type'] = 'credit'
        else:
            for key in ['amount', 'transaction amount']:
                if key in row_lower:
                    amount = self.parse_amount(row_lower[key])
                    break
        
        transaction['amount'] = amount
        
        # Determine transaction type if not already set
        if transaction['type'] == 'unknown' and amount is not None:
            transaction['type'] = 'credit' if amount >= 0 else 'debit'
        
        # Parse balance
        for key in ['balance', 'running balance', 'account balance']:
            if key in row_lower:
                transaction['balance'] = self.parse_amount(row_lower[key])
                break
        
        return transaction
    
    def parse_csv_file(self, file_path: str) -> List[Dict]:
        """Parse CSV file and extract transactions."""
        transactions = []
        
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
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Detect format from headers
                headers = reader.fieldnames or []
                format_type = self.detect_csv_format(headers)
                self.detected_format = format_type
                
                print(f"Detected CSV format: {format_type}")
                print(f"Headers: {headers}")
                print("-" * 50)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        transaction = self.normalize_transaction(row, format_type)
                        if transaction['date'] or transaction['description'] or transaction['amount']:
                            transactions.append(transaction)
                    except Exception as e:
                        print(f"Warning: Error parsing row {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
        
        return transactions
    
    def parse_csv_string(self, csv_content: str) -> List[Dict]: