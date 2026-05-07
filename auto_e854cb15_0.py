```python
#!/usr/bin/env python3
"""
Bank Transaction Categorization Script

This script reads CSV bank transaction files and automatically categorizes expenses
using regex patterns and keyword dictionaries. It validates transaction data formats
and provides detailed categorization results.

Features:
- Reads CSV files with bank transaction data
- Validates transaction format (date, amount, description)
- Categorizes transactions using keyword matching and regex patterns
- Handles various date formats and amount formats
- Provides summary statistics by category
- Exports categorized results

Usage: python script.py [csv_file_path]
If no file is provided, uses sample data for demonstration.
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions using regex patterns and keyword dictionaries."""
    
    def __init__(self):
        self.categories = {
            'groceries': {
                'keywords': ['grocery', 'market', 'food', 'supermarket', 'walmart', 'target', 
                           'kroger', 'safeway', 'whole foods', 'trader joe', 'costco', 'sam\'s club'],
                'patterns': [r'\b(grocery|market|food)\b', r'walmart|target', r'costco|sam\'s']
            },
            'utilities': {
                'keywords': ['electric', 'gas', 'water', 'internet', 'phone', 'cable', 
                           'utility', 'power', 'energy', 'telecom', 'verizon', 'at&t'],
                'patterns': [r'\b(electric|gas|water|utility)\b', r'(verizon|at&t)', r'power\s+company']
            },
            'entertainment': {
                'keywords': ['netflix', 'spotify', 'movie', 'theater', 'cinema', 'concert', 
                           'gaming', 'steam', 'xbox', 'playstation', 'entertainment'],
                'patterns': [r'\b(netflix|spotify|steam)\b', r'movie|theater|cinema', r'gaming|xbox|playstation']
            },
            'transportation': {
                'keywords': ['gas station', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus', 
                           'parking', 'toll', 'shell', 'chevron', 'exxon'],
                'patterns': [r'\b(gas|fuel|uber|lyft)\b', r'shell|chevron|exxon', r'parking|toll']
            },
            'dining': {
                'keywords': ['restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'pizza', 
                           'dining', 'bar', 'pub', 'bistro'],
                'patterns': [r'\b(restaurant|cafe|coffee)\b', r'starbucks|mcdonald', r'pizza|dining']
            },
            'healthcare': {
                'keywords': ['pharmacy', 'doctor', 'medical', 'hospital', 'clinic', 'cvs', 
                           'walgreens', 'health', 'dental', 'vision'],
                'patterns': [r'\b(pharmacy|medical|doctor)\b', r'cvs|walgreens', r'hospital|clinic']
            },
            'shopping': {
                'keywords': ['amazon', 'ebay', 'store', 'retail', 'mall', 'clothing', 'shoes'],
                'patterns': [r'\b(amazon|ebay|store)\b', r'retail|mall', r'clothing|shoes']
            }
        }
    
    def validate_transaction(self, row: Dict[str, str]) -> Tuple[bool, str]:
        """Validate transaction data format."""
        try:
            # Check required fields
            required_fields = ['date', 'amount', 'description']
            for field in required_fields:
                if field not in row or not row[field].strip():
                    return False, f"Missing or empty field: {field}"
            
            # Validate date format
            date_str = row['date'].strip()
            if not self._validate_date(date_str):
                return False, f"Invalid date format: {date_str}"
            
            # Validate amount format
            amount_str = row['amount'].strip()
            if not self._validate_amount(amount_str):
                return False, f"Invalid amount format: {amount_str}"
            
            return True, "Valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date string in common formats."""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m-%d-%Y']
        
        for fmt in date_formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        return False
    
    def _validate_amount(self, amount_str: str) -> bool:
        """Validate amount string format."""
        # Remove common currency symbols and whitespace
        clean_amount = re.sub(r'[$,\s]', '', amount_str)
        
        # Check if it's a valid number (positive or negative)
        pattern = r'^-?\d+(\.\d{1,2})?$'
        return bool(re.match(pattern, clean_amount))
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, rules in self.categories.items():
            # Check keywords
            for keyword in rules['keywords']:
                if keyword.lower() in description_lower:
                    return category
            
            # Check regex patterns
            for pattern in rules['patterns']:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        return 'other'
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        # Remove currency symbols and whitespace
        clean_amount = re.sub(r'[$,\s]', '', amount_str.strip())
        return float(clean_amount)


def create_sample_data() -> str:
    """Create sample CSV data for demonstration."""
    sample_data = """date,amount,description
2024-01-15,-45.67,Walmart Grocery Store
2024-01-16,-12.99,Netflix Subscription
2024-01-17,-89.34,Shell Gas Station
2024-01-18,-156.78,Electric Company Bill
2024-01-19,-34.56,Starbucks Coffee
2024-01-20,-23.45,CVS Pharmacy
2024-01-21,-78.90,Amazon Purchase
2024-01-22,-25.67,McDonald's Restaurant
2024-01-23,-45.32,Target Store
2024-01-24,-67.89,Verizon Wireless
2024-01-25,2500.00,Salary Deposit
2024-01-26,-123.45,Whole Foods Market
2024-01-27,-56.78,Uber Ride
2024-01-28,-89.12,Movie Theater
2024-01-29,-34.56,Water Utility Bill
2024-01-30,-45.67,Pizza Delivery"""
    
    filename = 'sample_transactions.csv'
    with open(filename, 'w', newline='') as f:
        f.write(sample_data)
    return filename


def process_transactions(csv_file: str) -> None:
    """Process transactions from CSV file."""
    categorizer = TransactionCategorizer()
    transactions = []
    errors = []
    category_totals = defaultdict(float)
    category_counts = defaultdict(int)
    
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)