```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

This script reads CSV files containing bank transaction data and categorizes
transactions by merchant names using regex patterns. It provides spending
summaries by category with total amounts.

Supports common transaction CSV formats with columns for:
- Transaction descriptions/merchant names
- Transaction amounts (positive or negative)
- Dates (optional)

Categories include: Groceries, Restaurants, Utilities, Gas/Fuel, Shopping,
Healthcare, Entertainment, Transportation, and Others.

Usage: python script.py
"""

import csv
import re
import os
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation


class TransactionCategorizer:
    """Categorizes bank transactions using regex patterns."""
    
    def __init__(self):
        """Initialize categorizer with predefined merchant patterns."""
        self.categories = {
            'Groceries': [
                r'\b(walmart|kroger|safeway|publix|whole foods|trader joe|costco|sam\'s club)\b',
                r'\b(grocery|market|food|supermarket)\b',
                r'\b(aldi|target.*grocery|wegmans|harris teeter)\b'
            ],
            'Restaurants': [
                r'\b(mcdonalds|burger king|subway|kfc|taco bell|pizza hut|dominos)\b',
                r'\b(starbucks|dunkin|chipotle|panera|chick-fil-a)\b',
                r'\b(restaurant|cafe|diner|grill|bistro|eatery)\b'
            ],
            'Utilities': [
                r'\b(electric|gas|water|sewer|trash|garbage)\b',
                r'\b(utility|utilities|power|energy)\b',
                r'\b(comcast|verizon|at&t|spectrum|cox|internet|cable|phone)\b'
            ],
            'Gas/Fuel': [
                r'\b(shell|exxon|chevron|bp|mobil|citgo|sunoco|marathon)\b',
                r'\b(gas|fuel|gasoline|station)\b'
            ],
            'Shopping': [
                r'\b(amazon|ebay|target|best buy|home depot|lowes)\b',
                r'\b(shopping|retail|store|mall)\b',
                r'\b(walmart.*general|cvs|walgreens|rite aid)\b'
            ],
            'Healthcare': [
                r'\b(hospital|clinic|doctor|physician|medical|pharmacy)\b',
                r'\b(cvs.*pharmacy|walgreens.*rx|rite aid.*pharmacy)\b',
                r'\b(dental|dentist|vision|optometry)\b'
            ],
            'Entertainment': [
                r'\b(netflix|hulu|spotify|disney|amazon prime|apple music)\b',
                r'\b(movie|theater|cinema|entertainment|gaming)\b',
                r'\b(gym|fitness|recreation|sports)\b'
            ],
            'Transportation': [
                r'\b(uber|lyft|taxi|bus|train|metro|transit)\b',
                r'\b(parking|toll|transportation)\b'
            ]
        }
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.categories.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, description):
        """Categorize a transaction based on its description."""
        description = description.strip().lower()
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(description):
                    return category
        
        return 'Others'
    
    def parse_amount(self, amount_str):
        """Parse amount string to Decimal, handling various formats."""
        try:
            # Remove common currency symbols and whitespace
            cleaned = re.sub(r'[\$,\s]', '', str(amount_str))
            
            # Handle parentheses as negative (common in accounting)
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return Decimal('0')


def detect_csv_format(filepath):
    """Detect CSV format and return column mappings."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Read first few lines to detect format
            sample_lines = [file.readline().strip() for _ in range(3)]
            
        if not any(sample_lines):
            return None
            
        # Try to detect delimiter
        delimiter = ','
        if ';' in sample_lines[0]:
            delimiter = ';'
        elif '\t' in sample_lines[0]:
            delimiter = '\t'
            
        # Parse header
        headers = [h.strip().lower() for h in sample_lines[0].split(delimiter)]
        
        # Find relevant columns
        description_col = None
        amount_col = None
        date_col = None
        
        for i, header in enumerate(headers):
            if any(keyword in header for keyword in ['description', 'merchant', 'payee', 'memo']):
                description_col = i
            elif any(keyword in header for keyword in ['amount', 'debit', 'credit', 'transaction']):
                amount_col = i
            elif any(keyword in header for keyword in ['date', 'posted', 'transaction_date']):
                date_col = i
        
        if description_col is None or amount_col is None:
            # Try positional defaults if headers don't match
            if len(headers) >= 3:
                date_col = 0
                description_col = 1
                amount_col = 2
            else:
                return None
                
        return {
            'delimiter': delimiter,
            'description_col': description_col,
            'amount_col': amount_col,
            'date_col': date_col
        }
        
    except Exception as e:
        print(f"Error detecting CSV format: {e}")
        return None


def process_csv_file(filepath, categorizer):
    """Process a single CSV file and return categorized transactions."""
    format_info = detect_csv_format(filepath)
    if not format_info:
        raise ValueError(f"Could not detect CSV format for {filepath}")
    
    transactions = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=format_info['delimiter'])
            
            # Skip header
            next(csv_reader, None)
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    if len(row) <= max(format_info['description_col'], format_info['amount_col']):
                        continue
                        
                    description = row[format_info['description_col']]
                    amount_str = row[format_info['amount_col']]
                    
                    if not description.strip():
                        continue
                        
                    amount = categorizer.parse_amount(amount_str)
                    category = categorizer.categorize_transaction(description)
                    
                    transactions.append({
                        'description': description.strip(),
                        'amount': amount,
                        'category': category,
                        'row': row_num
                    })
                    
                except (IndexError, ValueError) as e:
                    print(f"Warning: Skipping row {row_num} in {filepath}: {e}")
                    continue
                    
    except Exception as e:
        raise Exception(f"Error reading {filepath}: {e}")
    
    return transactions


def generate_summary(transactions):
    """Generate spending summary by category."""
    category_totals = defaultdict(Decimal)
    category_counts = defaultdict(int)
    
    total_spent = Decimal('0')
    total_transactions = 0
    
    for transaction in transactions:
        amount = abs(transaction['amount'])  # Use absolute value for spending
        category = transaction['category']
        
        category_totals[category