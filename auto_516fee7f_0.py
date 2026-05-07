```python
#!/usr/bin/env python3
"""
Expense Analysis Script

This module reads CSV expense data, categorizes transactions using keyword matching,
calculates monthly spending totals by category, and identifies budget overages.

The script expects a CSV file named 'expenses.csv' with columns:
- date (YYYY-MM-DD format)
- description (transaction description)
- amount (positive numbers for expenses)
- category (optional, will be auto-categorized if empty)

Budget limits are predefined in the script and can be modified as needed.
"""

import csv
import re
from datetime import datetime
from collections import defaultdict
import sys
import os


def load_expense_data(filename='expenses.csv'):
    """
    Load expense data from CSV file.
    
    Returns:
        list: List of dictionaries containing expense records
    """
    expenses = []
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Parse date and amount
                    date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
                    amount = float(row['amount'])
                    
                    expenses.append({
                        'date': date_obj,
                        'description': row['description'].strip(),
                        'amount': amount,
                        'category': row.get('category', '').strip()
                    })
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid row {row}: {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    return expenses


def categorize_transaction(description, existing_category=''):
    """
    Categorize a transaction based on description keywords.
    
    Args:
        description (str): Transaction description
        existing_category (str): Pre-existing category (if any)
    
    Returns:
        str: Category name
    """
    if existing_category:
        return existing_category
    
    # Category keywords mapping
    categories = {
        'Food': ['grocery', 'restaurant', 'food', 'dining', 'cafe', 'pizza', 'burger', 'coffee', 'lunch', 'dinner'],
        'Transportation': ['gas', 'fuel', 'uber', 'taxi', 'bus', 'train', 'parking', 'metro', 'car', 'vehicle'],
        'Shopping': ['amazon', 'store', 'mall', 'shop', 'retail', 'clothing', 'clothes', 'target', 'walmart'],
        'Utilities': ['electric', 'water', 'gas bill', 'internet', 'phone', 'cable', 'utility', 'power'],
        'Healthcare': ['doctor', 'hospital', 'pharmacy', 'medical', 'dentist', 'health', 'clinic', 'medicine'],
        'Entertainment': ['movie', 'theater', 'concert', 'game', 'netflix', 'spotify', 'entertainment', 'gym'],
        'Housing': ['rent', 'mortgage', 'property', 'home', 'apartment', 'lease', 'hoa'],
        'Insurance': ['insurance', 'premium', 'policy', 'coverage'],
        'Education': ['school', 'tuition', 'book', 'course', 'education', 'learning', 'training'],
        'Banking': ['fee', 'charge', 'atm', 'bank', 'transfer', 'withdrawal']
    }
    
    description_lower = description.lower()
    
    for category, keywords in categories.items():
        if any(keyword in description_lower for keyword in keywords):
            return category
    
    return 'Other'


def calculate_monthly_totals(expenses):
    """
    Calculate monthly spending totals by category.
    
    Args:
        expenses (list): List of expense records
    
    Returns:
        dict: Nested dictionary {year-month: {category: total}}
    """
    monthly_totals = defaultdict(lambda: defaultdict(float))
    
    for expense in expenses:
        month_key = expense['date'].strftime('%Y-%m')
        category = categorize_transaction(expense['description'], expense['category'])
        monthly_totals[month_key][category] += expense['amount']
    
    return dict(monthly_totals)


def check_budget_overages(monthly_totals, budget_limits):
    """
    Identify budget overages by comparing actual spending to limits.
    
    Args:
        monthly_totals (dict): Monthly spending by category
        budget_limits (dict): Budget limits by category
    
    Returns:
        dict: Overages by month and category
    """
    overages = defaultdict(dict)
    
    for month, categories in monthly_totals.items():
        for category, amount in categories.items():
            limit = budget_limits.get(category, float('inf'))
            if amount > limit:
                overages[month][category] = {
                    'actual': amount,
                    'budget': limit,
                    'overage': amount - limit
                }
    
    return dict(overages)


def create_sample_data():
    """Create sample CSV file if it doesn't exist."""
    if not os.path.exists('expenses.csv'):
        sample_data = [
            ['date', 'description', 'amount', 'category'],
            ['2024-01-15', 'Grocery Store Purchase', '85.32', ''],
            ['2024-01-20', 'Gas Station Fill-up', '45.50', ''],
            ['2024-01-25', 'Amazon Purchase', '125.99', ''],
            ['2024-02-01', 'Restaurant Dinner', '67.80', ''],
            ['2024-02-05', 'Electric Bill', '112.45', ''],
            ['2024-02-10', 'Uber Ride', '23.50', ''],
            ['2024-02-15', 'Grocery Shopping', '93.21', ''],
            ['2024-02-20', 'Movie Theater', '35.00', ''],
            ['2024-03-01', 'Coffee Shop', '12.50', ''],
            ['2024-03-05', 'Gas Station', '48.75', ''],
        ]
        
        try:
            with open('expenses.csv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(sample_data)
            print("Created sample expenses.csv file")
        except Exception as e:
            print(f"Error creating sample file: {e}")


def main():
    """Main function to execute the expense analysis."""
    
    # Create sample data if no CSV exists
    create_sample_data()
    
    # Define budget limits (monthly)
    budget_limits = {
        'Food': 400.00,
        'Transportation': 200.00,
        'Shopping': 300.00,
        'Utilities': 150.00,
        'Healthcare': 100.00,
        'Entertainment': 100.00,
        'Housing': 1500.00,
        'Insurance': 200.00,
        'Education': 500.00,
        'Banking': 50.00,
        'Other': 200.00
    }
    
    try:
        # Load and process expenses
        print("Loading expense data...")
        expenses = load_expense_data()
        
        if not expenses:
            print("No valid expense data found.")
            return
        
        print(f"Loaded {len(expenses)} expense records\n")
        
        # Calculate monthly totals
        print("Calculating monthly totals by category...")
        monthly_totals = calculate_monthly_totals(expenses)
        
        # Display monthly spending
        print("\n" + "="*60)
        print("MONTHLY SPENDING BY CATEGORY")
        print("="*60)
        
        for month in sorted(monthly_totals.keys()):
            print(f"\n{month}:")
            print("-" * 30)
            total_month