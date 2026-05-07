```python
"""
Transaction Categorization Script

This script reads CSV transaction files and categorizes transactions based on
predefined keyword dictionaries. It processes transaction data including date,
description, amount, and account information, then assigns categories like
groceries, entertainment, utilities, transportation, and dining based on
description keywords.

The script is self-contained and requires only standard library modules.
It reads CSV files, processes transactions, and outputs categorized results
to stdout with summary statistics.

Usage: python script.py
"""

import csv
import re
import os
from datetime import datetime
from collections import defaultdict


class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'grocery', 'supermarket', 'food mart', 'market', 'costco',
                'target', 'sam\'s club', 'aldi', 'publix', 'wegmans'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'movie', 'theater',
                'cinema', 'game', 'entertainment', 'subscription', 'music',
                'streaming', 'hulu', 'disney+', 'youtube', 'twitch'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'internet', 'phone', 'utility',
                'power', 'energy', 'telecom', 'cable', 'heating', 'cooling',
                'sewer', 'trash', 'waste', 'verizon', 'att', 'comcast'
            ],
            'transportation': [
                'gas station', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train',
                'metro', 'parking', 'toll', 'car wash', 'auto', 'vehicle',
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'transport'
            ],
            'dining': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald',
                'burger', 'pizza', 'taco', 'food delivery', 'doordash',
                'grubhub', 'uber eats', 'dining', 'bar', 'pub', 'kitchen'
            ]
        }
        self.transactions = []
        
    def categorize_transaction(self, description):
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def parse_amount(self, amount_str):
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[\$,\s]', '', str(amount_str))
            # Handle negative amounts in parentheses
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def parse_date(self, date_str):
        """Parse date string to datetime object."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', 
            '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        
        # If no format matches, return None
        return None
    
    def read_csv_file(self, filename):
        """Read and parse CSV transaction file."""
        transactions = []
        
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Common column name variations
                date_columns = ['date', 'transaction_date', 'Date', 'Transaction Date']
                desc_columns = ['description', 'desc', 'Description', 'transaction_description']
                amount_columns = ['amount', 'Amount', 'transaction_amount', 'value']
                account_columns = ['account', 'Account', 'account_number', 'Account Number']
                
                for row in reader:
                    transaction = {}
                    
                    # Find date column
                    for col in date_columns:
                        if col in row and row[col]:
                            transaction['date'] = self.parse_date(row[col])
                            break
                    
                    # Find description column
                    for col in desc_columns:
                        if col in row and row[col]:
                            transaction['description'] = row[col].strip()
                            break
                    
                    # Find amount column
                    for col in amount_columns:
                        if col in row and row[col]:
                            transaction['amount'] = self.parse_amount(row[col])
                            break
                    
                    # Find account column
                    for col in account_columns:
                        if col in row and row[col]:
                            transaction['account'] = row[col].strip()
                            break
                    
                    # Only add transaction if we have minimum required fields
                    if 'description' in transaction and 'amount' in transaction:
                        if 'date' not in transaction:
                            transaction['date'] = None
                        if 'account' not in transaction:
                            transaction['account'] = 'Unknown'
                        
                        transaction['category'] = self.categorize_transaction(
                            transaction['description']
                        )
                        transactions.append(transaction)
                
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []
        except Exception as e:
            print(f"Error reading CSV file: {str(e)}")
            return []
        
        return transactions
    
    def process_transactions(self, filenames):
        """Process multiple transaction files."""
        all_transactions = []
        
        for filename in filenames:
            print(f"Processing file: {filename}")
            transactions = self.read_csv_file(filename)
            all_transactions.extend(transactions)
            print(f"Loaded {len(transactions)} transactions from {filename}")
        
        self.transactions = all_transactions
        return all_transactions
    
    def generate_report(self):
        """Generate categorization report."""
        if not self.transactions:
            print("No transactions to report.")
            return
        
        print("\n" + "="*60)
        print("TRANSACTION CATEGORIZATION REPORT")
        print("="*60)
        
        # Category summary
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        
        for transaction in self.transactions:
            category = transaction['category']
            amount = abs(transaction['amount'])  # Use absolute value for totals
            category_totals[category] += amount
            category_counts[category] += 1
        
        print(f"\nTotal transactions processed: {len(self.transactions)}")
        print(f"Total amount: ${sum(abs(t['amount']) for t in self.transactions):,.2f}")
        
        print("\nCategory Summary:")
        print("-" * 50)
        print(f"{'Category':<15} {'Count':<8} {'Amount':<12} {'Percentage':<10}")
        print("-" * 50)
        
        total_amount = sum(category_totals.values())
        for category in sorted(category_totals.keys()):
            count = category_counts[category]
            amount = category_totals[category]
            percentage = (amount / total_amount * 100) if total_amount > 0