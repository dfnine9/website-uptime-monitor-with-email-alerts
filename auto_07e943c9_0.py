```python
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements and automatically categorizes transactions
based on keyword matching. It calculates spending totals by category with
monthly and weekly breakdowns.

Features:
- Keyword-based transaction categorization
- Monthly and weekly spending analysis
- Configurable category rules
- Error handling for malformed data
- Support for common CSV bank statement formats

Usage:
    python script.py

The script expects a CSV file named 'bank_statement.csv' with columns:
- Date (YYYY-MM-DD format)
- Description (transaction description)
- Amount (negative for expenses, positive for income)
"""

import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple
import os


class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'publix', 'whole foods',
                'trader joe', 'costco', 'sam\'s club', 'aldi', 'food lion',
                'harris teeter', 'giant', 'stop shop', 'wegmans', 'heb',
                'grocery', 'supermarket', 'market', 'fresh'
            ],
            'utilities': [
                'electric', 'electricity', 'gas company', 'water', 'sewer',
                'internet', 'cable', 'phone', 'wireless', 'verizon', 'att',
                'comcast', 'xfinity', 'spectrum', 'duke energy', 'pge',
                'utility', 'bill payment'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime',
                'movie', 'cinema', 'theater', 'theatre', 'concert',
                'game', 'steam', 'xbox', 'playstation', 'entertainment',
                'music', 'streaming', 'subscription'
            ],
            'restaurants': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'starbucks',
                'dunkin', 'pizza', 'taco bell', 'kfc', 'wendys', 'chipotle',
                'panera', 'olive garden', 'applebee', 'chili', 'outback',
                'dining', 'cafe', 'bistro', 'grill', 'bar', 'pub'
            ],
            'transportation': [
                'gas', 'fuel', 'gasoline', 'shell', 'exxon', 'bp', 'chevron',
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'airline',
                'parking', 'toll', 'car wash', 'auto', 'repair'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital',
                'medical', 'doctor', 'dentist', 'clinic', 'health',
                'prescription', 'medicine', 'copay'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes',
                'macy', 'nordstrom', 'tj maxx', 'old navy', 'gap',
                'clothing', 'department store', 'mall', 'outlet'
            ],
            'banking': [
                'fee', 'atm', 'overdraft', 'interest', 'transfer',
                'deposit', 'withdrawal', 'maintenance', 'service charge'
            ]
        }

    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'

    def parse_date(self, date_str: str) -> datetime:
        """Parse date string in various formats."""
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")

    def get_week_start(self, date: datetime) -> datetime:
        """Get the start of the week (Monday) for a given date."""
        days_since_monday = date.weekday()
        return date - timedelta(days=days_since_monday)

    def read_csv_file(self, filename: str) -> List[Tuple[datetime, str, float]]:
        """Read and parse CSV bank statement file."""
        transactions = []
        
        with open(filename, 'r', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            delimiter = ',' if sample.count(',') > sample.count(';') else ';'
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            # Try to find correct column names
            fieldnames = [name.lower().strip() for name in reader.fieldnames]
            
            date_col = None
            desc_col = None
            amount_col = None
            
            # Find date column
            for col in fieldnames:
                if any(word in col for word in ['date', 'transaction_date', 'posted']):
                    date_col = col
                    break
            
            # Find description column
            for col in fieldnames:
                if any(word in col for word in ['description', 'memo', 'detail', 'merchant']):
                    desc_col = col
                    break
            
            # Find amount column
            for col in fieldnames:
                if any(word in col for word in ['amount', 'debit', 'credit', 'transaction']):
                    amount_col = col
                    break
            
            if not all([date_col, desc_col, amount_col]):
                raise ValueError("Could not identify required columns in CSV file")
            
            for row in reader:
                try:
                    date = self.parse_date(row[date_col])
                    description = row[desc_col].strip()
                    
                    # Clean amount string
                    amount_str = row[amount_col].strip()
                    amount_str = re.sub(r'[^\d.-]', '', amount_str)
                    amount = float(amount_str) if amount_str else 0.0
                    
                    # Skip if essential data is missing
                    if not description or amount == 0:
                        continue
                    
                    transactions.append((date, description, amount))
                
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid row: {e}")
                    continue
        
        return transactions

    def analyze_spending(self, transactions: List[Tuple[datetime, str, float]]) -> Dict:
        """Analyze spending by category with time breakdowns."""
        category_totals = defaultdict(float)
        monthly_spending = defaultdict(lambda: defaultdict(float))
        weekly_spending = defaultdict(lambda: defaultdict(float))
        
        for date, description, amount in transactions:
            # Only process expenses (negative amounts)
            if amount >= 0:
                continue
            
            expense_amount = abs(amount)
            category = self.categorize_transaction(description)
            
            # Total by category
            category_totals[category] += expense_amount
            
            # Monthly breakdown
            month_key = date.strftime('%Y-%m')
            monthly_spending[month_key][category] += expense_amount
            
            # Weekly breakdown
            week_start = self.get_week_start(date)
            week_key = week_start.strftime('%Y-%m-%d')
            weekly_spending[week_key][category] += expense_amount
        
        return {
            'category_totals': dict(category_