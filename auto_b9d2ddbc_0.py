```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

A self-contained Python script that reads bank CSV files and categorizes transactions
based on keywords. Supports multiple CSV formats and outputs categorized data in
structured JSON format.

Features:
- Automatic CSV format detection
- Keyword-based transaction categorization
- Error handling for malformed files
- JSON output with category summaries
- Configurable category keywords

Usage: python script.py [csv_file_path]
If no file path provided, looks for 'transactions.csv' in current directory.
"""

import csv
import json
import sys
import re
from datetime import datetime
from collections import defaultdict
import os

class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            'food': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'mcdonalds', 'subway',
                'grocery', 'supermarket', 'walmart', 'safeway', 'kroger', 'whole foods',
                'starbucks', 'dunkin', 'taco bell', 'kfc', 'dominos', 'uber eats',
                'doordash', 'grubhub', 'food', 'dining', 'bakery', 'deli'
            ],
            'transport': [
                'gas', 'fuel', 'shell', 'exxon', 'bp', 'chevron', 'uber', 'lyft',
                'taxi', 'bus', 'metro', 'subway', 'train', 'airline', 'flight',
                'parking', 'tolls', 'car wash', 'auto', 'mechanic', 'oil change'
            ],
            'utilities': [
                'electric', 'gas bill', 'water', 'internet', 'phone', 'cable',
                'verizon', 'att', 'comcast', 'xfinity', 'spectrum', 'utility',
                'power', 'energy', 'sewer', 'trash', 'waste management'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'apple music',
                'movie', 'theater', 'cinema', 'concert', 'spotify', 'gaming',
                'steam', 'playstation', 'xbox', 'nintendo', 'youtube premium',
                'twitch', 'entertainment', 'subscription', 'streaming'
            ],
            'shopping': [
                'amazon', 'target', 'costco', 'walmart', 'best buy', 'home depot',
                'lowes', 'macy', 'nordstrom', 'clothing', 'shoes', 'electronics',
                'furniture', 'shopping', 'retail', 'store', 'mall'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'doctor', 'hospital',
                'medical', 'health', 'dental', 'vision', 'insurance', 'clinic',
                'urgent care', 'prescription', 'medicine'
            ],
            'financial': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'credit card', 'mortgage',
                'investment', 'transfer', 'payment', 'overdraft', 'maintenance'
            ],
            'education': [
                'school', 'tuition', 'books', 'supplies', 'course', 'training',
                'university', 'college', 'education', 'learning'
            ]
        }

    def detect_csv_format(self, file_path):
        """Detect CSV format and return appropriate field mappings."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                file.seek(0)
                
                # Try to detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = [h.lower().strip() for h in reader.fieldnames]
                
                # Common field mappings
                field_mapping = {}
                
                # Date field detection
                date_fields = ['date', 'transaction date', 'posted date', 'trans date']
                for field in date_fields:
                    if field in headers:
                        field_mapping['date'] = field
                        break
                
                # Description field detection
                desc_fields = ['description', 'desc', 'memo', 'transaction', 'details']
                for field in desc_fields:
                    if field in headers:
                        field_mapping['description'] = field
                        break
                
                # Amount field detection
                amount_fields = ['amount', 'debit', 'credit', 'transaction amount']
                for field in amount_fields:
                    if field in headers:
                        field_mapping['amount'] = field
                        break
                
                return field_mapping, delimiter
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return {}, ','

    def categorize_transaction(self, description, amount=None):
        """Categorize a transaction based on description keywords."""
        if not description:
            return 'other'
        
        description_lower = description.lower()
        
        # Check each category's keywords
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        # Special cases based on amount patterns
        if amount:
            try:
                amt = float(str(amount).replace('$', '').replace(',', '').replace('(', '').replace(')', ''))
                # Small amounts might be coffee/snacks
                if 0 < amt < 10 and any(word in description_lower for word in ['card', 'purchase', 'pos']):
                    return 'food'
            except (ValueError, TypeError):
                pass
        
        return 'other'

    def parse_date(self, date_str):
        """Parse date string into standardized format."""
        if not date_str:
            return None
        
        # Common date formats
        formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y',
            '%Y/%m/%d', '%m/%d/%y', '%m-%d-%y', '%B %d, %Y',
            '%d %B %Y', '%d-%m-%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return str(date_str)

    def parse_amount(self, amount_str):
        """Parse amount string into float."""
        if not amount_str:
            return 0.0
        
        try:
            # Remove currency symbols and normalize
            clean_amount = str(amount_str).replace('$', '').replace(',', '').strip()
            
            # Handle parentheses for negative amounts
            if clean_amount.startswith('(') and clean_amount.endswith(')'):
                clean_amount = '-' + clean_amount[1:-1]
            
            return float(clean_amount)
        except (ValueError, TypeError):
            return 0.0

    def process_csv(self, file_path):
        """Process CSV file and categorize transactions."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        field_mapping, delimiter = self.detect_csv_format(file_path)
        
        if not field_mapping:
            raise ValueError("Could not detect CSV format or required fields")
        
        transactions = []
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader,