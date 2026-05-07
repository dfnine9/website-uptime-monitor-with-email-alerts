```python
#!/usr/bin/env python3
"""
Bank Transaction Categorization Script

This module reads CSV files containing bank transaction data and automatically
categorizes transactions based on predefined keywords and spending categories.
It validates data integrity and provides a summary of spending patterns.

Features:
- Reads bank transaction CSV files with columns: Date, Description, Amount
- Categorizes transactions using keyword matching
- Validates data for common issues (missing values, invalid amounts, date formats)
- Provides spending summary by category
- Handles various CSV formats and encodings

Usage:
    python script.py

The script will look for 'transactions.csv' in the current directory.
If not found, it will create a sample file for demonstration.
"""

import csv
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import sys


class TransactionCategorizer:
    """Categorizes bank transactions based on predefined keywords."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods',
                'trader joe', 'costco', 'grocery', 'supermarket', 'food mart',
                'publix', 'wegmans', 'harris teeter', 'giant', 'stop shop'
            ],
            'dining': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'pizza',
                'starbucks', 'dunkin', 'taco bell', 'kfc', 'wendy',
                'chipotle', 'panera', 'cafe', 'diner', 'bar', 'pub'
            ],
            'utilities': [
                'electric', 'gas company', 'water', 'internet', 'cable',
                'phone', 'cellular', 'utility', 'power', 'energy',
                'verizon', 'att', 'comcast', 'spectrum', 'duke energy'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'amazon prime', 'disney',
                'movie', 'theater', 'cinema', 'concert', 'event',
                'gym', 'fitness', 'spotify', 'apple music', 'youtube'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'parking', 'metro', 'bus',
                'airline', 'airport', 'car wash', 'auto repair'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'department store', 'clothing',
                'best buy', 'home depot', 'lowes', 'pharmacy', 'cvs',
                'walgreens', 'online purchase', 'paypal', 'store'
            ],
            'healthcare': [
                'hospital', 'doctor', 'clinic', 'pharmacy', 'medical',
                'dental', 'vision', 'health', 'cvs pharmacy', 'walgreens',
                'prescription', 'medicare', 'insurance'
            ],
            'banking': [
                'atm fee', 'bank fee', 'overdraft', 'transfer', 'deposit',
                'withdrawal', 'interest', 'loan payment', 'mortgage'
            ]
        }
    
    def categorize_transaction(self, description):
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class DataValidator:
    """Validates transaction data for common issues."""
    
    @staticmethod
    def validate_date(date_str):
        """Validate and parse date string."""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Invalid date format: {date_str}")
    
    @staticmethod
    def validate_amount(amount_str):
        """Validate and parse amount string."""
        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid amount format: {amount_str}")
    
    @staticmethod
    def validate_description(description):
        """Validate transaction description."""
        if not description or not description.strip():
            raise ValueError("Empty description")
        return description.strip()


def create_sample_data():
    """Create sample transaction data for demonstration."""
    sample_data = [
        ['Date', 'Description', 'Amount'],
        ['2024-01-15', 'WALMART SUPERCENTER', '-85.43'],
        ['2024-01-16', 'STARBUCKS COFFEE', '-5.67'],
        ['2024-01-17', 'DUKE ENERGY', '-120.00'],
        ['2024-01-18', 'NETFLIX STREAMING', '-15.99'],
        ['2024-01-19', 'SHELL GAS STATION', '-45.20'],
        ['2024-01-20', 'AMAZON PURCHASE', '-67.89'],
        ['2024-01-21', 'KROGER GROCERY', '-92.15'],
        ['2024-01-22', 'VERIZON WIRELESS', '-80.00'],
        ['2024-01-23', 'MCDONALDS', '-12.45'],
        ['2024-01-24', 'CVS PHARMACY', '-23.78'],
        ['2024-01-25', 'SALARY DEPOSIT', '2500.00'],
        ['2024-01-26', 'ATM WITHDRAWAL', '-100.00'],
        ['2024-01-27', 'UBER RIDE', '-18.30'],
        ['2024-01-28', 'TARGET STORE', '-156.77']
    ]
    
    with open('transactions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(sample_data)
    
    print("Created sample transactions.csv file")


def read_transactions(filename):
    """Read transactions from CSV file with error handling."""
    transactions = []
    errors = []
    categorizer = TransactionCategorizer()
    validator = DataValidator()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Try to detect if file has headers
            sample = f.read(1024)
            f.seek(0)
            
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(sample)
            
            reader = csv.reader(f)
            
            if has_header:
                headers = next(reader)
                print(f"Detected headers: {headers}")
            
            for row_num, row in enumerate(reader, start=2 if has_header else 1):
                try:
                    if len(row) < 3:
                        errors.append(f"Row {row_num}: Insufficient columns ({len(row)} < 3)")
                        continue
                    
                    date_str, description, amount_str = row[0], row[1], row[2]
                    
                    # Validate data
                    date_obj = validator.validate_date(date_str)
                    description = validator.validate_description(description)
                    amount = validator.validate_amount(amount_str)
                    
                    # Categorize transaction
                    category = categorizer.categorize_transaction(description)
                    
                    transactions.append({