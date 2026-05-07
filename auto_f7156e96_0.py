```python
#!/usr/bin/env python3
"""
Bank CSV Transaction Categorization Script

This script reads bank CSV files and automatically categorizes transactions
using keyword-based regex patterns. It performs data validation, preprocessing,
and categorizes transactions into common expense categories like groceries,
utilities, entertainment, dining, and transportation.

Features:
- Reads CSV files with flexible column detection
- Implements regex-based transaction categorization
- Performs data validation and preprocessing
- Handles various CSV formats and edge cases
- Outputs categorized transactions with summary statistics

Usage: python script.py
"""

import csv
import re
import os
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions using keyword-based regex patterns."""
    
    def __init__(self):
        # Define category patterns (case-insensitive)
        self.category_patterns = {
            'Groceries': [
                r'\b(walmart|kroger|safeway|publix|whole\s*foods|trader\s*joe|costco|sams?\s*club)\b',
                r'\b(grocery|supermarket|market|food\s*lion|giant\s*eagle|wegmans)\b',
                r'\b(aldi|target.*grocery|meijer|harris\s*teeter)\b'
            ],
            'Utilities': [
                r'\b(electric|electricity|gas\s*company|water|sewer|trash|garbage)\b',
                r'\b(utility|utilities|power|energy|pg&e|duke\s*energy)\b',
                r'\b(internet|cable|phone|telecom|verizon|at&t|comcast|spectrum)\b'
            ],
            'Entertainment': [
                r'\b(netflix|hulu|disney|spotify|apple\s*music|amazon\s*prime)\b',
                r'\b(movie|cinema|theater|theatre|concert|tickets)\b',
                r'\b(gaming|xbox|playstation|steam|entertainment)\b'
            ],
            'Dining': [
                r'\b(restaurant|mcdonalds|burger\s*king|kfc|taco\s*bell|subway)\b',
                r'\b(pizza|starbucks|dunkin|coffee|cafe|bistro|grill)\b',
                r'\b(dining|takeout|delivery|doordash|uber\s*eats|grubhub)\b'
            ],
            'Transportation': [
                r'\b(gas\s*station|shell|bp|exxon|chevron|mobil|texaco)\b',
                r'\b(uber|lyft|taxi|parking|toll|metro|bus|train)\b',
                r'\b(auto|car\s*wash|mechanic|repair|insurance.*auto)\b'
            ]
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        if not description:
            return 'Other'
        
        description = str(description).strip()
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(description):
                    return category
        
        return 'Other'


class CSVProcessor:
    """Processes bank CSV files with data validation and preprocessing."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
        self.errors = []
    
    def detect_csv_format(self, file_path: str) -> Optional[Dict[str, int]]:
        """Detect CSV column format by examining headers."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try different delimiters
                for delimiter in [',', ';', '\t']:
                    file.seek(0)
                    reader = csv.reader(file, delimiter=delimiter)
                    headers = next(reader, [])
                    
                    if len(headers) >= 3:  # Minimum columns needed
                        column_mapping = self._map_columns(headers)
                        if column_mapping:
                            return column_mapping
            
            return None
            
        except Exception as e:
            self.errors.append(f"Error detecting CSV format: {str(e)}")
            return None
    
    def _map_columns(self, headers: List[str]) -> Optional[Dict[str, int]]:
        """Map CSV headers to required columns."""
        headers_lower = [h.lower().strip() for h in headers]
        mapping = {}
        
        # Date column patterns
        date_patterns = ['date', 'transaction_date', 'trans_date', 'posting_date']
        for i, header in enumerate(headers_lower):
            if any(pattern in header for pattern in date_patterns):
                mapping['date'] = i
                break
        
        # Description column patterns
        desc_patterns = ['description', 'memo', 'details', 'transaction_details', 'merchant']
        for i, header in enumerate(headers_lower):
            if any(pattern in header for pattern in desc_patterns):
                mapping['description'] = i
                break
        
        # Amount column patterns
        amount_patterns = ['amount', 'debit', 'credit', 'transaction_amount', 'value']
        for i, header in enumerate(headers_lower):
            if any(pattern in header for pattern in amount_patterns):
                mapping['amount'] = i
                break
        
        # Check if we found all required columns
        if len(mapping) >= 3 and 'date' in mapping and 'description' in mapping and 'amount' in mapping:
            return mapping
        
        return None
    
    def validate_date(self, date_str: str) -> Optional[datetime]:
        """Validate and parse date string."""
        if not date_str:
            return None
        
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def validate_amount(self, amount_str: str) -> Optional[Decimal]:
        """Validate and parse amount string."""
        if not amount_str:
            return None
        
        try:
            # Clean amount string
            amount_clean = str(amount_str).strip()
            amount_clean = re.sub(r'[^\d.-]', '', amount_clean)
            
            if not amount_clean:
                return None
            
            return Decimal(amount_clean)
            
        except (ValueError, InvalidOperation):
            return None
    
    def process_csv(self, file_path: str) -> bool:
        """Process the CSV file and categorize transactions."""
        if not os.path.exists(file_path):
            self.errors.append(f"File not found: {file_path}")
            return False
        
        column_mapping = self.detect_csv_format(file_path)
        if not column_mapping:
            self.errors.append("Could not detect CSV format or required columns")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader, [])
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) <= max(column_mapping.values()):
                        self.errors.append(f"Row {row_num}: Insufficient columns")
                        continue
                    
                    # Extract data
                    date_str = row[column_mapping['date']]
                    description = row[column_mapping['description']]