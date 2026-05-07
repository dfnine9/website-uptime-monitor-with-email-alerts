```python
"""
Transaction Analysis and Visualization Script

This module analyzes categorized transaction data and generates comprehensive
spending analysis with visualizations. It processes transaction data to:
- Calculate monthly spending totals by category
- Identify spending trends over time
- Find top merchants by transaction volume
- Generate visualizations (pie charts, bar charts, line graphs)
- Export results as PNG and HTML files

The script creates a sample dataset if no external data is provided and
generates all visualizations using matplotlib and plotly.

Dependencies: matplotlib, plotly, pandas, numpy (beyond standard library)
Usage: python script.py
"""

import json
import csv
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import calendar

# Check for required packages and provide fallback implementations
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Skipping matplotlib visualizations.")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.offline import plot
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    print("Warning: plotly not available. Skipping plotly visualizations.")

try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas/numpy not available. Using basic Python data structures.")


class TransactionAnalyzer:
    """Analyzes transaction data and generates spending insights."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
        self.merchant_totals = defaultdict(float)
        
    def generate_sample_data(self):
        """Generate sample transaction data for demonstration."""
        print("Generating sample transaction data...")
        
        categories = ['Groceries', 'Gas', 'Restaurants', 'Shopping', 'Utilities', 
                     'Entertainment', 'Healthcare', 'Transportation']
        merchants = {
            'Groceries': ['Walmart', 'Target', 'Kroger', 'Whole Foods'],
            'Gas': ['Shell', 'BP', 'Exxon', 'Chevron'],
            'Restaurants': ['McDonalds', 'Subway', 'Pizza Hut', 'Starbucks'],
            'Shopping': ['Amazon', 'Best Buy', 'Macys', 'Home Depot'],
            'Utilities': ['Electric Company', 'Gas Company', 'Water Dept', 'Internet ISP'],
            'Entertainment': ['Netflix', 'Spotify', 'Movie Theater', 'Gaming Store'],
            'Healthcare': ['CVS Pharmacy', 'Doctor Office', 'Dental Clinic', 'Hospital'],
            'Transportation': ['Uber', 'Lyft', 'Bus Pass', 'Parking Meter']
        }
        
        import random
        random.seed(42)  # For reproducible results
        
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 1, 31)
        current_date = start_date
        
        while current_date <= end_date:
            # Generate 5-15 transactions per day
            daily_transactions = random.randint(5, 15)
            
            for _ in range(daily_transactions):
                category = random.choice(categories)
                merchant = random.choice(merchants[category])
                
                # Category-specific amount ranges
                if category == 'Groceries':
                    amount = round(random.uniform(20, 200), 2)
                elif category == 'Gas':
                    amount = round(random.uniform(25, 80), 2)
                elif category == 'Restaurants':
                    amount = round(random.uniform(8, 75), 2)
                elif category == 'Utilities':
                    amount = round(random.uniform(50, 300), 2)
                else:
                    amount = round(random.uniform(10, 150), 2)
                
                transaction = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'merchant': merchant,
                    'category': category,
                    'amount': amount
                }
                self.transactions.append(transaction)
            
            current_date += timedelta(days=1)
        
        print(f"Generated {len(self.transactions)} sample transactions")
    
    def load_transaction_data(self, filepath=None):
        """Load transaction data from CSV or JSON file, or generate sample data."""
        if filepath and os.path.exists(filepath):
            try:
                if filepath.endswith('.csv'):
                    with open(filepath, 'r') as f:
                        reader = csv.DictReader(f)
                        self.transactions = list(reader)
                        # Convert amount to float
                        for t in self.transactions:
                            t['amount'] = float(t['amount'])
                elif filepath.endswith('.json'):
                    with open(filepath, 'r') as f:
                        self.transactions = json.load(f)
                print(f"Loaded {len(self.transactions)} transactions from {filepath}")
            except Exception as e:
                print(f"Error loading data from {filepath}: {e}")
                self.generate_sample_data()
        else:
            self.generate_sample_data()
    
    def analyze_monthly_spending(self):
        """Analyze monthly spending by category."""
        print("Analyzing monthly spending patterns...")
        
        for transaction in self.transactions:
            try:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = f"{date.year}-{date.month:02d}"
                category = transaction['category']
                amount = float(transaction['amount'])
                merchant = transaction['merchant']
                
                self.monthly_data[month_key][category] += amount
                self.category_totals[category] += amount
                self.merchant_totals[merchant] += amount
                
            except (ValueError, KeyError) as e:
                print(f"Error processing transaction: {e}")
                continue
    
    def get_spending_trends(self):
        """Calculate spending trends over time."""
        trends = {}
        months = sorted(self.monthly_data.keys())
        
        for category in self.category_totals.keys():
            category_by_month = []
            for month in months:
                amount = self.monthly_data[month].get(category, 0)
                category_by_month.append(amount)
            trends[category] = category_by_month
        
        return trends, months
    
    def get_top_merchants(self, top_n=10):
        """Get top merchants by total transaction amount."""
        return sorted(self.merchant_totals.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def print_analysis_summary(self):
        """Print analysis summary to stdout."""
        print("\n" + "="*60)
        print("TRANSACTION ANALYSIS SUMMARY")
        print("="*60)
        
        # Overall statistics
        total_transactions = len(self.transactions)
        total_amount = sum(self.category_totals.values())
        avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0
        
        print(f"Total Transactions: {total_transactions:,}")
        print(f"Total Amount: ${total_amount:,.2f}")
        print(f"Average Transaction: ${avg_transaction:.2f}")
        
        # Category breakdown
        print("\nSPENDING BY CATEGORY:")
        print("-" * 40)
        sorted_categories = sorted(self.category_totals.items(), key=lambda x: x[1], reverse=True)
        for category, amount in sorted_categories:
            percentage = (amount / total_amount * 100) if total_amount > 0 else 0
            print(f"{category:<20} ${amount:>10,.2f} ({percentage:>5.1f}%)")
        
        # Top