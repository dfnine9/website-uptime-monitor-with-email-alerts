```python
"""
Bank Transaction CSV Parser

This module provides a comprehensive solution for parsing CSV transaction files from major banks
(Chase, Wells Fargo, Bank of America) with configurable column mapping and data validation.

Features:
- Configurable column mapping for different bank formats
- Data integrity validation (date formats, amount parsing, required fields)
- Error handling with detailed reporting
- Support for common CSV variations (different delimiters, encodings)
- Transaction categorization and summary statistics

Usage:
    python script.py [csv_file_path]

If no file path is provided, the script will look for CSV files in the current directory.
"""

import csv
import os
import sys
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple, Any
import argparse


class BankCSVParser:
    """
    A comprehensive CSV parser for bank transaction files with support for multiple bank formats.
    """
    
    # Bank-specific column mappings
    BANK_FORMATS = {
        'chase': {
            'date': ['Transaction Date', 'Date', 'Post Date'],
            'description': ['Description', 'Transaction Description'],
            'amount': ['Amount', 'Transaction Amount'],
            'balance': ['Balance', 'Running Balance'],
            'type': ['Transaction Type', 'Type'],
            'category': ['Category', 'Transaction Category']
        },
        'wells_fargo': {
            'date': ['Date', 'Transaction Date'],
            'description': ['Description', 'Transaction Description', 'Memo'],
            'amount': ['Amount', 'Transaction Amount', 'Debit', 'Credit'],
            'balance': ['Available Balance', 'Balance'],
            'type': ['Transaction Type', 'Type'],
            'reference': ['Reference Number', 'Check Number']
        },
        'bank_of_america': {
            'date': ['Posted Date', 'Date', 'Transaction Date'],
            'description': ['Payee', 'Description', 'Transaction Description'],
            'amount': ['Amount', 'Transaction Amount'],
            'balance': ['Running Balance', 'Balance'],
            'type': ['Transaction Type', 'Type'],
            'reference': ['Reference Number', 'Check Number']
        },
        'generic': {
            'date': ['date', 'transaction_date', 'posted_date', 'Date', 'Transaction Date'],
            'description': ['description', 'memo', 'payee', 'Description', 'Memo', 'Payee'],
            'amount': ['amount', 'transaction_amount', 'Amount', 'Transaction Amount'],
            'balance': ['balance', 'running_balance', 'Balance', 'Running Balance'],
            'type': ['type', 'transaction_type', 'Type', 'Transaction Type']
        }
    }
    
    def __init__(self, custom_mapping: Optional[Dict] = None):
        """
        Initialize the parser with optional custom column mapping.
        
        Args:
            custom_mapping: Custom column mapping dictionary
        """
        self.custom_mapping = custom_mapping or {}
        self.errors = []
        self.warnings = []
        self.transactions = []
        
    def detect_bank_format(self, headers: List[str]) -> str:
        """
        Detect the bank format based on CSV headers.
        
        Args:
            headers: List of column headers from CSV
            
        Returns:
            Detected bank format name
        """
        headers_lower = [h.lower().strip() for h in headers]
        
        # Check for bank-specific patterns
        if any('chase' in h for h in headers_lower):
            return 'chase'
        elif any('wells fargo' in h for h in headers_lower):
            return 'wells_fargo'
        elif any('bank of america' in h for h in headers_lower):
            return 'bank_of_america'
        
        # Score each format based on header matches
        scores = {}
        for bank, mapping in self.BANK_FORMATS.items():
            score = 0
            for field_type, possible_names in mapping.items():
                for name in possible_names:
                    if name.lower() in headers_lower:
                        score += 1
                        break
            scores[bank] = score
        
        # Return the format with the highest score
        best_format = max(scores, key=scores.get)
        return best_format if scores[best_format] > 0 else 'generic'
    
    def map_columns(self, headers: List[str], bank_format: str) -> Dict[str, int]:
        """
        Map standard field names to column indices.
        
        Args:
            headers: List of column headers
            bank_format: Detected bank format
            
        Returns:
            Dictionary mapping field names to column indices
        """
        mapping = {}
        format_config = self.BANK_FORMATS.get(bank_format, self.BANK_FORMATS['generic'])
        
        # Add custom mapping if provided
        if self.custom_mapping:
            format_config.update(self.custom_mapping)
        
        for field_type, possible_names in format_config.items():
            for i, header in enumerate(headers):
                for possible_name in possible_names:
                    if header.strip().lower() == possible_name.lower():
                        mapping[field_type] = i
                        break
                if field_type in mapping:
                    break
        
        return mapping
    
    def validate_date(self, date_str: str, row_num: int) -> Optional[datetime]:
        """
        Validate and parse date string.
        
        Args:
            date_str: Date string to validate
            row_num: Row number for error reporting
            
        Returns:
            Parsed datetime object or None if invalid
        """
        if not date_str or date_str.strip() == '':
            self.errors.append(f"Row {row_num}: Empty date field")
            return None
        
        date_formats = [
            '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y',
            '%B %d, %Y', '%b %d, %Y', '%Y%m%d', '%m-%d-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        self.errors.append(f"Row {row_num}: Invalid date format '{date_str}'")
        return None
    
    def validate_amount(self, amount_str: str, row_num: int) -> Optional[Decimal]:
        """
        Validate and parse amount string.
        
        Args:
            amount_str: Amount string to validate
            row_num: Row number for error reporting
            
        Returns:
            Parsed Decimal amount or None if invalid
        """
        if not amount_str or amount_str.strip() == '':
            self.warnings.append(f"Row {row_num}: Empty amount field")
            return None
        
        # Clean the amount string
        cleaned = re.sub(r'[^\d.,\-+]', '', amount_str.strip())
        
        # Handle parentheses for negative amounts
        if '(' in amount_str and ')' in amount_str:
            cleaned = '-' + cleaned.replace('(', '').replace(')', '')
        
        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            self.errors.append(f"Row {row_num}: Invalid amount format '{amount_str}'")
            return None
    
    def parse_csv_file(self, file_path: str, encoding: str = 'utf-8') -> bool:
        """
        Parse a CSV file and extract transaction data.
        
        Args:
            file_path: Path to the CSV file
            encoding: File encoding (default: utf-8)
            
        Returns:
            True if parsing was successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding=encoding, newline='') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if '\t' in sample and sample.count('\t') >