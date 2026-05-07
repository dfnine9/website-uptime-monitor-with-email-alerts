```python
#!/usr/bin/env python3
"""
Bank CSV Transaction Parser and Standardizer

This module parses transaction CSV files from major banks (Chase, Bank of America, Wells Fargo)
and standardizes them into a unified schema. It automatically detects the bank format based on
CSV headers and converts all transactions to a consistent format with fields:
- date: ISO format date (YYYY-MM-DD)
- amount: float value (negative for debits, positive for credits)
- description: transaction description text
- account: account identifier (last 4 digits or full account number)

Usage:
    python script.py [csv_file_path]

If no file path is provided, the script will create sample data for demonstration.
"""

import csv
import sys
import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json


class BankCSVParser:
    """Parses and standardizes bank CSV transaction files."""
    
    def __init__(self):
        self.bank_formats = {
            'chase': {
                'headers': ['Transaction Date', 'Post Date', 'Description', 'Category', 'Type', 'Amount', 'Memo'],
                'date_field': 'Transaction Date',
                'amount_field': 'Amount',
                'description_field': 'Description',
                'account_field': None,
                'date_format': '%m/%d/%Y'
            },
            'bofa': {
                'headers': ['Date', 'Description', 'Amount', 'Running Bal.'],
                'date_field': 'Date',
                'amount_field': 'Amount',
                'description_field': 'Description',
                'account_field': None,
                'date_format': '%m/%d/%Y'
            },
            'wells_fargo': {
                'headers': ['Date', 'Amount', 'Description', 'Account'],
                'date_field': 'Date',
                'amount_field': 'Amount',
                'description_field': 'Description',
                'account_field': 'Account',
                'date_format': '%m/%d/%Y'
            }
        }
    
    def detect_bank_format(self, headers: List[str]) -> Optional[str]:
        """Detect bank format based on CSV headers."""
        try:
            headers_lower = [h.lower().strip() for h in headers]
            
            # Chase detection
            chase_indicators = ['transaction date', 'post date', 'category', 'type']
            if all(indicator in headers_lower for indicator in chase_indicators[:2]):
                return 'chase'
            
            # Wells Fargo detection (has Account field)
            if 'account' in headers_lower and 'amount' in headers_lower:
                return 'wells_fargo'
            
            # Bank of America detection (has Running Bal.)
            if 'running bal.' in headers_lower or 'running balance' in headers_lower:
                return 'bofa'
            
            # Fallback detection by common fields
            if 'date' in headers_lower and 'amount' in headers_lower and 'description' in headers_lower:
                return 'bofa'  # Default to BOA format
            
            return None
        except Exception as e:
            print(f"Error detecting bank format: {e}", file=sys.stderr)
            return None
    
    def clean_amount(self, amount_str: str) -> float:
        """Clean and convert amount string to float."""
        try:
            # Remove currency symbols, commas, and extra spaces
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            
            # Handle parentheses as negative (some banks use this format)
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, AttributeError) as e:
            print(f"Error cleaning amount '{amount_str}': {e}", file=sys.stderr)
            return 0.0
    
    def parse_date(self, date_str: str, date_format: str) -> str:
        """Parse date string and return ISO format."""
        try:
            date_obj = datetime.strptime(date_str.strip(), date_format)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError as e:
            # Try alternative formats
            alternative_formats = ['%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y', '%Y/%m/%d']
            for fmt in alternative_formats:
                try:
                    date_obj = datetime.strptime(date_str.strip(), fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            print(f"Error parsing date '{date_str}': {e}", file=sys.stderr)
            return date_str
    
    def extract_account_info(self, description: str, account_field: Optional[str]) -> str:
        """Extract account information from description or account field."""
        try:
            if account_field:
                return str(account_field)
            
            # Try to extract account number from description
            account_match = re.search(r'(\d{4,})', description)
            if account_match:
                account_num = account_match.group(1)
                return f"***{account_num[-4:]}" if len(account_num) > 4 else account_num
            
            return "Unknown"
        except Exception:
            return "Unknown"
    
    def parse_csv_file(self, file_path: str) -> List[Dict]:
        """Parse CSV file and return standardized transactions."""
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                delimiter = ',' if ',' in sample else '\t'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    raise ValueError("No headers found in CSV file")
                
                bank_format = self.detect_bank_format(headers)
                if not bank_format:
                    raise ValueError(f"Unknown bank format. Headers: {headers}")
                
                print(f"Detected bank format: {bank_format.upper()}")
                format_config = self.bank_formats[bank_format]
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Extract standardized fields
                        raw_date = row.get(format_config['date_field'], '')
                        raw_amount = row.get(format_config['amount_field'], '')
                        raw_description = row.get(format_config['description_field'], '')
                        raw_account = row.get(format_config['account_field']) if format_config['account_field'] else None
                        
                        if not all([raw_date, raw_amount, raw_description]):
                            continue  # Skip incomplete rows
                        
                        # Parse and standardize
                        standardized_transaction = {
                            'date': self.parse_date(raw_date, format_config['date_format']),
                            'amount': self.clean_amount(raw_amount),
                            'description': raw_description.strip(),
                            'account': self.extract_account_info(raw_description, raw_account)
                        }
                        
                        transactions.append(standardized_transaction)
                        
                    except Exception as e:
                        print(f"Error processing row {row_num}: {e}", file=sys.stderr)
                        continue
                        
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found", file=sys.stderr)
        except Exception as e:
            print(f"Error parsing CSV file: {e}", file=sys.stderr)
        
        return transactions
    
    def create_sample_data(self) -> str:
        """Create sample CSV data for demonstration."""
        sample_file = "sample_transactions.csv"
        
        try:
            with open(sample_file, 'w', newline