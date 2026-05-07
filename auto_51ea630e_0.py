```python
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements and automatically categorizes transactions
using keyword matching. It identifies transaction types such as groceries, gas,
restaurants, utilities, and more based on merchant names and descriptions.

The script reads a CSV file containing bank transactions, applies categorization
rules based on predefined keywords, and outputs the categorized data in a
structured format to stdout.

Usage:
    python script.py

The script expects a CSV file named 'bank_statement.csv' in the same directory
with columns: Date, Description, Amount, Balance (optional)
"""

import csv
import re
import json
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class TransactionCategorizer:
    """Handles categorization of bank transactions based on keyword matching."""
    
    def __init__(self):
        """Initialize the categorizer with predefined category keywords."""
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'grocery', 'supermarket', 'food store',
                'market', 'aldi', 'publix', 'wegmans', 'harris teeter'
            ],
            'gas': [
                'shell', 'exxon', 'chevron', 'bp', 'mobil', 'texaco', 'valero',
                'marathon', 'sunoco', 'citgo', 'gas station', 'fuel', 'petrol'
            ],
            'restaurants': [
                'mcdonald', 'burger king', 'subway', 'starbucks', 'pizza',
                'restaurant', 'cafe', 'diner', 'grill', 'bistro', 'bar',
                'taco bell', 'kfc', 'wendy', 'chipotle', 'panera'
            ],
            'utilities': [
                'electric', 'electricity', 'gas company', 'water', 'sewer',
                'internet', 'cable', 'phone', 'wireless', 'utility',
                'comcast', 'verizon', 'att', 'spectrum'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime',
                'movie', 'theater', 'cinema', 'game', 'entertainment',
                'youtube', 'twitch', 'steam'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'metro', 'parking',
                'toll', 'transit', 'airline', 'airport', 'flight'
            ],
            'healthcare': [
                'pharmacy', 'hospital', 'clinic', 'doctor', 'medical',
                'cvs', 'walgreens', 'rite aid', 'dentist', 'vision'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes',
                'macy', 'nike', 'apple store', 'online purchase'
            ],
            'banking': [
                'atm fee', 'overdraft', 'transfer', 'interest', 'dividend',
                'deposit', 'withdrawal', 'fee', 'charge'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: The transaction description/merchant name
            
        Returns:
            str: The category name or 'other' if no match found
        """
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class BankStatementParser:
    """Parses and processes bank statement CSV files."""
    
    def __init__(self, filename: str):
        """
        Initialize the parser with a CSV filename.
        
        Args:
            filename: Path to the CSV file containing bank statements
        """
        self.filename = filename
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def parse_csv(self) -> List[Dict]:
        """
        Parse the CSV file and extract transaction data.
        
        Returns:
            List[Dict]: List of parsed transactions
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV format is invalid
        """
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                # Try to detect the CSV dialect
                sample = file.read(1024)
                file.seek(0)
                dialect = csv.Sniffer().sniff(sample)
                
                reader = csv.DictReader(file, dialect=dialect)
                
                # Normalize column names (handle variations)
                fieldnames = [field.strip().lower() for field in reader.fieldnames]
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        transaction = self._parse_row(row, fieldnames, row_num)
                        if transaction:
                            self.transactions.append(transaction)
                    except Exception as e:
                        print(f"Warning: Error parsing row {row_num}: {e}", file=sys.stderr)
                        continue
                
                return self.transactions
                
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file '{self.filename}' not found")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
    
    def _parse_row(self, row: Dict, fieldnames: List[str], row_num: int) -> Optional[Dict]:
        """
        Parse a single CSV row into a transaction dictionary.
        
        Args:
            row: The CSV row data
            fieldnames: List of column names
            row_num: Row number for error reporting
            
        Returns:
            Optional[Dict]: Parsed transaction or None if invalid
        """
        # Map common column name variations
        date_fields = ['date', 'transaction date', 'posted date']
        desc_fields = ['description', 'merchant', 'payee', 'memo']
        amount_fields = ['amount', 'transaction amount', 'debit', 'credit']
        
        # Find the appropriate columns
        date_col = self._find_column(fieldnames, date_fields)
        desc_col = self._find_column(fieldnames, desc_fields)
        amount_col = self._find_column(fieldnames, amount_fields)
        
        if not all([date_col, desc_col, amount_col]):
            if row_num == 2:  # Only warn once
                print("Warning: Could not identify required columns. Expected: date, description, amount", file=sys.stderr)
            return None
        
        # Get the actual values
        row_values = {k.strip().lower(): v for k, v in row.items()}
        
        date_str = row_values.get(date_col, '').strip()
        description = row_values.get(desc_col, '').strip()
        amount_str = row_values.get(amount_col, '').strip()
        
        if not all([date_str, description, amount_str]):
            return None
        
        # Parse date
        try:
            date = self._parse_date(date_str)
        except ValueError:
            print(f"Warning: Invalid date format in row {row_num}: {date_str}", file=sys.stderr)
            return None
        
        # Parse amount
        try:
            amount = self._parse_amount(amount_str)
        except ValueError:
            print(f"Warning: Invalid amount format in row {row_num}: {amount_str}", file=sys.stderr)
            return None
        
        # Categorize transaction
        category = self.categorizer.categorize_transaction(description)
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'description': description,
            'amount': amount,
            'category': category,
            'raw_amount': amount_str