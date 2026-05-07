```python
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements and automatically categorizes transactions
using keyword matching and merchant identification. It calculates spending totals
by category and provides a summary report.

Features:
- Parses CSV files with transaction data
- Automatically categorizes transactions based on description keywords
- Identifies common merchants and maps them to appropriate categories
- Calculates total spending per category
- Handles various CSV formats and missing data
- Provides detailed error handling and logging

Usage: python script.py
"""

import csv
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import sys
import os

class TransactionCategorizer:
    def __init__(self):
        # Define category keywords and merchant patterns
        self.category_keywords = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'deli', 'bakery',
                'mcdonald', 'starbucks', 'subway', 'kfc', 'taco bell', 'domino',
                'grocery', 'supermarket', 'market', 'food', 'dining'
            ],
            'Gas & Transportation': [
                'gas', 'fuel', 'exxon', 'shell', 'bp', 'chevron', 'mobil', 'station',
                'uber', 'lyft', 'taxi', 'transport', 'metro', 'bus', 'train'
            ],
            'Shopping': [
                'amazon', 'walmart', 'target', 'costco', 'mall', 'store', 'retail',
                'shopping', 'purchase', 'clothing', 'apparel', 'electronics'
            ],
            'Bills & Utilities': [
                'electric', 'power', 'water', 'gas bill', 'phone', 'internet', 'cable',
                'utility', 'bill', 'payment', 'service', 'subscription'
            ],
            'Healthcare': [
                'pharmacy', 'doctor', 'hospital', 'medical', 'clinic', 'health',
                'cvs', 'walgreens', 'dental', 'vision'
            ],
            'Entertainment': [
                'movie', 'cinema', 'theater', 'netflix', 'spotify', 'game', 'entertainment',
                'concert', 'event', 'ticket', 'streaming'
            ],
            'ATM & Banking': [
                'atm', 'withdrawal', 'fee', 'bank', 'transfer', 'check', 'deposit'
            ],
            'Other': []
        }

    def parse_csv(self, file_path: str) -> List[Dict]:
        """Parse CSV file and return list of transaction dictionaries."""
        transactions = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        transaction = self._process_row(row)
                        if transaction:
                            transactions.append(transaction)
                    except Exception as e:
                        print(f"Warning: Error processing row {row_num}: {e}")
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
            
        return transactions

    def _process_row(self, row: Dict) -> Optional[Dict]:
        """Process a single CSV row and extract transaction data."""
        # Common column name variations
        date_fields = ['Date', 'date', 'Transaction Date', 'Posted Date']
        description_fields = ['Description', 'description', 'Merchant', 'merchant', 'Details', 'details']
        amount_fields = ['Amount', 'amount', 'Debit', 'debit', 'Credit', 'credit', 'Transaction Amount']
        
        # Find the actual column names
        date = self._find_field_value(row, date_fields)
        description = self._find_field_value(row, description_fields)
        amount = self._find_field_value(row, amount_fields)
        
        if not description or not amount:
            return None
            
        # Clean and parse amount
        try:
            # Remove currency symbols and clean amount
            amount_str = str(amount).replace('$', '').replace(',', '').strip()
            # Handle negative amounts in parentheses
            if amount_str.startswith('(') and amount_str.endswith(')'):
                amount_str = '-' + amount_str[1:-1]
            amount_float = float(amount_str)
        except (ValueError, TypeError):
            print(f"Warning: Could not parse amount: {amount}")
            return None
            
        return {
            'date': date or '',
            'description': description.strip(),
            'amount': amount_float
        }

    def _find_field_value(self, row: Dict, field_names: List[str]) -> Optional[str]:
        """Find the first matching field value from a list of possible field names."""
        for field in field_names:
            if field in row and row[field]:
                return row[field]
        return None

    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        # Check each category for keyword matches
        for category, keywords in self.category_keywords.items():
            if category == 'Other':
                continue
                
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'

    def calculate_totals(self, transactions: List[Dict]) -> Dict[str, float]:
        """Calculate spending totals by category."""
        category_totals = defaultdict(float)
        
        for transaction in transactions:
            category = self.categorize_transaction(transaction['description'])
            # Only count negative amounts as spending (positive might be deposits/credits)
            if transaction['amount'] < 0:
                category_totals[category] += abs(transaction['amount'])
        
        return dict(category_totals)

    def generate_report(self, transactions: List[Dict], totals: Dict[str, float]) -> str:
        """Generate a formatted spending report."""
        report = []
        report.append("=" * 60)
        report.append("BANK STATEMENT SPENDING ANALYSIS")
        report.append("=" * 60)
        report.append(f"Total transactions processed: {len(transactions)}")
        
        spending_transactions = [t for t in transactions if t['amount'] < 0]
        report.append(f"Spending transactions: {len(spending_transactions)}")
        
        total_spending = sum(totals.values())
        report.append(f"Total spending: ${total_spending:.2f}")
        report.append("")
        
        report.append("SPENDING BY CATEGORY:")
        report.append("-" * 30)
        
        # Sort categories by spending amount (descending)
        sorted_categories = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        
        for category, amount in sorted_categories:
            percentage = (amount / total_spending) * 100 if total_spending > 0 else 0
            report.append(f"{category:<25} ${amount:>10.2f} ({percentage:>5.1f}%)")
        
        report.append("")
        report.append("TOP TRANSACTIONS BY CATEGORY:")
        report.append("-" * 40)
        
        # Show top 3 transactions per category
        for category, _ in sorted_categories[:5]:  # Top 5 categories only
            category_transactions = [
                t for t in spending_transactions 
                if self.categorize_transaction(t['description']) == category
            ]
            category_transactions.sort(key=lambda x