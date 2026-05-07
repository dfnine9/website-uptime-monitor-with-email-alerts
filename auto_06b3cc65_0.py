```python
#!/usr/bin/env python3
"""
Bank Statement CSV Parser and Validator

This module parses CSV bank statements from major banks and validates transaction data.
Supports common CSV formats and validates date, description, and amount fields.
Handles various date formats and currency representations commonly used by banks.

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Optional, Tuple
import os


class BankStatementParser:
    """Parse and validate bank statement CSV files."""
    
    # Common date formats used by banks
    DATE_FORMATS = [
        '%m/%d/%Y',     # US format: 12/31/2023
        '%m-%d-%Y',     # US format: 12-31-2023
        '%Y-%m-%d',     # ISO format: 2023-12-31
        '%d/%m/%Y',     # EU format: 31/12/2023
        '%d-%m-%Y',     # EU format: 31-12-2023
        '%m/%d/%y',     # US short: 12/31/23
        '%d/%m/%y',     # EU short: 31/12/23
    ]
    
    # Common field name variations across banks
    FIELD_MAPPINGS = {
        'date': ['date', 'transaction date', 'posted date', 'trans date', 'effective date'],
        'description': ['description', 'memo', 'transaction', 'details', 'reference', 'payee'],
        'amount': ['amount', 'transaction amount', 'debit', 'credit', 'withdrawal', 'deposit']
    }

    def __init__(self):
        self.transactions = []
        self.errors = []
        self.stats = {
            'total_rows': 0,
            'valid_transactions': 0,
            'invalid_transactions': 0,
            'parsing_errors': 0
        }

    def detect_delimiter(self, file_path: str) -> str:
        """Detect CSV delimiter by sampling the file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                return delimiter
        except Exception:
            return ','  # Default to comma

    def normalize_field_names(self, headers: List[str]) -> Dict[str, str]:
        """Map CSV headers to standardized field names."""
        field_map = {}
        headers_lower = [h.lower().strip() for h in headers]
        
        for standard_field, variations in self.FIELD_MAPPINGS.items():
            for header_idx, header in enumerate(headers_lower):
                if any(variation in header for variation in variations):
                    field_map[standard_field] = headers[header_idx]
                    break
        
        return field_map

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string using common bank date formats."""
        if not date_str or date_str.strip() == '':
            return None
            
        date_str = date_str.strip()
        
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None

    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string handling various currency formats."""
        if not amount_str or amount_str.strip() == '':
            return None
            
        # Remove common currency symbols and whitespace
        cleaned = re.sub(r'[$£€¥,\s]', '', amount_str.strip())
        
        # Handle parentheses for negative amounts (accounting format)
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None

    def validate_transaction(self, row: Dict[str, Any], field_map: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate a single transaction row."""
        errors = []
        
        # Check for required fields
        if 'date' not in field_map:
            errors.append("No date field found")
        elif not row.get(field_map['date']):
            errors.append("Date field is empty")
        else:
            parsed_date = self.parse_date(row[field_map['date']])
            if parsed_date is None:
                errors.append(f"Invalid date format: {row[field_map['date']]}")
        
        if 'description' not in field_map:
            errors.append("No description field found")
        elif not row.get(field_map['description'], '').strip():
            errors.append("Description field is empty")
        
        if 'amount' not in field_map:
            errors.append("No amount field found")
        elif not row.get(field_map['amount']):
            errors.append("Amount field is empty")
        else:
            parsed_amount = self.parse_amount(row[field_map['amount']])
            if parsed_amount is None:
                errors.append(f"Invalid amount format: {row[field_map['amount']]}")
        
        return len(errors) == 0, errors

    def parse_csv_file(self, file_path: str) -> bool:
        """Parse CSV file and validate transactions."""
        if not os.path.exists(file_path):
            self.errors.append(f"File not found: {file_path}")
            return False
        
        try:
            delimiter = self.detect_delimiter(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try to detect if file has headers
                sample_lines = [file.readline() for _ in range(2)]
                file.seek(0)
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    self.errors.append("Could not detect CSV headers")
                    return False
                
                field_map = self.normalize_field_names(headers)
                
                if not any(field in field_map for field in ['date', 'description', 'amount']):
                    self.errors.append("Could not identify required fields (date, description, amount)")
                    return False
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    self.stats['total_rows'] += 1
                    
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    is_valid, validation_errors = self.validate_transaction(row, field_map)
                    
                    if is_valid:
                        # Parse and store valid transaction
                        transaction = {
                            'row_number': row_num,
                            'date': self.parse_date(row[field_map['date']]) if 'date' in field_map else None,
                            'description': row[field_map['description']].strip() if 'description' in field_map else '',
                            'amount': self.parse_amount(row[field_map['amount']]) if 'amount' in field_map else None,
                            'raw_data': row
                        }
                        self.transactions.append(transaction)
                        self.stats['valid_transactions'] += 1
                    else:
                        self.stats['invalid_transactions'] += 1
                        for error in validation_errors:
                            self.errors.append(f"Row {row_num}: {error}")
                
                return True
                
        except Exception as e:
            self.errors.append(f"Error parsing CSV file: {str(e)}")
            self.stats['parsing_errors'] += 1
            return False

    def print_results(self):
        """Print parsing results to stdout."""
        print("=" * 60)
        print("BANK STATEMENT CSV PARSER