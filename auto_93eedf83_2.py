```python
"""
Monthly Spending Report Generator

This module processes categorized financial transactions and generates comprehensive
monthly spending reports including category breakdowns, trend analysis, and budget
variance calculations. It handles CSV transaction data and produces formatted
summary reports to help users understand their spending patterns.

Features:
- Category-wise spending summaries
- Month-over-month trend analysis
- Budget vs actual variance calculations
- Statistical insights and recommendations
- Error handling for data validation
- Self-contained with minimal dependencies

Usage: python script.py
"""

import csv
import json
from datetime import datetime, timedelta
from collections import defaultdict, namedtuple
from typing import Dict, List, Tuple, Optional
import io

Transaction = namedtuple('Transaction', ['date', 'amount', 'category', 'description'])

class MonthlyReportGenerator:
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        
    def load_sample_data(self):
        """Generate sample transaction data for demonstration."""
        try:
            # Sample budget data
            self.budgets = {
                'Food': 800.00,
                'Transportation': 400.00,
                'Entertainment': 300.00,
                'Utilities': 200.00,
                'Shopping': 500.00,
                'Healthcare': 150.00,
                'Miscellaneous': 100.00
            }
            
            # Generate sample transactions for last 3 months
            sample_data = [
                # Current month
                ('2024-01-05', 45.50, 'Food', 'Grocery store'),
                ('2024-01-08', 12.99, 'Food', 'Coffee shop'),
                ('2024-01-10', 85.00, 'Transportation', 'Gas station'),
                ('2024-01-12', 25.00, 'Entertainment', 'Movie tickets'),
                ('2024-01-15', 120.00, 'Utilities', 'Electric bill'),
                ('2024-01-18', 78.50, 'Shopping', 'Clothing'),
                ('2024-01-20', 35.00, 'Food', 'Restaurant'),
                ('2024-01-22', 15.00, 'Entertainment', 'Streaming service'),
                ('2024-01-25', 67.25, 'Food', 'Grocery store'),
                ('2024-01-28', 200.00, 'Healthcare', 'Doctor visit'),
                
                # Previous month
                ('2023-12-03', 52.30, 'Food', 'Grocery store'),
                ('2023-12-07', 90.00, 'Transportation', 'Gas station'),
                ('2023-12-12', 45.00, 'Entertainment', 'Concert'),
                ('2023-12-15', 125.00, 'Utilities', 'Gas bill'),
                ('2023-12-18', 95.75, 'Shopping', 'Electronics'),
                ('2023-12-22', 28.50, 'Food', 'Fast food'),
                ('2023-12-28', 75.00, 'Miscellaneous', 'Gifts'),
                
                # Two months ago
                ('2023-11-05', 48.90, 'Food', 'Grocery store'),
                ('2023-11-10', 88.00, 'Transportation', 'Gas station'),
                ('2023-11-15', 110.00, 'Utilities', 'Water bill'),
                ('2023-11-20', 156.25, 'Shopping', 'Home goods'),
                ('2023-11-25', 32.00, 'Food', 'Pizza delivery'),
            ]
            
            for date_str, amount, category, description in sample_data:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                self.transactions.append(Transaction(date, amount, category, description))
                
            print(f"✓ Loaded {len(self.transactions)} sample transactions")
            
        except Exception as e:
            print(f"✗ Error loading sample data: {e}")
            
    def categorize_transactions(self) -> Dict[str, Dict[str, float]]:
        """Categorize transactions by month and category."""
        try:
            monthly_categories = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                month_key = transaction.date.strftime('%Y-%m')
                monthly_categories[month_key][transaction.category] += transaction.amount
                
            return dict(monthly_categories)
            
        except Exception as e:
            print(f"✗ Error categorizing transactions: {e}")
            return {}
    
    def calculate_trends(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate month-over-month trend percentages."""
        try:
            trends = {}
            months = sorted(monthly_data.keys())
            
            if len(months) < 2:
                return trends
                
            current_month = months[-1]
            previous_month = months[-2]
            
            current_data = monthly_data[current_month]
            previous_data = monthly_data[previous_month]
            
            all_categories = set(current_data.keys()) | set(previous_data.keys())
            
            for category in all_categories:
                current_amount = current_data.get(category, 0)
                previous_amount = previous_data.get(category, 0)
                
                if previous_amount == 0:
                    trends[category] = 100.0 if current_amount > 0 else 0.0
                else:
                    trends[category] = ((current_amount - previous_amount) / previous_amount) * 100
                    
            return trends
            
        except Exception as e:
            print(f"✗ Error calculating trends: {e}")
            return {}
    
    def calculate_budget_variance(self, current_spending: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Calculate budget variance for each category."""
        try:
            variance_data = {}
            
            for category, budgeted in self.budgets.items():
                spent = current_spending.get(category, 0)
                variance_amount = spent - budgeted
                variance_percent = (variance_amount / budgeted) * 100 if budgeted > 0 else 0
                
                variance_data[category] = {
                    'budgeted': budgeted,
                    'spent': spent,
                    'variance_amount': variance_amount,
                    'variance_percent': variance_percent,
                    'remaining': budgeted - spent
                }
                
            return variance_data
            
        except Exception as e:
            print(f"✗ Error calculating budget variance: {e}")
            return {}
    
    def generate_insights(self, monthly_data: Dict[str, Dict[str, float]], 
                         trends: Dict[str, float], 
                         variance_data: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate spending insights and recommendations."""
        try:
            insights = []
            months = sorted(monthly_data.keys())
            
            if not months:
                return insights
                
            current_month = months[-1]
            current_spending = monthly_data[current_month]
            
            # Total spending insight
            total_spent = sum(current_spending.values())
            total_budget = sum(self.budgets.values())
            insights.append(f"Total spending this month: ${total_spent:.2f} (Budget: ${total_budget:.2f})")
            
            # Highest spending category
            if current_spending:
                max_category = max(current_spending, key=current_spending.get)
                insights.append(f"Highest spending category: {max_category} (${current_spending[max_category]:.2f})")
            
            # Budget overruns
            overruns = [cat for cat, data in variance_data.items() if data['variance_amount'] > 0]
            if overruns:
                insights.append(f"Categories over budget: {', '.join(overruns)}")