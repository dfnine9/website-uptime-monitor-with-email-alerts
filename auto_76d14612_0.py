```python
#!/usr/bin/env python3
"""
CSV Transaction Parser and Expense Categorizer

This module provides functionality to parse CSV transaction data and automatically
categorize expenses using predefined keyword dictionaries. It reads transaction
data from CSV files, analyzes transaction descriptions, and assigns categories
based on keyword matching.

Features:
- CSV parsing with flexible column detection
- Automated expense categorization using keyword matching
- Error handling for file operations and data parsing
- Summary statistics and reporting
- Self-contained with minimal dependencies

Usage:
    python script.py

The script will look for a 'transactions.csv' file in the current directory
or create sample data if none exists.
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Handles transaction parsing and categorization logic."""
    
    def __init__(self):
        """Initialize categorizer with predefined keyword dictionaries."""
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'pizza', 'burger', 'starbucks', 'mcdonalds',
                'grocery', 'supermarket', 'food', 'dining', 'lunch', 'dinner',
                'breakfast', 'coffee', 'subway', 'dominos', 'kfc', 'taco'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train', 'metro',
                'parking', 'toll', 'car', 'auto', 'vehicle', 'airline', 'flight'
            ],
            'Shopping': [
                'amazon', 'walmart', 'target', 'store', 'shop', 'retail',
                'clothing', 'electronics', 'mall', 'outlet', 'purchase'
            ],
            'Utilities': [
                'electric', 'electricity', 'water', 'gas bill', 'internet',
                'phone', 'cable', 'utility', 'power', 'heating', 'cooling'
            ],
            'Healthcare': [
                'hospital', 'doctor', 'pharmacy', 'medical', 'dental',
                'health', 'clinic', 'medicine', 'prescription', 'cvs', 'walgreens'
            ],
            'Entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'gaming', 'concert',
                'event', 'ticket', 'entertainment', 'streaming', 'music'
            ],
            'Banking': [
                'atm', 'fee', 'bank', 'transfer', 'withdrawal', 'deposit',
                'interest', 'credit card', 'loan', 'mortgage'
            ],
            'Insurance': [
                'insurance', 'premium', 'policy', 'coverage', 'claim'
            ]
        }
        
    def categorize_transaction(self, description: str, amount: float = 0) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description text
            amount: Transaction amount (for future logic expansion)
            
        Returns:
            Category name or 'Other' if no match found
        """
        if not description:
            return 'Other'
            
        description_lower = description.lower()
        
        # Check each category for keyword matches
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
                    
        return 'Other'


class CSVTransactionParser:
    """Handles CSV parsing and transaction data extraction."""
    
    def __init__(self):
        """Initialize parser with categorizer."""
        self.categorizer = TransactionCategorizer()
        
    def detect_csv_structure(self, filepath: str) -> Optional[Dict[str, int]]:
        """
        Detect CSV column structure by examining headers.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Dictionary mapping column types to indices, or None if detection fails
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                file.seek(0)
                
                # Try different delimiters
                for delimiter in [',', ';', '\t']:
                    if sample.count(delimiter) > sample.count(',') and delimiter != ',':
                        reader = csv.reader(file, delimiter=delimiter)
                    else:
                        reader = csv.reader(file)
                    
                    try:
                        headers = next(reader)
                        headers_lower = [h.lower().strip() for h in headers]
                        
                        column_map = {}
                        
                        # Map common column names
                        for i, header in enumerate(headers_lower):
                            if any(keyword in header for keyword in ['date', 'time']):
                                column_map['date'] = i
                            elif any(keyword in header for keyword in ['description', 'desc', 'memo', 'detail']):
                                column_map['description'] = i
                            elif any(keyword in header for keyword in ['amount', 'value', 'sum']):
                                column_map['amount'] = i
                            elif any(keyword in header for keyword in ['category', 'type']):
                                column_map['category'] = i
                                
                        return column_map
                        
                    except StopIteration:
                        continue
                        
                    file.seek(0)
                    
        except Exception as e:
            print(f"Error detecting CSV structure: {e}")
            return None
            
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: String representation of amount
            
        Returns:
            Parsed amount as float
        """
        if not amount_str:
            return 0.0
            
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$€£¥,\s]', '', str(amount_str))
        
        # Handle parentheses for negative amounts
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
            
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
            
    def parse_csv(self, filepath: str) -> List[Dict]:
        """
        Parse CSV file and extract transaction data.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        
        try:
            # Detect CSV structure
            column_map = self.detect_csv_structure(filepath)
            if not column_map:
                raise ValueError("Could not detect CSV structure")
                
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)  # Skip header row
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) < len(column_map):
                            continue
                            
                        transaction = {}
                        
                        # Extract data based on detected columns
                        if 'date' in column_map:
                            transaction['date'] = row[column_map['date']].strip()
                        else:
                            transaction['date'] = ''
                            
                        if 'description' in column_map:
                            transaction['description'] = row[column_map['description']].strip()
                        else:
                            transaction['description'] = ''
                            
                        if 'amount' in column_map:
                            transaction['amount'] = self.parse_amount(row[column_map['amount']])
                        else:
                            transaction['amount'] = 0.0
                            
                        # Categorize transaction
                        transaction['category'] = self.categorizer.categorize_transaction(
                            transaction['description'], 
                            transaction['amount']
                        )
                        
                        transaction['row_number'] = row_num
                        transactions.append(transaction)