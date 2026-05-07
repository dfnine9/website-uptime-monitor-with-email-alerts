```python
"""
Spending Pattern Analysis Module

This module provides comprehensive analysis of spending patterns including:
- Monthly spending trend calculations
- Unusual transaction detection using statistical methods
- Category-wise spending insights and statistics
- Visualization of spending behavior patterns

The module processes transaction data to identify spending anomalies,
calculate trends, and provide actionable insights for financial analysis.
"""

import json
import statistics
import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import random
import math

class SpendingPatternAnalyzer:
    def __init__(self):
        self.transactions = []
        self.categories = set()
        
    def load_sample_data(self) -> None:
        """Generate sample transaction data for analysis"""
        categories = ['Groceries', 'Dining', 'Transportation', 'Entertainment', 
                     'Utilities', 'Shopping', 'Healthcare', 'Gas', 'Insurance']
        
        base_date = datetime.datetime(2024, 1, 1)
        
        for i in range(300):  # 300 sample transactions
            date = base_date + datetime.timedelta(days=random.randint(0, 365))
            category = random.choice(categories)
            
            # Create realistic spending patterns with some categories having higher amounts
            if category == 'Groceries':
                amount = random.uniform(20, 150)
            elif category == 'Dining':
                amount = random.uniform(10, 80)
            elif category == 'Transportation':
                amount = random.uniform(5, 200)
            elif category == 'Utilities':
                amount = random.uniform(50, 300)
            elif category == 'Shopping':
                amount = random.uniform(15, 400)
            else:
                amount = random.uniform(10, 100)
                
            # Add some unusual transactions (outliers)
            if random.random() < 0.05:  # 5% chance of unusual transaction
                amount *= random.uniform(3, 8)
                
            transaction = {
                'date': date.strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'category': category,
                'description': f'{category} purchase'
            }
            
            self.transactions.append(transaction)
            self.categories.add(category)
    
    def calculate_monthly_trends(self) -> Dict[str, Any]:
        """Calculate monthly spending trends"""
        try:
            monthly_totals = defaultdict(float)
            monthly_counts = defaultdict(int)
            
            for transaction in self.transactions:
                date_obj = datetime.datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                monthly_totals[month_key] += transaction['amount']
                monthly_counts[month_key] += 1
            
            months = sorted(monthly_totals.keys())
            amounts = [monthly_totals[month] for month in months]
            
            # Calculate trend statistics
            if len(amounts) >= 2:
                trend_slope = self._calculate_trend_slope(amounts)
                trend_direction = "Increasing" if trend_slope > 0 else "Decreasing" if trend_slope < 0 else "Stable"
            else:
                trend_slope = 0
                trend_direction = "Insufficient data"
            
            avg_monthly_spending = statistics.mean(amounts) if amounts else 0
            
            return {
                'monthly_totals': dict(monthly_totals),
                'monthly_counts': dict(monthly_counts),
                'average_monthly_spending': round(avg_monthly_spending, 2),
                'trend_slope': round(trend_slope, 4),
                'trend_direction': trend_direction,
                'months_analyzed': len(months)
            }
            
        except Exception as e:
            print(f"Error calculating monthly trends: {str(e)}")
            return {}
    
    def _calculate_trend_slope(self, amounts: List[float]) -> float:
        """Calculate linear trend slope using least squares method"""
        n = len(amounts)
        x_values = list(range(n))
        
        sum_x = sum(x_values)
        sum_y = sum(amounts)
        sum_xy = sum(x * y for x, y in zip(x_values, amounts))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def identify_unusual_transactions(self) -> Dict[str, Any]:
        """Identify unusual transactions using statistical analysis"""
        try:
            unusual_transactions = []
            category_stats = {}
            
            # Calculate statistics for each category
            for category in self.categories:
                category_amounts = [t['amount'] for t in self.transactions if t['category'] == category]
                
                if len(category_amounts) >= 3:
                    mean_amount = statistics.mean(category_amounts)
                    stdev_amount = statistics.stdev(category_amounts)
                    median_amount = statistics.median(category_amounts)
                    
                    category_stats[category] = {
                        'mean': round(mean_amount, 2),
                        'stdev': round(stdev_amount, 2),
                        'median': round(median_amount, 2),
                        'count': len(category_amounts)
                    }
                    
                    # Identify outliers using z-score (transactions > 2.5 standard deviations)
                    threshold = 2.5
                    
                    for transaction in self.transactions:
                        if transaction['category'] == category:
                            z_score = (transaction['amount'] - mean_amount) / stdev_amount if stdev_amount > 0 else 0
                            
                            if abs(z_score) > threshold:
                                unusual_transactions.append({
                                    'date': transaction['date'],
                                    'amount': transaction['amount'],
                                    'category': transaction['category'],
                                    'description': transaction['description'],
                                    'z_score': round(z_score, 2),
                                    'deviation_from_mean': round(transaction['amount'] - mean_amount, 2)
                                })
            
            return {
                'unusual_transactions': unusual_transactions,
                'category_statistics': category_stats,
                'total_unusual_found': len(unusual_transactions)
            }
            
        except Exception as e:
            print(f"Error identifying unusual transactions: {str(e)}")
            return {}
    
    def generate_category_insights(self) -> Dict[str, Any]:
        """Generate statistical insights for spending categories"""
        try:
            category_insights = {}
            total_spending = sum(t['amount'] for t in self.transactions)
            
            for category in self.categories:
                category_transactions = [t for t in self.transactions if t['category'] == category]
                category_amounts = [t['amount'] for t in category_transactions]
                category_total = sum(category_amounts)
                
                if category_amounts:
                    insights = {
                        'total_spent': round(category_total, 2),
                        'percentage_of_total': round((category_total / total_spending) * 100, 2) if total_spending > 0 else 0,
                        'transaction_count': len(category_amounts),
                        'average_transaction': round(statistics.mean(category_amounts), 2),
                        'median_transaction': round(statistics.median(category_amounts), 2),
                        'min_transaction': round(min(category_amounts), 2),
                        'max_transaction': round(max(category_amounts), 2)
                    }
                    
                    if len(category_amounts) >= 2:
                        insights['std_deviation'] = round(statistics.stdev(category_amounts), 2)
                    else:
                        insights['std_deviation'] = 0
                        
                    category_insights[category] = insights
            
            # Find top spending categories
            sorted_categories = sorted(category_insights.items(),