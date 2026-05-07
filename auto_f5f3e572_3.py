```python
"""
Personal Finance Reporting System

A comprehensive financial reporting tool that generates visual spending insights,
budget comparisons, and exportable reports. Features include:
- Visual charts and graphs for spending analysis
- Monthly and weekly financial summaries
- Budget vs actual spending comparisons
- PDF and HTML report export capabilities
- Self-contained implementation with minimal dependencies

Usage: python script.py
"""

import json
import csv
import io
import base64
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import calendar
import random
import math

class FinanceReporter:
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        self.categories = [
            'Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities',
            'Entertainment', 'Health & Medical', 'Travel', 'Education',
            'Investment', 'Income', 'Other'
        ]
        
    def generate_sample_data(self):
        """Generate sample financial data for demonstration"""
        try:
            # Sample budgets
            self.budgets = {
                'Food & Dining': 800,
                'Shopping': 500,
                'Transportation': 300,
                'Bills & Utilities': 1200,
                'Entertainment': 400,
                'Health & Medical': 200,
                'Travel': 600,
                'Education': 300,
                'Other': 200
            }
            
            # Generate sample transactions for last 3 months
            start_date = datetime.now() - timedelta(days=90)
            
            for i in range(150):
                transaction_date = start_date + timedelta(days=random.randint(0, 90))
                category = random.choice(self.categories[:-2])  # Exclude Income and Other mostly
                
                # Realistic amount ranges by category
                amount_ranges = {
                    'Food & Dining': (15, 85),
                    'Shopping': (25, 150),
                    'Transportation': (10, 45),
                    'Bills & Utilities': (50, 300),
                    'Entertainment': (20, 80),
                    'Health & Medical': (30, 200),
                    'Travel': (100, 500),
                    'Education': (50, 250)
                }
                
                amount = random.uniform(*amount_ranges.get(category, (20, 100)))
                
                # Add some income transactions
                if random.random() < 0.1:
                    category = 'Income'
                    amount = random.uniform(2000, 4000)
                
                self.transactions.append({
                    'date': transaction_date,
                    'amount': round(amount, 2),
                    'category': category,
                    'description': f"Sample {category.lower()} transaction",
                    'type': 'income' if category == 'Income' else 'expense'
                })
                
            print("✓ Generated sample financial data")
            
        except Exception as e:
            print(f"✗ Error generating sample data: {e}")
    
    def create_ascii_bar_chart(self, data, title, max_width=50):
        """Create ASCII bar chart"""
        try:
            if not data:
                return f"{title}\nNo data available\n"
            
            max_value = max(data.values()) if data else 1
            chart = f"\n{title}\n" + "=" * len(title) + "\n\n"
            
            for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
                bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
                bar = "█" * bar_length + "░" * (max_width - bar_length)
                chart += f"{label[:20]:20} │{bar}│ ${value:8.2f}\n"
                
            return chart + "\n"
            
        except Exception as e:
            return f"{title}\nError creating chart: {e}\n"
    
    def create_ascii_line_chart(self, data_points, title, height=10):
        """Create ASCII line chart for trends"""
        try:
            if not data_points:
                return f"{title}\nNo data available\n"
            
            values = list(data_points.values())
            labels = list(data_points.keys())
            
            if not values:
                return f"{title}\nNo values to chart\n"
                
            min_val = min(values)
            max_val = max(values)
            
            if max_val == min_val:
                max_val += 1
            
            chart = f"\n{title}\n" + "=" * len(title) + "\n\n"
            
            # Create the chart
            for i in range(height, -1, -1):
                line = f"{max_val - (max_val - min_val) * i / height:8.0f} │"
                
                for value in values:
                    normalized = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
                    if normalized >= i / height:
                        line += "██"
                    else:
                        line += "  "
                line += "│\n"
                chart += line
            
            # Add x-axis
            chart += "         " + "─" * (len(values) * 2) + "\n"
            chart += "         "
            for label in labels:
                chart += f"{str(label)[:2]:2}"
            chart += "\n\n"
            
            return chart
            
        except Exception as e:
            return f"{title}\nError creating line chart: {e}\n"
    
    def generate_spending_insights(self):
        """Generate visual spending insights"""
        try:
            print("\n" + "=" * 60)
            print("FINANCIAL SPENDING INSIGHTS")
            print("=" * 60)
            
            # Category spending analysis
            category_spending = defaultdict(float)
            for transaction in self.transactions:
                if transaction['type'] == 'expense':
                    category_spending[transaction['category']] += transaction['amount']
            
            print(self.create_ascii_bar_chart(
                dict(category_spending), 
                "SPENDING BY CATEGORY"
            ))
            
            # Monthly trend analysis
            monthly_spending = defaultdict(float)
            monthly_income = defaultdict(float)
            
            for transaction in self.transactions:
                month_key = transaction['date'].strftime('%Y-%m')
                if transaction['type'] == 'expense':
                    monthly_spending[month_key] += transaction['amount']
                else:
                    monthly_income[month_key] += transaction['amount']
            
            print(self.create_ascii_line_chart(
                dict(monthly_spending), 
                "MONTHLY SPENDING TREND"
            ))
            
            # Weekly analysis
            weekly_spending = defaultdict(float)
            for transaction in self.transactions:
                if transaction['type'] == 'expense':
                    week = transaction['date'].strftime('%Y-W%U')
                    weekly_spending[week] += transaction['amount']
            
            # Show last 8 weeks
            recent_weeks = dict(list(weekly_spending.items())[-8:])
            print(self.create_ascii_bar_chart(
                recent_weeks, 
                "RECENT WEEKLY SPENDING"
            ))
            
        except Exception as e:
            print(f"✗ Error generating spending insights: {e}")
    
    def generate_budget_comparison(self):
        """Generate budget vs actual comparisons"""
        try:
            print("\n" + "=" * 60)
            print("BUDGET VS ACTUAL COMPARISON")
            print("=" * 60)
            
            # Calculate current month spending
            current_month = datetime.now().strftime('%Y-%m')
            current_spending = defaultdict(float)
            
            for transaction in self.transactions:
                if (transaction['type'] == 'expense' and 
                    transaction['date'].strftime('%Y-%m') == current_month):
                    current_spending[transaction['category']] += transaction['amount']