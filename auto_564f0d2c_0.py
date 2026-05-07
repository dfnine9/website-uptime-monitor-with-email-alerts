```python
"""
Personal Finance Transaction Analyzer

This module reads CSV transaction data, categorizes transactions using rule-based logic,
and generates spending analysis with basic ASCII visualizations. Designed to be 
self-contained with minimal dependencies.

Usage: python script.py

Expected CSV format:
- Headers: date, description, amount
- Date format: YYYY-MM-DD or MM/DD/YYYY
- Amount: negative for expenses, positive for income
"""

import csv
import sys
from datetime import datetime
from collections import defaultdict
import re
import os

class TransactionCategorizer:
    def __init__(self):
        # Category rules - keywords mapped to categories
        self.rules = {
            'food': ['grocery', 'restaurant', 'food', 'cafe', 'starbucks', 'mcdonald', 'pizza', 'dining'],
            'transport': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'metro', 'parking', 'car'],
            'utilities': ['electric', 'water', 'internet', 'phone', 'utility', 'power', 'gas_bill'],
            'entertainment': ['movie', 'netflix', 'spotify', 'game', 'theater', 'concert', 'bar'],
            'shopping': ['amazon', 'target', 'walmart', 'mall', 'store', 'retail', 'clothing'],
            'healthcare': ['doctor', 'hospital', 'pharmacy', 'medical', 'dentist', 'clinic'],
            'income': ['salary', 'paycheck', 'deposit', 'refund', 'transfer_in'],
            'other': []
        }
    
    def categorize(self, description, amount):
        """Categorize transaction based on description and amount."""
        description_lower = description.lower()
        
        # Income check first
        if amount > 0:
            for keyword in self.rules['income']:
                if keyword in description_lower:
                    return 'income'
            return 'income'  # Default for positive amounts
        
        # Expense categorization
        for category, keywords in self.rules.items():
            if category == 'income':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'

class FinanceAnalyzer:
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
        self.categories = defaultdict(float)
        self.monthly_data = defaultdict(float)
    
    def parse_date(self, date_str):
        """Parse date string in various formats."""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def load_csv(self, filename):
        """Load transactions from CSV file."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ',' if sample.count(',') > sample.count(';') else ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row in reader:
                    try:
                        # Handle different possible column names
                        date_col = None
                        desc_col = None
                        amount_col = None
                        
                        for key in row.keys():
                            key_lower = key.lower().strip()
                            if 'date' in key_lower:
                                date_col = key
                            elif 'description' in key_lower or 'desc' in key_lower:
                                desc_col = key
                            elif 'amount' in key_lower or 'value' in key_lower:
                                amount_col = key
                        
                        if not all([date_col, desc_col, amount_col]):
                            print(f"Warning: Could not find required columns in CSV")
                            continue
                        
                        date = self.parse_date(row[date_col])
                        description = row[desc_col].strip()
                        amount = float(row[amount_col].replace('$', '').replace(',', ''))
                        
                        category = self.categorizer.categorize(description, amount)
                        
                        transaction = {
                            'date': date,
                            'description': description,
                            'amount': amount,
                            'category': category
                        }
                        
                        self.transactions.append(transaction)
                        self.categories[category] += abs(amount)
                        self.monthly_data[date.strftime('%Y-%m')] += abs(amount) if amount < 0 else 0
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping invalid row: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            sys.exit(1)
    
    def create_sample_csv(self, filename='sample_transactions.csv'):
        """Create a sample CSV file for testing."""
        sample_data = [
            ['date', 'description', 'amount'],
            ['2024-01-15', 'Grocery Store Purchase', '-85.50'],
            ['2024-01-16', 'Gas Station Fill Up', '-45.00'],
            ['2024-01-17', 'Salary Deposit', '3000.00'],
            ['2024-01-18', 'Restaurant Dinner', '-32.75'],
            ['2024-01-20', 'Electric Utility Bill', '-120.00'],
            ['2024-01-22', 'Amazon Purchase', '-67.99'],
            ['2024-01-25', 'Movie Theater', '-24.50'],
            ['2024-01-28', 'Doctor Visit', '-150.00'],
            ['2024-02-01', 'Coffee Shop', '-12.50'],
            ['2024-02-03', 'Uber Ride', '-18.75']
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(sample_data)
        
        print(f"Sample CSV file '{filename}' created successfully!")
    
    def print_ascii_chart(self, data, title, max_width=50):
        """Print ASCII bar chart."""
        if not data:
            return
        
        print(f"\n{title}")
        print("=" * len(title))
        
        max_value = max(data.values()) if data.values() else 0
        if max_value == 0:
            print("No data to display")
            return
        
        for category, amount in sorted(data.items(), key=lambda x: x[1], reverse=True):
            if amount == 0:
                continue
            
            bar_length = int((amount / max_value) * max_width)
            bar = "█" * bar_length
            
            print(f"{category:<12} │{bar:<{max_width}} ${amount:>8.2f}")
    
    def analyze(self):
        """Perform comprehensive analysis of transactions."""
        if not self.transactions:
            print("No transactions to analyze")
            return
        
        # Basic statistics
        total_income = sum(t['amount'] for t in self.transactions if t['amount'] > 0)
        total_expenses = sum(abs(t['amount']) for t in self.transactions if t['amount'] < 0)
        net_income = total_income - total_expenses
        
        print("PERSONAL FINANCE ANALYSIS")
        print("=" * 40)
        print(f"Total Transactions: {len(self.transactions)}")
        print(f"Date Range: {min(t['date']