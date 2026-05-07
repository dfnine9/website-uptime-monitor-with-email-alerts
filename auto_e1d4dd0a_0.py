```python
"""
Bank Transaction Categorizer

This script reads CSV bank transaction data and automatically categorizes expenses
using rule-based keyword matching and regex patterns. It processes common expense
categories like groceries, utilities, entertainment, restaurants, gas, and shopping.

The script outputs a new CSV file with categorized transactions and prints
summary statistics to stdout.

Usage: python script.py

Requirements:
- Input CSV file named 'transactions.csv' in the same directory
- CSV must have columns: 'date', 'description', 'amount'
- Amount should be negative for expenses, positive for income
"""

import pandas as pd
import re
import sys
from pathlib import Path


def load_transaction_data(file_path='transactions.csv'):
    """Load transaction data from CSV file with error handling."""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['date', 'description', 'amount']
        
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"CSV must contain columns: {required_columns}")
        
        # Convert amount to numeric, handling any string formatting
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df.dropna(subset=['amount'])
        
        print(f"Successfully loaded {len(df)} transactions from {file_path}")
        return df
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)


def categorize_transactions(df):
    """Categorize transactions using rule-based keyword matching and regex patterns."""
    
    # Define category rules with keywords and regex patterns
    category_rules = {
        'groceries': {
            'keywords': ['grocery', 'supermarket', 'kroger', 'walmart', 'safeway', 'whole foods', 
                        'trader joe', 'costco', 'publix', 'market', 'food lion', 'giant'],
            'patterns': [r'\b(fresh|organic|produce)\b', r'\bfood\s+(mart|store|shop)\b']
        },
        'utilities': {
            'keywords': ['electric', 'gas company', 'water', 'internet', 'cable', 'phone', 
                        'verizon', 'at&t', 'comcast', 'utility', 'energy', 'power'],
            'patterns': [r'\b(elec|gas|water|sewer|internet|cable)\s+(co|company|corp)\b']
        },
        'entertainment': {
            'keywords': ['netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'movie', 
                        'theater', 'cinema', 'concert', 'tickets', 'gaming', 'music'],
            'patterns': [r'\b(streaming|subscription)\b', r'\bmovie\s+(theater|theatre)\b']
        },
        'restaurants': {
            'keywords': ['restaurant', 'cafe', 'coffee', 'starbucks', 'dunkin', 'mcdonalds', 
                        'burger', 'pizza', 'subway', 'chipotle', 'dining', 'bar', 'pub'],
            'patterns': [r'\b(fast\s+food|take\s+out|delivery)\b', r'\b(bar|grill|bistro)\b']
        },
        'gas': {
            'keywords': ['shell', 'exxon', 'bp', 'chevron', 'mobil', 'gas station', 'fuel', 
                        'petro', 'sunoco', 'speedway', 'wawa'],
            'patterns': [r'\bgas\s+(station|stop)\b', r'\b(fuel|petrol)\b']
        },
        'shopping': {
            'keywords': ['amazon', 'target', 'best buy', 'home depot', 'lowes', 'macy', 
                        'nordstrom', 'clothing', 'retail', 'store', 'shop'],
            'patterns': [r'\b(department|retail)\s+store\b', r'\bonline\s+purchase\b']
        },
        'healthcare': {
            'keywords': ['doctor', 'hospital', 'pharmacy', 'medical', 'dental', 'vision', 
                        'cvs', 'walgreens', 'clinic', 'health'],
            'patterns': [r'\b(medical|dental|vision)\s+(center|clinic)\b']
        },
        'transportation': {
            'keywords': ['uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'parking', 
                        'toll', 'car wash', 'auto repair'],
            'patterns': [r'\b(public\s+transport|ride\s+share)\b', r'\bcar\s+(service|repair)\b']
        }
    }
    
    def get_category(description):
        """Determine category for a single transaction description."""
        if pd.isna(description):
            return 'other'
        
        description_lower = str(description).lower()
        
        for category, rules in category_rules.items():
            # Check keywords
            for keyword in rules['keywords']:
                if keyword.lower() in description_lower:
                    return category
            
            # Check regex patterns
            for pattern in rules['patterns']:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        return 'other'
    
    # Apply categorization
    df['category'] = df['description'].apply(get_category)
    
    # Only categorize expenses (negative amounts)
    df.loc[df['amount'] >= 0, 'category'] = 'income'
    
    return df


def generate_summary_stats(df):
    """Generate and print summary statistics."""
    print("\n" + "="*50)
    print("TRANSACTION CATEGORIZATION SUMMARY")
    print("="*50)
    
    # Overall stats
    total_transactions = len(df)
    total_expenses = len(df[df['amount'] < 0])
    total_income = len(df[df['amount'] >= 0])
    
    print(f"Total Transactions: {total_transactions}")
    print(f"Expenses: {total_expenses}")
    print(f"Income Entries: {total_income}")
    
    # Category breakdown (expenses only)
    expense_df = df[df['amount'] < 0].copy()
    if len(expense_df) > 0:
        print(f"\nExpense Categories:")
        category_stats = expense_df.groupby('category').agg({
            'amount': ['count', 'sum']
        }).round(2)
        category_stats.columns = ['Count', 'Total Amount']
        category_stats = category_stats.sort_values('Total Amount')
        
        for category, row in category_stats.iterrows():
            print(f"  {category.title()}: {row['Count']} transactions, ${abs(row['Total Amount']):,.2f}")
    
    # Monthly breakdown if date column exists
    try:
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        monthly_expenses = df[df['amount'] < 0].groupby('month')['amount'].sum().abs()
        
        if len(monthly_expenses) > 0:
            print(f"\nMonthly Expense Totals:")
            for month, amount in monthly_expenses.items():
                print(f"  {month}: ${amount:,.2f}")
                
    except Exception as e:
        print(f"Note: Could not generate monthly breakdown - {e}")


def save_categorized_data(df, output_file='categorized_transactions.csv'):
    """Save categorized transactions to new CSV file."""
    try:
        df.to_csv(output_file, index=False)
        print(f"\nCategorized transactions saved to: {output_file}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False


def