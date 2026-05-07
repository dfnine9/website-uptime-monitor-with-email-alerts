```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements and automatically categorizes transactions
based on configurable keyword rules. It parses transaction data including dates,
descriptions, and amounts, then assigns categories like groceries, dining, utilities,
and entertainment based on transaction descriptions.

Usage: python script.py

The script expects a CSV file named 'bank_statements.csv' in the same directory
with columns: Date, Description, Amount

Author: T.O.A.A Intelligence Swarm
"""

import csv
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any
import os


class TransactionCategorizer:
    """Handles categorization of bank transactions based on keyword matching."""
    
    def __init__(self):
        """Initialize categorizer with default category rules."""
        self.category_rules = {
            'groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway',
                'whole foods', 'trader joe', 'costco', 'food mart', 'market'
            ],
            'dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'burger',
                'pizza', 'subway', 'chipotle', 'taco bell', 'kfc', 'dining'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'trash', 'internet', 'cable',
                'phone', 'utility', 'power', 'energy', 'telecom'
            ],
            'entertainment': [
                'netflix', 'spotify', 'movie', 'theater', 'cinema', 'concert',
                'game', 'entertainment', 'streaming', 'hulu', 'disney'
            ],
            'transportation': [
                'gas station', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus',
                'parking', 'toll', 'car wash', 'automotive'
            ],
            'shopping': [
                'amazon', 'ebay', 'store', 'retail', 'mall', 'shop', 'purchase',
                'order', 'merchandise'
            ],
            'healthcare': [
                'pharmacy', 'medical', 'doctor', 'hospital', 'clinic', 'dental',
                'health', 'cvs', 'walgreens'
            ],
            'banking': [
                'fee', 'charge', 'interest', 'transfer', 'withdrawal', 'deposit',
                'overdraft', 'maintenance'
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
        description_lower = description.lower()
        
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class BankStatementParser:
    """Handles parsing and processing of CSV bank statements."""
    
    def __init__(self, filename: str = 'bank_statements.csv'):
        """
        Initialize parser with CSV filename.
        
        Args:
            filename: Path to CSV file containing bank statements
        """
        self.filename = filename
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def parse_date(self, date_str: str) -> datetime:
        """
        Parse date string into datetime object.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If date format is not recognized
        """
        # Common date formats
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m-%d-%Y',
            '%d/%m/%Y',
            '%Y/%m/%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string into float.
        
        Args:
            amount_str: Amount string (may include currency symbols)
            
        Returns:
            Parsed amount as float
            
        Raises:
            ValueError: If amount cannot be parsed
        """
        # Remove common currency symbols and whitespace
        cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
        
        try:
            return float(cleaned)
        except ValueError:
            raise ValueError(f"Unable to parse amount: {amount_str}")
    
    def read_csv(self) -> List[Dict[str, Any]]:
        """
        Read and parse CSV bank statement file.
        
        Returns:
            List of parsed transaction dictionaries
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid
        """
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"CSV file not found: {self.filename}")
        
        transactions = []
        
        try:
            with open(self.filename, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                # Auto-detect CSV dialect
                try:
                    dialect = csv.Sniffer().sniff(sample)
                except csv.Error:
                    dialect = csv.excel  # Default to excel dialect
                
                reader = csv.DictReader(csvfile, dialect=dialect)
                
                # Handle different column name variations
                fieldnames = [field.lower().strip() for field in reader.fieldnames]
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Map common column variations
                        date_col = self._find_column(fieldnames, ['date', 'transaction date', 'trans date'])
                        desc_col = self._find_column(fieldnames, ['description', 'desc', 'memo', 'details'])
                        amount_col = self._find_column(fieldnames, ['amount', 'debit', 'credit'])
                        
                        if not all([date_col, desc_col, amount_col]):
                            raise ValueError("Required columns not found. Expected: Date, Description, Amount")
                        
                        # Get original column names for accessing row data
                        orig_date_col = reader.fieldnames[fieldnames.index(date_col)]
                        orig_desc_col = reader.fieldnames[fieldnames.index(desc_col)]
                        orig_amount_col = reader.fieldnames[fieldnames.index(amount_col)]
                        
                        transaction = {
                            'date': self.parse_date(row[orig_date_col]),
                            'description': row[orig_desc_col].strip(),
                            'amount': self.parse_amount(row[orig_amount_col]),
                            'category': self.categorizer.categorize_transaction(row[orig_desc_col])
                        }
                        
                        transactions.append(transaction)
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping row {row_num} due to error: {e}")
                        continue
                        
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
        
        return transactions
    
    def _find_column(self, fieldnames: List[str], possible_names: List[str]) -> str:
        """Find column name from list of possibilities."""
        for name in possible_names:
            if name in fieldnames:
                return name
        return None
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics for transactions.
        
        Returns:
            Dictionary containing