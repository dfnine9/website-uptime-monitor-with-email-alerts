```python
#!/usr/bin/env python3
"""
Bank CSV Transaction Parser and Validator

This module parses CSV files exported from various bank formats, validates the data integrity,
and creates a standardized transaction data structure. It handles common CSV variations,
performs data validation, and outputs standardized transaction records.

Features:
- Auto-detects common CSV formats from major banks
- Validates data integrity (date formats, numeric amounts, required fields)
- Standardizes transaction data into consistent format
- Handles encoding issues and malformed CSV data
- Provides detailed error reporting and validation statistics

Usage: python script.py [csv_file_path]
If no file path provided, uses sample data for demonstration.
"""

import csv
import sys
import re
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal, InvalidOperation
import io


@dataclass
class StandardizedTransaction:
    """Standardized transaction data structure"""
    date: str  # ISO format YYYY-MM-DD
    amount: str  # Decimal string with 2 decimal places
    merchant: str  # Merchant/payee name
    description: str  # Full transaction description
    original_data: Dict[str, Any]  # Original CSV row for reference


class BankCSVParser:
    """Main parser class for bank CSV files"""
    
    def __init__(self):
        self.validation_errors = []
        self.processed_count = 0
        self.valid_count = 0
        
    def detect_csv_format(self, headers: List[str]) -> str:
        """Detect bank CSV format based on headers"""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Common header patterns for different banks
        format_patterns = {
            'chase': ['date', 'description', 'amount', 'balance'],
            'bofa': ['date', 'description', 'amount', 'running bal.'],
            'wells_fargo': ['date', 'amount', 'description'],
            'citi': ['date', 'description', 'debit', 'credit'],
            'generic': ['date', 'amount', 'description']
        }
        
        for format_name, pattern in format_patterns.items():
            if all(any(p in h for h in headers_lower) for p in pattern):
                return format_name
                
        return 'unknown'
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats to ISO format"""
        if not date_str or not date_str.strip():
            return None
            
        date_str = date_str.strip()
        
        # Common date formats
        date_formats = [
            '%Y-%m-%d',     # 2023-12-01
            '%m/%d/%Y',     # 12/01/2023
            '%m-%d-%Y',     # 12-01-2023
            '%d/%m/%Y',     # 01/12/2023
            '%Y/%m/%d',     # 2023/12/01
            '%m/%d/%y',     # 12/01/23
            '%d-%m-%Y',     # 01-12-2023
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[str]:
        """Parse and validate amount strings"""
        if not amount_str or not amount_str.strip():
            return None
            
        # Clean amount string
        amount_str = amount_str.strip()
        amount_str = re.sub(r'[^\d.-]', '', amount_str)  # Remove currency symbols, commas
        
        if not amount_str:
            return None
            
        try:
            # Handle negative amounts in parentheses
            if amount_str.startswith('(') and amount_str.endswith(')'):
                amount_str = '-' + amount_str[1:-1]
                
            decimal_amount = Decimal(amount_str)
            return f"{decimal_amount:.2f}"
        except (InvalidOperation, ValueError):
            return None
    
    def extract_merchant(self, description: str, amount: str) -> str:
        """Extract merchant name from description"""
        if not description:
            return "Unknown Merchant"
            
        description = description.strip()
        
        # Common patterns for merchant extraction
        merchant_patterns = [
            r'^([A-Z\s&]+\s+[A-Z]{2,3}\s+\d+)',  # "WALMART SUPERCENTER #1234"
            r'^([A-Z][A-Za-z\s&]+?)(?:\s+\d+|$)',  # "Target Store 1234"
            r'([A-Z][A-Za-z\s&]+)',  # General uppercase merchant names
        ]
        
        for pattern in merchant_patterns:
            match = re.search(pattern, description)
            if match:
                merchant = match.group(1).strip()
                if len(merchant) > 3:  # Ensure meaningful merchant name
                    return merchant
        
        # Fallback: use first few words
        words = description.split()[:3]
        return ' '.join(words) if words else "Unknown Merchant"
    
    def map_csv_fields(self, row: Dict[str, str], csv_format: str) -> Dict[str, str]:
        """Map CSV fields to standard fields based on detected format"""
        field_mappings = {
            'chase': {
                'date': 'Date',
                'amount': 'Amount',
                'description': 'Description'
            },
            'bofa': {
                'date': 'Date',
                'amount': 'Amount',
                'description': 'Description'
            },
            'wells_fargo': {
                'date': 'Date',
                'amount': 'Amount',
                'description': 'Description'
            },
            'citi': {
                'date': 'Date',
                'amount': 'Amount',  # Will need special handling for debit/credit
                'description': 'Description'
            },
            'generic': {
                'date': next((k for k in row.keys() if 'date' in k.lower()), ''),
                'amount': next((k for k in row.keys() if 'amount' in k.lower()), ''),
                'description': next((k for k in row.keys() if 'description' in k.lower() or 'desc' in k.lower()), '')
            }
        }
        
        if csv_format not in field_mappings:
            csv_format = 'generic'
            
        mapping = field_mappings[csv_format]
        
        # Handle special case for Citi with separate debit/credit columns
        if csv_format == 'citi' and 'Debit' in row and 'Credit' in row:
            debit_amount = self.parse_amount(row.get('Debit', '0'))
            credit_amount = self.parse_amount(row.get('Credit', '0'))
            
            if debit_amount and float(debit_amount) != 0:
                amount = f"-{debit_amount}"
            elif credit_amount and float(credit_amount) != 0:
                amount = credit_amount
            else:
                amount = "0.00"
        else:
            amount = row.get(mapping.get('amount', ''), '')
        
        return {
            'date': row.get(mapping.get('date', ''), ''),
            'amount': amount,
            'description': row.get(mapping.get('description', ''), '')
        }
    
    def validate_transaction(self, mapped_fields: Dict[str, str], row_num: int) -> Optional[StandardizedTransaction]:
        """Validate and create standardized transaction"""
        errors = []
        
        # Parse and validate date
        parsed_date = self.parse_date(mapped_fields['date'])
        if not parsed_date:
            errors.append(f"Invalid date: