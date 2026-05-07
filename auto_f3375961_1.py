```python
"""
Personal Finance Data Analysis Script

This script processes categorized transaction data to generate comprehensive spending insights.
It analyzes monthly spending by category, identifies trends over time, highlights top merchants,
and calculates budget variance. The script uses sample transaction data and provides
actionable financial insights through statistical analysis.

Features:
- Monthly spending totals by category
- Spending trend analysis with percentage changes
- Top merchant identification
- Budget variance calculations
- Transaction pattern analysis

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from decimal import Decimal, ROUND_HALF_UP
import calendar


class FinancialAnalyzer:
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        
    def load_sample_data(self):
        """Load sample transaction data for demonstration"""
        sample_transactions = [
            {"date": "2024-01-15", "amount": 450.00, "category": "Groceries", "merchant": "Whole Foods", "description": "Weekly shopping"},
            {"date": "2024-01-20", "amount": 85.50, "category": "Dining", "merchant": "Italian Bistro", "description": "Dinner"},
            {"date": "2024-01-25", "amount": 1200.00, "category": "Rent", "merchant": "Property Management", "description": "Monthly rent"},
            {"date": "2024-02-01", "amount": 75.20, "category": "Utilities", "merchant": "Electric Company", "description": "Electricity bill"},
            {"date": "2024-02-10", "amount": 320.00, "category": "Groceries", "merchant": "Safeway", "description": "Monthly groceries"},
            {"date": "2024-02-14", "amount": 150.00, "category": "Dining", "merchant": "Steakhouse", "description": "Valentine's dinner"},
            {"date": "2024-02-28", "amount": 1200.00, "category": "Rent", "merchant": "Property Management", "description": "Monthly rent"},
            {"date": "2024-03-05", "amount": 65.30, "category": "Utilities", "merchant": "Gas Company", "description": "Gas bill"},
            {"date": "2024-03-12", "amount": 380.00, "category": "Groceries", "merchant": "Trader Joes", "description": "Grocery shopping"},
            {"date": "2024-03-18", "amount": 95.75, "category": "Dining", "merchant": "Sushi Place", "description": "Lunch meeting"},
            {"date": "2024-03-25", "amount": 1200.00, "category": "Rent", "merchant": "Property Management", "description": "Monthly rent"},
            {"date": "2024-04-02", "amount": 180.00, "category": "Entertainment", "merchant": "Movie Theater", "description": "Movie night"},
            {"date": "2024-04-08", "amount": 420.00, "category": "Groceries", "merchant": "Costco", "description": "Bulk shopping"},
            {"date": "2024-04-15", "amount": 220.50, "category": "Clothing", "merchant": "Department Store", "description": "Spring clothes"},
            {"date": "2024-04-22", "amount": 125.00, "category": "Dining", "merchant": "Cafe Downtown", "description": "Brunch"},
        ]
        
        sample_budgets = {
            "Groceries": 400.00,
            "Dining": 200.00,
            "Rent": 1200.00,
            "Utilities": 150.00,
            "Entertainment": 250.00,
            "Clothing": 300.00
        }
        
        self.transactions = sample_transactions
        self.budgets = sample_budgets
        
    def parse_date(self, date_string):
        """Parse date string to datetime object"""
        try:
            return datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_string}") from e
    
    def round_currency(self, amount):
        """Round amount to 2 decimal places for currency"""
        return float(Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    def get_monthly_totals(self):
        """Calculate monthly spending totals by category"""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        try:
            for transaction in self.transactions:
                date_obj = self.parse_date(transaction["date"])
                month_key = date_obj.strftime("%Y-%m")
                category = transaction["category"]
                amount = float(transaction["amount"])
                
                monthly_data[month_key][category] += amount
                
            # Convert to regular dict with rounded values
            result = {}
            for month, categories in monthly_data.items():
                result[month] = {cat: self.round_currency(amount) for cat, amount in categories.items()}
                
            return result
        except Exception as e:
            raise RuntimeError(f"Error calculating monthly totals: {e}") from e
    
    def analyze_spending_trends(self):
        """Analyze spending trends over time"""
        monthly_totals = self.get_monthly_totals()
        trends = {}
        
        try:
            # Calculate total spending per month
            monthly_spending = {}
            for month, categories in monthly_totals.items():
                monthly_spending[month] = sum(categories.values())
            
            # Sort months chronologically
            sorted_months = sorted(monthly_spending.keys())
            
            # Calculate month-over-month changes
            for i in range(1, len(sorted_months)):
                current_month = sorted_months[i]
                previous_month = sorted_months[i-1]
                
                current_total = monthly_spending[current_month]
                previous_total = monthly_spending[previous_month]
                
                if previous_total > 0:
                    change_percent = ((current_total - previous_total) / previous_total) * 100
                    trends[current_month] = {
                        "total": self.round_currency(current_total),
                        "change_from_previous": self.round_currency(change_percent)
                    }
                else:
                    trends[current_month] = {
                        "total": self.round_currency(current_total),
                        "change_from_previous": 0.0
                    }
            
            return trends
        except Exception as e:
            raise RuntimeError(f"Error analyzing spending trends: {e}") from e
    
    def get_top_merchants(self, limit=5):
        """Identify top merchants by spending amount"""
        merchant_totals = defaultdict(float)
        merchant_transactions = defaultdict(int)
        
        try:
            for transaction in self.transactions:
                merchant = transaction["merchant"]
                amount = float(transaction["amount"])
                
                merchant_totals[merchant] += amount
                merchant_transactions[merchant] += 1
            
            # Sort by total spending
            top_merchants = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            result = []
            for merchant, total in top_merchants:
                result.append({
                    "merchant": merchant,
                    "total_spent": self.round_currency(total),
                    "transaction_count": merchant_transactions[merchant],
                    "average_transaction": self.round_currency(total / merchant_transactions[merchant])
                })
            
            return result
        except Exception as e:
            raise RuntimeError(f"Error analyzing top merchants: {e}") from e
    
    def calculate_budget_variance(self):
        """Calculate budget variance by category"""
        monthly_totals = self.get_monthly_totals()
        variance_analysis = {}
        
        try:
            # Calculate average monthly spending per category
            category_spending = defaultdict(list)
            for month_data in monthly_totals.values():
                for category, amount in month