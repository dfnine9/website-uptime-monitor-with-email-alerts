```python
#!/usr/bin/env python3
"""
Bank Transaction CSV Processor and Expense Categorizer

This module reads bank transaction CSV files and automatically categorizes expenses
based on configurable keyword patterns. It provides data cleaning, transaction parsing,
and expense categorization functionality for personal finance management.

Features:
- Reads CSV files with flexible column mapping
- Cleans and normalizes transaction data
- Categorizes transactions using keyword-based rules
- Handles various CSV formats and edge cases
- Provides summary statistics by category

Usage:
    python script.py

The script will look for CSV files in the current directory or you can modify
the sample data section to test with generated transactions.
"""

import csv
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, InvalidOperation


class TransactionCategorizer:
    """Handles categorization of bank transactions based on description keywords."""
    
    def __init__(self):
        self.category_keywords = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'publix', 'whole foods',
                'trader joe', 'costco', 'grocery', 'supermarket', 'food lion',
                'harris teeter', 'wegmans', 'giant eagle', 'meijer'
            ],
            'utilities': [
                'electric', 'power', 'gas company', 'water', 'sewer', 'internet',
                'comcast', 'verizon', 'at&t', 'spectrum', 'utility', 'energy',
                'phone bill', 'cable'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney+', 'amazon prime', 'movie',
                'theater', 'cinema', 'concert', 'gaming', 'steam', 'xbox',
                'playstation', 'entertainment', 'music', 'streaming'
            ],
            'dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonalds', 'burger',
                'pizza', 'taco', 'subway', 'chipotle', 'dining', 'food delivery',
                'uber eats', 'doordash', 'grubhub'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'chevron', 'bp', 'uber', 'lyft',
                'taxi', 'metro', 'bus fare', 'parking', 'toll', 'car payment',
                'insurance auto'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'clinic', 'doctor',
                'medical', 'dentist', 'health insurance', 'prescription'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'clothing', 'shoes', 'electronics',
                'best buy', 'home depot', 'lowes', 'retail', 'department store'
            ],
            'banking': [
                'atm fee', 'bank fee', 'overdraft', 'transfer', 'interest',
                'service charge'
            ],
            'income': [
                'salary', 'payroll', 'deposit', 'refund', 'dividend', 'interest income'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on its description and amount.
        
        Args:
            description: Transaction description text
            amount: Transaction amount (positive for income, negative for expenses)
            
        Returns:
            Category string
        """
        description_lower = description.lower().strip()
        
        # Handle income transactions
        if amount > 0:
            for keyword in self.category_keywords['income']:
                if keyword in description_lower:
                    return 'income'
            return 'income'  # Default positive amounts to income
        
        # Handle expense transactions
        for category, keywords in self.category_keywords.items():
            if category == 'income':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class TransactionProcessor:
    """Main class for processing bank transaction CSV files."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
        
    def clean_amount(self, amount_str: str) -> Optional[float]:
        """
        Clean and convert amount string to float.
        
        Args:
            amount_str: Raw amount string from CSV
            
        Returns:
            Float amount or None if conversion fails
        """
        try:
            # Remove common currency symbols and whitespace
            cleaned = re.sub(r'[,$\s]', '', str(amount_str))
            
            # Handle parentheses notation for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError, InvalidOperation):
            return None
    
    def clean_date(self, date_str: str) -> Optional[str]:
        """
        Clean and standardize date format.
        
        Args:
            date_str: Raw date string from CSV
            
        Returns:
            Standardized date string (YYYY-MM-DD) or None if parsing fails
        """
        common_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d/%m/%y',
            '%Y/%m/%d', '%m-%d-%Y', '%d-%m-%Y', '%b %d, %Y', '%B %d, %Y'
        ]
        
        date_str = str(date_str).strip()
        
        for fmt in common_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def detect_csv_format(self, filepath: str) -> Dict[str, str]:
        """
        Detect CSV column format by examining headers.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Dictionary mapping standard field names to CSV column names
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                file.seek(0)
                reader = csv.reader(file)
                headers = next(reader)
            
            headers_lower = [h.lower().strip() for h in headers]
            column_mapping = {}
            
            # Map common column patterns
            for i, header in enumerate(headers_lower):
                if any(keyword in header for keyword in ['date', 'trans date', 'posted']):
                    column_mapping['date'] = headers[i]
                elif any(keyword in header for keyword in ['description', 'memo', 'details']):
                    column_mapping['description'] = headers[i]
                elif any(keyword in header for keyword in ['amount', 'debit', 'credit']):
                    column_mapping['amount'] = headers[i]
                elif 'balance' in header:
                    column_mapping['balance'] = headers[i]
            
            return column_mapping
            
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return {}
    
    def parse_csv_file(self, filepath: str) -> List[Dict]:
        """
        Parse CSV file and extract transaction data.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        
        try:
            column_mapping = self.detect_csv_format(filepath)
            
            if not column_mapping:
                print(f"Could not detect column format for {filepath}")
                return transactions
            
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, start=