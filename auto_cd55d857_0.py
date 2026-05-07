```python
"""
CSV Transaction Parser and Categorizer

This module parses CSV transaction data, categorizes expenses based on keywords,
and validates data integrity with comprehensive error handling.

Features:
- Parses CSV files with transaction data (date, description, amount)
- Categorizes transactions into predefined categories using keyword matching
- Validates data integrity and handles various error conditions
- Provides summary statistics and detailed transaction reports
- Self-contained with only standard library dependencies

Usage:
    python script.py
"""

import csv
import re
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import sys
import io

# Categorization rules - keyword mappings
CATEGORY_KEYWORDS = {
    'food': [
        'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'sandwich', 'food',
        'grocery', 'supermarket', 'deli', 'bakery', 'dining', 'kitchen',
        'mcdonalds', 'subway', 'starbucks', 'dominos', 'uber eats', 'doordash'
    ],
    'transport': [
        'uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'gas', 'fuel',
        'parking', 'toll', 'automotive', 'car wash', 'vehicle', 'transit'
    ],
    'utilities': [
        'electric', 'electricity', 'water', 'gas bill', 'internet', 'phone',
        'cable', 'utility', 'power', 'heating', 'cooling', 'telecom'
    ],
    'entertainment': [
        'movie', 'cinema', 'netflix', 'spotify', 'gaming', 'concert',
        'theater', 'streaming', 'entertainment', 'music', 'gym', 'fitness'
    ],
    'shopping': [
        'amazon', 'target', 'walmart', 'store', 'retail', 'clothing',
        'electronics', 'home depot', 'costco', 'mall', 'purchase'
    ],
    'healthcare': [
        'pharmacy', 'doctor', 'medical', 'hospital', 'health', 'dental',
        'insurance', 'prescription', 'clinic', 'cvs', 'walgreens'
    ]
}

class TransactionParser:
    def __init__(self):
        self.transactions = []
        self.errors = []
        self.categories = defaultdict(list)
        
    def validate_date(self, date_str: str) -> Optional[datetime]:
        """Validate and parse date string."""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
    
    def validate_amount(self, amount_str: str) -> Optional[float]:
        """Validate and parse amount string."""
        try:
            # Remove currency symbols and whitespace
            clean_amount = re.sub(r'[\$,\s]', '', amount_str.strip())
            # Handle negative amounts in parentheses
            if clean_amount.startswith('(') and clean_amount.endswith(')'):
                clean_amount = '-' + clean_amount[1:-1]
            return float(clean_amount)
        except (ValueError, AttributeError):
            return None
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords."""
        description_lower = description.lower()
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def parse_csv_data(self, csv_content: str) -> bool:
        """Parse CSV content and validate transactions."""
        try:
            csv_reader = csv.reader(io.StringIO(csv_content))
            headers = next(csv_reader, None)
            
            if not headers:
                self.errors.append("CSV file is empty")
                return False
            
            # Normalize headers
            headers = [h.strip().lower() for h in headers]
            
            # Find required columns
            date_col = None
            desc_col = None
            amount_col = None
            
            for i, header in enumerate(headers):
                if 'date' in header:
                    date_col = i
                elif 'description' in header or 'desc' in header:
                    desc_col = i
                elif 'amount' in header or 'value' in header:
                    amount_col = i
            
            if date_col is None or desc_col is None or amount_col is None:
                self.errors.append("Required columns not found. Need: date, description, amount")
                return False
            
            row_num = 1
            for row in csv_reader:
                row_num += 1
                
                if len(row) < max(date_col, desc_col, amount_col) + 1:
                    self.errors.append(f"Row {row_num}: Insufficient columns")
                    continue
                
                # Validate date
                date_obj = self.validate_date(row[date_col])
                if not date_obj:
                    self.errors.append(f"Row {row_num}: Invalid date format '{row[date_col]}'")
                    continue
                
                # Validate amount
                amount = self.validate_amount(row[amount_col])
                if amount is None:
                    self.errors.append(f"Row {row_num}: Invalid amount format '{row[amount_col]}'")
                    continue
                
                # Validate description
                description = row[desc_col].strip()
                if not description:
                    self.errors.append(f"Row {row_num}: Empty description")
                    continue
                
                # Categorize transaction
                category = self.categorize_transaction(description)
                
                transaction = {
                    'date': date_obj,
                    'description': description,
                    'amount': amount,
                    'category': category,
                    'row': row_num
                }
                
                self.transactions.append(transaction)
                self.categories[category].append(transaction)
            
            return True
            
        except Exception as e:
            self.errors.append(f"Error parsing CSV: {str(e)}")
            return False
    
    def print_summary(self):
        """Print transaction summary and statistics."""
        print("=" * 60)
        print("TRANSACTION ANALYSIS SUMMARY")
        print("=" * 60)
        
        if self.errors:
            print(f"\n⚠️  ERRORS FOUND ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if not self.transactions:
            print("\n❌ No valid transactions found")
            return
        
        print(f"\n✅ Successfully processed {len(self.transactions)} transactions")
        
        # Category breakdown
        print(f"\n📊 CATEGORY BREAKDOWN:")
        category_totals = {}
        for category, transactions in self.categories.items():
            total = sum(t['amount'] for t in transactions)
            count = len(transactions)
            category_totals[category] = total
            print(f"   {category.upper():12} | {count:3d} transactions | ${total:10.2f}")
        
        # Overall statistics
        total_amount = sum(t['amount'] for t in self.transactions)
        expenses = [t['amount'] for t in self.transactions if t['amount'] < 0]
        income = [t['amount'] for t in self.transactions if t['amount'] > 0]
        
        print(f"\n💰 FINANCIAL SUMMARY:")
        print(f"   Total Transactions: ${total_amount:10.2f}")
        print(f"   Total Expenses:     ${sum(expenses):10.2f}")
        print(f"   Total Income:       ${sum(income):10.2f}")