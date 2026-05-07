```python
"""
Bank Statement Analyzer

This module reads CSV bank statement files, automatically detects column formats
(date, description, amount), categorizes transactions using keyword matching rules,
and outputs spending totals by category.

Features:
- Automatic column detection for common bank statement formats
- Keyword-based transaction categorization
- Flexible date parsing
- Error handling for malformed data
- Summary reporting by category

Usage:
    python script.py

The script will look for CSV files in the current directory with names containing
'statement', 'bank', or 'transaction' and process them automatically.
"""

import csv
import re
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any


class BankStatementAnalyzer:
    def __init__(self):
        self.category_rules = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'food', 'dining',
                'mcdonalds', 'subway', 'starbucks', 'dominos', 'uber eats', 'doordash',
                'grubhub', 'takeaway', 'delivery', 'kitchen', 'bistro', 'bar', 'pub'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'metro', 'train',
                'parking', 'toll', 'airline', 'flight', 'car', 'auto', 'mechanic',
                'insurance', 'registration', 'dmv'
            ],
            'Shopping': [
                'amazon', 'walmart', 'target', 'costco', 'store', 'shop', 'retail',
                'mall', 'online', 'ebay', 'purchase', 'buy', 'clothing', 'shoes'
            ],
            'Entertainment': [
                'movie', 'cinema', 'theater', 'netflix', 'spotify', 'game', 'concert',
                'ticket', 'entertainment', 'music', 'streaming', 'subscription'
            ],
            'Utilities': [
                'electric', 'electricity', 'water', 'gas bill', 'internet', 'phone',
                'cable', 'utility', 'power', 'heating', 'cooling'
            ],
            'Healthcare': [
                'doctor', 'medical', 'pharmacy', 'hospital', 'clinic', 'dentist',
                'health', 'medicine', 'prescription', 'insurance'
            ],
            'Banking': [
                'bank', 'atm', 'fee', 'interest', 'transfer', 'deposit', 'withdrawal',
                'overdraft', 'maintenance'
            ]
        }
        
        self.spending_by_category = defaultdict(float)
        self.total_transactions = 0
        self.processed_files = []

    def detect_columns(self, headers: List[str]) -> Dict[str, int]:
        """Detect which columns contain date, description, and amount data."""
        columns = {'date': -1, 'description': -1, 'amount': -1}
        
        # Normalize headers for comparison
        normalized_headers = [h.lower().strip() for h in headers]
        
        # Date column detection
        date_keywords = ['date', 'transaction date', 'posted date', 'trans date']
        for i, header in enumerate(normalized_headers):
            if any(keyword in header for keyword in date_keywords):
                columns['date'] = i
                break
        
        # Description column detection
        desc_keywords = ['description', 'memo', 'details', 'transaction', 'payee']
        for i, header in enumerate(normalized_headers):
            if any(keyword in header for keyword in desc_keywords):
                columns['description'] = i
                break
        
        # Amount column detection (prefer debit/withdrawal columns for spending analysis)
        amount_keywords = ['amount', 'debit', 'withdrawal', 'charge', 'payment']
        for i, header in enumerate(normalized_headers):
            if any(keyword in header for keyword in amount_keywords):
                columns['amount'] = i
                break
        
        # Fallback: if no amount column found, look for any numeric-sounding column
        if columns['amount'] == -1:
            for i, header in enumerate(normalized_headers):
                if 'credit' in header or 'balance' in header or '$' in header:
                    columns['amount'] = i
                    break
        
        return columns

    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return 0.0
        
        try:
            # Remove currency symbols, commas, and extra whitespace
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            
            # Handle parentheses (often indicate negative amounts)
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string using common formats."""
        if not date_str or date_str.strip() == '':
            return None
        
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None

    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords."""
        if not description:
            return 'Other'
        
        description_lower = description.lower()
        
        for category, keywords in self.category_rules.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'Other'

    def process_csv_file(self, filepath: str) -> bool:
        """Process a single CSV file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader, [])
                
                if not headers:
                    print(f"Warning: No headers found in {filepath}")
                    return False
                
                columns = self.detect_columns(headers)
                
                if columns['description'] == -1 or columns['amount'] == -1:
                    print(f"Warning: Could not detect required columns in {filepath}")
                    print(f"Headers found: {headers}")
                    return False
                
                transactions_processed = 0
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(columns['description'], columns['amount']):
                            continue
                        
                        description = row[columns['description']].strip()
                        amount_str = row[columns['amount']].strip()
                        
                        if not description or not amount_str:
                            continue
                        
                        amount = self.parse_amount(amount_str)
                        
                        # Only process negative amounts (expenses) or positive amounts in debit columns
                        if amount != 0:
                            # Convert to positive for spending analysis
                            spending_amount = abs(amount)
                            category = self.categorize_transaction(description)
                            self.spending_by_category[category] += spending_amount
                            transactions_processed += 1
                    
                    except