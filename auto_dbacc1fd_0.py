```python
"""
Bank CSV Transaction Parser and Categorizer

This module parses bank CSV files containing transaction data and automatically
categorizes transactions based on keyword matching rules. It extracts date,
description, and amount fields from CSV files and applies predefined rules to
classify expenses into common categories like groceries, utilities, entertainment,
dining, and transportation.

The script is self-contained and only requires the pandas library for CSV processing.
It includes comprehensive error handling and outputs categorized results to stdout.

Usage: python script.py
"""

import pandas as pd
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Optional


class TransactionCategorizer:
    """Handles transaction categorization based on keyword matching."""
    
    def __init__(self):
        self.category_rules = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'grocery', 'supermarket', 'food store', 'market', 'costco', 'sams club',
                'fresh market', 'aldi', 'publix', 'wegmans', 'heb', 'meijer'
            ],
            'utilities': [
                'electric', 'electricity', 'gas company', 'water', 'sewer', 'trash',
                'internet', 'phone', 'cable', 'utility', 'power', 'energy',
                'verizon', 'att', 'comcast', 'xfinity', 'spectrum', 'cox'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'movie',
                'theater', 'cinema', 'concert', 'entertainment', 'gaming',
                'steam', 'xbox', 'playstation', 'tickets', 'streaming'
            ],
            'dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonalds', 'burger',
                'pizza', 'dining', 'food delivery', 'uber eats', 'doordash',
                'grubhub', 'takeout', 'fast food', 'bar', 'pub', 'diner'
            ],
            'transportation': [
                'gas station', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train',
                'subway', 'parking', 'toll', 'car wash', 'auto', 'vehicle',
                'shell', 'bp', 'chevron', 'exxon', 'mobil', 'transit'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description string
            
        Returns:
            Category name or 'other' if no match found
        """
        if not description:
            return 'other'
        
        description_lower = description.lower()
        
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class BankCSVParser:
    """Main class for parsing bank CSV files and categorizing transactions."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions_df = None
    
    def detect_csv_format(self, file_path: str) -> Dict[str, str]:
        """
        Detect the CSV format and column mappings.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary mapping standard fields to actual column names
        """
        try:
            # Read first few rows to analyze structure
            sample_df = pd.read_csv(file_path, nrows=5)
            columns = [col.lower().strip() for col in sample_df.columns]
            
            mapping = {}
            
            # Map date column
            date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
            for pattern in date_patterns:
                matches = [col for col in columns if pattern in col]
                if matches:
                    mapping['date'] = sample_df.columns[columns.index(matches[0])]
                    break
            
            # Map description column
            desc_patterns = ['description', 'memo', 'transaction', 'details', 'merchant']
            for pattern in desc_patterns:
                matches = [col for col in columns if pattern in col]
                if matches:
                    mapping['description'] = sample_df.columns[columns.index(matches[0])]
                    break
            
            # Map amount column
            amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
            for pattern in amount_patterns:
                matches = [col for col in columns if pattern in col and 'balance' not in col]
                if matches:
                    mapping['amount'] = sample_df.columns[columns.index(matches[0])]
                    break
            
            return mapping
            
        except Exception as e:
            raise ValueError(f"Error detecting CSV format: {str(e)}")
    
    def parse_amount(self, amount_str) -> float:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: Amount string from CSV
            
        Returns:
            Float value of the amount
        """
        if pd.isna(amount_str):
            return 0.0
        
        # Convert to string and clean
        amount_str = str(amount_str).strip()
        
        # Remove currency symbols and commas
        amount_str = re.sub(r'[$,]', '', amount_str)
        
        # Handle parentheses as negative
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            return float(amount_str)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str) -> Optional[datetime]:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: Date string from CSV
            
        Returns:
            Datetime object or None if parsing fails
        """
        if pd.isna(date_str):
            return None
        
        date_formats = [
            '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y',
            '%m-%d-%Y', '%Y/%m/%d', '%B %d, %Y', '%b %d, %Y'
        ]
        
        date_str = str(date_str).strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def load_and_parse_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load and parse the CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Parsed DataFrame with standardized columns
        """
        try:
            # Detect format
            column_mapping = self.detect_csv_format(file_path)
            
            if not all(key in column_mapping for key in ['date', 'description', 'amount']):
                raise ValueError("Could not detect required columns (date, description, amount)")
            
            # Load full CSV
            df = pd.read_csv(file_path)
            
            # Extract and rename columns
            parsed_df = pd.DataFrame()
            parsed_df['date'] = df[column_mapping['date']].apply(self.parse_date)
            parsed_df['description'] = df[column_mapping['description']].astype(str)
            parsed_df['amount'] = df[column_mapping['amount']].apply(self.parse_amount)
            
            # Remove rows with invalid dates
            parsed_df = parsed_df.dropna(subset=['date'])
            
            # Add category column
            parsed_df['category'] = parsed_df['description'].apply(
                self.categorizer.categorize_