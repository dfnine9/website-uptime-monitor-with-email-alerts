```python
#!/usr/bin/env python3
"""
Financial Spending Insights Analysis Module

This module processes financial transaction data to provide comprehensive spending insights including:
- Monthly spending totals by category
- Percentage breakdowns of spending by category
- Trend analysis showing month-over-month changes
- Identification of top merchants per spending category

The module generates sample transaction data for demonstration purposes and calculates
various financial metrics to help users understand their spending patterns.

Usage: python script.py
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random


class SpendingInsightsProcessor:
    """Processes financial transaction data to generate spending insights."""
    
    def __init__(self):
        self.transactions = []
        self.categories = ['Food & Dining', 'Shopping', 'Transportation', 'Entertainment', 
                          'Utilities', 'Healthcare', 'Gas', 'Groceries', 'Travel']
        self.merchants = {
            'Food & Dining': ['McDonald\'s', 'Starbucks', 'Pizza Hut', 'Subway', 'Local Diner'],
            'Shopping': ['Amazon', 'Target', 'Walmart', 'Best Buy', 'Macy\'s'],
            'Transportation': ['Uber', 'Lyft', 'Gas Station', 'Parking Meter', 'Bus Fare'],
            'Entertainment': ['Netflix', 'Movie Theater', 'Concert Venue', 'Gaming Store', 'Spotify'],
            'Utilities': ['Electric Co', 'Water Dept', 'Internet Provider', 'Phone Company', 'Gas Utility'],
            'Healthcare': ['CVS Pharmacy', 'Doctor Office', 'Dentist', 'Hospital', 'Health Insurance'],
            'Gas': ['Shell', 'Exxon', 'BP', 'Chevron', 'Mobil'],
            'Groceries': ['Whole Foods', 'Safeway', 'Kroger', 'Costco', 'Local Market'],
            'Travel': ['Hotel Chain', 'Airline', 'Car Rental', 'Travel Agency', 'Airbnb']
        }
    
    def generate_sample_data(self, num_transactions: int = 100) -> List[Dict]:
        """Generate sample transaction data for analysis."""
        transactions = []
        
        try:
            # Generate transactions over the last 6 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            for _ in range(num_transactions):
                # Random date within range
                random_days = random.randint(0, 180)
                transaction_date = start_date + timedelta(days=random_days)
                
                # Random category and merchant
                category = random.choice(self.categories)
                merchant = random.choice(self.merchants[category])
                
                # Random amount based on category
                amount_ranges = {
                    'Food & Dining': (5, 75),
                    'Shopping': (10, 300),
                    'Transportation': (3, 50),
                    'Entertainment': (8, 100),
                    'Utilities': (50, 200),
                    'Healthcare': (20, 500),
                    'Gas': (25, 80),
                    'Groceries': (15, 150),
                    'Travel': (100, 1000)
                }
                
                min_amount, max_amount = amount_ranges.get(category, (10, 100))
                amount = round(random.uniform(min_amount, max_amount), 2)
                
                transaction = {
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'merchant': merchant,
                    'category': category,
                    'amount': amount,
                    'id': f'txn_{len(transactions) + 1:04d}'
                }
                
                transactions.append(transaction)
            
            # Sort by date
            transactions.sort(key=lambda x: x['date'])
            self.transactions = transactions
            return transactions
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
        monthly_totals = defaultdict(lambda: defaultdict(float))
        
        try:
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_totals[month_key][category] += amount
            
            return dict(monthly_totals)
            
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def calculate_percentage_breakdown(self) -> Dict[str, float]:
        """Calculate percentage breakdown of spending by category."""
        category_totals = defaultdict(float)
        total_spending = 0
        
        try:
            for transaction in self.transactions:
                amount = transaction['amount']
                category = transaction['category']
                category_totals[category] += amount
                total_spending += amount
            
            if total_spending == 0:
                return {}
            
            percentages = {}
            for category, amount in category_totals.items():
                percentages[category] = round((amount / total_spending) * 100, 2)
            
            return percentages
            
        except Exception as e:
            print(f"Error calculating percentage breakdown: {e}")
            return {}
    
    def analyze_trends(self) -> Dict[str, Dict[str, Any]]:
        """Analyze spending trends month-over-month."""
        monthly_totals = self.calculate_monthly_totals()
        trends = {}
        
        try:
            months = sorted(monthly_totals.keys())
            
            for category in self.categories:
                category_trends = {
                    'monthly_amounts': [],
                    'growth_rates': [],
                    'average_monthly': 0,
                    'trend_direction': 'stable'
                }
                
                # Get monthly amounts for this category
                monthly_amounts = []
                for month in months:
                    amount = monthly_totals[month].get(category, 0)
                    monthly_amounts.append(amount)
                    category_trends['monthly_amounts'].append({
                        'month': month,
                        'amount': amount
                    })
                
                if monthly_amounts:
                    category_trends['average_monthly'] = round(sum(monthly_amounts) / len(monthly_amounts), 2)
                    
                    # Calculate growth rates
                    for i in range(1, len(monthly_amounts)):
                        if monthly_amounts[i-1] > 0:
                            growth_rate = ((monthly_amounts[i] - monthly_amounts[i-1]) / monthly_amounts[i-1]) * 100
                            category_trends['growth_rates'].append(round(growth_rate, 2))
                    
                    # Determine trend direction
                    if len(category_trends['growth_rates']) > 0:
                        avg_growth = sum(category_trends['growth_rates']) / len(category_trends['growth_rates'])
                        if avg_growth > 5:
                            category_trends['trend_direction'] = 'increasing'
                        elif avg_growth < -5:
                            category_trends['trend_direction'] = 'decreasing'
                
                trends[category] = category_trends
            
            return trends
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
            return {}
    
    def identify_top_merchants(self, top_n: int = 3) -> Dict[str, List[Tuple[str, float]]]:
        """Identify top merchants per category by total spending."""
        category_merchants = defaultdict(lambda: defaultdict(float))
        
        try:
            for transaction in self.transactions:
                category = transaction['category']
                merchant = transaction['merchant']
                amount = transaction['amount']
                
                category_merchants