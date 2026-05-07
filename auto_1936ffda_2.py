```python
#!/usr/bin/env python3
"""
Financial Transaction Analysis Module

This module processes categorized financial transactions to generate comprehensive
spending insights including:
- Monthly and weekly spending patterns
- Top expense categories analysis
- Budget variance calculations
- Trend analysis over configurable time periods

The module is designed to be self-contained and provides actionable financial
intelligence through statistical analysis of transaction data.

Usage: python script.py

Dependencies: Standard library only (datetime, json, statistics, collections)
"""

import json
import datetime
from collections import defaultdict, Counter
from statistics import mean, median
from typing import Dict, List, Tuple, Any
import sys


class TransactionAnalyzer:
    """Analyzes financial transactions to generate spending insights."""
    
    def __init__(self):
        self.transactions = []
        self.budget_limits = {}
        
    def load_sample_data(self):
        """Load sample transaction data for demonstration."""
        try:
            # Generate sample data spanning 6 months
            sample_transactions = [
                {"date": "2024-01-15", "amount": -45.67, "category": "Groceries", "description": "Supermarket"},
                {"date": "2024-01-18", "amount": -1200.00, "category": "Rent", "description": "Monthly rent"},
                {"date": "2024-01-20", "amount": -35.50, "category": "Dining", "description": "Restaurant"},
                {"date": "2024-01-22", "amount": -89.99, "category": "Utilities", "description": "Electric bill"},
                {"date": "2024-02-01", "amount": -52.30, "category": "Groceries", "description": "Grocery store"},
                {"date": "2024-02-15", "amount": -1200.00, "category": "Rent", "description": "Monthly rent"},
                {"date": "2024-02-18", "amount": -67.89, "category": "Dining", "description": "Restaurant"},
                {"date": "2024-02-25", "amount": -95.50, "category": "Utilities", "description": "Gas bill"},
                {"date": "2024-03-10", "amount": -78.45, "category": "Groceries", "description": "Supermarket"},
                {"date": "2024-03-15", "amount": -1200.00, "category": "Rent", "description": "Monthly rent"},
                {"date": "2024-03-20", "amount": -125.00, "category": "Entertainment", "description": "Concert tickets"},
                {"date": "2024-03-28", "amount": -42.75, "category": "Dining", "description": "Fast food"},
                {"date": "2024-04-05", "amount": -56.78, "category": "Groceries", "description": "Grocery shopping"},
                {"date": "2024-04-15", "amount": -1200.00, "category": "Rent", "description": "Monthly rent"},
                {"date": "2024-04-22", "amount": -89.50, "category": "Entertainment", "description": "Movie night"},
                {"date": "2024-05-12", "amount": -65.33, "category": "Groceries", "description": "Weekly groceries"},
                {"date": "2024-05-15", "amount": -1200.00, "category": "Rent", "description": "Monthly rent"},
                {"date": "2024-05-25", "amount": -156.75, "category": "Shopping", "description": "Clothing"},
                {"date": "2024-06-08", "amount": -43.21, "category": "Groceries", "description": "Quick shopping"},
                {"date": "2024-06-15", "amount": -1200.00, "category": "Rent", "description": "Monthly rent"},
            ]
            
            # Sample budget limits
            sample_budget = {
                "Groceries": 200.00,
                "Dining": 150.00,
                "Entertainment": 100.00,
                "Shopping": 200.00,
                "Utilities": 150.00,
                "Rent": 1200.00
            }
            
            self.transactions = sample_transactions
            self.budget_limits = sample_budget
            return True
            
        except Exception as e:
            print(f"Error loading sample data: {str(e)}")
            return False
    
    def parse_date(self, date_str: str) -> datetime.date:
        """Parse date string into datetime.date object."""
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
    
    def get_monthly_spending(self) -> Dict[str, float]:
        """Calculate total spending by month."""
        try:
            monthly_spending = defaultdict(float)
            
            for transaction in self.transactions:
                if transaction['amount'] < 0:  # Only expenses
                    date = self.parse_date(transaction['date'])
                    month_key = f"{date.year}-{date.month:02d}"
                    monthly_spending[month_key] += abs(transaction['amount'])
            
            return dict(monthly_spending)
        except Exception as e:
            print(f"Error calculating monthly spending: {str(e)}")
            return {}
    
    def get_weekly_spending(self) -> Dict[str, float]:
        """Calculate total spending by week."""
        try:
            weekly_spending = defaultdict(float)
            
            for transaction in self.transactions:
                if transaction['amount'] < 0:  # Only expenses
                    date = self.parse_date(transaction['date'])
                    # Get Monday of the week
                    monday = date - datetime.timedelta(days=date.weekday())
                    week_key = monday.strftime("%Y-W%U")
                    weekly_spending[week_key] += abs(transaction['amount'])
            
            return dict(weekly_spending)
        except Exception as e:
            print(f"Error calculating weekly spending: {str(e)}")
            return {}
    
    def get_category_spending(self) -> Dict[str, float]:
        """Calculate total spending by category."""
        try:
            category_spending = defaultdict(float)
            
            for transaction in self.transactions:
                if transaction['amount'] < 0:  # Only expenses
                    category = transaction['category']
                    category_spending[category] += abs(transaction['amount'])
            
            return dict(category_spending)
        except Exception as e:
            print(f"Error calculating category spending: {str(e)}")
            return {}
    
    def get_top_expense_categories(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Get top expense categories by total amount."""
        try:
            category_spending = self.get_category_spending()
            sorted_categories = sorted(category_spending.items(), 
                                     key=lambda x: x[1], reverse=True)
            return sorted_categories[:limit]
        except Exception as e:
            print(f"Error getting top expense categories: {str(e)}")
            return []
    
    def calculate_budget_variance(self) -> Dict[str, Dict[str, float]]:
        """Calculate budget variance by category."""
        try:
            category_spending = self.get_category_spending()
            variance_analysis = {}
            
            for category, budget_limit in self.budget_limits.items():
                actual_spending = category_spending.get(category, 0)
                variance = actual_spending - budget_limit
                variance_percent = (variance / budget_limit * 100) if budget_limit > 0 else 0
                
                variance_analysis[category] = {
                    'budget': budget_limit,
                    'actual': actual_spending,
                    'variance': variance,
                    'variance_percent': variance_percent,
                    'status': 'over' if variance > 0 else 'under'
                }
            
            return variance_analysis
        except Exception as e:
            print(f"Error calculating budget variance: {str(e)}")
            return {}