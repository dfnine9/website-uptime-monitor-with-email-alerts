```python
#!/usr/bin/env python3
"""
Personal Finance Spending Analyzer Module

This module analyzes categorized spending data to generate insights including:
- Monthly and weekly spending patterns
- Top expense categories identification
- Spending trends over time
- Statistical summaries and visualizations

The module processes spending data from various sources and provides
comprehensive analysis for personal financial management.

Dependencies: Standard library only (datetime, json, statistics, collections)
Usage: python script.py
"""

import json
import datetime
from collections import defaultdict, Counter
from statistics import mean, median
import calendar


class SpendingAnalyzer:
    """Analyzes spending data to extract patterns and trends."""
    
    def __init__(self):
        self.transactions = []
        self.categories = set()
        
    def load_sample_data(self):
        """Load sample spending data for demonstration."""
        sample_data = [
            {"date": "2024-01-15", "amount": 45.50, "category": "Groceries", "description": "Supermarket"},
            {"date": "2024-01-20", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-01-22", "amount": 85.30, "category": "Utilities", "description": "Electricity bill"},
            {"date": "2024-02-03", "amount": 32.75, "category": "Dining", "description": "Restaurant"},
            {"date": "2024-02-10", "amount": 67.80, "category": "Groceries", "description": "Grocery store"},
            {"date": "2024-02-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-02-18", "amount": 120.00, "category": "Entertainment", "description": "Movie tickets"},
            {"date": "2024-02-25", "amount": 89.45, "category": "Utilities", "description": "Water bill"},
            {"date": "2024-03-05", "amount": 78.90, "category": "Groceries", "description": "Supermarket"},
            {"date": "2024-03-12", "amount": 45.60, "category": "Dining", "description": "Fast food"},
            {"date": "2024-03-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-03-20", "amount": 234.50, "category": "Shopping", "description": "Clothing"},
            {"date": "2024-03-28", "amount": 95.75, "category": "Utilities", "description": "Internet bill"},
            {"date": "2024-04-02", "amount": 56.30, "category": "Groceries", "description": "Grocery store"},
            {"date": "2024-04-08", "amount": 89.99, "category": "Entertainment", "description": "Concert tickets"},
            {"date": "2024-04-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-04-22", "amount": 145.20, "category": "Dining", "description": "Fine dining"},
            {"date": "2024-04-30", "amount": 73.85, "category": "Utilities", "description": "Gas bill"},
        ]
        
        for transaction in sample_data:
            self.add_transaction(
                transaction["date"],
                transaction["amount"],
                transaction["category"],
                transaction["description"]
            )
    
    def add_transaction(self, date_str, amount, category, description=""):
        """Add a spending transaction to the dataset."""
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            self.transactions.append({
                "date": date_obj,
                "amount": float(amount),
                "category": category,
                "description": description
            })
            self.categories.add(category)
        except (ValueError, TypeError) as e:
            print(f"Error adding transaction: {e}")
    
    def get_monthly_patterns(self):
        """Analyze monthly spending patterns."""
        monthly_spending = defaultdict(float)
        monthly_transactions = defaultdict(int)
        
        for transaction in self.transactions:
            month_key = transaction["date"].strftime("%Y-%m")
            monthly_spending[month_key] += transaction["amount"]
            monthly_transactions[month_key] += 1
        
        return dict(monthly_spending), dict(monthly_transactions)
    
    def get_weekly_patterns(self):
        """Analyze weekly spending patterns."""
        weekly_spending = defaultdict(float)
        day_of_week_spending = defaultdict(list)
        
        for transaction in self.transactions:
            week_key = transaction["date"].strftime("%Y-W%U")
            weekly_spending[week_key] += transaction["amount"]
            
            day_name = transaction["date"].strftime("%A")
            day_of_week_spending[day_name].append(transaction["amount"])
        
        # Calculate average spending by day of week
        avg_by_day = {}
        for day, amounts in day_of_week_spending.items():
            avg_by_day[day] = mean(amounts) if amounts else 0
        
        return dict(weekly_spending), avg_by_day
    
    def get_top_categories(self, top_n=5):
        """Identify top expense categories by total spending."""
        category_spending = defaultdict(float)
        category_count = defaultdict(int)
        
        for transaction in self.transactions:
            category_spending[transaction["category"]] += transaction["amount"]
            category_count[transaction["category"]] += 1
        
        # Sort by total spending
        sorted_categories = sorted(
            category_spending.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_categories[:top_n], dict(category_count)
    
    def calculate_spending_trends(self):
        """Calculate spending trends over time."""
        if len(self.transactions) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort transactions by date
        sorted_transactions = sorted(self.transactions, key=lambda x: x["date"])
        
        # Calculate monthly totals
        monthly_totals = defaultdict(float)
        for transaction in sorted_transactions:
            month_key = transaction["date"].strftime("%Y-%m")
            monthly_totals[month_key] += transaction["amount"]
        
        months = sorted(monthly_totals.keys())
        amounts = [monthly_totals[month] for month in months]
        
        if len(amounts) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate simple trend
        first_half = amounts[:len(amounts)//2]
        second_half = amounts[len(amounts)//2:]
        
        avg_first = mean(first_half)
        avg_second = mean(second_half)
        
        trend_direction = "increasing" if avg_second > avg_first else "decreasing"
        trend_magnitude = abs(avg_second - avg_first)
        trend_percentage = (trend_magnitude / avg_first) * 100 if avg_first > 0 else 0
        
        return {
            "trend": trend_direction,
            "magnitude": trend_magnitude,
            "percentage_change": trend_percentage,
            "first_period_avg": avg_first,
            "second_period_avg": avg_second,
            "monthly_amounts": dict(zip(months, amounts))
        }
    
    def get_statistics_summary(self):
        """Generate statistical summary of spending data."""
        if not self.transactions:
            return {"error": "No transaction data available"}
        
        amounts = [t["amount"] for t in self.transactions]
        
        return {
            "total_transactions": len(self.transactions),
            "total_amount": sum(amounts),
            "average_transaction": mean(amounts),
            "median_transaction": median(amounts),
            "max_transaction": max(amounts),