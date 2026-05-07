```python
"""
Bank Transaction Categorizer

This module parses CSV bank transaction files, validates the data structure,
and implements rule-based text matching to automatically categorize expenses
into predefined categories such as groceries, utilities, entertainment, etc.

The script processes transaction data by:
1. Reading and validating CSV file structure
2. Cleaning and normalizing transaction descriptions
3. Applying rule-based categorization using keyword matching
4. Outputting categorized transactions with summary statistics

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class TransactionCategorizer:
    def __init__(self):
        # Define categorization rules with keywords and patterns
        self.category_rules = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'grocery', 'supermarket', 'food', 'market',
                'aldi', 'publix', 'wegmans', 'harris teeter', 'food lion'
            ],
            'utilities': [
                'electric', 'electricity', 'gas', 'water', 'sewer', 'trash',
                'internet', 'cable', 'phone', 'wireless', 'verizon', 'att',
                'comcast', 'xfinity', 'spectrum', 'utility', 'power', 'energy'
            ],
            'entertainment': [
                'netflix', 'hulu', 'disney', 'spotify', 'amazon prime', 'apple music',
                'movie', 'theater', 'cinema', 'concert', 'spotify', 'gaming',
                'steam', 'playstation', 'xbox', 'entertainment', 'streaming'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'uber', 'lyft', 'taxi', 'subway', 'bus', 'train', 'parking',
                'toll', 'auto', 'car', 'vehicle', 'transport'
            ],
            'dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'dunkin', 'mcdonald',
                'burger', 'pizza', 'taco', 'subway', 'chipotle', 'dining',
                'takeout', 'delivery', 'doordash', 'grubhub', 'ubereats'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'store', 'retail', 'clothing',
                'shoes', 'department', 'online', 'purchase', 'buy',
                'shop', 'merchandise', 'goods'
            ],
            'healthcare': [
                'hospital', 'clinic', 'doctor', 'medical', 'pharmacy', 'cvs',
                'walgreens', 'health', 'dental', 'vision', 'prescription',
                'medicine', 'drug', 'healthcare'
            ],
            'finance': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'credit', 'investment',
                'transfer', 'payment', 'finance', 'insurance', 'premium'
            ]
        }

    def validate_csv_structure(self, file_path: str) -> bool:
        """Validate that CSV has required columns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                required_fields = ['date', 'description', 'amount']
                for field in required_fields:
                    if field not in [h.lower() for h in headers]:
                        print(f"Error: Required field '{field}' not found in CSV headers: {headers}")
                        return False
                return True
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return False
        except Exception as e:
            print(f"Error validating CSV structure: {e}")
            return False

    def clean_description(self, description: str) -> str:
        """Clean and normalize transaction description."""
        if not description:
            return ""
        
        # Convert to lowercase and remove special characters
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', description.lower())
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        return cleaned

    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description using rule-based matching."""
        cleaned_desc = self.clean_description(description)
        
        if not cleaned_desc:
            return 'other'
        
        # Score each category based on keyword matches
        category_scores = defaultdict(int)
        
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in cleaned_desc:
                    # Give higher score for exact matches
                    if keyword == cleaned_desc:
                        category_scores[category] += 10
                    # Partial matches get lower scores
                    elif keyword in cleaned_desc.split():
                        category_scores[category] += 5
                    else:
                        category_scores[category] += 1
        
        # Return category with highest score, or 'other' if no matches
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return 'other'

    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.-]', '', str(amount_str))
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y%m%d']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        return None

    def process_transactions(self, file_path: str) -> List[Dict]:
        """Process transactions from CSV file."""
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, start=1):
                    try:
                        # Find case-insensitive column names
                        date_col = next((k for k in row.keys() if k.lower() == 'date'), None)
                        desc_col = next((k for k in row.keys() if k.lower() == 'description'), None)
                        amount_col = next((k for k in row.keys() if k.lower() == 'amount'), None)
                        
                        if not all([date_col, desc_col, amount_col]):
                            print(f"Warning: Missing required columns in row {row_num}")
                            continue
                        
                        # Parse and validate data
                        date_obj = self.parse_date(row[date_col])
                        description = str(row[desc_col]).strip()
                        amount = self.parse_amount(row[amount_col])
                        
                        if not date_obj:
                            print(f"Warning: Invalid date in row {row_num}: {row[date_col]}")
                            continue
                        
                        if not description:
                            print(f"Warning: Empty description in row {row_num}")
                            continue
                        
                        # Categorize transaction
                        category = self.categorize_transaction(description)
                        
                        transactions.append({
                            'date': date_obj,
                            '