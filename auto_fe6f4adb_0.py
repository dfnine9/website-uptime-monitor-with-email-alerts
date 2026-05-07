```python
#!/usr/bin/env python3
"""
Personal Finance Transaction Categorization and Reporting Tool

This module reads CSV transaction data, categorizes transactions using keyword matching,
and generates monthly spending reports with matplotlib visualizations.

Features:
- Reads CSV files with transaction data (date, description, amount columns)
- Categorizes transactions based on configurable keyword patterns
- Generates monthly spending summaries
- Creates matplotlib charts for visual analysis
- Handles various CSV formats and missing data
- Provides detailed error reporting

Usage:
    python script.py

The script expects a 'transactions.csv' file in the same directory with columns:
- date (YYYY-MM-DD format)
- description (transaction description)
- amount (positive for income, negative for expenses)

If no CSV file exists, sample data will be generated for demonstration.
"""

import csv
import datetime
import os
import sys
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import StringIO

# Transaction categorization keywords
CATEGORY_KEYWORDS = {
    'Food & Dining': ['restaurant', 'food', 'dining', 'pizza', 'coffee', 'grocery', 'supermarket', 'cafe'],
    'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'metro', 'bus', 'train'],
    'Shopping': ['amazon', 'store', 'mall', 'shopping', 'target', 'walmart', 'retail'],
    'Entertainment': ['movie', 'theater', 'netflix', 'spotify', 'gaming', 'concert', 'bar', 'pub'],
    'Utilities': ['electric', 'water', 'internet', 'phone', 'cable', 'utility', 'bill'],
    'Healthcare': ['doctor', 'pharmacy', 'medical', 'hospital', 'dentist', 'clinic'],
    'Income': ['salary', 'paycheck', 'deposit', 'refund', 'transfer', 'payment'],
    'Other': []  # Default category for unmatched transactions
}

class TransactionCategorizer:
    """Handles transaction categorization and analysis."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on keywords in the description."""
        description_lower = description.lower()
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            if category == 'Other':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'
    
    def parse_csv_file(self, filename: str) -> bool:
        """Parse CSV file and load transactions."""
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Handle different possible column names
                        date_col = None
                        desc_col = None
                        amount_col = None
                        
                        for col in row.keys():
                            col_lower = col.lower().strip()
                            if 'date' in col_lower:
                                date_col = col
                            elif 'desc' in col_lower or 'description' in col_lower:
                                desc_col = col
                            elif 'amount' in col_lower or 'value' in col_lower:
                                amount_col = col
                        
                        if not all([date_col, desc_col, amount_col]):
                            print(f"Warning: Could not identify all required columns in row {row_num}")
                            continue
                        
                        # Parse date
                        date_str = row[date_col].strip()
                        try:
                            transaction_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                        except ValueError:
                            try:
                                transaction_date = datetime.datetime.strptime(date_str, '%m/%d/%Y').date()
                            except ValueError:
                                try:
                                    transaction_date = datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
                                except ValueError:
                                    print(f"Warning: Could not parse date '{date_str}' in row {row_num}")
                                    continue
                        
                        # Parse amount
                        amount_str = row[amount_col].strip().replace('$', '').replace(',', '')
                        amount = float(amount_str)
                        
                        description = row[desc_col].strip()
                        category = self.categorize_transaction(description)
                        
                        transaction = {
                            'date': transaction_date,
                            'description': description,
                            'amount': amount,
                            'category': category
                        }
                        
                        self.transactions.append(transaction)
                        
                        # Group by month for reporting
                        month_key = transaction_date.strftime('%Y-%m')
                        self.monthly_data[month_key][category] += amount
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Error processing row {row_num}: {e}")
                        continue
                
                print(f"Successfully loaded {len(self.transactions)} transactions from {filename}")
                return True
                
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
    
    def generate_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        print("Generating sample data for demonstration...")
        
        sample_transactions = [
            ('2024-01-15', 'Grocery Store Purchase', -85.50),
            ('2024-01-16', 'Gas Station Fill-up', -45.20),
            ('2024-01-20', 'Restaurant Dinner', -67.80),
            ('2024-01-25', 'Salary Deposit', 3500.00),
            ('2024-01-28', 'Electric Bill Payment', -120.45),
            ('2024-02-02', 'Amazon Shopping', -156.99),
            ('2024-02-05', 'Coffee Shop', -8.75),
            ('2024-02-10', 'Movie Theater', -28.50),
            ('2024-02-15', 'Grocery Store Purchase', -92.30),
            ('2024-02-20', 'Uber Ride', -15.60),
            ('2024-02-25', 'Salary Deposit', 3500.00),
            ('2024-03-01', 'Internet Bill', -79.99),
            ('2024-03-05', 'Pharmacy', -23.45),
            ('2024-03-10', 'Restaurant Lunch', -34.20),
            ('2024-03-15', 'Grocery Store Purchase', -78.90),
            ('2024-03-20', 'Gas Station Fill-up', -52.30),
            ('2024-03-25', 'Salary Deposit', 3500.00),
            ('2024-03-28', 'Netflix Subscription', -15.99),
        ]
        
        for date_str, description, amount in sample_transactions:
            transaction_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            category = self.categorize_transaction(description)
            
            transaction = {
                'date': transaction_date,
                'description': description,
                'amount': amount,
                'category': category
            }
            
            self.transactions.append(transaction)
            
            month_key = transaction_