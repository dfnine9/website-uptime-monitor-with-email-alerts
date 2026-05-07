```python
"""
Bank Statement Transaction Categorizer

This script parses CSV bank statements, categorizes transactions using keyword matching,
and calculates total spending by category. It reads transaction data from a CSV file,
applies predefined categorization rules based on transaction descriptions, and outputs
spending summaries by category.

The script expects a CSV file with columns: Date, Description, Amount
Amount should be negative for expenses, positive for income.

Usage: python script.py
"""

import csv
import os
from collections import defaultdict
from datetime import datetime


def load_sample_data():
    """Create a sample CSV file for demonstration if none exists."""
    sample_data = [
        ['Date', 'Description', 'Amount'],
        ['2024-01-15', 'GROCERY STORE PURCHASE', '-85.43'],
        ['2024-01-16', 'SHELL GAS STATION', '-45.20'],
        ['2024-01-17', 'AMAZON.COM ORDER', '-129.99'],
        ['2024-01-18', 'SALARY DEPOSIT', '2500.00'],
        ['2024-01-19', 'NETFLIX SUBSCRIPTION', '-15.99'],
        ['2024-01-20', 'WALMART SUPERCENTER', '-67.84'],
        ['2024-01-21', 'STARBUCKS COFFEE', '-5.85'],
        ['2024-01-22', 'RENT PAYMENT', '-1200.00'],
        ['2024-01-23', 'ELECTRIC COMPANY', '-89.45'],
        ['2024-01-24', 'RESTAURANT DINING', '-42.30']
    ]
    
    with open('sample_bank_statement.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(sample_data)
    
    return 'sample_bank_statement.csv'


def get_category_keywords():
    """Return dictionary of categories and their associated keywords."""
    return {
        'Groceries': ['grocery', 'supermarket', 'walmart', 'target', 'costco', 'kroger'],
        'Gas': ['shell', 'bp', 'exxon', 'chevron', 'gas station', 'fuel'],
        'Restaurants': ['restaurant', 'cafe', 'starbucks', 'mcdonald', 'burger', 'pizza'],
        'Shopping': ['amazon', 'ebay', 'store', 'mall', 'retail'],
        'Entertainment': ['netflix', 'spotify', 'movie', 'theater', 'gaming'],
        'Utilities': ['electric', 'gas company', 'water', 'internet', 'phone'],
        'Housing': ['rent', 'mortgage', 'property'],
        'Income': ['salary', 'deposit', 'payroll', 'income'],
        'Transportation': ['uber', 'lyft', 'taxi', 'metro', 'bus']
    }


def categorize_transaction(description, category_keywords):
    """
    Categorize a transaction based on description keywords.
    
    Args:
        description (str): Transaction description
        category_keywords (dict): Dictionary of categories and keywords
    
    Returns:
        str: Category name or 'Other' if no match found
    """
    description_lower = description.lower()
    
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword.lower() in description_lower:
                return category
    
    return 'Other'


def parse_csv_file(filename):
    """
    Parse CSV bank statement file.
    
    Args:
        filename (str): Path to CSV file
    
    Returns:
        list: List of transaction dictionaries
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If CSV format is invalid
    """
    transactions = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # Try to detect if file has headers
            sample = file.read(1024)
            file.seek(0)
            
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(sample)
            
            reader = csv.reader(file)
            
            if has_header:
                headers = next(reader)
                print(f"Detected headers: {headers}")
            
            for row_num, row in enumerate(reader, start=2 if has_header else 1):
                if len(row) < 3:
                    print(f"Warning: Row {row_num} has insufficient columns: {row}")
                    continue
                
                try:
                    date_str = row[0].strip()
                    description = row[1].strip()
                    amount = float(row[2].strip().replace('$', '').replace(',', ''))
                    
                    # Basic date validation
                    try:
                        datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        try:
                            datetime.strptime(date_str, '%m/%d/%Y')
                        except ValueError:
                            print(f"Warning: Invalid date format in row {row_num}: {date_str}")
                    
                    transactions.append({
                        'date': date_str,
                        'description': description,
                        'amount': amount
                    })
                    
                except (ValueError, IndexError) as e:
                    print(f"Warning: Error parsing row {row_num}: {row} - {e}")
                    continue
    
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file '{filename}' not found.")
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    return transactions


def calculate_spending_by_category(transactions, category_keywords):
    """
    Calculate total spending by category.
    
    Args:
        transactions (list): List of transaction dictionaries
        category_keywords (dict): Dictionary of categories and keywords
    
    Returns:
        dict: Dictionary with category totals
    """
    category_totals = defaultdict(float)
    transaction_count = defaultdict(int)
    
    for transaction in transactions:
        category = categorize_transaction(transaction['description'], category_keywords)
        amount = transaction['amount']
        
        category_totals[category] += amount
        transaction_count[category] += 1
    
    return dict(category_totals), dict(transaction_count)


def print_results(category_totals, transaction_counts, transactions):
    """Print formatted results to stdout."""
    print("\n" + "="*60)
    print("BANK STATEMENT ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\nTotal transactions processed: {len(transactions)}")
    
    # Separate income and expenses
    income_categories = {}
    expense_categories = {}
    
    for category, total in category_totals.items():
        if total > 0:
            income_categories[category] = total
        else:
            expense_categories[category] = abs(total)
    
    # Print expenses
    if expense_categories:
        print(f"\n{'EXPENSES BY CATEGORY':<30}")
        print("-" * 60)
        print(f"{'Category':<20} {'Amount':<12} {'Count':<8} {'Avg':<10}")
        print("-" * 60)
        
        total_expenses = 0
        for category in sorted(expense_categories.keys()):
            amount = expense_categories[category]
            count = transaction_counts[category]
            avg = amount / count if count > 0 else 0
            total_expenses += amount
            print(f"{category:<20} ${amount:<11.2f} {count:<8} ${avg:<9.2f}")
        
        print("-" * 60)
        print(f"{'TOTAL EXPENSES':<20} ${total_expenses:<11.2f}")
    
    # Print income
    if income_categories:
        print(f"\n{'INCOME BY CATEGORY':<30}")
        print("-" * 60)
        print(f"{'Category':<20} {'Amount':<12} {'Count':<8} {'Avg':<10}")
        print("-" *