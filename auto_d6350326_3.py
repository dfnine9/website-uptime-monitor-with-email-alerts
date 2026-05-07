```python
"""
Budget Recommendation Engine

This module analyzes historical spending data to generate intelligent budget recommendations
and financial optimization insights. It processes transaction data, identifies spending patterns,
calculates statistical baselines, and provides actionable recommendations for budget limits
per category along with optimization strategies.

Key features:
- Historical spending pattern analysis
- Statistical budget limit calculations using multiple methodologies
- Seasonal and trend adjustments
- Risk-based recommendations (conservative, moderate, aggressive)
- Actionable financial optimization insights
- Anomaly detection for unusual spending patterns

Usage: python script.py
"""

import json
import statistics
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random
import math


class BudgetRecommendationEngine:
    def __init__(self):
        self.spending_data = []
        self.categories = set()
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.insights = []
        
    def generate_sample_data(self, months: int = 12) -> List[Dict]:
        """Generate realistic sample spending data for demonstration"""
        categories = [
            'groceries', 'dining_out', 'transportation', 'utilities', 
            'entertainment', 'shopping', 'healthcare', 'subscriptions',
            'travel', 'miscellaneous'
        ]
        
        base_amounts = {
            'groceries': 400, 'dining_out': 200, 'transportation': 150,
            'utilities': 120, 'entertainment': 100, 'shopping': 180,
            'healthcare': 80, 'subscriptions': 50, 'travel': 300,
            'miscellaneous': 75
        }
        
        data = []
        current_date = datetime.datetime.now() - datetime.timedelta(days=months * 30)
        
        for month in range(months):
            month_date = current_date + datetime.timedelta(days=month * 30)
            seasonal_factor = 1 + 0.3 * math.sin(month * math.pi / 6)  # Seasonal variation
            
            for category in categories:
                base = base_amounts[category]
                # Add trend (slight increase over time)
                trend_factor = 1 + (month * 0.02)
                # Add randomness
                random_factor = random.uniform(0.7, 1.4)
                
                amount = base * seasonal_factor * trend_factor * random_factor
                
                # Generate multiple transactions per category per month
                num_transactions = random.randint(3, 12)
                for _ in range(num_transactions):
                    transaction_amount = amount / num_transactions * random.uniform(0.5, 2.0)
                    data.append({
                        'date': month_date.strftime('%Y-%m-%d'),
                        'category': category,
                        'amount': round(transaction_amount, 2),
                        'description': f'{category.replace("_", " ").title()} expense'
                    })
        
        return data
    
    def load_data(self, data: List[Dict]):
        """Load and process spending data"""
        try:
            self.spending_data = data
            self.categories = set(item['category'] for item in data)
            
            # Group by month and category
            for item in data:
                date_obj = datetime.datetime.strptime(item['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                self.monthly_totals[month_key][item['category']] += item['amount']
                
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def calculate_statistics(self, amounts: List[float]) -> Dict[str, float]:
        """Calculate statistical measures for a list of amounts"""
        if not amounts:
            return {'mean': 0, 'median': 0, 'std': 0, 'percentile_75': 0, 'percentile_90': 0}
        
        return {
            'mean': statistics.mean(amounts),
            'median': statistics.median(amounts),
            'std': statistics.stdev(amounts) if len(amounts) > 1 else 0,
            'percentile_75': sorted(amounts)[int(len(amounts) * 0.75)],
            'percentile_90': sorted(amounts)[int(len(amounts) * 0.90)]
        }
    
    def detect_trends(self, monthly_amounts: List[Tuple[str, float]]) -> Dict[str, Any]:
        """Detect spending trends over time"""
        if len(monthly_amounts) < 3:
            return {'trend': 'insufficient_data', 'slope': 0, 'r_squared': 0}
        
        # Sort by date
        sorted_data = sorted(monthly_amounts, key=lambda x: x[0])
        amounts = [x[1] for x in sorted_data]
        
        # Simple linear regression
        n = len(amounts)
        x = list(range(n))
        
        sum_x = sum(x)
        sum_y = sum(amounts)
        sum_xy = sum(xi * yi for xi, yi in zip(x, amounts))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate R-squared
        y_pred = [slope * xi + intercept for xi in x]
        ss_res = sum((yi - y_pred[i]) ** 2 for i, yi in enumerate(amounts))
        ss_tot = sum((yi - statistics.mean(amounts)) ** 2 for yi in amounts)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        trend = 'increasing' if slope > 0.05 else 'decreasing' if slope < -0.05 else 'stable'
        
        return {
            'trend': trend,
            'slope': slope,
            'r_squared': r_squared,
            'monthly_change': slope
        }
    
    def calculate_budget_recommendations(self) -> Dict[str, Dict]:
        """Calculate budget recommendations for each category"""
        recommendations = {}
        
        try:
            for category in self.categories:
                # Get monthly amounts for this category
                monthly_amounts = []
                for month_data in self.monthly_totals.values():
                    monthly_amounts.append(month_data.get(category, 0))
                
                # Calculate statistics
                stats = self.calculate_statistics(monthly_amounts)
                
                # Get trend analysis
                monthly_with_dates = [(month, data.get(category, 0)) 
                                    for month, data in self.monthly_totals.items()]
                trends = self.detect_trends(monthly_with_dates)
                
                # Calculate different budget scenarios
                conservative = stats['percentile_75'] * 1.1  # 75th percentile + 10% buffer
                moderate = stats['mean'] + stats['std']       # Mean + 1 standard deviation
                aggressive = stats['median'] * 1.05          # Median + 5% buffer
                
                # Adjust for trends
                trend_adjustment = 1.0
                if trends['trend'] == 'increasing':
                    trend_adjustment = 1.1  # 10% increase for growing categories
                elif trends['trend'] == 'decreasing':
                    trend_adjustment = 0.95  # 5% decrease for declining categories
                
                recommendations[category] = {
                    'statistics': stats,
                    'trends': trends,
                    'budget_recommendations': {
                        'conservative': round(conservative * trend_adjustment, 2),
                        'moderate': round(moderate * trend_adjustment, 2),
                        'aggressive': round(aggressive * trend_adjustment, 2)
                    },
                    'current_average': round(stats['mean'], 2),
                    'volatility': 'high' if stats['std'] > stats['mean'] * 0.5