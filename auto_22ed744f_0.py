```python
#!/usr/bin/env python3
"""
Bank CSV Parser and Transaction Standardizer

This module parses bank CSV files from various financial institutions and converts
them into a standardized transaction data structure. It automatically detects common
column formats for dates, descriptions, and amounts, handles multiple date formats,
and validates all required fields.

Features:
- Auto-detection of CSV column headers (case-insensitive)
- Multiple date format parsing (MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD, etc.)
- Amount parsing with currency symbols and parentheses for negative values
- Data validation with detailed error reporting
- Standardized output format for consistent downstream processing

Usage: python script.py <csv_file_path>
"""

import csv
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Optional, Tuple
import os


class Transaction:
    """Standardized transaction data structure"""
    
    def __init__(self, date: str, description: str, amount: Decimal, 
                 account_id: Optional[str] = None, category: Optional[str] = None):
        self.date = date
        self.description = description
        self.amount = amount
        self.account_id = account_id
        self.category = category
        
    def __dict__(self):
        return {
            'date': self.date,
            'description': self.description,
            'amount': float(self.amount),
            'account_id': self.account_id,
            'category': self.category
        }
        
    def __str__(self):
        return f"Transaction(date='{self.date}', desc='{self.description[:30]}...', amount=${self.amount})"


class BankCSVParser:
    """Main parser class for bank CSV files"""
    
    # Common column name patterns (case-insensitive)
    DATE_PATTERNS = [
        r'date', r'trans.*date', r'posting.*date', r'effective.*date', 
        r'value.*date', r'transaction.*date'
    ]
    
    DESCRIPTION_PATTERNS = [
        r'description', r'desc', r'memo', r'details', r'transaction.*desc',
        r'reference', r'narrative', r'payee'
    ]
    
    AMOUNT_PATTERNS = [
        r'amount', r'value', r'sum', r'total', r'balance', r'credit',
        r'debit', r'transaction.*amount'
    ]
    
    DEBIT_PATTERNS = [r'debit', r'withdrawal', r'out']
    CREDIT_PATTERNS = [r'credit', r'deposit', r'in']
    
    # Date format patterns
    DATE_FORMATS = [
        '%m/%d/%Y', '%m-%d-%Y', '%m.%d.%Y',
        '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
        '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d',
        '%m/%d/%y', '%m-%d-%y', '%d/%m/%y', '%d-%m-%y',
        '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y'
    ]
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.errors: List[str] = []
    
    def detect_delimiter(self, file_path: str) -> str:
        """Detect CSV delimiter by sampling first few lines"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                
            for delimiter in [',', ';', '\t', '|']:
                if sample.count(delimiter) > 2:
                    return delimiter
            return ','
        except Exception:
            return ','
    
    def match_column_pattern(self, header: str, patterns: List[str]) -> bool:
        """Check if header matches any of the given patterns"""
        header_clean = re.sub(r'[^\w\s]', '', header.lower().strip())
        return any(re.search(pattern, header_clean) for pattern in patterns)
    
    def detect_columns(self, headers: List[str]) -> Dict[str, int]:
        """Detect column indices for date, description, and amount fields"""
        column_map = {}
        
        for i, header in enumerate(headers):
            if 'date' not in column_map and self.match_column_pattern(header, self.DATE_PATTERNS):
                column_map['date'] = i
            elif 'description' not in column_map and self.match_column_pattern(header, self.DESCRIPTION_PATTERNS):
                column_map['description'] = i
            elif 'amount' not in column_map and self.match_column_pattern(header, self.AMOUNT_PATTERNS):
                column_map['amount'] = i
            elif 'debit' not in column_map and self.match_column_pattern(header, self.DEBIT_PATTERNS):
                column_map['debit'] = i
            elif 'credit' not in column_map and self.match_column_pattern(header, self.CREDIT_PATTERNS):
                column_map['credit'] = i
        
        return column_map
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string and return in YYYY-MM-DD format"""
        if not date_str or date_str.strip() == '':
            return None
            
        date_str = date_str.strip()
        
        for fmt in self.DATE_FORMATS:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string, handling currency symbols and negative indicators"""
        if not amount_str or amount_str.strip() == '':
            return None
            
        amount_str = amount_str.strip()
        
        # Check if amount is in parentheses (negative)
        is_negative = False
        if amount_str.startswith('(') and amount_str.endswith(')'):
            is_negative = True
            amount_str = amount_str[1:-1]
        
        # Remove currency symbols and whitespace
        amount_str = re.sub(r'[$€£¥₹,\s]', '', amount_str)
        
        # Handle negative signs
        if amount_str.startswith('-'):
            is_negative = True
            amount_str = amount_str[1:]
        
        try:
            amount = Decimal(amount_str)
            return -amount if is_negative else amount
        except (InvalidOperation, ValueError):
            return None
    
    def calculate_net_amount(self, row: List[str], column_map: Dict[str, int]) -> Optional[Decimal]:
        """Calculate net amount from separate debit/credit columns"""
        debit = Decimal('0')
        credit = Decimal('0')
        
        if 'debit' in column_map:
            debit_str = row[column_map['debit']] if column_map['debit'] < len(row) else ''
            debit_amount = self.parse_amount(debit_str)
            if debit_amount:
                debit = abs(debit_amount)
        
        if 'credit' in column_map:
            credit_str = row[column_map['credit']] if column_map['credit'] < len(row) else ''
            credit_amount = self.parse_amount(credit_str)
            if credit_amount:
                credit = abs(credit_amount)
        
        if debit == 0 and credit == 0:
            return None
        
        return credit - debit
    
    def validate_transaction(self, transaction: Transaction, row_num: int) -> bool:
        """Validate transaction data and log errors"""
        valid = True
        
        if not transaction.date:
            self.errors.append(f"Row {row_num