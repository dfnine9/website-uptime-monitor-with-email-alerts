```python
"""
Bank Transaction Categorizer

A self-contained Python script that parses bank CSV exports and automatically 
categorizes expenses using keyword matching rules. The script reads transaction 
data from CSV files and applies predefined categorization rules to classify 
expenses into categories like grocery, gas, restaurant, etc.

Usage:
    python script.py

Features:
- Parses CSV files with transaction data
- Automatic expense categorization using keyword matching
- Error handling for file operations and data parsing
- Self-contained with minimal dependencies
- Results printed to stdout
"""

import csv
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions based on description keywords."""
    
    def __init__(self):
        self.categories = {
            'grocery': [
                'walmart', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'grocery', 'supermarket', 'food lion', 'harris teeter',
                'publix', 'aldi', 'costco', 'sam\'s club', 'market'
            ],
            'gas': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'texaco',
                'gas station', 'fuel', 'gasoline', 'petrol', 'speedway',
                'circle k', 'wawa', '7-eleven'
            ],
            'restaurant': [
                'restaurant', 'cafe', 'pizza', 'mcdonald', 'burger',
                'taco bell', 'subway', 'starbucks', 'dunkin', 'kfc',
                'domino', 'papa john', 'chipotle', 'panera', 'dining'
            ],
            'shopping': [
                'amazon', 'target', 'best buy', 'walmart', 'ebay',
                'shopping', 'retail', 'store', 'mall', 'outlet'
            ],
            'utilities': [
                'electric', 'gas bill', 'water', 'internet', 'phone',
                'cable', 'utility', 'power company', 'verizon', 'at&t',
                'comcast', 'spectrum'
            ],
            'entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'gaming',
                'entertainment', 'concert', 'show', 'amusement'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'metro', 'parking',
                'toll', 'train', 'airline', 'flight'
            ],
            'healthcare': [
                'pharmacy', 'doctor', 'medical', 'hospital', 'clinic',
                'cvs', 'walgreens', 'health', 'dental'
            ],
            'banking': [
                'atm fee', 'bank fee', 'overdraft', 'interest', 'transfer',
                'withdrawal fee', 'maintenance fee'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description
            amount: Transaction amount
            
        Returns:
            Category name or 'uncategorized'
        """
        if amount > 0:
            return 'income'
            
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
                    
        return 'uncategorized'


class CSVParser:
    """Parses bank CSV files with various formats."""
    
    @staticmethod
    def detect_csv_format(file_path: str) -> Optional[Dict]:
        """
        Detect the CSV format by examining headers.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dictionary with column mappings or None if format not recognized
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader, [])
                
            headers_lower = [h.lower().strip() for h in headers]
            
            # Common column name variations
            date_cols = ['date', 'transaction date', 'post date', 'posting date']
            desc_cols = ['description', 'memo', 'transaction description', 'details']
            amount_cols = ['amount', 'transaction amount', 'debit', 'credit']
            
            format_map = {}
            
            for i, header in enumerate(headers_lower):
                if any(date_col in header for date_col in date_cols):
                    format_map['date'] = i
                elif any(desc_col in header for desc_col in desc_cols):
                    format_map['description'] = i
                elif any(amount_col in header for amount_col in amount_cols):
                    format_map['amount'] = i
                    
            return format_map if len(format_map) >= 3 else None
            
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    @staticmethod
    def parse_amount(amount_str: str) -> float:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: String representation of amount
            
        Returns:
            Float amount
        """
        if not amount_str:
            return 0.0
            
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$,\s]', '', str(amount_str))
        
        # Handle parentheses for negative amounts
        if '(' in cleaned and ')' in cleaned:
            cleaned = '-' + cleaned.replace('(', '').replace(')', '')
            
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """
        Parse date string with multiple format attempts.
        
        Args:
            date_str: String representation of date
            
        Returns:
            datetime object or None if parsing fails
        """
        formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%d/%m/%Y',
            '%m/%d/%y', '%m-%d-%y', '%y-%m-%d', '%d/%m/%y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
                
        return None


def process_csv_file(file_path: str) -> List[Dict]:
    """
    Process a bank CSV file and return categorized transactions.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of transaction dictionaries
    """
    parser = CSVParser()
    categorizer = TransactionCategorizer()
    
    # Detect CSV format
    format_map = parser.detect_csv_format(file_path)
    if not format_map:
        raise ValueError("Could not detect CSV format")
    
    transactions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip headers
            
            for row_num, row in enumerate(reader, 2):
                try:
                    if len(row) <= max(format_map.values()):
                        continue
                        
                    date_str = row[format_map['date']]
                    description = row[format_map['description']]
                    amount_str = row[format_map['amount']]
                    
                    # Parse components
                    transaction_date = parser.parse_date(date_str)
                    amount = parser.parse_amount(amount_str)
                    category = categorizer.categorize_transaction(description, amount)
                    
                    transaction = {
                        'date': transaction_date.strftime('%Y-%m-%d') if