```python
"""
Personal Spending Analysis Engine

This module provides a comprehensive spending analysis system that:
1. Calculates monthly spending totals by category
2. Identifies spending trends over time using linear regression
3. Generates budget recommendations based on historical patterns and percentage rules

The engine processes transaction data to provide insights into spending habits
and suggests budget allocations based on the 50/30/20 rule (needs/wants/savings)
with category-specific recommendations.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import random


class SpendingAnalysisEngine:
    """Main engine for analyzing spending patterns and generating budget recommendations."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.category_trends = {}
        
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        categories = ['groceries', 'dining', 'transportation', 'utilities', 'entertainment', 
                     'healthcare', 'shopping', 'rent', 'insurance', 'miscellaneous']
        
        # Generate 12 months of sample data
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(200):  # 200 transactions over 12 months
            transaction_date = base_date + timedelta(days=random.randint(0, 365))
            category = random.choice(categories)
            
            # Create realistic spending patterns
            amount_ranges = {
                'rent': (1200, 2000),
                'groceries': (50, 300),
                'dining': (15, 150),
                'utilities': (80, 200),
                'transportation': (20, 150),
                'entertainment': (25, 200),
                'healthcare': (30, 500),
                'shopping': (20, 400),
                'insurance': (100, 300),
                'miscellaneous': (10, 100)
            }
            
            min_amount, max_amount = amount_ranges.get(category, (10, 200))
            amount = round(random.uniform(min_amount, max_amount), 2)
            
            self.transactions.append({
                'date': transaction_date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': amount,
                'description': f'{category.title()} purchase'
            })
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate total spending by month and category."""
        try:
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                self.monthly_totals[month_key][category] += amount
                
            return dict(self.monthly_totals)
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def calculate_trends(self) -> Dict[str, Dict[str, Any]]:
        """Calculate spending trends for each category using simple linear regression."""
        try:
            category_data = defaultdict(list)
            
            # Organize data by category
            for month, categories in self.monthly_totals.items():
                month_num = int(month.replace('-', ''))  # Simple numeric representation
                for category, amount in categories.items():
                    category_data[category].append((month_num, amount))
            
            trends = {}
            for category, data_points in category_data.items():
                if len(data_points) < 2:
                    continue
                    
                # Simple linear regression
                n = len(data_points)
                x_values = [point[0] for point in data_points]
                y_values = [point[1] for point in data_points]
                
                x_mean = statistics.mean(x_values)
                y_mean = statistics.mean(y_values)
                
                numerator = sum((x - x_mean) * (y - y_mean) for x, y in data_points)
                denominator = sum((x - x_mean) ** 2 for x in x_values)
                
                if denominator == 0:
                    slope = 0
                else:
                    slope = numerator / denominator
                
                # Calculate trend direction and average spending
                avg_spending = statistics.mean(y_values)
                trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
                
                trends[category] = {
                    'slope': round(slope, 4),
                    'direction': trend_direction,
                    'average_monthly': round(avg_spending, 2),
                    'total_months': n
                }
            
            self.category_trends = trends
            return trends
            
        except (ValueError, ZeroDivisionError, TypeError) as e:
            print(f"Error calculating trends: {e}")
            return {}
    
    def generate_budget_recommendations(self) -> Dict[str, Any]:
        """Generate budget recommendations based on historical patterns and 50/30/20 rule."""
        try:
            if not self.category_trends:
                print("No trend data available for recommendations")
                return {}
            
            total_avg_spending = sum(trend['average_monthly'] for trend in self.category_trends.values())
            
            # Category classifications for 50/30/20 rule
            needs_categories = {'rent', 'groceries', 'utilities', 'healthcare', 'insurance', 'transportation'}
            wants_categories = {'dining', 'entertainment', 'shopping', 'miscellaneous'}
            
            needs_spending = sum(trend['average_monthly'] for cat, trend in self.category_trends.items() 
                               if cat in needs_categories)
            wants_spending = sum(trend['average_monthly'] for cat, trend in self.category_trends.items() 
                               if cat in wants_categories)
            
            # Calculate recommended budget based on current total spending
            recommended_income = total_avg_spending / 0.8  # Assuming 20% should go to savings
            recommended_needs = recommended_income * 0.5
            recommended_wants = recommended_income * 0.3
            recommended_savings = recommended_income * 0.2
            
            recommendations = {
                'current_analysis': {
                    'total_monthly_spending': round(total_avg_spending, 2),
                    'needs_spending': round(needs_spending, 2),
                    'wants_spending': round(wants_spending, 2),
                    'needs_percentage': round((needs_spending / total_avg_spending) * 100, 1) if total_avg_spending > 0 else 0,
                    'wants_percentage': round((wants_spending / total_avg_spending) * 100, 1) if total_avg_spending > 0 else 0
                },
                'recommendations': {
                    'target_monthly_income': round(recommended_income, 2),
                    'recommended_needs_budget': round(recommended_needs, 2),
                    'recommended_wants_budget': round(recommended_wants, 2),
                    'recommended_savings': round(recommended_savings, 2)
                },
                'category_specific_advice': {}
            }
            
            # Generate category-specific advice
            for category, trend in self.category_trends.items():
                advice = []
                
                if trend['direction'] == 'increasing':
                    advice.append(f"Spending is trending upward (+{abs(trend['slope']):.2f}/month)")
                    advice.append("Consider setting a monthly limit to control growth")
                elif trend['direction'] == 'decreasing':
                    advice.append(f"Good job! Spending is trending downward (-{abs(trend['slope']):.2f}/month)")
                
                # Budget allocation advice
                if category in needs_categories:
                    target_percentage = (trend['average_monthly'] / recommended_needs