```python
#!/usr/bin/env python3
"""
Bank Statement CSV Parser and Categorizer

This module provides functionality to parse CSV bank statements from various banks,
categorize transactions based on configurable keyword matching, and validate data
formats. Supports configurable column mapping to handle different bank CSV formats.

Features:
- Configurable CSV column mapping for different bank formats
- Keyword-based transaction categorization with predefined dictionaries
- Data validation for common CSV formats from major banks
- Comprehensive error handling and reporting
- Self-contained implementation using only standard library

Usage:
    python script.py

The script will process sample data and demonstrate the categorization functionality.
"""

import csv
import re
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from io import StringIO


@dataclass
class Transaction:
    """Represents a single bank transaction."""
    date: datetime
    description: str
    amount: Decimal
    balance: Optional[Decimal] = None
    category: str = "Uncategorized"
    reference: str = ""


class BankStatementParser:
    """Parses and categorizes bank statement CSV files."""
    
    def __init__(self):
        """Initialize parser with predefined bank formats and categories."""
        self.bank_formats = {
            'chase': {
                'date': ['Transaction Date', 'Date'],
                'description': ['Description'],
                'amount': ['Amount'],
                'balance': ['Balance'],
                'reference': ['Check or Slip #']
            },
            'bank_of_america': {
                'date': ['Posted Date', 'Date'],
                'description': ['Payee'],
                'amount': ['Amount'],
                'balance': ['Running Bal.'],
                'reference': ['Reference Number']
            },
            'wells_fargo': {
                'date': ['Date'],
                'description': ['Description'],
                'amount': ['Amount'],
                'balance': ['Balance'],
                'reference': ['Reference']
            },
            'generic': {
                'date': ['date', 'transaction_date', 'Date', 'Transaction Date'],
                'description': ['description', 'Description', 'Payee', 'Details'],
                'amount': ['amount', 'Amount', 'Debit', 'Credit'],
                'balance': ['balance', 'Balance', 'Running Balance', 'Running Bal.'],
                'reference': ['reference', 'Reference', 'Check Number', 'Check or Slip #']
            }
        }
        
        self.category_keywords = {
            'Food & Dining': [
                'restaurant', 'mcdonalds', 'burger', 'pizza', 'starbucks', 'coffee',
                'grocery', 'safeway', 'kroger', 'walmart', 'target', 'whole foods',
                'food', 'cafe', 'diner', 'bistro', 'bar', 'pub', 'grill'
            ],
            'Transportation': [
                'gas', 'fuel', 'shell', 'chevron', 'exxon', 'bp', 'uber', 'lyft',
                'taxi', 'metro', 'bus', 'train', 'parking', 'toll', 'dmv',
                'auto', 'car wash', 'mechanic', 'tire'
            ],
            'Shopping': [
                'amazon', 'ebay', 'shop', 'store', 'mall', 'outlet', 'retail',
                'clothing', 'shoes', 'electronics', 'best buy', 'costco'
            ],
            'Utilities': [
                'electric', 'gas bill', 'water', 'internet', 'phone', 'cable',
                'utility', 'pg&e', 'comcast', 'verizon', 'at&t', 'tmobile'
            ],
            'Healthcare': [
                'hospital', 'doctor', 'medical', 'pharmacy', 'cvs', 'walgreens',
                'dental', 'vision', 'clinic', 'lab', 'health'
            ],
            'Entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'game', 'concert',
                'event', 'ticket', 'entertainment', 'gym', 'fitness'
            ],
            'Banking': [
                'fee', 'atm', 'overdraft', 'interest', 'transfer', 'deposit',
                'withdrawal', 'check', 'wire', 'service charge'
            ],
            'Income': [
                'salary', 'payroll', 'wage', 'deposit', 'refund', 'cashback',
                'dividend', 'interest income', 'bonus', 'freelance'
            ]
        }

    def detect_bank_format(self, headers: List[str]) -> str:
        """
        Detect bank format based on CSV headers.
        
        Args:
            headers: List of column headers from CSV
            
        Returns:
            String identifying the bank format
        """
        header_lower = [h.lower().strip() for h in headers]
        
        # Check for specific bank patterns
        for bank, format_def in self.bank_formats.items():
            if bank == 'generic':
                continue
                
            matches = 0
            total_fields = len(format_def)
            
            for field, possible_names in format_def.items():
                if any(name.lower() in header_lower for name in possible_names):
                    matches += 1
                    
            if matches >= total_fields * 0.6:  # 60% match threshold
                return bank
                
        return 'generic'

    def map_columns(self, headers: List[str], bank_format: str) -> Dict[str, int]:
        """
        Map CSV columns to standard field names.
        
        Args:
            headers: List of column headers
            bank_format: Detected bank format
            
        Returns:
            Dictionary mapping field names to column indices
        """
        mapping = {}
        format_def = self.bank_formats.get(bank_format, self.bank_formats['generic'])
        
        for field, possible_names in format_def.items():
            for i, header in enumerate(headers):
                if any(name.lower() == header.lower().strip() for name in possible_names):
                    mapping[field] = i
                    break
                    
        return mapping

    def validate_date(self, date_str: str) -> datetime:
        """
        Validate and parse date string.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If date format is invalid
        """
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%d/%m/%Y',
            '%m/%d/%y', '%m-%d-%y', '%y-%m-%d', '%d/%m/%y',
            '%B %d, %Y', '%b %d, %Y'
        ]
        
        date_str = date_str.strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        raise ValueError(f"Unable to parse date: {date_str}")

    def validate_amount(self, amount_str: str) -> Decimal:
        """
        Validate and parse amount string.
        
        Args:
            amount_str: Amount string to parse
            
        Returns:
            Parsed Decimal amount
            
        Raises:
            ValueError: If amount format is invalid
        """
        # Clean the amount string
        amount_str = amount_str.strip()
        
        # Remove currency symbols and extra whitespace
        amount_str = re.sub(r'[$,\s]', '', amount_str)
        
        # Handle parentheses for negative amounts
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
            
        try:
            return Decimal(amount_str)
        except InvalidOperation:
            raise ValueError(f"Unable to parse amount: