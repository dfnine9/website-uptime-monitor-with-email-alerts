```python
"""
Transaction CSV Parser and Categorizer

This module provides functionality to read transaction data from CSV files and apply
rule-based categorization logic to classify transactions into predefined categories
such as groceries, utilities, entertainment, etc.

The script uses pattern matching on transaction descriptions and merchant names to
automatically categorize financial transactions, making expense tracking and budgeting
more efficient.

Usage:
    python script.py

The script expects a CSV file named 'transactions.csv' in the same directory with
columns: date, description, amount, merchant (optional)
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Handles rule-based categorization of financial transactions."""
    
    def __init__(self):
        """Initialize categorizer with predefined rules."""
        self.category_rules = {
            'groceries': [
                r'walmart', r'kroger', r'safeway', r'whole foods', r'trader joe',
                r'grocery', r'supermarket', r'food lion', r'publix', r'aldi'
            ],
            'restaurants': [
                r'mcdonald', r'burger king', r'subway', r'pizza', r'restaurant',
                r'cafe', r'starbucks', r'dunkin', r'kfc', r'taco bell'
            ],
            'gas': [
                r'shell', r'exxon', r'bp', r'chevron', r'mobil', r'gas station',
                r'fuel', r'gasoline', r'petro'
            ],
            'utilities': [
                r'electric', r'water', r'gas bill', r'utility', r'power company',
                r'energy', r'sewage', r'internet', r'phone bill', r'cable'
            ],
            'entertainment': [
                r'movie', r'theater', r'netflix', r'spotify', r'hulu', r'disney',
                r'cinema', r'concert', r'game', r'entertainment'
            ],
            'shopping': [
                r'amazon', r'target', r'best buy', r'mall', r'store', r'retail',
                r'department', r'clothing', r'shoes', r'fashion'
            ],
            'transportation': [
                r'uber', r'lyft', r'taxi', r'bus', r'train', r'metro', r'subway',
                r'parking', r'toll', r'transportation'
            ],
            'healthcare': [
                r'pharmacy', r'doctor', r'hospital', r'medical', r'dental',
                r'insurance', r'clinic', r'health'
            ],
            'banking': [
                r'atm fee', r'bank fee', r'overdraft', r'transfer', r'interest',
                r'service charge'
            ]
        }
    
    def categorize_transaction(self, description: str, merchant: str = "") -> str:
        """
        Categorize a transaction based on description and merchant name.
        
        Args:
            description: Transaction description
            merchant: Merchant name (optional)
            
        Returns:
            Category name or 'uncategorized'
        """
        text_to_match = f"{description} {merchant}".lower()
        
        for category, patterns in self.category_rules.items():
            for pattern in patterns:
                if re.search(pattern, text_to_match, re.IGNORECASE):
                    return category
        
        return 'uncategorized'


class TransactionParser:
    """Handles CSV parsing and transaction processing."""
    
    def __init__(self):
        """Initialize parser with categorizer."""
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def parse_csv(self, filename: str) -> List[Dict]:
        """
        Parse CSV file and extract transaction data.
        
        Args:
            filename: Path to CSV file
            
        Returns:
            List of transaction dictionaries
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid
        """
        transactions = []
        
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Normalize column names (handle case variations)
                        normalized_row = {k.lower().strip(): v.strip() for k, v in row.items()}
                        
                        # Extract required fields with flexible column naming
                        date_field = self._find_field(normalized_row, ['date', 'transaction_date', 'trans_date'])
                        desc_field = self._find_field(normalized_row, ['description', 'desc', 'memo', 'details'])
                        amount_field = self._find_field(normalized_row, ['amount', 'transaction_amount', 'value'])
                        merchant_field = self._find_field(normalized_row, ['merchant', 'vendor', 'payee'], default="")
                        
                        if not all([date_field, desc_field, amount_field]):
                            print(f"Warning: Skipping row {row_num} - missing required fields")
                            continue
                        
                        # Parse and validate data
                        transaction = {
                            'date': self._parse_date(date_field),
                            'description': desc_field,
                            'amount': self._parse_amount(amount_field),
                            'merchant': merchant_field,
                            'category': self.categorizer.categorize_transaction(desc_field, merchant_field)
                        }
                        
                        transactions.append(transaction)
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Error parsing row {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file '{filename}' not found")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
        
        return transactions
    
    def _find_field(self, row: Dict, field_names: List[str], default: Optional[str] = None) -> Optional[str]:
        """Find field value by trying multiple possible column names."""
        for field_name in field_names:
            if field_name in row and row[field_name]:
                return row[field_name]
        return default
    
    def _parse_date(self, date_string: str) -> str:
        """Parse date string into standardized format."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y',
            '%Y/%m/%d', '%m/%d/%y', '%m-%d-%y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_string, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_string}")
    
    def _parse_amount(self, amount_string: str) -> float:
        """Parse amount string into float value."""
        # Remove currency symbols and whitespace
        cleaned_amount = re.sub(r'[$,\s]', '', amount_string)
        
        # Handle parentheses for negative amounts
        if cleaned_amount.startswith('(') and cleaned_amount.endswith(')'):
            cleaned_amount = '-' + cleaned_amount[1:-1]
        
        try:
            return float(cleaned_amount)
        except ValueError:
            raise ValueError(f"Unable to parse amount: {amount_string}")
    
    def generate_summary(self, transactions: List[Dict]) -> Dict:
        """Generate summary statistics by category."""
        summary = {}
        
        for transaction in transactions:
            category = transaction['category']
            amount = abs(transaction['amount'])