```python
#!/usr/bin/env python3
"""
CSV Transaction Parser and Categorizer

This module provides functionality to parse CSV transaction files and categorize
transactions based on keyword matching. It calculates spending totals by category
and provides a summary report.

Features:
- Parses CSV files with transaction data
- Categorizes transactions using configurable keyword matching
- Calculates total spending per category
- Handles various CSV formats and encoding issues
- Provides error handling for file operations and data parsing

Usage:
    python script.py

The script expects a CSV file with columns containing transaction descriptions
and amounts. It will automatically detect common column names and categorize
transactions based on predefined keywords.
"""

import csv
import re
import sys
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import os

class TransactionCategorizer:
    """Categorizes financial transactions based on keyword matching."""
    
    def __init__(self):
        """Initialize the categorizer with predefined categories and keywords."""
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'mcdonalds', 'burger',
                'starbucks', 'food', 'dining', 'lunch', 'dinner', 'breakfast',
                'grocery', 'supermarket', 'walmart', 'target', 'safeway'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus', 'train',
                'parking', 'car', 'auto', 'transport', 'airline', 'flight'
            ],
            'Shopping': [
                'amazon', 'ebay', 'store', 'shop', 'retail', 'mall', 'purchase',
                'buy', 'clothing', 'electronics', 'book'
            ],
            'Entertainment': [
                'movie', 'cinema', 'theater', 'netflix', 'spotify', 'music',
                'game', 'entertainment', 'park', 'museum', 'concert'
            ],
            'Healthcare': [
                'doctor', 'hospital', 'medical', 'pharmacy', 'health', 'dental',
                'clinic', 'medicine', 'prescription'
            ],
            'Bills & Utilities': [
                'electric', 'gas bill', 'water', 'internet', 'phone', 'cable',
                'utility', 'bill', 'payment', 'subscription'
            ],
            'Banking & Finance': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'credit', 'finance',
                'investment', 'transfer'
            ],
            'Other': []  # Default category for unmatched transactions
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description string
            
        Returns:
            Category name as string
        """
        if not description:
            return 'Other'
        
        description_lower = description.lower()
        
        # Check each category's keywords
        for category, keywords in self.categories.items():
            if category == 'Other':
                continue
            
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
        
        return 'Other'

class CSVTransactionParser:
    """Parses CSV transaction files and categorizes spending."""
    
    def __init__(self):
        """Initialize the parser with transaction categorizer."""
        self.categorizer = TransactionCategorizer()
        self.spending_by_category = defaultdict(float)
        self.transactions = []
    
    def detect_columns(self, headers: List[str]) -> Tuple[Optional[int], Optional[int]]:
        """
        Auto-detect description and amount columns from CSV headers.
        
        Args:
            headers: List of column headers
            
        Returns:
            Tuple of (description_col_index, amount_col_index)
        """
        description_col = None
        amount_col = None
        
        description_keywords = ['description', 'memo', 'detail', 'merchant', 'payee', 'name']
        amount_keywords = ['amount', 'value', 'total', 'sum', 'debit', 'credit', 'transaction']
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            
            if description_col is None:
                for keyword in description_keywords:
                    if keyword in header_lower:
                        description_col = i
                        break
            
            if amount_col is None:
                for keyword in amount_keywords:
                    if keyword in header_lower:
                        amount_col = i
                        break
        
        return description_col, amount_col
    
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: String representation of amount
            
        Returns:
            Float value of amount
        """
        if not amount_str:
            return 0.0
        
        # Remove common currency symbols and whitespace
        cleaned = re.sub(r'[\$,\s]', '', str(amount_str))
        
        # Handle negative amounts in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_csv_file(self, filepath: str) -> bool:
        """
        Parse CSV file and categorize transactions.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            True if parsing successful, False otherwise
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            file_content = None
            
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as file:
                        file_content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if file_content is None:
                print(f"Error: Could not decode file {filepath} with any encoding")
                return False
            
            # Parse CSV content
            csv_reader = csv.reader(file_content.splitlines())
            rows = list(csv_reader)
            
            if not rows:
                print("Error: CSV file is empty")
                return False
            
            headers = rows[0]
            desc_col, amount_col = self.detect_columns(headers)
            
            if desc_col is None or amount_col is None:
                print("Error: Could not detect description and amount columns")
                print(f"Available columns: {headers}")
                print("Expected columns containing: 'description', 'amount', or similar")
                return False
            
            print(f"Using column '{headers[desc_col]}' for descriptions")
            print(f"Using column '{headers[amount_col]}' for amounts")
            print()
            
            # Process transactions
            for i, row in enumerate(rows[1:], start=2):
                if len(row) <= max(desc_col, amount_col):
                    continue
                
                description = row[desc_col].strip()
                amount = self.parse_amount(row[amount_col])
                
                if amount == 0:
                    continue
                
                # Only count expenses (negative amounts or positive depending on format)
                # Convert to positive for spending calculations
                spending_amount = abs(amount)
                
                category = self.categorizer.categorize_transaction(description)
                self.spending_by_category[category] += spending_amount
                
                self.transactions.append({
                    'description': description,
                    'amount': amount,
                    'category': category,
                    'row': i
                })
            
            return True
            
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found")
            return False
        except Exception as e:
            print(f"Error parsing CSV file: {str(e)}")
            return