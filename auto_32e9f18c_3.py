```python
#!/usr/bin/env python3
"""
Monthly Expense Report Generator

This module generates comprehensive monthly expense reports with visualizations,
budget vs actual comparisons, and actionable insights for spending optimization.

Features:
- Monthly expense tracking and categorization
- Budget vs actual spending analysis
- ASCII-based visualizations (charts and graphs)
- Spending trend analysis
- Actionable optimization recommendations
- Export capabilities for reports

The module uses only standard library components plus httpx and anthropic
for enhanced data processing capabilities when available.
"""

import json
import csv
import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import statistics
import io
import sys

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ExpenseReportGenerator:
    """Main class for generating monthly expense reports with visualizations."""
    
    def __init__(self):
        self.expenses = []
        self.budgets = {}
        self.categories = [
            "Food & Dining", "Transportation", "Housing", "Utilities",
            "Healthcare", "Entertainment", "Shopping", "Travel",
            "Education", "Insurance", "Miscellaneous"
        ]
    
    def add_expense(self, date: str, category: str, amount: float, description: str = ""):
        """Add an expense entry."""
        try:
            expense = {
                "date": datetime.datetime.strptime(date, "%Y-%m-%d"),
                "category": category,
                "amount": amount,
                "description": description
            }
            self.expenses.append(expense)
        except ValueError as e:
            print(f"Error adding expense: Invalid date format. Use YYYY-MM-DD. {e}")
        except Exception as e:
            print(f"Error adding expense: {e}")
    
    def set_budget(self, category: str, amount: float):
        """Set budget for a category."""
        try:
            self.budgets[category] = amount
        except Exception as e:
            print(f"Error setting budget: {e}")
    
    def load_sample_data(self):
        """Load sample expense and budget data for demonstration."""
        try:
            # Sample expenses for current month
            current_month = datetime.datetime.now().replace(day=1)
            sample_expenses = [
                ("2024-01-05", "Food & Dining", 45.50, "Grocery shopping"),
                ("2024-01-07", "Transportation", 25.00, "Gas"),
                ("2024-01-10", "Entertainment", 15.99, "Movie tickets"),
                ("2024-01-12", "Food & Dining", 32.75, "Restaurant dinner"),
                ("2024-01-15", "Utilities", 120.00, "Electric bill"),
                ("2024-01-18", "Shopping", 89.99, "Clothing"),
                ("2024-01-20", "Healthcare", 35.00, "Pharmacy"),
                ("2024-01-22", "Food & Dining", 67.25, "Groceries"),
                ("2024-01-25", "Transportation", 30.00, "Public transit"),
                ("2024-01-28", "Entertainment", 42.50, "Concert tickets"),
            ]
            
            for expense in sample_expenses:
                self.add_expense(*expense)
            
            # Sample budgets
            sample_budgets = {
                "Food & Dining": 300.00,
                "Transportation": 150.00,
                "Entertainment": 100.00,
                "Utilities": 200.00,
                "Shopping": 150.00,
                "Healthcare": 100.00,
            }
            
            for category, budget in sample_budgets.items():
                self.set_budget(category, budget)
                
        except Exception as e:
            print(f"Error loading sample data: {e}")
    
    def filter_expenses_by_month(self, year: int, month: int) -> List[Dict]:
        """Filter expenses for a specific month and year."""
        try:
            return [
                expense for expense in self.expenses
                if expense["date"].year == year and expense["date"].month == month
            ]
        except Exception as e:
            print(f"Error filtering expenses: {e}")
            return []
    
    def calculate_category_totals(self, expenses: List[Dict]) -> Dict[str, float]:
        """Calculate total spending by category."""
        try:
            totals = defaultdict(float)
            for expense in expenses:
                totals[expense["category"]] += expense["amount"]
            return dict(totals)
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return {}
    
    def create_ascii_bar_chart(self, data: Dict[str, float], title: str, max_width: int = 50) -> str:
        """Create an ASCII bar chart from data."""
        try:
            if not data:
                return f"{title}\nNo data available.\n"
            
            max_value = max(data.values())
            chart_lines = [f"\n{title}", "=" * len(title)]
            
            for category, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
                bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
                bar = "█" * bar_length
                chart_lines.append(f"{category:<20} {bar} ${value:,.2f}")
            
            return "\n".join(chart_lines) + "\n"
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            return f"{title}\nError generating chart.\n"
    
    def create_budget_comparison_chart(self, actual: Dict[str, float], budgets: Dict[str, float]) -> str:
        """Create budget vs actual comparison chart."""
        try:
            chart_lines = ["\nBudget vs Actual Comparison", "=" * 28]
            
            for category in set(list(actual.keys()) + list(budgets.keys())):
                actual_amount = actual.get(category, 0)
                budget_amount = budgets.get(category, 0)
                
                if budget_amount == 0:
                    percentage = 0 if actual_amount == 0 else 100
                    status = "No Budget Set"
                else:
                    percentage = (actual_amount / budget_amount) * 100
                    if percentage <= 80:
                        status = "✓ Under Budget"
                    elif percentage <= 100:
                        status = "⚠ Near Budget"
                    else:
                        status = "✗ Over Budget"
                
                chart_lines.append(
                    f"{category:<20} ${actual_amount:>7.2f} / ${budget_amount:>7.2f} "
                    f"({percentage:>6.1f}%) {status}"
                )
            
            return "\n".join(chart_lines) + "\n"
        except Exception as e:
            print(f"Error creating comparison chart: {e}")
            return "\nBudget vs Actual Comparison\nError generating chart.\n"
    
    def create_trend_analysis(self, expenses: List[Dict]) -> str:
        """Analyze spending trends within the month."""
        try:
            if not expenses:
                return "\nTrend Analysis\nNo expenses to analyze.\n"
            
            # Group by week
            weekly_totals = defaultdict(float)
            for expense in expenses:
                week = expense["date"].isocalendar()[1]
                weekly_totals[week] += expense["amount"]
            
            # Calculate daily average
            daily_amounts = defaultdict(float)
            daily_counts = defaultdict(int)
            
            for expense in expenses:
                day = expense["date"].day
                daily_amounts[day] += expense["amount"]
                daily_counts[day] += 1
            
            total_days_with_expenses = len(daily_amounts)
            avg_daily_spending = sum(daily_amounts