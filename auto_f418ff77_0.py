```python
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements and categorizes transactions based on
keyword matching against predefined spending categories. It extracts transaction
data (date, description, amount) and assigns each transaction to categories like
groceries, utilities, entertainment, etc.

Usage: python script.py

The script looks for a CSV file named 'bank_statement.csv' in the current directory
with columns: Date, Description, Amount (or similar variations).
"""

import csv
import re
from datetime import datetime
from collections import defaultdict
import os


def load_spending_categories():
    """Load predefined spending categories with associated keywords."""
    return {
        'groceries': ['grocery', 'supermarket', 'food', 'walmart', 'target', 'kroger', 
                     'safeway', 'whole foods', 'trader joe', 'costco', 'sams club'],
        'utilities': ['electric', 'gas', 'water', 'sewer', 'internet', 'cable', 'phone',
                     'att', 'verizon', 'comcast', 'xfinity', 'pge', 'duke energy'],
        'entertainment': ['netflix', 'spotify', 'hulu', 'disney', 'movie', 'theater',
                         'entertainment', 'games', 'steam', 'xbox', 'playstation'],
        'restaurants': ['restaurant', 'mcdonald', 'burger', 'pizza', 'starbucks', 'coffee',
                       'cafe', 'dine', 'eat', 'food truck', 'subway', 'chipotle'],
        'transportation': ['gas station', 'shell', 'chevron', 'exxon', 'bp', 'uber', 'lyft',
                          'taxi', 'bus', 'metro', 'parking', 'toll', 'car wash'],
        'healthcare': ['pharmacy', 'cvs', 'walgreens', 'doctor', 'medical', 'hospital',
                      'dental', 'vision', 'clinic', 'urgent care'],
        'shopping': ['amazon', 'ebay', 'mall', 'department store', 'clothing', 'shoes',
                    'electronics', 'best buy', 'apple store', 'home depot', 'lowes'],
        'banking': ['bank', 'atm', 'fee', 'interest', 'transfer', 'withdrawal', 'deposit',
                   'overdraft', 'maintenance'],
        'insurance': ['insurance', 'premium', 'policy', 'coverage', 'allstate', 'geico',
                     'state farm', 'progressive']
    }


def normalize_header(header):
    """Normalize CSV header names to standard format."""
    header = header.lower().strip()
    if 'date' in header:
        return 'date'
    elif 'description' in header or 'memo' in header or 'detail' in header:
        return 'description'
    elif 'amount' in header or 'debit' in header or 'credit' in header:
        return 'amount'
    return header


def parse_date(date_str):
    """Parse date string into datetime object with multiple format support."""
    date_formats = [
        '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
        '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def parse_amount(amount_str):
    """Parse amount string into float, handling various formats."""
    if not amount_str:
        return 0.0
    
    # Remove currency symbols, commas, and extra spaces
    clean_amount = re.sub(r'[$,\s]', '', str(amount_str))
    
    # Handle parentheses as negative (accounting format)
    if clean_amount.startswith('(') and clean_amount.endswith(')'):
        clean_amount = '-' + clean_amount[1:-1]
    
    try:
        return float(clean_amount)
    except ValueError:
        return 0.0


def categorize_transaction(description, categories):
    """Categorize a transaction based on description keywords."""
    description_lower = description.lower()
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    
    return 'other'


def read_csv_file(filename):
    """Read CSV file and return transactions as list of dictionaries."""
    transactions = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # Detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            delimiter = ',' if sample.count(',') > sample.count(';') else ';'
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            # Normalize headers
            normalized_fieldnames = [normalize_header(field) for field in reader.fieldnames]
            
            for row in reader:
                # Create normalized row
                normalized_row = {}
                for original, normalized in zip(reader.fieldnames, normalized_fieldnames):
                    normalized_row[normalized] = row[original]
                
                transactions.append(normalized_row)
                
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []
    
    return transactions


def process_transactions(transactions, categories):
    """Process transactions and return categorized results."""
    processed = []
    category_totals = defaultdict(float)
    
    for row in transactions:
        try:
            # Extract and validate required fields
            date_str = row.get('date', '')
            description = row.get('description', '')
            amount_str = row.get('amount', '0')
            
            if not date_str or not description:
                continue
            
            # Parse date and amount
            transaction_date = parse_date(date_str)
            amount = parse_amount(amount_str)
            
            # Categorize transaction
            category = categorize_transaction(description, categories)
            
            # Store processed transaction
            transaction = {
                'date': transaction_date.strftime('%Y-%m-%d'),
                'description': description.strip(),
                'amount': amount,
                'category': category
            }
            
            processed.append(transaction)
            category_totals[category] += abs(amount)  # Use absolute value for totals
            
        except Exception as e:
            print(f"Warning: Skipping invalid transaction - {e}")
            continue
    
    return processed, dict(category_totals)


def print_results(transactions, category_totals):
    """Print categorized transactions and summary to stdout."""
    print("=" * 80)
    print("BANK STATEMENT TRANSACTION CATEGORIZER")
    print("=" * 80)
    
    if not transactions:
        print("No valid transactions found.")
        return
    
    # Print transactions by category
    transactions_by_category = defaultdict(list)
    for transaction in transactions:
        transactions_by_category[transaction['category']].append(transaction)
    
    for category in sorted(transactions_by_category.keys()):
        print(f"\n{category.upper()}")
        print("-" * 40)
        
        for transaction in transactions_by_category[category]:
            print(f"{transaction['date']} | ${transaction['amount']:>8.2f} | {transaction['description'][:50]}")
    
    # Print category summary
    print("\n" + "=" * 80)
    print("CATEGORY SUMMARY")
    print("=" * 80)
    
    total_expenses = sum(category_totals.values())
    
    for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (total / total_expenses * 100)