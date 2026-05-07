```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements and automatically categorizes transactions
based on keyword matching. It detects common CSV formats and applies rule-based
categorization for expenses like groceries, gas, dining, and utilities.

Features:
- Auto-detects transaction columns (date, description, amount)
- Keyword-based categorization with customizable rules
- Handles multiple CSV formats and delimiters
- Robust error handling for malformed data
- Outputs categorized transactions to stdout

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any


class TransactionCategorizer:
    """Categorizes bank transactions based on description keywords."""
    
    def __init__(self):
        self.category_rules = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'publix', 'whole foods',
                'trader joe', 'costco', 'sam\'s club', 'grocery', 'supermarket',
                'food lion', 'harris teeter', 'wegmans', 'aldi', 'giant eagle'
            ],
            'gas': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'texaco', 'citgo',
                'speedway', 'wawa', 'gas station', 'fuel', 'petrol'
            ],
            'dining': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'pizza',
                'starbucks', 'dunkin', 'taco bell', 'kfc', 'wendy\'s',
                'chipotle', 'panera', 'cafe', 'diner', 'bistro'
            ],
            'utilities': [
                'electric', 'gas company', 'water', 'sewer', 'internet',
                'cable', 'phone', 'verizon', 'at&t', 'comcast', 'utility'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'clinic',
                'doctor', 'medical', 'dental', 'vision'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'hulu', 'disney',
                'movie', 'theater', 'cinema', 'streaming'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes',
                'macy\'s', 'nordstrom', 'store', 'retail'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'metro',
                'parking', 'toll', 'transit'
            ]
        }
    
    def categorize(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class CSVParser:
    """Parses CSV bank statements and detects transaction columns."""
    
    def __init__(self):
        self.date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}'
        ]
        self.amount_pattern = r'[-+]?\$?\d+\.?\d*'
    
    def detect_delimiter(self, file_content: str) -> str:
        """Detect CSV delimiter by analyzing first few lines."""
        lines = file_content.strip().split('\n')[:5]
        delimiters = [',', ';', '\t', '|']
        
        for delimiter in delimiters:
            consistent_count = None
            is_consistent = True
            
            for line in lines:
                count = line.count(delimiter)
                if consistent_count is None:
                    consistent_count = count
                elif count != consistent_count or count == 0:
                    is_consistent = False
                    break
            
            if is_consistent and consistent_count > 0:
                return delimiter
        
        return ','  # Default fallback
    
    def is_date_column(self, values: List[str]) -> bool:
        """Check if column contains dates."""
        date_count = 0
        for value in values[:10]:  # Check first 10 non-header rows
            for pattern in self.date_patterns:
                if re.search(pattern, str(value)):
                    date_count += 1
                    break
        return date_count >= len(values[:10]) * 0.7
    
    def is_amount_column(self, values: List[str]) -> bool:
        """Check if column contains monetary amounts."""
        amount_count = 0
        for value in values[:10]:
            clean_value = str(value).replace('$', '').replace(',', '').strip()
            try:
                float(clean_value)
                amount_count += 1
            except ValueError:
                if re.match(self.amount_pattern, clean_value):
                    amount_count += 1
        return amount_count >= len(values[:10]) * 0.7
    
    def is_description_column(self, values: List[str], header: str) -> bool:
        """Check if column contains transaction descriptions."""
        desc_keywords = ['description', 'memo', 'payee', 'merchant', 'details']
        if any(keyword in header.lower() for keyword in desc_keywords):
            return True
        
        # Check if values look like descriptions
        avg_length = sum(len(str(v)) for v in values[:10]) / min(10, len(values))
        return avg_length > 5  # Descriptions typically longer than codes
    
    def detect_columns(self, rows: List[List[str]]) -> Dict[str, int]:
        """Detect date, description, and amount column indices."""
        if not rows:
            raise ValueError("No data rows found")
        
        headers = rows[0]
        data_rows = rows[1:] if len(rows) > 1 else rows
        
        columns = {'date': -1, 'description': -1, 'amount': -1}
        
        for i, header in enumerate(headers):
            if i >= len(data_rows[0]):
                continue
                
            column_values = [row[i] if i < len(row) else '' for row in data_rows]
            
            if self.is_date_column(column_values):
                columns['date'] = i
            elif self.is_amount_column(column_values):
                columns['amount'] = i
            elif self.is_description_column(column_values, header):
                columns['description'] = i
        
        # Verify we found essential columns
        missing = [col for col, idx in columns.items() if idx == -1]
        if missing:
            raise ValueError(f"Could not detect columns: {', '.join(missing)}")
        
        return columns


def parse_amount(amount_str: str) -> float:
    """Parse amount string to float, handling various formats."""
    try:
        # Remove currency symbols and spaces
        clean_amount = re.sub(r'[$,\s]', '', str(amount_str))
        
        # Handle parentheses as negative
        if '(' in clean_amount and ')' in clean_amount:
            clean_amount = '-' + clean_amount.replace('(', '').replace(')', '')
        
        return float(clean_amount)
    except ValueError:
        return 0.0


def format_amount(amount: float) -> str:
    """Format amount for display."""
    return f"${amount:,.2f}" if amount >= 0 else f"-${abs(amount):,.2f}"


def main():