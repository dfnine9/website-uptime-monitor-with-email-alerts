```python
"""
Personal Finance Spending Analysis Tool

This module analyzes spending patterns from transaction data, providing:
- Monthly and weekly spending totals by category
- Trend analysis over time periods
- Statistical detection of unusual transaction patterns
- Comprehensive spending insights and recommendations

The tool processes transaction data and generates detailed reports with
statistical insights to help users understand their spending habits.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math
import random


class SpendingAnalyzer:
    def __init__(self):
        self.transactions = []
        self.categories = set()
        
    def load_sample_data(self):
        """Generate sample transaction data for demonstration"""
        categories = ['Groceries', 'Restaurants', 'Gas', 'Shopping', 'Utilities', 
                     'Entertainment', 'Healthcare', 'Transportation', 'Subscriptions']
        
        # Generate 3 months of sample data
        start_date = datetime.now() - timedelta(days=90)
        
        for i in range(200):
            date = start_date + timedelta(days=random.randint(0, 90))
            category = random.choice(categories)
            
            # Category-based amount ranges for realism
            amount_ranges = {
                'Groceries': (20, 150),
                'Restaurants': (15, 80),
                'Gas': (30, 70),
                'Shopping': (25, 200),
                'Utilities': (50, 200),
                'Entertainment': (10, 100),
                'Healthcare': (20, 300),
                'Transportation': (5, 50),
                'Subscriptions': (9.99, 49.99)
            }
            
            min_amt, max_amt = amount_ranges.get(category, (10, 100))
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            # Add some unusual transactions for anomaly detection
            if random.random() < 0.05:  # 5% chance of unusual amount
                amount *= random.uniform(3, 8)
                amount = round(amount, 2)
            
            self.transactions.append({
                'date': date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': amount,
                'description': f"{category} purchase #{i+1}"
            })
            self.categories.add(category)
        
        # Sort by date
        self.transactions.sort(key=lambda x: x['date'])
    
    def calculate_monthly_totals(self):
        """Calculate spending totals by month and category"""
        monthly_totals = defaultdict(lambda: defaultdict(float))
        monthly_grand_totals = defaultdict(float)
        
        for transaction in self.transactions:
            try:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_totals[month_key][category] += amount
                monthly_grand_totals[month_key] += amount
            except (ValueError, KeyError) as e:
                print(f"Error processing transaction: {e}")
                continue
        
        return dict(monthly_totals), dict(monthly_grand_totals)
    
    def calculate_weekly_totals(self):
        """Calculate spending totals by week and category"""
        weekly_totals = defaultdict(lambda: defaultdict(float))
        weekly_grand_totals = defaultdict(float)
        
        for transaction in self.transactions:
            try:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                # Get Monday of the week
                monday = date - timedelta(days=date.weekday())
                week_key = monday.strftime('%Y-%m-%d')
                category = transaction['category']
                amount = transaction['amount']
                
                weekly_totals[week_key][category] += amount
                weekly_grand_totals[week_key] += amount
            except (ValueError, KeyError) as e:
                print(f"Error processing transaction: {e}")
                continue
        
        return dict(weekly_totals), dict(weekly_grand_totals)
    
    def identify_spending_trends(self):
        """Analyze spending trends over time"""
        monthly_totals, monthly_grand_totals = self.calculate_monthly_totals()
        
        trends = {}
        
        # Overall spending trend
        if len(monthly_grand_totals) >= 2:
            months = sorted(monthly_grand_totals.keys())
            amounts = [monthly_grand_totals[month] for month in months]
            
            # Calculate trend direction
            if len(amounts) >= 2:
                recent_avg = statistics.mean(amounts[-2:]) if len(amounts) >= 2 else amounts[-1]
                earlier_avg = statistics.mean(amounts[:-2]) if len(amounts) > 2 else amounts[0]
                
                trend_direction = "increasing" if recent_avg > earlier_avg else "decreasing"
                trend_percentage = ((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0
                
                trends['overall'] = {
                    'direction': trend_direction,
                    'percentage_change': round(trend_percentage, 2),
                    'recent_average': round(recent_avg, 2),
                    'earlier_average': round(earlier_avg, 2)
                }
        
        # Category-specific trends
        category_trends = {}
        for category in self.categories:
            category_monthly = []
            for month in sorted(monthly_totals.keys()):
                amount = monthly_totals[month].get(category, 0)
                category_monthly.append(amount)
            
            if len(category_monthly) >= 2:
                recent_avg = statistics.mean(category_monthly[-2:]) if len(category_monthly) >= 2 else category_monthly[-1]
                earlier_avg = statistics.mean(category_monthly[:-2]) if len(category_monthly) > 2 else category_monthly[0]
                
                if earlier_avg > 0:
                    trend_percentage = ((recent_avg - earlier_avg) / earlier_avg * 100)
                    category_trends[category] = {
                        'direction': "increasing" if recent_avg > earlier_avg else "decreasing",
                        'percentage_change': round(trend_percentage, 2)
                    }
        
        trends['categories'] = category_trends
        return trends
    
    def detect_unusual_patterns(self):
        """Detect unusual transaction patterns using statistical analysis"""
        anomalies = []
        
        # Group transactions by category for analysis
        category_amounts = defaultdict(list)
        for transaction in self.transactions:
            try:
                category_amounts[transaction['category']].append(transaction['amount'])
            except KeyError:
                continue
        
        # Detect outliers using IQR method for each category
        for category, amounts in category_amounts.items():
            if len(amounts) < 4:  # Need at least 4 data points
                continue
                
            try:
                q1 = statistics.quantiles(amounts, n=4)[0]  # 25th percentile
                q3 = statistics.quantiles(amounts, n=4)[2]  # 75th percentile
                iqr = q3 - q1
                
                lower_bound = q1 - (1.5 * iqr)
                upper_bound = q3 + (1.5 * iqr)
                
                # Find transactions outside bounds
                for transaction in self.transactions:
                    if (transaction['category'] == category and 
                        (transaction['amount'] < lower_bound or transaction['amount'] > upper_bound)):
                        
                        anomalies.append({
                            'date': transaction['date'],
                            'category': category,
                            'amount': transaction['amount'],
                            'description': transaction['description'],
                            'type': 'unusually_high' if transaction['amount'] > upper_bound else 'unusually_low',
                            'category_avg': round(statistics.mean(amounts