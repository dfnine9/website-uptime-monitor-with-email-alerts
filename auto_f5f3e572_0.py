```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements and automatically categorizes transactions
into predefined expense categories using regex patterns and keyword matching.

Categories supported:
- Food & Dining
- Transportation
- Utilities
- Entertainment
- Shopping
- Healthcare
- Transfer/Investment
- Income
- Other

The script processes CSV files with columns: date, description, amount
and outputs categorized transactions to stdout.

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os


class TransactionCategorizer:
    """Categorizes bank transactions using regex and keyword matching."""
    
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                r'\b(restaurant|cafe|coffee|pizza|burger|food|dining|starbucks|subway|mcdonalds)\b',
                r'\b(grocery|supermarket|market|walmart|target|safeway|kroger)\b',
                r'\b(doordash|ubereats|grubhub|postmates|delivery)\b'
            ],
            'Transportation': [
                r'\b(gas|fuel|shell|chevron|bp|exxon|mobil)\b',
                r'\b(uber|lyft|taxi|parking|metro|bus|train)\b',
                r'\b(car|auto|vehicle|repair|maintenance|insurance)\b'
            ],
            'Utilities': [
                r'\b(electric|electricity|gas|water|sewer|trash|utility)\b',
                r'\b(internet|cable|phone|cellular|verizon|att|comcast)\b',
                r'\b(pg&e|pge|duke energy|con edison)\b'
            ],
            'Entertainment': [
                r'\b(movie|cinema|theater|netflix|spotify|hulu|disney)\b',
                r'\b(game|gaming|steam|xbox|playstation|nintendo)\b',
                r'\b(concert|event|ticket|entertainment)\b'
            ],
            'Shopping': [
                r'\b(amazon|ebay|store|shop|retail|clothing|apparel)\b',
                r'\b(home depot|lowes|costco|sams club|best buy)\b',
                r'\b(purchase|buy|order|merchant)\b'
            ],
            'Healthcare': [
                r'\b(doctor|medical|health|hospital|pharmacy|cvs|walgreens)\b',
                r'\b(dental|vision|insurance|copay|prescription)\b',
                r'\b(clinic|urgent care|lab|x-ray|mri)\b'
            ],
            'Transfer/Investment': [
                r'\b(transfer|deposit|withdrawal|investment|savings)\b',
                r'\b(bank|atm|check|wire|zelle|venmo|paypal)\b',
                r'\b(401k|ira|retirement|brokerage|trading)\b'
            ],
            'Income': [
                r'\b(salary|paycheck|wage|income|bonus|refund)\b',
                r'\b(direct deposit|dd|employer|company)\b',
                r'\b(freelance|contract|consulting|payment received)\b'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on description and amount.
        
        Args:
            description: Transaction description
            amount: Transaction amount (negative for expenses)
            
        Returns:
            Category name as string
        """
        if amount > 0:
            # Check if it's income
            for pattern in self.categories['Income']:
                if re.search(pattern, description, re.IGNORECASE):
                    return 'Income'
        
        description_lower = description.lower()
        
        for category, patterns in self.categories.items():
            if category == 'Income':  # Already handled above
                continue
                
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    return category
        
        return 'Other'


class CSVProcessor:
    """Processes CSV bank statements and categorizes transactions."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
    
    def detect_csv_format(self, file_path: str) -> Optional[Dict[str, int]]:
        """
        Detect CSV format and return column mappings.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dictionary mapping standard names to column indices
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)
                
            header_lower = [col.lower().strip() for col in header]
            
            # Common column name variations
            date_variations = ['date', 'transaction date', 'posted date', 'trans date']
            desc_variations = ['description', 'desc', 'transaction', 'memo', 'details']
            amount_variations = ['amount', 'debit', 'credit', 'transaction amount']
            
            column_map = {}
            
            for i, col in enumerate(header_lower):
                if any(var in col for var in date_variations):
                    column_map['date'] = i
                elif any(var in col for var in desc_variations):
                    column_map['description'] = i
                elif any(var in col for var in amount_variations):
                    column_map['amount'] = i
            
            if len(column_map) >= 3:
                return column_map
            
            return None
            
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string to float.
        
        Args:
            amount_str: Amount as string
            
        Returns:
            Amount as float
        """
        try:
            # Remove currency symbols, commas, and extra whitespace
            cleaned = re.sub(r'[^\d.-]', '', amount_str.strip())
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: Date as string
            
        Returns:
            datetime object or None if parsing fails
        """
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',
            '%d/%m/%Y', '%d/%m/%y', '%Y/%m/%d',
            '%m-%d-%Y', '%m-%d-%y', '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def process_csv(self, file_path: str) -> List[Tuple[str, str, float, str]]:
        """
        Process CSV file and return categorized transactions.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of tuples (date, description, amount, category)
        """
        column_map = self.detect_csv_format(file_path)
        if not column_map:
            raise ValueError("Could not detect CSV format. Expected columns: date, description, amount")
        
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(column_map.values()):
                            continue
                        
                        date_str = row[column_map['date']]
                        description = row[column_map['description']]
                        amount_str = row[column_map['amount']]
                        
                        # Parse data
                        parsed_date = self.