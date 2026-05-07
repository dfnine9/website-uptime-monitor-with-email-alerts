```python
#!/usr/bin/env python3
"""
Personal Finance Data Analysis Module

This module processes categorized financial transactions to generate comprehensive
spending insights including:
- Monthly spending totals by category
- Trend analysis showing spending patterns over time
- Budget variance calculations comparing actual vs planned spending
- Statistical summaries and recommendations

The module uses sample transaction data and budgets to demonstrate functionality.
All calculations use standard library components for maximum compatibility.
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from statistics import mean, median
from typing import Dict, List, Tuple, Any
import calendar

class TransactionAnalyzer:
    """Analyzes financial transactions to provide spending insights."""
    
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        
    def load_sample_data(self):
        """Load sample transaction and budget data for demonstration."""
        # Sample transactions spanning 6 months
        sample_transactions = [
            {"date": "2024-01-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-01-16", "amount": 85.50, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-01-20", "amount": 45.00, "category": "Dining", "description": "Restaurant dinner"},
            {"date": "2024-01-25", "amount": 120.00, "category": "Utilities", "description": "Electric bill"},
            {"date": "2024-01-30", "amount": 60.00, "category": "Transportation", "description": "Gas station"},
            
            {"date": "2024-02-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-02-18", "amount": 92.30, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-02-22", "amount": 78.00, "category": "Dining", "description": "Date night"},
            {"date": "2024-02-25", "amount": 110.00, "category": "Utilities", "description": "Gas bill"},
            {"date": "2024-02-28", "amount": 55.00, "category": "Transportation", "description": "Gas station"},
            
            {"date": "2024-03-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-03-17", "amount": 98.75, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-03-20", "amount": 125.00, "category": "Dining", "description": "Birthday dinner"},
            {"date": "2024-03-25", "amount": 130.00, "category": "Utilities", "description": "Water bill"},
            {"date": "2024-03-30", "amount": 65.00, "category": "Transportation", "description": "Gas station"},
            {"date": "2024-03-05", "amount": 200.00, "category": "Entertainment", "description": "Concert tickets"},
            
            {"date": "2024-04-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-04-18", "amount": 88.90, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-04-22", "amount": 65.00, "category": "Dining", "description": "Lunch meeting"},
            {"date": "2024-04-25", "amount": 115.00, "category": "Utilities", "description": "Internet bill"},
            {"date": "2024-04-30", "amount": 70.00, "category": "Transportation", "description": "Gas station"},
            {"date": "2024-04-10", "amount": 150.00, "category": "Entertainment", "description": "Theater show"},
            
            {"date": "2024-05-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-05-17", "amount": 105.20, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-05-20", "amount": 89.00, "category": "Dining", "description": "Weekend brunch"},
            {"date": "2024-05-25", "amount": 125.00, "category": "Utilities", "description": "Electric bill"},
            {"date": "2024-05-30", "amount": 58.00, "category": "Transportation", "description": "Gas station"},
            {"date": "2024-05-12", "amount": 180.00, "category": "Entertainment", "description": "Sports event"},
            
            {"date": "2024-06-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-06-18", "amount": 95.40, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-06-22", "amount": 110.00, "category": "Dining", "description": "Anniversary dinner"},
            {"date": "2024-06-25", "amount": 140.00, "category": "Utilities", "description": "Summer electric bill"},
            {"date": "2024-06-30", "amount": 62.00, "category": "Transportation", "description": "Gas station"},
            {"date": "2024-06-08", "amount": 220.00, "category": "Entertainment", "description": "Weekend getaway"},
        ]
        
        # Sample monthly budgets
        sample_budgets = {
            "Rent": 1200.00,
            "Groceries": 400.00,
            "Dining": 200.00,
            "Utilities": 150.00,
            "Transportation": 250.00,
            "Entertainment": 300.00
        }
        
        self.transactions = sample_transactions
        self.budgets = sample_budgets
        
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
        try:
            monthly_totals = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction["date"], "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                category = transaction["category"]
                amount = transaction["amount"]
                
                monthly_totals[month_key][category] += amount
                
            return dict(monthly_totals)
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze spending trends across categories and time periods."""
        try:
            monthly_totals = self.calculate_monthly_totals()
            trends = {}
            
            # Calculate category trends
            category_monthly_data = defaultdict(list)
            
            for month, categories in monthly_totals.items():
                for category, amount in categories.items():
                    category_monthly_data[category].append(amount)
            
            for category, amounts in category_monthly_data.items():
                if len(amounts) > 1:
                    # Calculate trend direction
                    recent_avg = mean(amounts[-2:]) if len(amounts) >= 2 else amounts[-1]
                    earlier_avg = mean(amounts[:-2]) if len(amounts) > 2 else amounts[0]
                    
                    trend_direction = "increasing" if recent_avg > earlier_avg else "decreasing"
                    if abs(recent_avg - earlier_avg) / earlier_avg < 0.05:  # Less than 5% change
                        trend_direction = "stable"
                    
                    trends[category] = {
                        "direction": trend_direction,
                        "average": round(mean(amounts), 2),
                        "median": round(median(amounts