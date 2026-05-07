```python
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statement files, automatically detects common column formats,
and categorizes transactions based on configurable keyword rules. Supports multiple
bank formats and provides detailed transaction analysis.

Features:
- Auto-detection of date, description, and amount columns
- Flexible date format parsing
- Keyword-based transaction categorization
- Configurable category mappings
- Summary statistics and reports
- Error handling for malformed data

Usage:
    python script.py
"""

import csv
import re
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any


class BankStatementParser:
    """Main class for parsing and categorizing bank statement transactions."""
    
    def __init__(self):
        self.category_keywords = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sams club', 'grocery', 'supermarket', 'food lion', 'publix',
                'wegmans', 'giant', 'stop shop', 'harris teeter', 'aldi', 'lidl'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonalds', 'burger king',
                'subway', 'pizza', 'kfc', 'taco bell', 'chipotle', 'panera', 'dominos',
                'wendys', 'dunkin', 'dining', 'bistro', 'grill', 'diner', 'bar & grill'
            ],
            'gas': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'sunoco', 'citgo', 'marathon',
                'speedway', 'wawa', '7-eleven', 'gas station', 'fuel', 'petro'
            ],
            'utilities': [
                'electric', 'power', 'gas company', 'water', 'sewer', 'internet',
                'cable', 'phone', 'verizon', 'att', 'comcast', 'spectrum', 'utility'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'theater',
                'cinema', 'movie', 'concert', 'spotify', 'apple music', 'gaming'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'department store', 'clothing', 'shoes',
                'electronics', 'best buy', 'home depot', 'lowes', 'macys', 'nordstrom'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'medical', 'doctor',
                'dentist', 'clinic', 'health', 'prescription', 'rite aid'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'parking', 'toll',
                'airline', 'flight', 'car rental', 'hertz', 'enterprise'
            ],
            'financial': [
                'bank fee', 'atm', 'interest', 'loan', 'mortgage', 'insurance',
                'investment', 'transfer', 'deposit', 'withdrawal', 'credit card'
            ]
        }
        
        self.date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',      # MM/DD/YYYY or M/D/YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',      # YYYY-MM-DD or YYYY-M-D
            r'\d{1,2}-\d{1,2}-\d{4}',      # MM-DD-YYYY or M-D-YYYY
            r'\d{1,2}/\d{1,2}/\d{2}',      # MM/DD/YY or M/D/YY
        ]
        
        self.amount_pattern = r'-?\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?'

    def detect_csv_format(self, filepath: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        Auto-detect date, description, and amount columns in CSV.
        Returns tuple of (date_col, description_col, amount_col) indices.
        """
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                # Try different delimiters
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ',' if sample.count(',') > sample.count(';') else ';'
                reader = csv.reader(file, delimiter=delimiter)
                
                # Read first few rows to analyze
                rows = []
                for i, row in enumerate(reader):
                    rows.append(row)
                    if i >= 5:  # Analyze first 6 rows
                        break
                
                if len(rows) < 2:
                    return None, None, None
                
                header = rows[0] if rows else []
                data_rows = rows[1:] if len(rows) > 1 else []
                
                date_col = self._find_date_column(header, data_rows)
                amount_col = self._find_amount_column(header, data_rows)
                description_col = self._find_description_column(header, data_rows, date_col, amount_col)
                
                return date_col, description_col, amount_col
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None, None, None

    def _find_date_column(self, header: List[str], data_rows: List[List[str]]) -> Optional[int]:
        """Find column containing dates."""
        # Check header keywords
        date_keywords = ['date', 'transaction date', 'posted date', 'trans date']
        for i, col_name in enumerate(header):
            if any(keyword in col_name.lower() for keyword in date_keywords):
                return i
        
        # Check data patterns
        for col_idx in range(len(header)):
            date_matches = 0
            for row in data_rows:
                if col_idx < len(row):
                    cell_value = row[col_idx].strip()
                    if any(re.match(pattern, cell_value) for pattern in self.date_patterns):
                        date_matches += 1
            
            if date_matches >= len(data_rows) * 0.7:  # 70% of rows match date pattern
                return col_idx
        
        return None

    def _find_amount_column(self, header: List[str], data_rows: List[List[str]]) -> Optional[int]:
        """Find column containing monetary amounts."""
        # Check header keywords
        amount_keywords = ['amount', 'debit', 'credit', 'transaction amount', 'balance']
        for i, col_name in enumerate(header):
            if any(keyword in col_name.lower() for keyword in amount_keywords):
                return i
        
        # Check data patterns
        for col_idx in range(len(header)):
            amount_matches = 0
            for row in data_rows:
                if col_idx < len(row):
                    cell_value = row[col_idx].strip()
                    if re.match(self.amount_pattern, cell_value):
                        amount_matches += 1
            
            if amount_matches >= len(data_rows) * 0.7:  # 70% of rows match amount pattern
                return col_idx
        
        return None

    def _find_description_column(self, header: List[str], data_rows: List[List[str]], 
                                date_col: Optional[int], amount_col: Optional[int]) -> Optional[int]:
        """Find column containing transaction descriptions."""
        # Check header keywords
        desc_keywords = ['description