```python
"""
Monthly Spending Summary Generator

This module generates comprehensive monthly spending summaries by:
1. Processing categorized transaction data
2. Aggregating totals by category and month
3. Identifying top spending patterns and trends
4. Providing detailed financial insights

The script simulates transaction data and generates realistic spending patterns
across various categories like groceries, utilities, entertainment, etc.
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import calendar


class SpendingAnalyzer:
    """Analyzes spending patterns from transaction data."""
    
    def __init__(self):
        self.transactions = []
        self.categories = [
            'Groceries', 'Utilities', 'Entertainment', 'Gas', 'Restaurants',
            'Shopping', 'Healthcare', 'Insurance', 'Subscriptions', 'Travel',
            'Education', 'Home Improvement', 'Gifts', 'Personal Care'
        ]
    
    def generate_sample_transactions(self, months: int = 12) -> None:
        """Generate sample transaction data for analysis."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            # Generate 500-1500 transactions
            num_transactions = random.randint(500, 1500)
            
            for _ in range(num_transactions):
                # Random date within the range
                random_days = random.randint(0, (end_date - start_date).days)
                transaction_date = start_date + timedelta(days=random_days)
                
                # Category-specific amount ranges
                category = random.choice(self.categories)
                amount_ranges = {
                    'Groceries': (20, 200),
                    'Utilities': (50, 300),
                    'Entertainment': (10, 150),
                    'Gas': (30, 80),
                    'Restaurants': (15, 100),
                    'Shopping': (25, 500),
                    'Healthcare': (50, 400),
                    'Insurance': (100, 500),
                    'Subscriptions': (5, 50),
                    'Travel': (100, 2000),
                    'Education': (50, 800),
                    'Home Improvement': (25, 1000),
                    'Gifts': (20, 300),
                    'Personal Care': (10, 150)
                }
                
                min_amt, max_amt = amount_ranges.get(category, (10, 200))
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                transaction = {
                    'id': f'TXN_{random.randint(100000, 999999)}',
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'category': category,
                    'amount': amount,
                    'description': f'{category} purchase'
                }
                
                self.transactions.append(transaction)
                
        except Exception as e:
            print(f"Error generating sample transactions: {e}")
            raise
    
    def aggregate_by_month_category(self) -> Dict[str, Dict[str, float]]:
        """Aggregate spending by month and category."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_key][category] += amount
            
            return dict(monthly_data)
            
        except Exception as e:
            print(f"Error aggregating data: {e}")
            return {}
    
    def calculate_monthly_totals(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate total spending per month."""
        try:
            monthly_totals = {}
            for month, categories in monthly_data.items():
                monthly_totals[month] = sum(categories.values())
            return monthly_totals
            
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def identify_top_categories(self, monthly_data: Dict[str, Dict[str, float]], top_n: int = 5) -> Dict[str, List[Tuple[str, float]]]:
        """Identify top spending categories for each month."""
        try:
            top_categories = {}
            
            for month, categories in monthly_data.items():
                # Sort categories by spending amount (descending)
                sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
                top_categories[month] = sorted_categories[:top_n]
            
            return top_categories
            
        except Exception as e:
            print(f"Error identifying top categories: {e}")
            return {}
    
    def analyze_spending_trends(self, monthly_totals: Dict[str, float]) -> Dict[str, Any]:
        """Analyze overall spending trends."""
        try:
            if not monthly_totals:
                return {}
            
            sorted_months = sorted(monthly_totals.keys())
            amounts = [monthly_totals[month] for month in sorted_months]
            
            avg_monthly = sum(amounts) / len(amounts)
            min_month = min(monthly_totals, key=monthly_totals.get)
            max_month = max(monthly_totals, key=monthly_totals.get)
            
            # Calculate month-over-month changes
            month_changes = []
            for i in range(1, len(amounts)):
                change = ((amounts[i] - amounts[i-1]) / amounts[i-1]) * 100
                month_changes.append(change)
            
            avg_change = sum(month_changes) / len(month_changes) if month_changes else 0
            
            return {
                'average_monthly_spending': round(avg_monthly, 2),
                'highest_month': min_month,
                'highest_amount': round(monthly_totals[max_month], 2),
                'lowest_month': max_month,
                'lowest_amount': round(monthly_totals[min_month], 2),
                'average_monthly_change': round(avg_change, 2)
            }
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
            return {}
    
    def generate_category_insights(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Generate insights for each spending category."""
        try:
            category_totals = defaultdict(float)
            category_months = defaultdict(list)
            
            for month, categories in monthly_data.items():
                for category, amount in categories.items():
                    category_totals[category] += amount
                    category_months[category].append(amount)
            
            insights = {}
            for category, total in category_totals.items():
                amounts = category_months[category]
                insights[category] = {
                    'total_spending': round(total, 2),
                    'average_monthly': round(total / len(monthly_data), 2),
                    'max_monthly': round(max(amounts), 2),
                    'min_monthly': round(min(amounts), 2)
                }
            
            return insights
            
        except Exception as e:
            print(f"Error generating category insights: {e}")
            return {}


def print_monthly_summary(monthly_data: Dict[str, Dict[str, float]], monthly_totals: Dict[str, float], top_categories: Dict[str, List[Tuple[str, float]]]) -> None:
    """Print detailed monthly spending summary."""
    try:
        print("\n" + "="*80)
        print("MONTHLY SPENDING SUMMARY")
        print("="*80)
        
        sorted_months = sorted(monthly_data.keys())
        
        for month in sorted_months:
            month_obj =