```python
#!/usr/bin/env python3
"""
Bank CSV Transaction Parser

This module parses common bank CSV formats to extract transaction data including
date, amount, and description fields. It automatically detects common CSV formats
from major banks and credit card companies by analyzing headers and data patterns.

Supported formats:
- Chase Bank CSV exports
- Bank of America CSV exports  
- Wells Fargo CSV exports
- Capital One CSV exports
- Generic CSV with date/amount/description columns

The script outputs parsed transactions in a standardized JSON format to stdout.
"""

import csv
import json
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class BankCSVParser:
    """Parser for bank CSV transaction files with automatic format detection."""
    
    def __init__(self):
        self.common_date_formats = [
            '%m/%d/%Y',
            '%m/%d/%y', 
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m-%d-%Y',
            '%Y/%m/%d'
        ]
        
        # Common field mappings for different banks
        self.field_mappings = {
            'chase': {
                'date': ['Transaction Date', 'Date'],
                'amount': ['Amount'],
                'description': ['Description']
            },
            'bofa': {
                'date': ['Date', 'Posted Date'],
                'amount': ['Amount'],
                'description': ['Description', 'Payee']
            },
            'wells_fargo': {
                'date': ['Date'],
                'amount': ['Amount'],
                'description': ['Description', 'Memo']
            },
            'capital_one': {
                'date': ['Transaction Date'],
                'amount': ['Debit', 'Credit'],
                'description': ['Description']
            },
            'generic': {
                'date': ['date', 'transaction_date', 'trans_date'],
                'amount': ['amount', 'debit', 'credit'],
                'description': ['description', 'memo', 'payee', 'merchant']
            }
        }

    def detect_csv_format(self, headers: List[str]) -> str:
        """Detect bank CSV format based on column headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Chase patterns
        if any('transaction date' in h for h in headers_lower):
            return 'chase'
            
        # Bank of America patterns  
        if any('posted date' in h for h in headers_lower):
            return 'bofa'
            
        # Capital One patterns
        if 'debit' in headers_lower and 'credit' in headers_lower:
            return 'capital_one'
            
        # Wells Fargo or generic
        return 'wells_fargo' if 'memo' in headers_lower else 'generic'

    def find_column_index(self, headers: List[str], possible_names: List[str]) -> Optional[int]:
        """Find column index by matching against possible field names."""
        headers_lower = [h.lower().strip() for h in headers]
        
        for name in possible_names:
            name_lower = name.lower()
            for i, header in enumerate(headers_lower):
                if name_lower in header or header in name_lower:
                    return i
        return None

    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string using common formats, return ISO format."""
        if not date_str or not date_str.strip():
            return None
            
        date_str = date_str.strip()
        
        for fmt in self.common_date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        return None

    def parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string, handling various formats and currencies."""
        if not amount_str or not amount_str.strip():
            return None
            
        # Remove currency symbols and whitespace
        clean_amount = re.sub(r'[\$£€¥,\s]', '', amount_str.strip())
        
        # Handle parentheses as negative (accounting format)
        if clean_amount.startswith('(') and clean_amount.endswith(')'):
            clean_amount = '-' + clean_amount[1:-1]
            
        try:
            return float(Decimal(clean_amount))
        except (InvalidOperation, ValueError):
            return None

    def parse_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse CSV file and extract transaction data."""
        transactions = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                delimiter = ','
                if sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                elif sample.count(';') > sample.count(','):
                    delimiter = ';'
                
                reader = csv.reader(csvfile, delimiter=delimiter)
                headers = next(reader, [])
                
                if not headers:
                    raise ValueError("CSV file has no headers")
                
                # Detect format and get field mappings
                csv_format = self.detect_csv_format(headers)
                mappings = self.field_mappings.get(csv_format, self.field_mappings['generic'])
                
                # Find column indices
                date_idx = self.find_column_index(headers, mappings['date'])
                amount_idx = self.find_column_index(headers, mappings['amount'])
                desc_idx = self.find_column_index(headers, mappings['description'])
                
                if date_idx is None:
                    raise ValueError(f"Could not find date column in headers: {headers}")
                if amount_idx is None:
                    raise ValueError(f"Could not find amount column in headers: {headers}")
                if desc_idx is None:
                    raise ValueError(f"Could not find description column in headers: {headers}")
                
                # Handle Capital One dual amount columns (Debit/Credit)
                credit_idx = None
                if csv_format == 'capital_one':
                    credit_idx = self.find_column_index(headers, ['credit'])
                
                # Parse rows
                for row_num, row in enumerate(reader, start=2):
                    if len(row) <= max(date_idx, amount_idx, desc_idx):
                        continue  # Skip incomplete rows
                    
                    # Parse date
                    transaction_date = self.parse_date(row[date_idx])
                    if not transaction_date:
                        print(f"Warning: Could not parse date '{row[date_idx]}' on row {row_num}", file=sys.stderr)
                        continue
                    
                    # Parse amount (handle Capital One debit/credit columns)
                    if csv_format == 'capital_one' and credit_idx is not None:
                        debit_amount = self.parse_amount(row[amount_idx]) or 0
                        credit_amount = self.parse_amount(row[credit_idx]) or 0
                        amount = credit_amount - debit_amount
                    else:
                        amount = self.parse_amount(row[amount_idx])
                    
                    if amount is None:
                        print(f"Warning: Could not parse amount '{row[amount_idx]}' on row {row_num}", file=sys.stderr)
                        continue
                    
                    # Parse description
                    description = row[desc_idx].strip() if desc_idx < len(row) else ""
                    
                    transaction = {
                        'date': transaction_date,
                        'amount': amount,
                        'description': description,
                        'raw_data': {
                            'row_number': row_num,
                            'format_detected': csv_format
                        }
                    }
                    
                    transactions.append(transaction)