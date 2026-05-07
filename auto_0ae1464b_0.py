```python
#!/usr/bin/env python3
"""
Bank Statement CSV Parser

A self-contained Python script that parses CSV bank statements and extracts 
transaction data (date, amount, description) into a structured DataFrame format
with comprehensive data validation and error handling.

This script automatically detects common CSV formats used by banks and financial
institutions, validates transaction data, and outputs a clean DataFrame with
standardized columns: Date, Amount, Description.

Features:
- Automatic CSV format detection
- Date parsing with multiple format support
- Amount validation and standardization
- Comprehensive error handling
- Data type validation
- Duplicate detection and handling

Usage:
    python script.py

The script will look for CSV files in the current directory or prompt for input.
"""

import csv
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path


class BankStatementParser:
    """Parser for bank statement CSV files with data validation."""
    
    def __init__(self):
        self.date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%m-%d-%Y', '%d-%m-%Y', '%b %d, %Y', '%B %d, %Y',
            '%d %b %Y', '%d %B %Y', '%Y%m%d'
        ]
        self.amount_pattern = re.compile(r'^-?\$?[\d,]+\.?\d*$')
        
    def detect_csv_format(self, filepath: str) -> Dict[str, int]:
        """Detect CSV column format by analyzing headers."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try different delimiters
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if ';' in sample and sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif '\t' in sample and sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                headers = [h.lower().strip() for h in headers]
                
                format_map = {'date': -1, 'amount': -1, 'description': -1}
                
                # Common header patterns
                date_patterns = ['date', 'transaction date', 'posted date', 'value date']
                amount_patterns = ['amount', 'debit', 'credit', 'transaction amount', 'value']
                desc_patterns = ['description', 'memo', 'details', 'transaction details', 'reference']
                
                for i, header in enumerate(headers):
                    # Date column detection
                    if any(pattern in header for pattern in date_patterns):
                        format_map['date'] = i
                    
                    # Amount column detection  
                    elif any(pattern in header for pattern in amount_patterns):
                        format_map['amount'] = i
                    
                    # Description column detection
                    elif any(pattern in header for pattern in desc_patterns):
                        format_map['description'] = i
                
                return format_map
                
        except Exception as e:
            raise ValueError(f"Error detecting CSV format: {str(e)}")
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string using multiple format attempts."""
        if not date_str or date_str.strip() == '':
            return None
            
        date_str = date_str.strip()
        
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try to handle some edge cases
        try:
            # Remove extra spaces and try parsing
            cleaned = re.sub(r'\s+', ' ', date_str)
            for fmt in self.date_formats:
                try:
                    return datetime.strptime(cleaned, fmt)
                except ValueError:
                    continue
        except:
            pass
            
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse and validate amount string."""
        if not amount_str or amount_str.strip() == '':
            return None
            
        amount_str = amount_str.strip()
        
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[\$£€¥\s]', '', amount_str)
        
        # Handle parentheses as negative
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        # Remove commas
        cleaned = cleaned.replace(',', '')
        
        # Validate format
        if not re.match(r'^-?\d+\.?\d*$', cleaned):
            return None
            
        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
    
    def validate_row(self, row: Dict) -> Tuple[bool, str]:
        """Validate a single transaction row."""
        errors = []
        
        if not row.get('date'):
            errors.append("Missing or invalid date")
            
        if row.get('amount') is None:
            errors.append("Missing or invalid amount")
            
        if not row.get('description') or row.get('description').strip() == '':
            errors.append("Missing description")
        
        return len(errors) == 0, "; ".join(errors)
    
    def parse_csv(self, filepath: str) -> List[Dict]:
        """Parse CSV file and return structured transaction data."""
        try:
            # Detect format
            format_map = self.detect_csv_format(filepath)
            
            if -1 in format_map.values():
                missing = [k for k, v in format_map.items() if v == -1]
                raise ValueError(f"Could not detect columns: {', '.join(missing)}")
            
            transactions = []
            errors = []
            
            with open(filepath, 'r', encoding='utf-8') as file:
                # Determine delimiter again
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if ';' in sample and sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif '\t' in sample and sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.reader(file, delimiter=delimiter)
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(format_map.values()):
                            errors.append(f"Row {row_num}: Insufficient columns")
                            continue
                        
                        # Extract data
                        date_str = row[format_map['date']] if format_map['date'] < len(row) else ''
                        amount_str = row[format_map['amount']] if format_map['amount'] < len(row) else ''
                        desc_str = row[format_map['description']] if format_map['description'] < len(row) else ''
                        
                        # Parse date
                        parsed_date = self.parse_date(date_str)
                        if not parsed_date:
                            errors.append(f"Row {row_num}: Invalid date '{date_str}'")
                            continue
                        
                        # Parse amount
                        parsed_amount = self.parse_amount(amount_str)
                        if parsed_amount is None:
                            errors.append(f"Row {row_num}: Invalid amount '{amount_str}'")
                            continue
                        
                        # Create transaction record
                        transaction = {
                            'Date': parsed_date.strftime('%Y-%m-%d'),
                            'Amount': float(parsed_amount),
                            'Description': desc_str.strip()
                        }
                        
                        # Validate
                        is_valid, error_msg = self.validate_row(transaction)
                        if not