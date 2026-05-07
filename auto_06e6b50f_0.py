```python
#!/usr/bin/env python3
"""
Bank Statement Parser Module

This module provides a flexible CSV bank statement parser that can handle multiple 
bank formats through configurable column mapping. It validates transaction data,
standardizes formats, and provides comprehensive error handling.

Features:
- Configurable column mapping for different bank formats
- Transaction data validation (dates, amounts, required fields)
- Support for multiple date formats
- Data type conversion and standardization
- Comprehensive error reporting
- Extensible bank format definitions

Usage:
    python script.py

The script will process sample data and demonstrate parsing capabilities
for different bank statement formats.
"""

import csv
import datetime
import re
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal, InvalidOperation
import sys
from io import StringIO


class BankStatementParser:
    """
    A flexible parser for bank statement CSV files with configurable column mapping
    and validation capabilities.
    """
    
    def __init__(self):
        self.bank_formats = {
            'chase': {
                'date': 'Transaction Date',
                'description': 'Description',
                'amount': 'Amount',
                'balance': 'Balance',
                'type': 'Type',
                'account': 'Account'
            },
            'wellsfargo': {
                'date': 'Date',
                'description': 'Description',
                'amount': 'Amount',
                'balance': 'Running Balance',
                'type': None,
                'account': None
            },
            'bofa': {
                'date': 'Posted Date',
                'description': 'Payee',
                'amount': 'Amount',
                'balance': None,
                'type': 'Transaction Type',
                'account': 'Account Number'
            },
            'generic': {
                'date': 'Date',
                'description': 'Description',
                'amount': 'Amount',
                'balance': 'Balance',
                'type': 'Type',
                'account': 'Account'
            }
        }
        
        self.date_formats = [
            '%Y-%m-%d',      # 2023-12-31
            '%m/%d/%Y',      # 12/31/2023
            '%d/%m/%Y',      # 31/12/2023
            '%m-%d-%Y',      # 12-31-2023
            '%Y/%m/%d',      # 2023/12/31
            '%b %d, %Y',     # Dec 31, 2023
            '%B %d, %Y',     # December 31, 2023
            '%m/%d/%y',      # 12/31/23
            '%d-%b-%Y',      # 31-Dec-2023
        ]
    
    def detect_bank_format(self, headers: List[str]) -> str:
        """
        Detect bank format based on CSV headers.
        
        Args:
            headers: List of column headers from CSV
            
        Returns:
            Bank format identifier
        """
        headers_lower = [h.lower().strip() for h in headers]
        
        # Score each format based on header matches
        scores = {}
        for bank, mapping in self.bank_formats.items():
            score = 0
            for field, column in mapping.items():
                if column and column.lower() in headers_lower:
                    score += 1
            scores[bank] = score
        
        # Return format with highest score, default to generic
        best_format = max(scores.items(), key=lambda x: x[1])
        return best_format[0] if best_format[1] > 0 else 'generic'
    
    def validate_date(self, date_str: str) -> Optional[datetime.date]:
        """
        Validate and parse date string using multiple format attempts.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Parsed date object or None if invalid
        """
        if not date_str or not isinstance(date_str, str):
            return None
            
        date_str = date_str.strip()
        
        for fmt in self.date_formats:
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    
    def validate_amount(self, amount_str: str) -> Optional[Decimal]:
        """
        Validate and parse amount string.
        
        Args:
            amount_str: Amount string to parse
            
        Returns:
            Parsed Decimal amount or None if invalid
        """
        if not amount_str or not isinstance(amount_str, str):
            return None
        
        # Clean amount string
        amount_str = amount_str.strip()
        
        # Remove currency symbols and spaces
        amount_str = re.sub(r'[$€£¥₹,\s]', '', amount_str)
        
        # Handle parentheses for negative amounts
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            return Decimal(amount_str)
        except (InvalidOperation, ValueError):
            return None
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single transaction record.
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            Validated transaction with validation results
        """
        validation_result = {
            'original': transaction.copy(),
            'validated': {},
            'errors': [],
            'warnings': []
        }
        
        # Validate date
        if 'date' in transaction and transaction['date']:
            parsed_date = self.validate_date(str(transaction['date']))
            if parsed_date:
                validation_result['validated']['date'] = parsed_date
            else:
                validation_result['errors'].append(f"Invalid date format: {transaction['date']}")
        else:
            validation_result['errors'].append("Missing or empty date field")
        
        # Validate amount
        if 'amount' in transaction and transaction['amount']:
            parsed_amount = self.validate_amount(str(transaction['amount']))
            if parsed_amount is not None:
                validation_result['validated']['amount'] = parsed_amount
            else:
                validation_result['errors'].append(f"Invalid amount format: {transaction['amount']}")
        else:
            validation_result['errors'].append("Missing or empty amount field")
        
        # Validate description
        if 'description' in transaction and transaction['description']:
            desc = str(transaction['description']).strip()
            if desc:
                validation_result['validated']['description'] = desc
            else:
                validation_result['warnings'].append("Empty description")
        else:
            validation_result['warnings'].append("Missing description field")
        
        # Copy other fields
        for field in ['balance', 'type', 'account']:
            if field in transaction and transaction[field]:
                if field == 'balance':
                    parsed_balance = self.validate_amount(str(transaction[field]))
                    if parsed_balance is not None:
                        validation_result['validated'][field] = parsed_balance
                    else:
                        validation_result['warnings'].append(f"Invalid balance format: {transaction[field]}")
                else:
                    validation_result['validated'][field] = str(transaction[field]).strip()
        
        return validation_result
    
    def parse_csv_content(self, csv_content: str, bank_format: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse CSV content and return structured transaction data.
        
        Args:
            csv_content: CSV file content as string
            bank_format: Specific bank format to use, or None for auto-detection
            
        Returns:
            Dictionary containing parsed transactions and metadata
        """
        result = {
            'transactions': [],
            'validation_summary': {
                'total_records': 0,
                'valid_records': 0,
                'records_with_errors': 0,
                'records_with_warnings': 0
            },
            'errors': [],
            'bank_format': None,
            'column_mapping': None
        }
        
        try:
            # Parse CSV