```python
"""
Bank CSV Parser and Standardizer

This module parses common bank CSV formats from major US banks (Chase, Wells Fargo, 
Bank of America) and standardizes transaction data into a unified format.

Unified format includes:
- date: Transaction date in YYYY-MM-DD format
- description: Transaction description/merchant
- amount: Transaction amount as float (negative for debits, positive for credits)
- account: Account identifier from the source file

Supports CSV files with headers matching common bank export formats.
"""

import csv
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class BankCSVParser:
    """Parser for standardizing bank CSV formats from major US banks."""
    
    def __init__(self):
        # Define field mappings for different bank formats
        self.bank_mappings = {
            'chase': {
                'date_fields': ['Transaction Date', 'Post Date', 'Date'],
                'description_fields': ['Description', 'Memo', 'Transaction Description'],
                'amount_fields': ['Amount', 'Transaction Amount'],
                'account_fields': ['Account Number', 'Account', 'Card Number']
            },
            'wells_fargo': {
                'date_fields': ['Date', 'Transaction Date', 'Posting Date'],
                'description_fields': ['Description', 'Memo', 'Details'],
                'amount_fields': ['Amount', 'Transaction Amount', 'Debit', 'Credit'],
                'account_fields': ['Account Number', 'Account', 'Card']
            },
            'bank_of_america': {
                'date_fields': ['Date', 'Posted Date', 'Transaction Date'],
                'description_fields': ['Description', 'Payee', 'Reference Number'],
                'amount_fields': ['Amount', 'Transaction Amount'],
                'account_fields': ['Account Number', 'Running Bal.', 'Account']
            }
        }
    
    def detect_date_format(self, date_string: str) -> Optional[str]:
        """Detect and return the date format of a date string."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', 
            '%d/%m/%Y', '%d/%m/%y', '%Y/%m/%d',
            '%m-%d-%Y', '%m-%d-%y', '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                datetime.strptime(date_string.strip(), fmt)
                return fmt
            except ValueError:
                continue
        return None
    
    def standardize_date(self, date_string: str) -> str:
        """Convert date string to standardized YYYY-MM-DD format."""
        if not date_string or date_string.strip() == '':
            return ''
        
        date_format = self.detect_date_format(date_string)
        if date_format:
            try:
                dt = datetime.strptime(date_string.strip(), date_format)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass
        return date_string.strip()
    
    def standardize_amount(self, amount_string: str, debit_col: str = '', credit_col: str = '') -> float:
        """Convert amount string to standardized float (negative for debits)."""
        try:
            # Handle cases where debit/credit are in separate columns
            if debit_col and credit_col:
                debit_val = float(debit_col.replace('$', '').replace(',', '').strip()) if debit_col.strip() else 0
                credit_val = float(credit_col.replace('$', '').replace(',', '').strip()) if credit_col.strip() else 0
                return credit_val - debit_val
            
            # Handle single amount column
            if not amount_string or amount_string.strip() == '':
                return 0.0
            
            # Clean the amount string
            clean_amount = amount_string.replace('$', '').replace(',', '').replace('+', '').strip()
            
            # Handle negative amounts in parentheses
            if clean_amount.startswith('(') and clean_amount.endswith(')'):
                clean_amount = '-' + clean_amount[1:-1]
            
            return float(clean_amount)
        except (ValueError, TypeError):
            return 0.0
    
    def find_field(self, headers: List[str], field_options: List[str]) -> Optional[str]:
        """Find the first matching field name in headers."""
        headers_lower = [h.lower().strip() for h in headers]
        for option in field_options:
            if option.lower().strip() in headers_lower:
                return headers[headers_lower.index(option.lower().strip())]
        return None
    
    def detect_bank_format(self, headers: List[str]) -> str:
        """Detect bank format based on CSV headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Check for bank-specific patterns
        if any('chase' in h for h in headers_lower):
            return 'chase'
        elif any('wells' in h or 'fargo' in h for h in headers_lower):
            return 'wells_fargo'
        elif any('bank of america' in h or 'boa' in h for h in headers_lower):
            return 'bank_of_america'
        
        # Try to match by common field patterns
        for bank, mappings in self.bank_mappings.items():
            matches = 0
            for field_type, field_options in mappings.items():
                if self.find_field(headers, field_options):
                    matches += 1
            if matches >= 2:  # Need at least 2 matching field types
                return bank
        
        return 'chase'  # Default fallback
    
    def parse_csv_file(self, filepath: str, account_name: str = None) -> List[Dict[str, Any]]:
        """Parse a bank CSV file and return standardized transaction data."""
        standardized_transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect dialect
                try:
                    sample = file.read(1024)
                    file.seek(0)
                    dialect = csv.Sniffer().sniff(sample)
                except:
                    dialect = csv.excel
                
                reader = csv.DictReader(file, dialect=dialect)
                headers = reader.fieldnames
                
                if not headers:
                    print(f"Error: No headers found in {filepath}")
                    return []
                
                bank_format = self.detect_bank_format(headers)
                mappings = self.bank_mappings[bank_format]
                
                # Find the relevant columns
                date_col = self.find_field(headers, mappings['date_fields'])
                desc_col = self.find_field(headers, mappings['description_fields'])
                amount_col = self.find_field(headers, mappings['amount_fields'])
                account_col = self.find_field(headers, mappings['account_fields'])
                
                # Check for separate debit/credit columns (common in Wells Fargo)
                debit_col = self.find_field(headers, ['Debit', 'Debit Amount'])
                credit_col = self.find_field(headers, ['Credit', 'Credit Amount'])
                
                if not date_col or not desc_col:
                    print(f"Warning: Could not find required columns in {filepath}")
                    print(f"Available headers: {headers}")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Extract and standardize data
                        date = self.standardize_date(row.get(date_col, '') if date_col else '')
                        description = row.get(desc_col, '').strip() if desc_col else ''
                        
                        # Handle amount calculation
                        if debit_col and credit_col:
                            amount = self.standardize_amount('', 
                                                           row.get(debit_col, ''),