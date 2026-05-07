```python
#!/usr/bin/env python3
"""
Personal Finance Data Analysis Module

This module analyzes personal spending patterns by:
- Calculating monthly spending totals and averages by category
- Identifying spending trends across time periods
- Comparing current month performance against historical data
- Detecting anomalies and unusual spending spikes using statistical methods

The module generates sample transaction data for demonstration purposes
and provides comprehensive analysis including trend detection, anomaly
identification, and comparative insights.

Usage: python script.py
"""

import json
import statistics
import random
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import math

class SpendingAnalyzer:
    """Analyzes spending patterns and detects financial anomalies."""
    
    def __init__(self):
        self.transactions = []
        self.categories = [
            'Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities',
            'Entertainment', 'Healthcare', 'Travel', 'Education', 'Groceries'
        ]
    
    def generate_sample_data(self, months: int = 6) -> List[Dict[str, Any]]:
        """Generate realistic sample transaction data."""
        transactions = []
        base_date = datetime.now() - timedelta(days=months * 30)
        
        # Base spending patterns by category
        category_patterns = {
            'Food & Dining': (200, 400),
            'Shopping': (100, 300),
            'Transportation': (150, 250),
            'Bills & Utilities': (300, 400),
            'Entertainment': (50, 200),
            'Healthcare': (0, 150),
            'Travel': (0, 500),
            'Education': (0, 200),
            'Groceries': (250, 350)
        }
        
        for month in range(months):
            month_date = base_date + timedelta(days=month * 30)
            
            # Add some seasonal variation
            seasonal_multiplier = 1.0
            if month_date.month in [11, 12]:  # Holiday spending
                seasonal_multiplier = 1.3
            elif month_date.month in [6, 7, 8]:  # Summer travel
                seasonal_multiplier = 1.1
            
            for category, (min_spend, max_spend) in category_patterns.items():
                # Generate 5-15 transactions per category per month
                num_transactions = random.randint(5, 15)
                monthly_budget = random.uniform(min_spend, max_spend) * seasonal_multiplier
                
                for _ in range(num_transactions):
                    amount = random.uniform(10, monthly_budget / num_transactions * 2)
                    
                    # Add some anomalies (5% chance of unusually high spending)
                    if random.random() < 0.05:
                        amount *= random.uniform(2.0, 4.0)
                    
                    transaction_date = month_date + timedelta(days=random.randint(0, 29))
                    
                    transactions.append({
                        'date': transaction_date.strftime('%Y-%m-%d'),
                        'amount': round(amount, 2),
                        'category': category,
                        'description': f'{category} expense'
                    })
        
        return sorted(transactions, key=lambda x: x['date'])
    
    def load_data(self, transactions: List[Dict[str, Any]]):
        """Load transaction data into the analyzer."""
        self.transactions = transactions
    
    def get_monthly_spending(self) -> Dict[str, Dict[str, float]]:
        """Calculate total spending by month and category."""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        for transaction in self.transactions:
            try:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                category = transaction['category']
                amount = float(transaction['amount'])
                
                monthly_data[month_key][category] += amount
                monthly_data[month_key]['TOTAL'] += amount
            except (ValueError, KeyError) as e:
                print(f"Error processing transaction: {e}")
                continue
        
        return dict(monthly_data)
    
    def calculate_trends(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
        """Identify spending trends across categories."""
        trends = {}
        
        for category in self.categories + ['TOTAL']:
            category_data = []
            months = sorted(monthly_data.keys())
            
            for month in months:
                amount = monthly_data[month].get(category, 0)
                category_data.append(amount)
            
            if len(category_data) < 2:
                continue
            
            # Calculate trend using simple linear regression
            n = len(category_data)
            x_values = list(range(n))
            
            try:
                # Calculate slope (trend)
                sum_x = sum(x_values)
                sum_y = sum(category_data)
                sum_xy = sum(x * y for x, y in zip(x_values, category_data))
                sum_x2 = sum(x * x for x in x_values)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                
                # Calculate average and percentage change
                avg_spending = statistics.mean(category_data)
                first_month = category_data[0] if category_data[0] > 0 else 1
                last_month = category_data[-1] if category_data[-1] > 0 else 1
                pct_change = ((last_month - first_month) / first_month) * 100
                
                trend_direction = 'Increasing' if slope > 5 else 'Decreasing' if slope < -5 else 'Stable'
                
                trends[category] = {
                    'average_monthly': round(avg_spending, 2),
                    'trend_slope': round(slope, 2),
                    'trend_direction': trend_direction,
                    'percent_change': round(pct_change, 1),
                    'monthly_values': category_data
                }
            except (ZeroDivisionError, statistics.StatisticsError):
                trends[category] = {
                    'average_monthly': 0,
                    'trend_slope': 0,
                    'trend_direction': 'No Data',
                    'percent_change': 0,
                    'monthly_values': category_data
                }
        
        return trends
    
    def compare_current_month(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Compare current month spending to historical averages."""
        if not monthly_data:
            return {}
        
        months = sorted(monthly_data.keys())
        current_month = months[-1]
        historical_months = months[:-1]
        
        if not historical_months:
            return {'error': 'Insufficient historical data for comparison'}
        
        comparison = {'current_month': current_month, 'comparisons': {}}
        
        for category in self.categories + ['TOTAL']:
            current_spending = monthly_data[current_month].get(category, 0)
            
            historical_amounts = []
            for month in historical_months:
                amount = monthly_data[month].get(category, 0)
                historical_amounts.append(amount)
            
            if historical_amounts:
                try:
                    historical_avg = statistics.mean(historical_amounts)
                    historical_median = statistics.median(historical_amounts)
                    
                    if historical_avg > 0:
                        pct_vs_avg = ((current_spending - historical_avg) / historical_avg) * 100
                    else:
                        pct_vs_avg = 0
                    
                    comparison['comparisons'][category] = {
                        'current': round(current_spending, 2),
                        'historical_average': round(historical_avg, 2),