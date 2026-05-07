```python
"""
Multi-Bank CSV Transaction Parser

This module parses CSV files from multiple bank formats, extracts transaction data
(date, amount, description, balance), and validates data integrity with comprehensive
error handling for malformed entries.

Supports common bank CSV formats and provides detailed error reporting for
data validation issues.

Usage: python script.py
"""

import csv
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple, Any
import os


class TransactionParser:
    """Parses and validates bank transaction data from CSV files."""
    
    def __init__(self):
        self.supported_formats = {
            'chase': {
                'headers': ['Transaction Date', 'Post Date', 'Description', 'Category', 'Type', 'Amount', 'Memo'],
                'date_col': 'Transaction Date',
                'amount_col': 'Amount',
                'description_col': 'Description',
                'balance_col': None
            },
            'wells_fargo': {
                'headers': ['Date', 'Amount', 'Description', 'Balance'],
                'date_col': 'Date',
                'amount_col': 'Amount',
                'description_col': 'Description',
                'balance_col': 'Balance'
            },
            'bank_of_america': {
                'headers': ['Posted Date', 'Reference Number', 'Payee', 'Address', 'Amount'],
                'date_col': 'Posted Date',
                'amount_col': 'Amount',
                'description_col': 'Payee',
                'balance_col': None
            },
            'generic': {
                'headers': ['date', 'amount', 'description', 'balance'],
                'date_col': 'date',
                'amount_col': 'amount',
                'description_col': 'description',
                'balance_col': 'balance'
            }
        }
        
    def detect_format(self, headers: List[str]) -> Optional[str]:
        """Detect bank format based on CSV headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        for format_name, format_info in self.supported_formats.items():
            format_headers = [h.lower() for h in format_info['headers']]
            if any(header in headers_lower for header in format_headers[:3]):  # Check first 3 key headers
                return format_name
        
        return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format support."""
        if not date_str or date_str.strip() == '':
            return None
            
        date_str = date_str.strip()
        date_formats = [
            '%m/%d/%Y',
            '%Y-%m-%d',
            '%m-%d-%Y',
            '%d/%m/%Y',
            '%m/%d/%y',
            '%Y/%m/%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string, handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return None
            
        # Clean the amount string
        amount_str = amount_str.strip()
        amount_str = re.sub(r'[,$\s]', '', amount_str)
        
        # Handle negative amounts in parentheses
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            return Decimal(amount_str)
        except (InvalidOperation, ValueError):
            return None
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single transaction record."""
        errors = []
        
        if transaction['date'] is None:
            errors.append("Invalid or missing date")
        
        if transaction['amount'] is None:
            errors.append("Invalid or missing amount")
        
        if not transaction['description'] or transaction['description'].strip() == '':
            errors.append("Missing description")
        
        if transaction['balance'] is not None and not isinstance(transaction['balance'], Decimal):
            errors.append("Invalid balance format")
        
        return len(errors) == 0, errors
    
    def parse_csv_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a single CSV file and return transaction data."""
        results = {
            'file_path': file_path,
            'format': None,
            'transactions': [],
            'errors': [],
            'total_transactions': 0,
            'valid_transactions': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    results['errors'].append("No headers found in CSV file")
                    return results
                
                # Detect format
                detected_format = self.detect_format(headers)
                if not detected_format:
                    results['errors'].append(f"Unsupported CSV format. Headers: {headers}")
                    return results
                
                results['format'] = detected_format
                format_info = self.supported_formats[detected_format]
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 since row 1 is headers
                    results['total_transactions'] += 1
                    
                    try:
                        # Extract fields based on format
                        date_str = row.get(format_info['date_col'], '')
                        amount_str = row.get(format_info['amount_col'], '')
                        description = row.get(format_info['description_col'], '').strip()
                        balance_str = row.get(format_info['balance_col'], '') if format_info['balance_col'] else ''
                        
                        # Parse fields
                        parsed_date = self.parse_date(date_str)
                        parsed_amount = self.parse_amount(amount_str)
                        parsed_balance = self.parse_amount(balance_str) if balance_str else None
                        
                        transaction = {
                            'row_number': row_num,
                            'date': parsed_date,
                            'amount': parsed_amount,
                            'description': description,
                            'balance': parsed_balance,
                            'raw_data': dict(row)
                        }
                        
                        # Validate transaction
                        is_valid, validation_errors = self.validate_transaction(transaction)
                        
                        if is_valid:
                            results['transactions'].append(transaction)
                            results['valid_transactions'] += 1
                        else:
                            error_msg = f"Row {row_num}: {'; '.join(validation_errors)}"
                            results['errors'].append(error_msg)
                    
                    except Exception as e:
                        results['errors'].append(f"Row {row_num}: Unexpected error - {str(e)}")
        
        except FileNotFoundError:
            results['errors'].append(f"File not found: {file_path}")
        except PermissionError:
            results['errors'].append(f"Permission denied: {file_path}")
        except Exception as e:
            results['errors'].append(f"Failed to read file: {str(e)}")
        
        return results
    
    def generate_sample_csv(self, file_path: str, format_name: str = 'generic'):
        """Generate a sample CSV file for testing."""
        format_info = self.supported_formats[format_name]
        headers = format_info['headers']