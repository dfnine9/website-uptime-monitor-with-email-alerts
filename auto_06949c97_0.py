```python
"""
Bank Statement Transaction Parser and Categorizer

This module parses CSV bank statements and categorizes transactions based on keyword matching.
It extracts transaction data (date, amount, description) and applies predefined rules to
categorize expenses into common categories like groceries, gas, restaurants, utilities, etc.

The script is self-contained and only uses standard library modules.
Run with: python script.py

Expected CSV format: Date, Amount, Description (or similar column names)
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions based on keyword matching rules."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'costco', 'safeway',
                'kroger', 'publix', 'whole foods', 'trader joe', 'food lion',
                'harris teeter', 'wegmans', 'aldi', 'fresh market'
            ],
            'gas': [
                'gas', 'fuel', 'shell', 'exxon', 'chevron', 'bp', 'mobil',
                'texaco', 'citgo', 'valero', 'sunoco', 'marathon', 'speedway'
            ],
            'restaurants': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'starbucks',
                'pizza', 'taco bell', 'kfc', 'wendy', 'chick-fil-a', 'domino',
                'chipotle', 'panera', 'olive garden', 'applebee', 'dining'
            ],
            'utilities': [
                'electric', 'power', 'water', 'sewer', 'gas company', 'utility',
                'pge', 'duke energy', 'southern company', 'xcel energy'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'metro', 'transit', 'parking',
                'toll', 'car wash', 'auto repair', 'mechanic'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'doctor', 'hospital',
                'medical', 'dental', 'vision', 'clinic', 'urgent care'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'hulu', 'disney',
                'movie', 'theater', 'cinema', 'concert', 'game'
            ],
            'shopping': [
                'amazon', 'ebay', 'department store', 'clothing', 'mall',
                'best buy', 'home depot', 'lowes', 'bed bath', 'tj maxx'
            ],
            'banking': [
                'atm fee', 'overdraft', 'maintenance fee', 'transfer fee',
                'check order', 'wire fee'
            ],
            'insurance': [
                'insurance', 'geico', 'state farm', 'allstate', 'progressive',
                'usaa', 'auto insurance', 'home insurance'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class BankStatementParser:
    """Parses CSV bank statements and extracts transaction data."""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def detect_csv_format(self, sample_rows: List[List[str]]) -> Tuple[int, int, int]:
        """
        Detect the column indices for date, amount, and description.
        Returns tuple of (date_col, amount_col, desc_col).
        """
        if not sample_rows or len(sample_rows) < 2:
            raise ValueError("CSV file must have at least 2 rows (header + data)")
        
        header = [col.lower().strip() for col in sample_rows[0]]
        
        # Common column name patterns
        date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
        amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
        desc_patterns = ['description', 'memo', 'payee', 'merchant', 'details']
        
        date_col = amount_col = desc_col = -1
        
        # Find columns by name matching
        for i, col in enumerate(header):
            if any(pattern in col for pattern in date_patterns):
                date_col = i
            elif any(pattern in col for pattern in amount_patterns):
                amount_col = i
            elif any(pattern in col for pattern in desc_patterns):
                desc_col = i
        
        # Fallback: assume first 3 columns if no matches
        if date_col == -1 or amount_col == -1 or desc_col == -1:
            if len(header) >= 3:
                date_col, amount_col, desc_col = 0, 1, 2
            else:
                raise ValueError("Cannot determine CSV format. Need at least 3 columns.")
        
        return date_col, amount_col, desc_col
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime object."""
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y',
            '%m-%d-%y', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string into float."""
        try:
            # Remove common currency symbols and whitespace
            cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def parse_csv(self) -> None:
        """Parse the CSV file and extract transactions."""
        try:
            with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Read sample to detect format
                sample_reader = csv.reader(csvfile)
                sample_rows = [next(sample_reader) for _ in range(min(5, sum(1 for _ in csvfile) + 1))]
                
                # Reset file pointer
                csvfile.seek(0)
                
                # Detect CSV format
                date_col, amount_col, desc_col = self.detect_csv_format(sample_rows)
                
                # Parse all rows
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(date_col, amount_col, desc_col):
                            print(f"Warning: Row {row_num} has insufficient columns, skipping")
                            continue
                        
                        # Extract data
                        date_obj = self.parse_date(row[date_col])
                        amount = self.parse_amount(row[amount_col])
                        description = row[desc_col].strip()
                        
                        if date_obj is None:
                            print(f"Warning: Could not parse date in row {