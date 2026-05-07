```python
"""
CSV Transaction Categorization Engine

This module parses CSV transaction data, validates required fields (date, amount, description),
and categorizes transactions using a keyword-based engine with predefined categories.

Categories supported: groceries, utilities, entertainment, dining, transportation, shopping, healthcare

Usage: python script.py

The script expects a CSV file named 'transactions.csv' in the same directory with columns:
date, amount, description (additional columns are ignored)
"""

import csv
import sys
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Keyword-based transaction categorization engine"""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway',
                'whole foods', 'trader joe', 'costco', 'food mart', 'market'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'internet', 'phone', 'cable',
                'verizon', 'att', 'comcast', 'utility', 'power', 'energy'
            ],
            'entertainment': [
                'netflix', 'spotify', 'movie', 'theater', 'cinema', 'concert',
                'game', 'entertainment', 'streaming', 'subscription', 'hulu'
            ],
            'dining': [
                'restaurant', 'mcdonalds', 'starbucks', 'pizza', 'cafe', 'diner',
                'fast food', 'takeout', 'delivery', 'doordash', 'uber eats'
            ],
            'transportation': [
                'gas station', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus',
                'parking', 'toll', 'car repair', 'auto', 'transport'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'store', 'retail', 'clothes', 'clothing',
                'department', 'online', 'purchase', 'buy'
            ],
            'healthcare': [
                'doctor', 'hospital', 'pharmacy', 'medical', 'health', 'dental',
                'prescription', 'clinic', 'medicine', 'cvs', 'walgreens'
            ]
        }
    
    def categorize(self, description: str) -> str:
        """Categorize transaction based on description keywords"""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class TransactionValidator:
    """Validates transaction data fields"""
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format (supports multiple common formats)"""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                datetime.strptime(date_str.strip(), fmt)
                return True
            except ValueError:
                continue
        return False
    
    @staticmethod
    def validate_amount(amount_str: str) -> bool:
        """Validate amount is a valid number"""
        try:
            # Remove currency symbols and whitespace
            cleaned_amount = re.sub(r'[$,\s]', '', amount_str.strip())
            float(cleaned_amount)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_description(description: str) -> bool:
        """Validate description is not empty"""
        return bool(description and description.strip())


class CSVTransactionProcessor:
    """Main processor for CSV transaction data"""
    
    def __init__(self):
        self.validator = TransactionValidator()
        self.categorizer = TransactionCategorizer()
        self.valid_transactions = []
        self.invalid_transactions = []
    
    def process_csv(self, filename: str) -> None:
        """Process CSV file and categorize valid transactions"""
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                delimiter = ',' if ',' in sample else ';' if ';' in sample else '\t'
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Check if required columns exist
                required_columns = {'date', 'amount', 'description'}
                if not required_columns.issubset(set(col.lower() for col in reader.fieldnames)):
                    raise ValueError(f"CSV must contain columns: {required_columns}")
                
                # Process each row
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    self._process_row(row, row_num)
                    
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing CSV: {e}")
            sys.exit(1)
    
    def _process_row(self, row: Dict[str, str], row_num: int) -> None:
        """Process individual CSV row"""
        # Normalize column names to lowercase
        normalized_row = {k.lower(): v for k, v in row.items()}
        
        date_val = normalized_row.get('date', '').strip()
        amount_val = normalized_row.get('amount', '').strip()
        description_val = normalized_row.get('description', '').strip()
        
        # Validate required fields
        validation_errors = []
        
        if not self.validator.validate_date(date_val):
            validation_errors.append("invalid date format")
        
        if not self.validator.validate_amount(amount_val):
            validation_errors.append("invalid amount")
        
        if not self.validator.validate_description(description_val):
            validation_errors.append("missing description")
        
        if validation_errors:
            self.invalid_transactions.append({
                'row': row_num,
                'data': normalized_row,
                'errors': validation_errors
            })
        else:
            # Categorize valid transaction
            category = self.categorizer.categorize(description_val)
            
            self.valid_transactions.append({
                'row': row_num,
                'date': date_val,
                'amount': amount_val,
                'description': description_val,
                'category': category
            })
    
    def print_results(self) -> None:
        """Print processing results to stdout"""
        print("=== TRANSACTION PROCESSING RESULTS ===\n")
        
        print(f"Total transactions processed: {len(self.valid_transactions) + len(self.invalid_transactions)}")
        print(f"Valid transactions: {len(self.valid_transactions)}")
        print(f"Invalid transactions: {len(self.invalid_transactions)}\n")
        
        # Print invalid transactions
        if self.invalid_transactions:
            print("INVALID TRANSACTIONS:")
            print("-" * 50)
            for invalid in self.invalid_transactions:
                print(f"Row {invalid['row']}: {', '.join(invalid['errors'])}")
                print(f"  Data: {invalid['data']}")
            print()
        
        # Print valid transactions by category
        if self.valid_transactions:
            print("VALID TRANSACTIONS BY CATEGORY:")
            print("-" * 50)
            
            # Group by category
            categories = {}
            for transaction in self.valid_transactions:
                category = transaction['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(transaction)
            
            # Print each category
            for category, transactions in sorted(categories.items()):
                print(f"\n{category.upper()} ({len(transactions)} transactions):")
                for txn in transactions: