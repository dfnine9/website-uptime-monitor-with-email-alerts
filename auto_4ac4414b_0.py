```python
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements from a specified directory, parses transaction data
(date, description, amount, category), and implements keyword-based categorization rules
for common expense types including groceries, dining, transportation, utilities, and entertainment.

The script processes all CSV files in the specified directory, categorizes transactions
based on description keywords, and outputs the results to stdout.

Usage: python script.py
"""

import csv
import os
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class TransactionCategorizer:
    def __init__(self):
        self.category_keywords = {
            'groceries': ['grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway', 
                         'whole foods', 'trader joe', 'costco', 'sam\'s club', 'food market',
                         'fresh market', 'publix', 'wegmans', 'aldi', 'heb'],
            'dining': ['restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'burger',
                      'pizza', 'taco', 'subway', 'chipotle', 'panera', 'dunkin', 'kfc',
                      'dining', 'bistro', 'grill', 'bar', 'pub', 'deli', 'bakery'],
            'transportation': ['gas', 'fuel', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                             'uber', 'lyft', 'taxi', 'metro', 'transit', 'parking',
                             'auto repair', 'mechanic', 'oil change', 'car wash', 'toll'],
            'utilities': ['electric', 'gas company', 'water', 'sewer', 'internet', 'cable',
                         'phone', 'verizon', 'at&t', 'comcast', 'utility', 'power company',
                         'spectrum', 't-mobile', 'sprint'],
            'entertainment': ['movie', 'theater', 'cinema', 'netflix', 'spotify', 'hulu',
                            'disney', 'amazon prime', 'gym', 'fitness', 'sports', 'concert',
                            'tickets', 'gaming', 'streaming', 'subscription', 'youtube']
        }
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[\$,\s]', '', str(amount_str))
            # Handle negative amounts in parentheses
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to standardized format."""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_str).strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def detect_csv_structure(self, file_path: str) -> Dict[str, int]:
        """Detect the column structure of the CSV file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first few lines to detect structure
                sample_lines = [file.readline() for _ in range(3)]
                file.seek(0)
                
                # Try to detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(''.join(sample_lines)).delimiter
                
                # Read header
                reader = csv.reader(file, delimiter=delimiter)
                header = next(reader, [])
                
                if not header:
                    return {}
                
                # Map common column names to indices
                column_mapping = {}
                header_lower = [col.lower().strip() for col in header]
                
                # Date column detection
                date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
                for i, col in enumerate(header_lower):
                    if any(pattern in col for pattern in date_patterns):
                        column_mapping['date'] = i
                        break
                
                # Description column detection
                desc_patterns = ['description', 'memo', 'transaction', 'details', 'merchant']
                for i, col in enumerate(header_lower):
                    if any(pattern in col for pattern in desc_patterns):
                        column_mapping['description'] = i
                        break
                
                # Amount column detection
                amount_patterns = ['amount', 'debit', 'credit', 'withdrawal', 'deposit']
                for i, col in enumerate(header_lower):
                    if any(pattern in col for pattern in amount_patterns):
                        column_mapping['amount'] = i
                        break
                
                # Category column detection (if exists)
                category_patterns = ['category', 'type', 'classification']
                for i, col in enumerate(header_lower):
                    if any(pattern in col for pattern in category_patterns):
                        column_mapping['existing_category'] = i
                        break
                
                column_mapping['delimiter'] = delimiter
                return column_mapping
                
        except Exception as e:
            print(f"Error detecting CSV structure for {file_path}: {e}")
            return {}
    
    def process_csv_file(self, file_path: str) -> List[Dict]:
        """Process a single CSV file and return categorized transactions."""
        transactions = []
        
        try:
            column_mapping = self.detect_csv_structure(file_path)
            if not column_mapping:
                print(f"Could not detect CSV structure for {file_path}")
                return transactions
            
            delimiter = column_mapping.get('delimiter', ',')
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=delimiter)
                header = next(reader, [])  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) < max(column_mapping.get('date', 0), 
                                        column_mapping.get('description', 0), 
                                        column_mapping.get('amount', 0)) + 1:
                            continue
                        
                        # Extract data using column mapping
                        date_raw = row[column_mapping.get('date', 0)] if 'date' in column_mapping else ''
                        description = row[column_mapping.get('description', 1)] if 'description' in column_mapping else ''
                        amount_raw = row[column_mapping.get('amount', 2)] if 'amount' in column_mapping else '0'
                        existing_category = row[column_mapping.get('existing_category', -1)] if 'existing_category' in column_mapping else ''
                        
                        # Parse and validate data
                        parsed_date = self.parse_date(date_raw)
                        if not parsed_date:
                            continue
                        
                        amount = self.parse_amount(amount_raw)
                        if amount == 0:
                            continue
                        
                        # Categorize transaction
                        auto_category = self.categorize_transaction(description)
                        
                        transaction = {
                            'file': os.path.basename(file_