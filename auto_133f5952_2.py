```python
"""
Spending Analysis Module

This module provides comprehensive spending analysis capabilities including:
- Monthly and quarterly spending summaries by category
- Spending trend identification and analysis
- Category percentage calculations
- Detection of unusual spending patterns and budget overruns

The module processes spending data and generates detailed reports to help
users understand their financial patterns and identify areas for optimization.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import calendar

class SpendingAnalyzer:
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        self.categories = set()
        
    def load_sample_data(self):
        """Load sample transaction data for demonstration"""
        try:
            # Sample transactions for the past 12 months
            sample_transactions = [
                {"date": "2024-01-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-01-16", "amount": 85.30, "category": "groceries", "description": "Whole Foods"},
                {"date": "2024-01-18", "amount": 45.20, "category": "utilities", "description": "Electricity bill"},
                {"date": "2024-01-20", "amount": 150.00, "category": "entertainment", "description": "Concert tickets"},
                {"date": "2024-02-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-02-16", "amount": 92.45, "category": "groceries", "description": "Safeway"},
                {"date": "2024-02-18", "amount": 52.30, "category": "utilities", "description": "Gas bill"},
                {"date": "2024-02-25", "amount": 75.00, "category": "dining", "description": "Restaurant dinner"},
                {"date": "2024-03-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-03-16", "amount": 110.80, "category": "groceries", "description": "Trader Joe's"},
                {"date": "2024-03-20", "amount": 200.00, "category": "shopping", "description": "Clothing"},
                {"date": "2024-03-25", "amount": 65.40, "category": "transportation", "description": "Gas"},
                {"date": "2024-04-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-04-16", "amount": 88.90, "category": "groceries", "description": "Whole Foods"},
                {"date": "2024-04-20", "amount": 300.00, "category": "entertainment", "description": "Concert + dinner"},
                {"date": "2024-05-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-05-16", "amount": 95.60, "category": "groceries", "description": "Safeway"},
                {"date": "2024-05-25", "amount": 120.00, "category": "dining", "description": "Multiple restaurants"},
                {"date": "2024-06-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-06-16", "amount": 105.30, "category": "groceries", "description": "Whole Foods"},
                {"date": "2024-06-20", "amount": 500.00, "category": "shopping", "description": "Electronics"},
                {"date": "2024-07-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-07-16", "amount": 78.20, "category": "groceries", "description": "Local market"},
                {"date": "2024-07-25", "amount": 90.00, "category": "utilities", "description": "Internet + phone"},
                {"date": "2024-08-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-08-16", "amount": 125.40, "category": "groceries", "description": "Costco"},
                {"date": "2024-08-20", "amount": 180.00, "category": "entertainment", "description": "Movie + dinner"},
                {"date": "2024-09-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-09-16", "amount": 98.75, "category": "groceries", "description": "Safeway"},
                {"date": "2024-09-25", "amount": 250.00, "category": "healthcare", "description": "Doctor visit"},
                {"date": "2024-10-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-10-16", "amount": 115.60, "category": "groceries", "description": "Whole Foods"},
                {"date": "2024-10-20", "amount": 80.00, "category": "transportation", "description": "Gas + parking"},
                {"date": "2024-11-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-11-16", "amount": 89.30, "category": "groceries", "description": "Local market"},
                {"date": "2024-11-25", "amount": 400.00, "category": "shopping", "description": "Black Friday shopping"},
                {"date": "2024-12-15", "amount": 1200.50, "category": "rent", "description": "Monthly rent"},
                {"date": "2024-12-16", "amount": 135.80, "category": "groceries", "description": "Holiday shopping"},
                {"date": "2024-12-20", "amount": 350.00, "category": "entertainment", "description": "Holiday party"},
            ]
            
            self.transactions = sample_transactions
            self.categories = set(t["category"] for t in self.transactions)
            
            # Sample budget limits
            self.budgets = {
                "rent": 1300.00,
                "groceries": 120.00,
                "utilities": 100.00,
                "entertainment": 200.00,
                "dining": 150.00,
                "shopping": 300.00,
                "transportation": 100.00,
                "healthcare": 200.00
            }
            
        except Exception as e:
            print(f"Error loading sample data: {str(e)}")
            raise
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            print(f"Error parsing date {date_str}: {str(e)}")
            raise
    
    def get_monthly_summary(self) -> Dict[str, Dict[str, float]]:
        """Generate monthly spending summary by category"""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = self.parse_date(transaction["date"])
                month_key = date_obj.strftime("%Y-%m")
                category = transaction["category"]
                amount = transaction["amount"]
                
                monthly_data[month_key][category] += amount
                monthly_data[month_key]["total"] += amount
            
            return dict(monthly_data)
            
        except Exception as e:
            print(f"Error generating monthly summary: {str(e)}")
            return {}
    
    def get_quarterly_summary(self) -> Dict[str, Dict[str, float]]:
        """Generate quarterly spending summary by category"""
        try:
            quarterly