```python
"""
Expense Categorization and Transaction Validation Script

This module reads CSV files containing financial transaction data, implements
keyword-based expense categorization logic, and validates transaction data structure.
The script processes transaction records, categorizes expenses based on description
keywords, and ensures data integrity through validation checks.

Features:
- CSV file reading and parsing
- Keyword-based expense categorization
- Transaction data structure validation
- Error handling for malformed data
- Summary reporting of categorized expenses

Requirements: Python 3.6+ with pandas (falls back to csv module if pandas unavailable)
"""

import csv
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

class ExpenseCategorizer:
    """Handles expense categorization based on keywords and validation of transaction data."""
    
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'food', 'dining', 'pizza', 'burger',
                'grocery', 'supermarket', 'market', 'mcdonalds', 'starbucks', 'subway'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'toll', 'metro',
                'bus', 'train', 'airline', 'flight', 'car', 'automotive'
            ],
            'Shopping': [
                'amazon', 'walmart', 'target', 'costco', 'mall', 'store', 'retail',
                'clothing', 'shoes', 'electronics', 'books'
            ],
            'Utilities': [
                'electric', 'electricity', 'water', 'gas company', 'internet',
                'phone', 'cable', 'utility', 'power'
            ],
            'Healthcare': [
                'medical', 'doctor', 'hospital', 'pharmacy', 'dental', 'health',
                'clinic', 'medicare', 'insurance'
            ],
            'Entertainment': [
                'movie', 'cinema', 'netflix', 'spotify', 'gaming', 'gym', 'fitness',
                'theatre', 'concert', 'sports'
            ],
            'Financial': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'credit', 'investment',
                'transfer', 'payment'
            ]
        }
        
    def categorize_expense(self, description: str) -> str:
        """
        Categorize an expense based on description keywords.
        
        Args:
            description (str): Transaction description
            
        Returns:
            str: Category name or 'Other' if no match found
        """
        if not description:
            return 'Other'
            
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
                    
        return 'Other'
    
    def validate_transaction(self, transaction: Dict) -> Tuple[bool, List[str]]:
        """
        Validate transaction data structure and content.
        
        Args:
            transaction (Dict): Transaction record
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        required_fields = ['date', 'description', 'amount']
        
        # Check required fields
        for field in required_fields:
            if field not in transaction or not transaction[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate date format
        if 'date' in transaction and transaction['date']:
            try:
                # Try multiple date formats
                date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
                date_parsed = False
                for fmt in date_formats:
                    try:
                        datetime.strptime(str(transaction['date']), fmt)
                        date_parsed = True
                        break
                    except ValueError:
                        continue
                
                if not date_parsed:
                    errors.append(f"Invalid date format: {transaction['date']}")
            except Exception as e:
                errors.append(f"Date validation error: {str(e)}")
        
        # Validate amount
        if 'amount' in transaction and transaction['amount']:
            try:
                amount = str(transaction['amount']).replace('$', '').replace(',', '')
                float(amount)
            except (ValueError, TypeError):
                errors.append(f"Invalid amount format: {transaction['amount']}")
        
        # Validate description
        if 'description' in transaction and transaction['description']:
            if len(str(transaction['description']).strip()) < 1:
                errors.append("Description cannot be empty")
        
        return len(errors) == 0, errors

class CSVProcessor:
    """Handles CSV file operations with fallback to standard library."""
    
    def __init__(self):
        self.use_pandas = self._check_pandas()
        
    def _check_pandas(self) -> bool:
        """Check if pandas is available."""
        try:
            import pandas as pd
            return True
        except ImportError:
            print("Warning: pandas not available, using csv module")
            return False
    
    def read_csv_file(self, filepath: str) -> List[Dict]:
        """
        Read CSV file using pandas or fallback to csv module.
        
        Args:
            filepath (str): Path to CSV file
            
        Returns:
            List[Dict]: List of transaction records
        """
        if self.use_pandas:
            return self._read_with_pandas(filepath)
        else:
            return self._read_with_csv(filepath)
    
    def _read_with_pandas(self, filepath: str) -> List[Dict]:
        """Read CSV using pandas."""
        import pandas as pd
        
        try:
            df = pd.read_csv(filepath)
            # Convert to list of dictionaries
            return df.to_dict('records')
        except Exception as e:
            raise Exception(f"Error reading CSV with pandas: {str(e)}")
    
    def _read_with_csv(self, filepath: str) -> List[Dict]:
        """Read CSV using standard csv module."""
        transactions = []
        
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                for row in reader:
                    transactions.append(dict(row))
                    
        except Exception as e:
            raise Exception(f"Error reading CSV with csv module: {str(e)}")
            
        return transactions

def create_sample_csv():
    """Create a sample CSV file for testing purposes."""
    sample_data = [
        ['date', 'description', 'amount', 'account'],
        ['2024-01-15', 'Starbucks Coffee Shop', '-4.50', 'Credit Card'],
        ['2024-01-16', 'Shell Gas Station', '-45.00', 'Debit Card'],
        ['2024-01-17', 'Amazon Purchase', '-89.99', 'Credit Card'],
        ['2024-01-18', 'Salary Deposit', '3000.00', 'Checking'],
        ['2024-01-19', 'Electric Company', '-120.50', 'Checking'],
        ['2024-01-20', 'Netflix Subscription', '-15.99', 'Credit Card'],
        ['2024-01-21', 'Grocery Store Market', '-67.34', 'Debit Card'],
        ['2024-01-22', 'ATM Fee', '-3.00', 'Checking'],
        ['2024-01-23', 'Doctor Visit Copay', '-25.00', 'Credit Card'],
        ['2024-01-24', 'Invalid Amount', 'not_a_number',