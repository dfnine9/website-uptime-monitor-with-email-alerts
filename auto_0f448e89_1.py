```python
#!/usr/bin/env python3
"""
Expense Analysis Module

A comprehensive expense tracking and analysis tool that processes spending data
to identify patterns, calculate category totals, analyze monthly trends, and
generate visualizations for expense breakdowns and trend analysis.

Features:
- Category-wise expense totals and percentages
- Monthly spending trend analysis
- Data visualization with matplotlib fallback to text charts
- Statistical insights including average, median, and variance
- Comprehensive error handling and data validation

Usage:
    python script.py

Dependencies:
    - Standard library modules only (csv, datetime, collections, statistics)
    - matplotlib (optional, falls back to text-based charts if unavailable)
"""

import csv
import datetime
import json
import os
import statistics
import sys
from collections import defaultdict, Counter
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Dict, List, Tuple, Optional, Any

# Try to import matplotlib, fall back to text-based visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("matplotlib not available, using text-based visualizations")


class ExpenseAnalyzer:
    """
    A comprehensive expense analysis tool for tracking spending patterns,
    calculating category totals, and generating trend visualizations.
    """
    
    def __init__(self):
        self.expenses = []
        self.categories = defaultdict(Decimal)
        self.monthly_totals = defaultdict(Decimal)
        self.monthly_categories = defaultdict(lambda: defaultdict(Decimal))
    
    def add_expense(self, date: str, category: str, amount: float, description: str = ""):
        """Add a single expense record with validation."""
        try:
            # Validate and parse date
            parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            
            # Validate amount
            if amount <= 0:
                raise ValueError(f"Amount must be positive, got: {amount}")
            
            amount_decimal = Decimal(str(amount))
            
            expense = {
                'date': parsed_date,
                'category': category.strip().title(),
                'amount': amount_decimal,
                'description': description.strip()
            }
            
            self.expenses.append(expense)
            self._update_aggregations(expense)
            
        except ValueError as e:
            print(f"Error adding expense: {e}")
            return False
        except InvalidOperation as e:
            print(f"Invalid amount format: {e}")
            return False
        
        return True
    
    def _update_aggregations(self, expense: Dict):
        """Update internal aggregation dictionaries."""
        category = expense['category']
        amount = expense['amount']
        date = expense['date']
        month_key = f"{date.year}-{date.month:02d}"
        
        self.categories[category] += amount
        self.monthly_totals[month_key] += amount
        self.monthly_categories[month_key][category] += amount
    
    def load_from_csv(self, csv_data: str) -> bool:
        """Load expenses from CSV data string."""
        try:
            csv_reader = csv.DictReader(StringIO(csv_data))
            
            for row in csv_reader:
                date = row.get('date', '').strip()
                category = row.get('category', '').strip()
                amount_str = row.get('amount', '').strip()
                description = row.get('description', '').strip()
                
                if not all([date, category, amount_str]):
                    print(f"Skipping incomplete row: {row}")
                    continue
                
                try:
                    amount = float(amount_str)
                except ValueError:
                    print(f"Invalid amount '{amount_str}' in row: {row}")
                    continue
                
                self.add_expense(date, category, amount, description)
            
            return True
            
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            return False
    
    def generate_sample_data(self):
        """Generate sample expense data for demonstration."""
        sample_expenses = [
            ("2024-01-15", "Food", 45.67, "Grocery shopping"),
            ("2024-01-20", "Transportation", 25.00, "Gas"),
            ("2024-01-25", "Food", 12.50, "Coffee"),
            ("2024-02-05", "Food", 67.89, "Dinner out"),
            ("2024-02-10", "Entertainment", 15.00, "Movie ticket"),
            ("2024-02-15", "Transportation", 30.00, "Gas"),
            ("2024-02-20", "Utilities", 120.00, "Electric bill"),
            ("2024-03-01", "Food", 89.45, "Grocery shopping"),
            ("2024-03-05", "Healthcare", 50.00, "Doctor visit"),
            ("2024-03-10", "Food", 23.75, "Lunch"),
            ("2024-03-15", "Entertainment", 40.00, "Concert ticket"),
            ("2024-03-20", "Transportation", 28.50, "Gas"),
            ("2024-03-25", "Utilities", 85.00, "Internet bill"),
            ("2024-04-02", "Food", 56.78, "Grocery shopping"),
            ("2024-04-08", "Transportation", 32.00, "Gas"),
            ("2024-04-12", "Entertainment", 25.00, "Streaming service"),
            ("2024-04-18", "Food", 18.90, "Fast food"),
            ("2024-04-22", "Healthcare", 75.00, "Pharmacy"),
        ]
        
        for date, category, amount, description in sample_expenses:
            self.add_expense(date, category, amount, description)
    
    def calculate_category_totals(self) -> Dict[str, Dict[str, Any]]:
        """Calculate total spending by category with percentages."""
        if not self.expenses:
            return {}
        
        total_spending = sum(self.categories.values())
        
        category_analysis = {}
        for category, amount in sorted(self.categories.items(), 
                                     key=lambda x: x[1], reverse=True):
            percentage = (amount / total_spending) * 100
            
            category_analysis[category] = {
                'total': float(amount),
                'percentage': float(percentage),
                'count': sum(1 for expense in self.expenses 
                           if expense['category'] == category)
            }
        
        return category_analysis
    
    def analyze_monthly_trends(self) -> Dict[str, Any]:
        """Analyze monthly spending trends and patterns."""
        if not self.monthly_totals:
            return {}
        
        # Sort months chronologically
        sorted_months = sorted(self.monthly_totals.keys())
        monthly_amounts = [float(self.monthly_totals[month]) for month in sorted_months]
        
        # Calculate statistics
        trend_analysis = {
            'months': sorted_months,
            'amounts': monthly_amounts,
            'total_months': len(sorted_months),
            'average_monthly': statistics.mean(monthly_amounts),
            'median_monthly': statistics.median(monthly_amounts),
            'min_month': {'month': sorted_months[monthly_amounts.index(min(monthly_amounts))], 
                         'amount': min(monthly_amounts)},
            'max_month': {'month': sorted_months[monthly_amounts.index(max(monthly_amounts))], 
                         'amount': max(monthly_amounts)},
        }
        
        if len(monthly_amounts) > 1:
            trend_analysis['variance'] = statistics.variance(monthly_amounts)
            trend_analysis['std_deviation'] = statistics.stdev(monthly_amounts)
            
            # Calculate month-over-month growth
            growth_rates = []
            for i in range(1, len(monthly_amounts)):
                prev_amount = monthly_amounts[i-1]
                curr_amount = monthly_amounts[i]
                if prev_amount > 0:
                    growth_