```python
#!/usr/bin/env python3
"""
CSV Expense Categorization Script

This module parses CSV files containing expense data and automatically categorizes
expenses based on configurable regex patterns. It uses pandas for data manipulation
and provides a flexible rule-based categorization system.

Features:
- Parse CSV files with expense data (amount, description, date)
- Apply regex-based categorization rules
- Generate summary statistics by category
- Export categorized results to new CSV file
- Built-in error handling and validation

Usage:
    python script.py

The script expects a CSV file with columns: date, description, amount
If no file exists, it creates sample data for demonstration.
"""

import csv
import re
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import os


class ExpenseCategorizer:
    """Expense categorization engine using regex patterns."""
    
    def __init__(self):
        self.rules = {
            'Food & Dining': [
                r'restaurant|cafe|coffee|pizza|burger|food|dining|starbucks|mcdonalds',
                r'grocery|supermarket|walmart|costco|whole foods|trader joe',
                r'delivery|uber eats|doordash|grubhub'
            ],
            'Transportation': [
                r'gas|fuel|chevron|shell|bp|exxon',
                r'uber|lyft|taxi|metro|bus|train|parking',
                r'car|auto|mechanic|repair|insurance|dmv'
            ],
            'Shopping': [
                r'amazon|ebay|target|best buy|home depot|lowes',
                r'clothing|apparel|shoes|nike|adidas',
                r'electronics|apple|microsoft|google store'
            ],
            'Utilities': [
                r'electric|electricity|gas bill|water|sewer|trash',
                r'internet|cable|phone|verizon|at&t|comcast',
                r'utility|pge|edison'
            ],
            'Healthcare': [
                r'doctor|hospital|pharmacy|cvs|walgreens|rite aid',
                r'medical|dental|vision|health|insurance',
                r'prescription|medicine|clinic'
            ],
            'Entertainment': [
                r'movie|cinema|theater|netflix|spotify|hulu',
                r'game|gaming|steam|playstation|xbox',
                r'concert|show|event|ticket'
            ],
            'Home': [
                r'rent|mortgage|property|real estate',
                r'furniture|ikea|bed bath|home goods',
                r'cleaning|maintenance|repair|contractor'
            ]
        }
    
    def categorize_expense(self, description: str) -> str:
        """Categorize an expense based on its description."""
        description_lower = description.lower()
        
        for category, patterns in self.rules.items():
            for pattern in patterns:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        return 'Other'
    
    def add_rule(self, category: str, pattern: str):
        """Add a new categorization rule."""
        if category not in self.rules:
            self.rules[category] = []
        self.rules[category].append(pattern)


def create_sample_data(filename: str = 'expenses.csv'):
    """Create sample expense data if no CSV file exists."""
    sample_data = [
        ['date', 'description', 'amount'],
        ['2024-01-15', 'Starbucks Coffee', '5.67'],
        ['2024-01-16', 'Shell Gas Station', '45.23'],
        ['2024-01-17', 'Amazon Purchase', '89.99'],
        ['2024-01-18', 'Grocery Store - Safeway', '127.45'],
        ['2024-01-19', 'Netflix Subscription', '15.99'],
        ['2024-01-20', 'CVS Pharmacy', '23.45'],
        ['2024-01-21', 'Uber Ride', '18.75'],
        ['2024-01-22', 'Electric Bill - PGE', '156.78'],
        ['2024-01-23', 'Restaurant - Olive Garden', '67.34'],
        ['2024-01-24', 'Target Shopping', '43.21'],
        ['2024-01-25', 'Movie Theater Tickets', '28.50'],
        ['2024-01-26', 'Rent Payment', '1200.00'],
        ['2024-01-27', 'Doctor Visit Copay', '35.00'],
        ['2024-01-28', 'Home Depot Supplies', '78.90'],
        ['2024-01-29', 'Spotify Premium', '9.99']
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(sample_data)
        print(f"Created sample data file: {filename}")
    except Exception as e:
        print(f"Error creating sample data: {e}")
        sys.exit(1)


def parse_csv_file(filename: str) -> List[Dict[str, Any]]:
    """Parse CSV file and return list of expense records."""
    expenses = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Validate required fields
                    if not all(key in row for key in ['date', 'description', 'amount']):
                        print(f"Warning: Row {row_num} missing required columns")
                        continue
                    
                    # Parse and validate amount
                    amount_str = row['amount'].replace('$', '').replace(',', '')
                    amount = float(amount_str)
                    
                    # Parse date
                    date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
                    
                    expenses.append({
                        'date': date_obj,
                        'description': row['description'].strip(),
                        'amount': amount,
                        'original_row': row_num
                    })
                    
                except ValueError as e:
                    print(f"Warning: Invalid data in row {row_num}: {e}")
                    continue
                except Exception as e:
                    print(f"Warning: Error processing row {row_num}: {e}")
                    continue
    
    except FileNotFoundError:
        print(f"File {filename} not found. Creating sample data...")
        create_sample_data(filename)
        return parse_csv_file(filename)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    return expenses


def categorize_expenses(expenses: List[Dict[str, Any]], categorizer: ExpenseCategorizer) -> List[Dict[str, Any]]:
    """Apply categorization rules to expenses."""
    categorized_expenses = []
    
    for expense in expenses:
        category = categorizer.categorize_expense(expense['description'])
        categorized_expense = expense.copy()
        categorized_expense['category'] = category
        categorized_expenses.append(categorized_expense)
    
    return categorized_expenses


def generate_summary(categorized_expenses: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Generate summary statistics by category."""
    summary = defaultdict(lambda: {'count': 0, 'total': 0.0, 'transactions': []})
    
    for expense in categorized_expenses:
        category = expense['category']
        summary[category]['count'] += 1
        summary[category]['total'] += expense['amount']
        summary[category]['transactions'].append({
            'date': expense['date'].strftime('%Y-%m-%d'),
            'description': expense['description'],
            'amount': expense['amount']
        })
    
    return dict(summary)


def export_results(categorized_expenses: List[Dict[str, Any]], output_filename: str =