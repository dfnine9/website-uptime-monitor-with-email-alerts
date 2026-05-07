```python
#!/usr/bin/env python3
"""
Spending Analysis Module

A comprehensive financial analysis tool that processes transaction data to generate:
- Monthly and weekly spending summaries
- Category-based spending percentages
- Spending trend analysis over time
- Export capabilities to JSON and CSV formats

This module provides insights into spending patterns, helps identify budget categories
that need attention, and tracks financial trends over customizable time periods.

Usage: python script.py
"""

import json
import csv
import sys
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict
from typing import Dict, List, Tuple, Any
import calendar


class SpendingAnalyzer:
    """Main class for analyzing spending patterns and generating reports."""
    
    def __init__(self):
        self.transactions = []
        self.categories = set()
        
    def load_sample_data(self) -> None:
        """Load sample transaction data for demonstration."""
        sample_transactions = [
            {"date": "2024-01-15", "amount": 45.67, "category": "Groceries", "description": "Whole Foods"},
            {"date": "2024-01-16", "amount": 12.50, "category": "Transportation", "description": "Gas Station"},
            {"date": "2024-01-18", "amount": 89.99, "category": "Utilities", "description": "Electric Bill"},
            {"date": "2024-01-20", "amount": 234.56, "category": "Groceries", "description": "Costco"},
            {"date": "2024-01-22", "amount": 67.89, "category": "Entertainment", "description": "Movie Theater"},
            {"date": "2024-01-25", "amount": 156.78, "category": "Dining", "description": "Restaurant"},
            {"date": "2024-01-28", "amount": 78.90, "category": "Transportation", "description": "Uber"},
            {"date": "2024-02-01", "amount": 123.45, "category": "Groceries", "description": "Safeway"},
            {"date": "2024-02-03", "amount": 45.67, "category": "Utilities", "description": "Internet"},
            {"date": "2024-02-05", "amount": 89.12, "category": "Entertainment", "description": "Concert"},
            {"date": "2024-02-08", "amount": 567.89, "category": "Shopping", "description": "Amazon"},
            {"date": "2024-02-10", "amount": 34.56, "category": "Dining", "description": "Coffee Shop"},
            {"date": "2024-02-12", "amount": 78.90, "category": "Transportation", "description": "Gas"},
            {"date": "2024-02-15", "amount": 234.56, "category": "Groceries", "description": "Trader Joes"},
            {"date": "2024-02-18", "amount": 123.45, "category": "Entertainment", "description": "Streaming"},
            {"date": "2024-02-20", "amount": 456.78, "category": "Shopping", "description": "Clothing"},
            {"date": "2024-02-22", "amount": 89.99, "category": "Utilities", "description": "Phone Bill"},
            {"date": "2024-02-25", "amount": 167.89, "category": "Dining", "description": "Date Night"},
            {"date": "2024-03-01", "amount": 345.67, "category": "Groceries", "description": "Monthly Shopping"},
            {"date": "2024-03-03", "amount": 78.90, "category": "Transportation", "description": "Parking"},
            {"date": "2024-03-05", "amount": 234.56, "category": "Entertainment", "description": "Sports Event"},
            {"date": "2024-03-08", "amount": 123.45, "category": "Utilities", "description": "Water Bill"},
            {"date": "2024-03-10", "amount": 567.89, "category": "Shopping", "description": "Electronics"},
            {"date": "2024-03-12", "amount": 45.67, "category": "Dining", "description": "Lunch"},
            {"date": "2024-03-15", "amount": 189.99, "category": "Groceries", "description": "Weekly Shop"},
        ]
        
        self.transactions = sample_transactions
        self.categories = {t["category"] for t in self.transactions}
        
    def parse_date(self, date_str: str) -> datetime:
        """Parse date string into datetime object."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
    
    def get_week_number(self, date: datetime) -> Tuple[int, int]:
        """Get year and week number for a given date."""
        year, week, _ = date.isocalendar()
        return year, week
    
    def generate_monthly_summary(self) -> Dict[str, Any]:
        """Generate monthly spending summaries."""
        try:
            monthly_data = defaultdict(lambda: {"total": 0, "transactions": 0, "categories": defaultdict(float)})
            
            for transaction in self.transactions:
                date = self.parse_date(transaction["date"])
                month_key = f"{date.year}-{date.month:02d}"
                amount = transaction["amount"]
                category = transaction["category"]
                
                monthly_data[month_key]["total"] += amount
                monthly_data[month_key]["transactions"] += 1
                monthly_data[month_key]["categories"][category] += amount
            
            # Sort by month
            sorted_months = OrderedDict(sorted(monthly_data.items()))
            
            return dict(sorted_months)
            
        except Exception as e:
            print(f"Error generating monthly summary: {e}")
            return {}
    
    def generate_weekly_summary(self) -> Dict[str, Any]:
        """Generate weekly spending summaries."""
        try:
            weekly_data = defaultdict(lambda: {"total": 0, "transactions": 0, "categories": defaultdict(float)})
            
            for transaction in self.transactions:
                date = self.parse_date(transaction["date"])
                year, week = self.get_week_number(date)
                week_key = f"{year}-W{week:02d}"
                amount = transaction["amount"]
                category = transaction["category"]
                
                weekly_data[week_key]["total"] += amount
                weekly_data[week_key]["transactions"] += 1
                weekly_data[week_key]["categories"][category] += amount
            
            # Sort by week
            sorted_weeks = OrderedDict(sorted(weekly_data.items()))
            
            return dict(sorted_weeks)
            
        except Exception as e:
            print(f"Error generating weekly summary: {e}")
            return {}
    
    def calculate_category_percentages(self) -> Dict[str, float]:
        """Calculate spending percentage by category."""
        try:
            category_totals = defaultdict(float)
            total_spending = 0
            
            for transaction in self.transactions:
                amount = transaction["amount"]
                category = transaction["category"]
                category_totals[category] += amount
                total_spending += amount
            
            if total_spending == 0:
                return {}
            
            percentages = {
                category: round((amount / total_spending) * 100, 2)
                for category, amount in category_totals.items()
            }
            
            return dict(sorted(percentages.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            print(f"Error calculating category percentages: {e}")
            return {}
    
    def identify_spending_trends(self) -> Dict[str, Any]:
        """Identify spending trends over time."""
        try:
            monthly_summary = self.generate_monthly_summary()
            
            if len(monthly_summary) < 2:
                return {"trend": "insufficient_data", "analysis": "Need