```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer and Monthly Spending Analyzer

This module reads CSV files containing bank transaction data, automatically
categorizes transactions based on configurable keyword matching, and calculates
monthly spending totals by category.

Features:
- Reads CSV files with flexible column detection
- Keyword-based transaction categorization
- Monthly spending aggregation
- Handles various CSV formats from different banks
- Error handling for malformed data

Usage:
    python script.py

Requirements:
- CSV file named 'transactions.csv' in the same directory
- CSV should contain columns for date, description, and amount
- Standard library only (no external dependencies)
"""

import csv
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path


class TransactionCategorizer:
    """Handles transaction categorization and monthly analysis."""
    
    def __init__(self):
        """Initialize categorizer with predefined keywords."""
        self.categories = {
            'groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'costco', 'safeway',
                'kroger', 'whole foods', 'trader joe', 'food', 'market'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'internet', 'phone', 'cable',
                'utility', 'power', 'energy', 'telecom', 'verizon', 'att'
            ],
            'entertainment': [
                'netflix', 'spotify', 'movie', 'theater', 'game', 'entertainment',
                'disney', 'hulu', 'amazon prime', 'youtube', 'concert', 'ticket'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonalds',
                'burger', 'pizza', 'dining', 'bar', 'pub', 'delivery'
            ],
            'transportation': [
                'gas station', 'uber', 'lyft', 'taxi', 'parking', 'metro',
                'bus', 'train', 'airline', 'car', 'auto', 'transport'
            ],
            'healthcare': [
                'pharmacy', 'doctor', 'hospital', 'medical', 'dental',
                'health', 'clinic', 'cvs', 'walgreens', 'prescription'
            ],
            'shopping': [
                'amazon', 'ebay', 'store', 'retail', 'clothing', 'shoes',
                'electronics', 'mall', 'online', 'purchase'
            ],
            'finance': [
                'bank', 'fee', 'interest', 'loan', 'credit', 'payment',
                'transfer', 'atm', 'finance', 'investment'
            ]
        }
    
    def categorize_transaction(self, description):
        """
        Categorize a transaction based on its description.
        
        Args:
            description (str): Transaction description
            
        Returns:
            str: Category name or 'other' if no match found
        """
        if not description:
            return 'other'
        
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def detect_csv_structure(self, filepath):
        """
        Detect CSV structure and identify relevant columns.
        
        Args:
            filepath (Path): Path to CSV file
            
        Returns:
            dict: Mapping of column purposes to indices
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.reader(file, delimiter=delimiter)
                header = next(reader)
                
                # Clean header names
                header = [col.strip().lower() for col in header]
                
                column_map = {}
                
                # Find date column
                for i, col in enumerate(header):
                    if any(keyword in col for keyword in ['date', 'transaction date', 'posted']):
                        column_map['date'] = i
                        break
                
                # Find description column
                for i, col in enumerate(header):
                    if any(keyword in col for keyword in ['description', 'memo', 'details', 'merchant']):
                        column_map['description'] = i
                        break
                
                # Find amount column
                for i, col in enumerate(header):
                    if any(keyword in col for keyword in ['amount', 'debit', 'withdrawal', 'charge']):
                        column_map['amount'] = i
                        break
                
                return column_map, delimiter
                
        except Exception as e:
            print(f"Error detecting CSV structure: {e}")
            return {}, ','
    
    def parse_date(self, date_str):
        """
        Parse date string into datetime object.
        
        Args:
            date_str (str): Date string in various formats
            
        Returns:
            datetime: Parsed date or None if parsing fails
        """
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m-%d-%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m/%d/%y',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_amount(self, amount_str):
        """
        Parse amount string into float.
        
        Args:
            amount_str (str): Amount string
            
        Returns:
            float: Parsed amount or 0.0 if parsing fails
        """
        if not amount_str:
            return 0.0
        
        try:
            # Remove currency symbols and extra spaces
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            
            # Handle parentheses as negative
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def read_transactions(self, filepath):
        """
        Read and parse transactions from CSV file.
        
        Args:
            filepath (Path): Path to CSV file
            
        Returns:
            list: List of transaction dictionaries
        """
        transactions = []
        
        try:
            column_map, delimiter = self.detect_csv_structure(filepath)
            
            if not all(key in column_map for key in ['date', 'description', 'amount']):
                print("Warning: Could not detect all required columns")
                print("Expected columns: date, description, amount")
                return transactions
            
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=delimiter)
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(column_map.values()):
                            continue
                        
                        date_str = row[column_map['date']]
                        description = row[column_map['description']]
                        amount_str = row[column_map['amount']]
                        
                        parsed_date = self.parse_date(date_str)
                        if not parsed_date:
                            print(f"Warning: Could not parse date '{date_str}' on row {row_num}")
                            continue
                        
                        amount = self.parse_amount(amount_str)
                        category = self.categor