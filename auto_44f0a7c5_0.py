```python
#!/usr/bin/env python3
"""
Bank Transaction CSV Parser and Categorizer

This module provides functionality to parse bank transaction CSV files and automatically
categorize expenses based on keyword matching. It supports common expense categories
like groceries, gas, restaurants, utilities, etc.

The script reads CSV files containing bank transactions and applies keyword-based
categorization logic to classify transactions into predefined expense categories.
Results are printed to stdout with categorized transaction summaries.

Usage:
    python script.py

Requirements:
    - Python 3.6+
    - Standard library modules only
"""

import csv
import sys
import os
from typing import Dict, List, Tuple
from datetime import datetime
import re


class TransactionCategorizer:
    """Handles categorization of bank transactions based on description keywords."""
    
    def __init__(self):
        """Initialize categorizer with predefined category keywords."""
        self.categories = {
            'Groceries': [
                'walmart', 'target', 'safeway', 'kroger', 'publix', 'whole foods',
                'trader joe', 'costco', 'sam\'s club', 'aldi', 'food lion',
                'harris teeter', 'giant', 'stop shop', 'wegmans', 'heb'
            ],
            'Gas/Fuel': [
                'shell', 'exxon', 'bp', 'chevron', 'texaco', 'mobil', 'sunoco',
                'marathon', 'valero', 'citgo', 'gas', 'fuel', 'petrol'
            ],
            'Restaurants': [
                'mcdonald', 'burger king', 'kfc', 'taco bell', 'subway', 'pizza',
                'starbucks', 'dunkin', 'restaurant', 'cafe', 'bar', 'grill',
                'bistro', 'diner', 'food truck', 'delivery'
            ],
            'Utilities': [
                'electric', 'gas bill', 'water', 'sewer', 'internet', 'cable',
                'phone', 'cellular', 'verizon', 'att', 'comcast', 'spectrum',
                'utility', 'power company'
            ],
            'Transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'metro', 'train', 'airline',
                'parking', 'toll', 'dmv', 'registration', 'car wash'
            ],
            'Healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'clinic', 'doctor',
                'medical', 'dental', 'vision', 'prescription', 'urgent care'
            ],
            'Entertainment': [
                'netflix', 'spotify', 'amazon prime', 'hulu', 'disney',
                'movie', 'theater', 'cinema', 'concert', 'game', 'entertainment'
            ],
            'Shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes', 'macy',
                'nordstrom', 'mall', 'outlet', 'store', 'shop'
            ],
            'Banking/Finance': [
                'bank fee', 'atm', 'interest', 'transfer', 'loan', 'mortgage',
                'insurance', 'investment', 'financial'
            ],
            'Subscription': [
                'subscription', 'monthly', 'annual', 'membership', 'gym',
                'fitness', 'software', 'app store', 'google play'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description (str): Transaction description text
            
        Returns:
            str: Category name or 'Uncategorized' if no match found
        """
        if not description:
            return 'Uncategorized'
        
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Uncategorized'


class CSVTransactionParser:
    """Handles parsing and processing of bank transaction CSV files."""
    
    def __init__(self):
        """Initialize parser with transaction categorizer."""
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def detect_csv_format(self, filepath: str) -> Dict[str, int]:
        """
        Detect CSV column format by examining headers.
        
        Args:
            filepath (str): Path to CSV file
            
        Returns:
            Dict[str, int]: Mapping of column names to indices
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                dialect = csv.Sniffer().sniff(sample)
                reader = csv.reader(file, dialect)
                headers = next(reader)
                
                # Normalize headers to lowercase for matching
                headers_lower = [h.lower().strip() for h in headers]
                
                column_map = {}
                
                # Map common column variations
                for i, header in enumerate(headers_lower):
                    if any(keyword in header for keyword in ['date', 'trans date', 'transaction date']):
                        column_map['date'] = i
                    elif any(keyword in header for keyword in ['description', 'desc', 'memo', 'payee']):
                        column_map['description'] = i
                    elif any(keyword in header for keyword in ['amount', 'debit', 'withdrawal', 'charge']):
                        column_map['amount'] = i
                    elif any(keyword in header for keyword in ['credit', 'deposit']):
                        column_map['credit'] = i
                    elif any(keyword in header for keyword in ['balance']):
                        column_map['balance'] = i
                
                return column_map
                
        except Exception as e:
            raise ValueError(f"Error detecting CSV format: {str(e)}")
    
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str (str): Amount string from CSV
            
        Returns:
            float: Parsed amount value
        """
        if not amount_str:
            return 0.0
        
        # Remove currency symbols, commas, and extra whitespace
        cleaned = re.sub(r'[$,\s]', '', str(amount_str))
        
        # Handle parentheses as negative
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_csv_file(self, filepath: str) -> List[Dict]:
        """
        Parse CSV file and categorize transactions.
        
        Args:
            filepath (str): Path to CSV file
            
        Returns:
            List[Dict]: List of categorized transactions
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        try:
            column_map = self.detect_csv_format(filepath)
            
            if 'date' not in column_map or 'description' not in column_map:
                raise ValueError("Required columns (date, description) not found in CSV")
            
            transactions = []
            
            with open(filepath, 'r', encoding='utf-8') as file:
                dialect = csv.Sniffer().sniff(file.read(1024))
                file.seek(0)
                reader = csv.reader(file, dialect)
                
                # Skip header
                next(reader)
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) <= max(column_map.values()):
                        continue
                    
                    try:
                        date_str = row[column_map['date']].strip()