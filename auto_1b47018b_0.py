```python
#!/usr/bin/env python3
"""
Financial Transaction Analyzer

This module reads CSV transaction data, categorizes expenses automatically,
and generates summary statistics with visualizations using matplotlib.

Features:
- Automatic expense categorization based on description keywords
- Statistical analysis of spending patterns
- Visual charts showing spending by category and over time
- Error handling for file operations and data processing

Usage:
    python script.py

The script expects a CSV file named 'transactions.csv' with columns:
- date: Transaction date (YYYY-MM-DD format)
- description: Transaction description
- amount: Transaction amount (negative for expenses, positive for income)

If no CSV file is found, sample data will be generated for demonstration.
"""

import csv
import sys
import os
from datetime import datetime, timedelta
import random
from collections import defaultdict
import re

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Charts will be skipped.")

def create_sample_data():
    """Generate sample transaction data for demonstration purposes."""
    sample_transactions = [
        ("2024-01-15", "GROCERY STORE PURCHASE", -85.43),
        ("2024-01-16", "COFFEE SHOP", -4.50),
        ("2024-01-17", "SALARY DEPOSIT", 3500.00),
        ("2024-01-18", "GAS STATION", -45.20),
        ("2024-01-19", "RESTAURANT DINNER", -67.89),
        ("2024-01-20", "GROCERY STORE", -92.15),
        ("2024-01-22", "AMAZON PURCHASE", -34.99),
        ("2024-01-23", "ELECTRIC BILL", -120.45),
        ("2024-01-24", "COFFEE SHOP", -5.25),
        ("2024-01-25", "PHARMACY", -23.67),
        ("2024-01-26", "MOVIE THEATER", -28.50),
        ("2024-01-27", "GROCERY STORE", -78.32),
        ("2024-01-28", "GAS STATION", -52.10),
        ("2024-01-29", "RESTAURANT LUNCH", -15.75),
        ("2024-01-30", "INTERNET BILL", -79.99),
        ("2024-02-01", "SALARY DEPOSIT", 3500.00),
        ("2024-02-02", "RENT PAYMENT", -1200.00),
        ("2024-02-03", "GROCERY STORE", -95.67),
        ("2024-02-04", "COFFEE SHOP", -4.75),
        ("2024-02-05", "CAR INSURANCE", -156.30)
    ]
    
    with open('transactions.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['date', 'description', 'amount'])
        writer.writerows(sample_transactions)
    
    print("Sample transactions.csv created for demonstration.")

def categorize_transaction(description, amount):
    """
    Categorize transactions based on description keywords and amount.
    
    Args:
        description (str): Transaction description
        amount (float): Transaction amount
    
    Returns:
        str: Category name
    """
    description = description.upper()
    
    if amount > 0:
        if 'SALARY' in description or 'DEPOSIT' in description:
            return 'Income'
        else:
            return 'Other Income'
    
    # Expense categorization
    categories = {
        'Food & Dining': ['GROCERY', 'RESTAURANT', 'COFFEE', 'FOOD', 'DINING', 'CAFE'],
        'Transportation': ['GAS', 'FUEL', 'UBER', 'LYFT', 'TAXI', 'PARKING'],
        'Utilities': ['ELECTRIC', 'WATER', 'GAS BILL', 'INTERNET', 'PHONE'],
        'Healthcare': ['PHARMACY', 'DOCTOR', 'HOSPITAL', 'MEDICAL'],
        'Entertainment': ['MOVIE', 'THEATER', 'NETFLIX', 'SPOTIFY', 'GAME'],
        'Shopping': ['AMAZON', 'TARGET', 'WALMART', 'MALL', 'STORE'],
        'Housing': ['RENT', 'MORTGAGE', 'PROPERTY'],
        'Insurance': ['INSURANCE']
    }
    
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    
    return 'Other Expenses'

def read_transactions(filename):
    """
    Read transaction data from CSV file.
    
    Args:
        filename (str): Path to CSV file
    
    Returns:
        list: List of transaction dictionaries
    """
    transactions = []
    
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    transaction = {
                        'date': datetime.strptime(row['date'], '%Y-%m-%d'),
                        'description': row['description'],
                        'amount': float(row['amount']),
                        'category': categorize_transaction(row['description'], float(row['amount']))
                    }
                    transactions.append(transaction)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid row: {row} - Error: {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"Error: {filename} not found. Creating sample data...")
        create_sample_data()
        return read_transactions(filename)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    return transactions

def calculate_statistics(transactions):
    """
    Calculate summary statistics for transactions.
    
    Args:
        transactions (list): List of transaction dictionaries
    
    Returns:
        dict: Summary statistics
    """
    if not transactions:
        return {}
    
    # Separate income and expenses
    income_transactions = [t for t in transactions if t['amount'] > 0]
    expense_transactions = [t for t in transactions if t['amount'] < 0]
    
    # Category totals
    category_totals = defaultdict(float)
    for transaction in transactions:
        category_totals[transaction['category']] += transaction['amount']
    
    # Calculate statistics
    total_income = sum(t['amount'] for t in income_transactions)
    total_expenses = abs(sum(t['amount'] for t in expense_transactions))
    net_amount = total_income - total_expenses
    
    # Date range
    dates = [t['date'] for t in transactions]
    date_range = (min(dates), max(dates))
    
    # Average transaction amounts
    avg_income = total_income / len(income_transactions) if income_transactions else 0
    avg_expense = total_expenses / len(expense_transactions) if expense_transactions else 0
    
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_amount': net_amount,
        'transaction_count': len(transactions),
        'income_count': len(income_transactions),
        'expense_count': len(expense_transactions),
        'avg_income': avg_income,
        'avg_expense': avg_expense,
        'date_range': date_range,
        'category_totals': dict(category_totals)
    }

def print_summary_report(stats, transactions):
    """Print formatted summary report to stdout."""
    print("\n" + "="*60)
    print("FINANCIAL TRANSACTION ANALYSIS REPORT")
    print("="*60)
    
    if not stats:
        print("No transaction data available.")
        return
    
    # Overview
    print(f"\nOVERVIEW:")
    print(f"Date Range: {stats['date_range'][0].strftime('%Y-%m-%d')} to {stats['date_range'][1