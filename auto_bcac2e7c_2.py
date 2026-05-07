```python
"""
Personal Finance Data Analysis Module

This module processes categorized financial transactions to generate comprehensive
spending insights including:
- Monthly spending totals by category
- Trend analysis over time periods
- Detection of unusual spending patterns and outliers
- Statistical summaries and variance analysis

The module uses statistical methods to identify anomalies in spending patterns
and provides actionable insights for personal financial management.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
import math

class TransactionAnalyzer:
    def __init__(self):
        self.transactions = []
        self.categories = set()
        
    def load_sample_data(self):
        """Generate sample transaction data for demonstration"""
        import random
        
        categories = ['Groceries', 'Restaurants', 'Gas', 'Shopping', 'Bills', 'Entertainment', 'Healthcare']
        base_date = datetime(2023, 1, 1)
        
        for i in range(365):
            date = base_date + timedelta(days=i)
            # Generate 1-5 transactions per day
            for _ in range(random.randint(1, 5)):
                category = random.choice(categories)
                
                # Create realistic spending patterns
                base_amounts = {
                    'Groceries': (30, 150),
                    'Restaurants': (15, 80),
                    'Gas': (40, 70),
                    'Shopping': (20, 200),
                    'Bills': (50, 300),
                    'Entertainment': (10, 100),
                    'Healthcare': (20, 500)
                }
                
                min_amt, max_amt = base_amounts[category]
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                # Add some outliers (5% chance of unusual spending)
                if random.random() < 0.05:
                    amount *= random.uniform(2, 5)
                
                self.transactions.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'category': category,
                    'amount': amount,
                    'description': f'{category} purchase'
                })
                
        self.categories = set(categories)
        
    def parse_date(self, date_str):
        """Parse date string into datetime object"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD") from e
            
    def get_monthly_totals(self):
        """Calculate monthly spending totals by category"""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        try:
            for transaction in self.transactions:
                date = self.parse_date(transaction['date'])
                month_key = date.strftime('%Y-%m')
                category = transaction['category']
                amount = float(transaction['amount'])
                
                monthly_data[month_key][category] += amount
                
            return dict(monthly_data)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error processing transaction data: {e}") from e
            
    def calculate_trends(self):
        """Analyze spending trends over time"""
        monthly_totals = {}
        category_trends = defaultdict(list)
        
        try:
            # Get monthly totals across all categories
            monthly_data = self.get_monthly_totals()
            
            for month, categories in monthly_data.items():
                monthly_totals[month] = sum(categories.values())
                
                for category, amount in categories.items():
                    category_trends[category].append((month, amount))
                    
            # Sort by month for trend analysis
            sorted_months = sorted(monthly_totals.items())
            
            # Calculate overall trend
            if len(sorted_months) >= 2:
                amounts = [amount for _, amount in sorted_months]
                overall_trend = self._calculate_trend_direction(amounts)
            else:
                overall_trend = "insufficient_data"
                
            # Calculate category-specific trends
            trends = {
                'overall': {
                    'direction': overall_trend,
                    'monthly_totals': dict(sorted_months),
                    'average_monthly': statistics.mean([amt for _, amt in sorted_months]) if sorted_months else 0
                },
                'by_category': {}
            }
            
            for category, data in category_trends.items():
                sorted_data = sorted(data, key=lambda x: x[0])
                amounts = [amount for _, amount in sorted_data]
                
                if len(amounts) >= 2:
                    trend_direction = self._calculate_trend_direction(amounts)
                    avg_amount = statistics.mean(amounts)
                    variance = statistics.variance(amounts) if len(amounts) > 1 else 0
                else:
                    trend_direction = "insufficient_data"
                    avg_amount = amounts[0] if amounts else 0
                    variance = 0
                    
                trends['by_category'][category] = {
                    'direction': trend_direction,
                    'average': round(avg_amount, 2),
                    'variance': round(variance, 2),
                    'data_points': len(amounts)
                }
                
            return trends
        except Exception as e:
            raise RuntimeError(f"Error calculating trends: {e}") from e
            
    def _calculate_trend_direction(self, amounts):
        """Determine if trend is increasing, decreasing, or stable"""
        if len(amounts) < 2:
            return "insufficient_data"
            
        # Calculate linear regression slope
        n = len(amounts)
        x_values = list(range(n))
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(amounts)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, amounts))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return "stable"
            
        slope = numerator / denominator
        
        # Determine trend based on slope and magnitude
        if abs(slope) < (y_mean * 0.01):  # Less than 1% change per period
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
            
    def identify_outliers(self):
        """Identify unusual spending patterns and outliers"""
        outliers = {
            'by_category': {},
            'by_transaction': []
        }
        
        try:
            # Group transactions by category
            category_amounts = defaultdict(list)
            
            for transaction in self.transactions:
                category = transaction['category']
                amount = float(transaction['amount'])
                category_amounts[category].append({
                    'amount': amount,
                    'date': transaction['date'],
                    'description': transaction.get('description', '')
                })
                
            # Find outliers within each category using IQR method
            for category, transactions in category_amounts.items():
                amounts = [t['amount'] for t in transactions]
                
                if len(amounts) < 4:  # Need at least 4 data points for IQR
                    continue
                    
                q1 = statistics.quantiles(amounts, n=4)[0]
                q3 = statistics.quantiles(amounts, n=4)[2]
                iqr = q3 - q1
                
                lower_bound = q1 - (1.5 * iqr)
                upper_bound = q3 + (1.5 * iqr)
                
                category_outliers = []
                for transaction in transactions:
                    amount = transaction['amount']
                    if amount < lower_bound or amount > upper_bound:
                        category_outliers.append({
                            'amount': amount,
                            'date': transaction['date'],
                            'description': transaction['description'],
                            'deviation': round(abs(amount - statistics.mean(amounts)), 2),
                            'type': 'high' if amount >