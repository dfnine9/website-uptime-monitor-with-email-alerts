```python
"""
Personal Finance Tracker with Interactive Visualizations

This module provides a comprehensive personal finance tracking system with interactive
visualizations and automated monthly report generation. It creates:
- Bar charts for category spending analysis
- Line graphs for monthly spending trends
- Pie charts for expense distribution
- Automated monthly PDF reports

Features:
- Sample data generation for demonstration
- Interactive plotly visualizations
- Matplotlib fallback for static charts
- PDF report generation with charts
- CSV data export/import functionality
- Error handling and logging

Usage: python script.py
"""

import json
import csv
import datetime
import random
from collections import defaultdict
from pathlib import Path
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_pdf import PdfPages
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available, using text-based visualizations")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available, using matplotlib only")


class FinanceTracker:
    """Main class for tracking personal finances and generating visualizations."""
    
    def __init__(self, data_file='expenses.json'):
        self.data_file = data_file
        self.expenses = []
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Health & Fitness', 'Travel', 'Education',
            'Personal Care', 'Home & Garden', 'Insurance', 'Miscellaneous'
        ]
        self.load_data()
    
    def load_data(self):
        """Load expense data from JSON file or generate sample data."""
        try:
            if Path(self.data_file).exists():
                with open(self.data_file, 'r') as f:
                    self.expenses = json.load(f)
                print(f"Loaded {len(self.expenses)} expenses from {self.data_file}")
            else:
                print("No existing data found, generating sample data...")
                self.generate_sample_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            print("Generating sample data instead...")
            self.generate_sample_data()
    
    def save_data(self):
        """Save expense data to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.expenses, f, indent=2)
            print(f"Data saved to {self.data_file}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def generate_sample_data(self):
        """Generate sample expense data for the last 12 months."""
        try:
            self.expenses = []
            current_date = datetime.date.today()
            start_date = current_date.replace(month=1, day=1)
            
            # Generate 200-300 random expenses over the year
            for _ in range(random.randint(200, 300)):
                # Random date in the last 12 months
                days_back = random.randint(0, 365)
                expense_date = current_date - datetime.timedelta(days=days_back)
                
                # Random category and amount
                category = random.choice(self.categories)
                
                # Category-specific amount ranges
                amount_ranges = {
                    'Food & Dining': (5, 150),
                    'Transportation': (10, 200),
                    'Shopping': (20, 500),
                    'Entertainment': (15, 200),
                    'Bills & Utilities': (50, 300),
                    'Health & Fitness': (20, 150),
                    'Travel': (100, 2000),
                    'Education': (50, 500),
                    'Personal Care': (10, 100),
                    'Home & Garden': (25, 400),
                    'Insurance': (100, 500),
                    'Miscellaneous': (5, 200)
                }
                
                min_amt, max_amt = amount_ranges.get(category, (10, 200))
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                # Generate description
                descriptions = {
                    'Food & Dining': ['Restaurant dinner', 'Coffee shop', 'Grocery shopping', 'Lunch out', 'Food delivery'],
                    'Transportation': ['Gas station', 'Uber ride', 'Public transit', 'Parking fee', 'Car maintenance'],
                    'Shopping': ['Online purchase', 'Clothing store', 'Electronics', 'Department store', 'Gift purchase'],
                    'Entertainment': ['Movie tickets', 'Concert', 'Streaming service', 'Games', 'Books'],
                    'Bills & Utilities': ['Electric bill', 'Internet bill', 'Phone bill', 'Water bill', 'Gas bill'],
                }
                
                description = random.choice(descriptions.get(category, ['General expense']))
                
                expense = {
                    'date': expense_date.isoformat(),
                    'amount': amount,
                    'category': category,
                    'description': description
                }
                self.expenses.append(expense)
            
            # Sort by date
            self.expenses.sort(key=lambda x: x['date'])
            self.save_data()
            print(f"Generated {len(self.expenses)} sample expenses")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
    
    def add_expense(self, date, amount, category, description):
        """Add a new expense."""
        try:
            expense = {
                'date': date if isinstance(date, str) else date.isoformat(),
                'amount': float(amount),
                'category': category,
                'description': description
            }
            self.expenses.append(expense)
            self.save_data()
            print(f"Added expense: {expense}")
        except Exception as e:
            print(f"Error adding expense: {e}")
    
    def get_monthly_totals(self):
        """Calculate total expenses by month."""
        try:
            monthly_totals = defaultdict(float)
            for expense in self.expenses:
                date = datetime.datetime.fromisoformat(expense['date']).date()
                month_key = date.strftime('%Y-%m')
                monthly_totals[month_key] += expense['amount']
            
            return dict(sorted(monthly_totals.items()))
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def get_category_totals(self):
        """Calculate total expenses by category."""
        try:
            category_totals = defaultdict(float)
            for expense in self.expenses:
                category_totals[expense['category']] += expense['amount']
            
            return dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True))
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return {}
    
    def create_plotly_charts(self):
        """Create interactive charts using Plotly."""
        if not PLOTLY_AVAILABLE:
            print("Plotly not available for interactive charts")
            return
        
        try:
            # Get data
            monthly_totals = self.get_monthly_totals()
            category_totals = self.get_category_totals()
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Monthly Spending Trends', 'Category Spending', 
                               'Expense Distribution', 'Top 5 Categories'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"type": "pie"}, {"secondary_y": False}]]
            )
            
            # Monthly trends line chart
            months = list(