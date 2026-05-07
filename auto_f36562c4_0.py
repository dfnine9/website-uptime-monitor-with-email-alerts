```python
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statement files and categorizes transactions based on keywords.
It calculates monthly spending totals by category with comprehensive data validation
and error handling. The script processes transaction data to help users understand
their spending patterns across different categories like groceries, utilities, and entertainment.

Usage: python script.py

The script expects CSV files with columns: Date, Description, Amount
Date format should be YYYY-MM-DD or MM/DD/YYYY or DD/MM/YYYY
Amount should be numeric (negative for expenses, positive for income)
"""

import csv
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import sys

class TransactionCategorizer:
    def __init__(self):
        # Define category keywords (case-insensitive matching)
        self.categories = {
            'Groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'costco', 'kroger',
                'safeway', 'whole foods', 'trader joe', 'publix', 'food lion',
                'market', 'deli', 'butcher', 'bakery', 'produce'
            ],
            'Utilities': [
                'electric', 'gas company', 'water', 'sewer', 'internet', 'cable',
                'phone', 'cellular', 'verizon', 'att', 'comcast', 'spectrum',
                'utility', 'power', 'energy', 'trash', 'waste management'
            ],
            'Entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'youtube',
                'movie', 'theater', 'cinema', 'concert', 'game', 'entertainment',
                'streaming', 'subscription', 'music', 'video'
            ],
            'Transportation': [
                'gas station', 'shell', 'exxon', 'chevron', 'bp', 'mobil',
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'parking',
                'toll', 'car payment', 'auto', 'vehicle', 'dmv'
            ],
            'Restaurants': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'pizza',
                'starbucks', 'coffee', 'cafe', 'dining', 'food delivery',
                'doordash', 'grubhub', 'uber eats', 'takeout', 'fast food'
            ],
            'Healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'doctor', 'medical',
                'dentist', 'clinic', 'health', 'insurance', 'prescription',
                'medicine', 'urgent care'
            ],
            'Shopping': [
                'amazon', 'ebay', 'store', 'retail', 'mall', 'department',
                'clothing', 'shoes', 'electronics', 'home depot', 'lowes',
                'best buy', 'online purchase'
            ],
            'Banking': [
                'fee', 'atm', 'overdraft', 'interest', 'transfer', 'payment',
                'withdrawal', 'deposit', 'bank charge', 'service fee'
            ]
        }
        
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.uncategorized = []

    def parse_date(self, date_str):
        """Parse various date formats and return datetime object"""
        date_formats = [
            '%Y-%m-%d',     # 2023-12-31
            '%m/%d/%Y',     # 12/31/2023
            '%d/%m/%Y',     # 31/12/2023
            '%m-%d-%Y',     # 12-31-2023
            '%d-%m-%Y',     # 31-12-2023
            '%Y/%m/%d',     # 2023/12/31
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")

    def parse_amount(self, amount_str):
        """Parse amount string and return float"""
        # Remove currency symbols, commas, and whitespace
        amount_clean = re.sub(r'[\$,\s]', '', str(amount_str))
        
        # Handle parentheses as negative (accounting format)
        if amount_clean.startswith('(') and amount_clean.endswith(')'):
            amount_clean = '-' + amount_clean[1:-1]
        
        try:
            return float(amount_clean)
        except ValueError:
            raise ValueError(f"Unable to parse amount: {amount_str}")

    def categorize_transaction(self, description):
        """Categorize transaction based on description keywords"""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
        
        return 'Uncategorized'

    def validate_csv_headers(self, headers):
        """Validate CSV headers contain required columns"""
        required_cols = {'date', 'description', 'amount'}
        header_lower = {h.lower().strip() for h in headers}
        
        missing_cols = required_cols - header_lower
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Return mapping of required columns to actual header names
        col_mapping = {}
        for req_col in required_cols:
            for header in headers:
                if header.lower().strip() == req_col:
                    col_mapping[req_col] = header
                    break
        
        return col_mapping

    def process_csv_file(self, filepath):
        """Process a single CSV file"""
        print(f"\nProcessing file: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if ';' in sample and sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif '\t' in sample and sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                if not reader.fieldnames:
                    raise ValueError("CSV file appears to be empty or has no headers")
                
                col_mapping = self.validate_csv_headers(reader.fieldnames)
                
                processed_count = 0
                error_count = 0
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Extract data using column mapping
                        date_str = row[col_mapping['date']]
                        description = row[col_mapping['description']]
                        amount_str = row[col_mapping['amount']]
                        
                        # Validate required fields are not empty
                        if not all([date_str, description, amount_str]):
                            print(f"Warning: Skipping row {row_num} - empty required fields")
                            error_count += 1
                            continue
                        
                        # Parse date and amount
                        transaction_date = self.parse_date(date_str)
                        amount = self.parse_amount(amount_str)
                        
                        # Only process expenses (negative amounts)
                        if amount >= 0:
                            continue
                        
                        # Categorize transaction
                        category = self.categorize_transaction(description)
                        
                        # Store in monthly totals (use absolute value for spending)
                        month_key = f"{transaction_date.year}-{transaction_date.month:02d}"
                        self.monthly_totals[month_key][category] += abs(amount)
                        
                        # Track uncategorized transactions
                        if category ==