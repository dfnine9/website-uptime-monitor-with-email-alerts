```python
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements and automatically categorizes transactions
using rule-based keyword matching patterns. It processes transaction data from
CSV files and assigns categories based on merchant names and transaction descriptions.

Features:
- Reads CSV bank statements with flexible column mapping
- Rule-based categorization using predefined keyword patterns
- Comprehensive error handling for file operations and data parsing
- Self-contained with minimal dependencies (standard library only)
- Outputs categorized transactions to stdout

Usage:
    python script.py

The script expects a CSV file named 'bank_statement.csv' in the same directory
with columns: Date, Description, Amount, Balance (or similar variations).
"""

import csv
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Handles transaction categorization using rule-based keyword matching."""
    
    def __init__(self):
        """Initialize the categorizer with predefined category rules."""
        self.category_rules = {
            'Groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'grocery', 'market', 'food', 'supermarket', 'costco', 'sams club'
            ],
            'Dining': [
                'restaurant', 'mcdonalds', 'burger king', 'starbucks', 'subway',
                'pizza', 'cafe', 'coffee', 'dining', 'fast food', 'delivery'
            ],
            'Gas': [
                'shell', 'exxon', 'bp', 'chevron', 'gas station', 'fuel',
                'gasoline', 'petrol', 'mobil', 'sunoco'
            ],
            'Shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes', 'macys',
                'nordstrom', 'shopping', 'retail', 'store', 'mall'
            ],
            'Utilities': [
                'electric', 'gas bill', 'water', 'internet', 'phone', 'cable',
                'utility', 'power company', 'telecom', 'verizon', 'att'
            ],
            'Transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'metro', 'parking', 'toll',
                'airline', 'airport', 'car rental', 'transit'
            ],
            'Healthcare': [
                'hospital', 'clinic', 'pharmacy', 'doctor', 'medical',
                'dental', 'cvs', 'walgreens', 'prescription'
            ],
            'Entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'gaming', 'concert',
                'entertainment', 'streaming', 'subscription', 'gym'
            ],
            'Banking': [
                'atm fee', 'bank fee', 'interest', 'transfer', 'deposit',
                'withdrawal', 'overdraft', 'service charge'
            ],
            'Income': [
                'salary', 'payroll', 'deposit', 'refund', 'dividend',
                'bonus', 'tax refund', 'insurance claim'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on description and amount.
        
        Args:
            description: Transaction description text
            amount: Transaction amount (positive for credits, negative for debits)
            
        Returns:
            Category name as string
        """
        description_lower = description.lower()
        
        # Handle income transactions (positive amounts)
        if amount > 0:
            for keyword in self.category_rules['Income']:
                if keyword in description_lower:
                    return 'Income'
            return 'Other Income'
        
        # Handle expense transactions (negative amounts)
        for category, keywords in self.category_rules.items():
            if category == 'Income':  # Skip income category for negative amounts
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'


class BankStatementParser:
    """Handles parsing of CSV bank statement files."""
    
    def __init__(self):
        """Initialize the parser with common CSV column mappings."""
        self.column_mappings = {
            'date': ['date', 'transaction date', 'posted date', 'trans date'],
            'description': ['description', 'transaction description', 'memo', 'details'],
            'amount': ['amount', 'transaction amount', 'debit', 'credit'],
            'balance': ['balance', 'running balance', 'account balance']
        }
    
    def detect_delimiter(self, file_path: str) -> str:
        """
        Detect the CSV delimiter by sampling the file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Detected delimiter character
        """
        delimiters = [',', ';', '\t', '|']
        with open(file_path, 'r', encoding='utf-8') as file:
            first_line = file.readline()
            delimiter_counts = {delim: first_line.count(delim) for delim in delimiters}
            return max(delimiter_counts, key=delimiter_counts.get)
    
    def map_columns(self, headers: List[str]) -> Dict[str, int]:
        """
        Map CSV headers to standard column names.
        
        Args:
            headers: List of column headers from CSV
            
        Returns:
            Dictionary mapping standard names to column indices
        """
        headers_lower = [h.lower().strip() for h in headers]
        column_map = {}
        
        for standard_name, possible_names in self.column_mappings.items():
            for i, header in enumerate(headers_lower):
                if any(possible_name in header for possible_name in possible_names):
                    column_map[standard_name] = i
                    break
        
        return column_map
    
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: String representation of amount
            
        Returns:
            Parsed amount as float
        """
        if not amount_str or amount_str.strip() == '':
            return 0.0
        
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$€£¥,\s]', '', str(amount_str))
        
        # Handle parentheses for negative amounts
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: String representation of date
            
        Returns:
            Parsed datetime object or None if parsing fails
        """
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def read_csv_file(self, file_path: str) -> List[Dict]:
        """
        Read and parse CSV bank statement file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        
        try:
            delimiter = self.detect_delimiter(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                column_map = self.map_