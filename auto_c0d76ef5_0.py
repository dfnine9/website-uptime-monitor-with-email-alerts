```python
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statement files and automatically categorizes transactions
using regex pattern matching on merchant names and transaction descriptions.

Features:
- Parses CSV files with transaction data (date, description, amount)
- Categorizes transactions by merchant patterns and transaction types
- Handles various CSV formats and encoding issues
- Provides detailed categorization statistics
- Self-contained with minimal dependencies

Usage: python script.py
"""

import csv
import re
import os
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions using regex pattern matching."""
    
    def __init__(self):
        self.merchant_patterns = {
            'Grocery': [
                r'walmart|target|kroger|safeway|albertsons|publix|whole foods|trader joe',
                r'grocery|supermarket|food mart|market.*food'
            ],
            'Gas': [
                r'shell|exxon|bp|chevron|mobil|valero|citgo|marathon|sunoco',
                r'gas.*station|fuel|petro'
            ],
            'Restaurant': [
                r'mcdonalds|burger king|subway|starbucks|chipotle|domino|pizza',
                r'restaurant|cafe|diner|bistro|grill'
            ],
            'Retail': [
                r'amazon|ebay|best buy|home depot|lowes|costco|sams club',
                r'store|retail|shop|mall'
            ],
            'Banking': [
                r'atm|bank|credit union|finance|loan|mortgage',
                r'fee|interest|transfer|deposit'
            ],
            'Utilities': [
                r'electric|gas.*company|water|sewer|trash|internet|phone|cable',
                r'utility|utilities|power|energy'
            ],
            'Healthcare': [
                r'hospital|clinic|pharmacy|cvs|walgreens|rite aid|medical',
                r'doctor|dentist|health|prescription'
            ],
            'Transportation': [
                r'uber|lyft|taxi|bus|metro|train|airline|airport',
                r'transportation|transit|parking'
            ]
        }
        
        self.transaction_types = {
            'ATM Withdrawal': [r'atm.*withdrawal|cash.*withdrawal|atm.*debit'],
            'Direct Deposit': [r'direct.*deposit|payroll|salary|wages'],
            'Check': [r'check.*#|ck.*#|chk.*#|check.*payment'],
            'Debit Card': [r'debit.*card|pos.*purchase|card.*purchase'],
            'Transfer': [r'transfer|xfer|online.*transfer'],
            'Fee': [r'fee|charge|penalty|overdraft'],
            'Interest': [r'interest.*earned|interest.*paid'],
            'Refund': [r'refund|return|reversal|credit']
        }
    
    def parse_csv_file(self, filepath: str) -> List[Dict]:
        """Parse CSV file and extract transaction data."""
        transactions = []
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin1', 'cp1252']
            file_content = None
            
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as file:
                        file_content = file.read()
                        break
                except UnicodeDecodeError:
                    continue
            
            if file_content is None:
                raise ValueError(f"Could not decode file {filepath}")
            
            # Detect delimiter
            delimiter = ','
            if file_content.count(';') > file_content.count(','):
                delimiter = ';'
            elif file_content.count('\t') > file_content.count(','):
                delimiter = '\t'
            
            # Parse CSV
            lines = file_content.strip().split('\n')
            reader = csv.DictReader(lines, delimiter=delimiter)
            
            for row in reader:
                # Try to identify date, description, and amount columns
                transaction = self._extract_transaction_data(row)
                if transaction:
                    transactions.append(transaction)
                    
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            
        return transactions
    
    def _extract_transaction_data(self, row: Dict) -> Optional[Dict]:
        """Extract date, description, and amount from CSV row."""
        # Common column name variations
        date_cols = ['date', 'transaction date', 'trans date', 'posting date']
        desc_cols = ['description', 'desc', 'transaction description', 'merchant', 'payee']
        amount_cols = ['amount', 'debit', 'credit', 'transaction amount']
        
        # Find columns (case insensitive)
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        
        date_val = None
        desc_val = None
        amount_val = None
        
        # Extract date
        for col in date_cols:
            if col in row_lower and row_lower[col]:
                date_val = row_lower[col]
                break
        
        # Extract description
        for col in desc_cols:
            if col in row_lower and row_lower[col]:
                desc_val = row_lower[col]
                break
        
        # Extract amount (handle debit/credit columns)
        if 'debit' in row_lower and 'credit' in row_lower:
            debit = self._parse_amount(row_lower.get('debit', ''))
            credit = self._parse_amount(row_lower.get('credit', ''))
            if debit:
                amount_val = -abs(debit)
            elif credit:
                amount_val = abs(credit)
        else:
            for col in amount_cols:
                if col in row_lower and row_lower[col]:
                    amount_val = self._parse_amount(row_lower[col])
                    break
        
        if date_val and desc_val and amount_val is not None:
            return {
                'date': self._parse_date(date_val),
                'description': desc_val.strip(),
                'amount': amount_val,
                'raw_row': row
            }
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime object."""
        date_formats = [
            '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y',
            '%m-%d-%Y', '%Y/%m/%d', '%d-%m-%Y', '%m.%d.%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string into float."""
        if not amount_str:
            return None
        
        # Clean amount string
        cleaned = re.sub(r'[^\d.-]', '', str(amount_str))
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def categorize_transaction(self, transaction: Dict) -> Tuple[str, str]:
        """Categorize transaction by merchant and transaction type."""
        description = transaction['description'].lower()
        amount = transaction['amount']
        
        # Determine merchant category
        merchant_category = 'Other'
        for category, patterns in self.merchant_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    merchant_category = category
                    break
            if merchant_category != 'Other':
                break
        
        # Determine transaction type
        transaction_type = 'Other'
        for t_type, patterns in self.transaction_types.items():
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    transaction_type = t