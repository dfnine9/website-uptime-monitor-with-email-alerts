```python
"""
Personal Budget Recommendation System

This module analyzes historical spending patterns to generate personalized monthly budgets
with category-specific limits and formatted reports with ASCII visualizations.

Features:
- Analyzes spending patterns from transaction data
- Generates category-based budget recommendations
- Creates spending limit alerts
- Outputs formatted budget reports with visual charts
- Tracks budget vs actual spending variance

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
import math

class BudgetRecommendationSystem:
    def __init__(self):
        self.transactions = []
        self.categories = {
            'housing': ['rent', 'mortgage', 'utilities', 'maintenance'],
            'food': ['groceries', 'dining', 'restaurants', 'takeout'],
            'transportation': ['gas', 'car payment', 'insurance', 'public transport'],
            'entertainment': ['movies', 'games', 'streaming', 'hobbies'],
            'shopping': ['clothing', 'electronics', 'household items'],
            'healthcare': ['medical', 'pharmacy', 'insurance', 'dental'],
            'misc': ['other', 'miscellaneous', 'cash']
        }
        
    def categorize_expense(self, description):
        """Categorize an expense based on description keywords"""
        description_lower = description.lower()
        for category, keywords in self.categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        return 'misc'
    
    def generate_sample_data(self):
        """Generate sample transaction data for demonstration"""
        import random
        
        sample_transactions = [
            # Housing
            {'date': '2024-01-01', 'description': 'rent payment', 'amount': -1200.00},
            {'date': '2024-01-05', 'description': 'utilities bill', 'amount': -150.00},
            {'date': '2024-02-01', 'description': 'rent payment', 'amount': -1200.00},
            {'date': '2024-02-03', 'description': 'utilities bill', 'amount': -145.00},
            {'date': '2024-03-01', 'description': 'rent payment', 'amount': -1200.00},
            {'date': '2024-03-04', 'description': 'utilities bill', 'amount': -160.00},
            
            # Food
            {'date': '2024-01-07', 'description': 'groceries supermarket', 'amount': -85.50},
            {'date': '2024-01-14', 'description': 'groceries store', 'amount': -92.30},
            {'date': '2024-01-21', 'description': 'dining restaurant', 'amount': -45.00},
            {'date': '2024-01-28', 'description': 'groceries shopping', 'amount': -78.90},
            {'date': '2024-02-04', 'description': 'groceries supermarket', 'amount': -88.75},
            {'date': '2024-02-11', 'description': 'takeout delivery', 'amount': -32.50},
            {'date': '2024-02-18', 'description': 'groceries store', 'amount': -95.20},
            {'date': '2024-02-25', 'description': 'dining out', 'amount': -67.80},
            {'date': '2024-03-03', 'description': 'groceries market', 'amount': -91.40},
            {'date': '2024-03-10', 'description': 'restaurants dinner', 'amount': -54.30},
            
            # Transportation
            {'date': '2024-01-08', 'description': 'gas station', 'amount': -42.00},
            {'date': '2024-01-15', 'description': 'car insurance', 'amount': -125.00},
            {'date': '2024-01-22', 'description': 'gas fill up', 'amount': -38.50},
            {'date': '2024-02-05', 'description': 'gas station', 'amount': -44.75},
            {'date': '2024-02-19', 'description': 'gas pump', 'amount': -41.20},
            {'date': '2024-03-07', 'description': 'gas station', 'amount': -39.80},
            
            # Entertainment
            {'date': '2024-01-12', 'description': 'streaming service', 'amount': -14.99},
            {'date': '2024-01-19', 'description': 'movies theater', 'amount': -28.50},
            {'date': '2024-02-09', 'description': 'games purchase', 'amount': -59.99},
            {'date': '2024-02-16', 'description': 'streaming netflix', 'amount': -14.99},
            {'date': '2024-03-14', 'description': 'hobbies supplies', 'amount': -73.25},
            
            # Shopping
            {'date': '2024-01-17', 'description': 'clothing store', 'amount': -129.99},
            {'date': '2024-02-23', 'description': 'electronics purchase', 'amount': -249.99},
            {'date': '2024-03-12', 'description': 'household items', 'amount': -67.50},
            
            # Healthcare
            {'date': '2024-01-25', 'description': 'pharmacy prescription', 'amount': -24.50},
            {'date': '2024-02-14', 'description': 'medical appointment', 'amount': -150.00},
            {'date': '2024-03-20', 'description': 'dental checkup', 'amount': -85.00},
        ]
        
        self.transactions = sample_transactions
        return len(sample_transactions)
    
    def analyze_spending_patterns(self):
        """Analyze historical spending to identify patterns"""
        try:
            if not self.transactions:
                self.generate_sample_data()
            
            monthly_spending = defaultdict(lambda: defaultdict(float))
            category_totals = defaultdict(list)
            
            for transaction in self.transactions:
                if transaction['amount'] >= 0:  # Skip income
                    continue
                    
                date_str = transaction['date']
                amount = abs(transaction['amount'])
                category = self.categorize_expense(transaction['description'])
                
                # Extract year-month
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                
                monthly_spending[month_key][category] += amount
                category_totals[category].append(amount)
            
            return monthly_spending, category_totals
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}, {}
    
    def calculate_budget_recommendations(self, monthly_spending, category_totals):
        """Calculate budget recommendations based on spending patterns"""
        try:
            recommendations = {}
            
            for category, amounts in category_totals.items():
                if not amounts:
                    continue
                    
                # Calculate statistics
                avg_spending = statistics.mean(amounts)
                if len(amounts) > 1:
                    std_dev = statistics.stdev(amounts)
                else:
                    std_dev = avg_spending * 0.1  # 10% if only one data point
                
                # Recommend budget with 10% buffer above average + 1 standard deviation
                recommended_budget = avg_spending + (std_dev * 0.5) + (avg_spending * 0.1)
                
                recommendations[category] = {
                    'recommended_budget': round(recommended_budget, 2),
                    'average_spending': round(avg_spending, 2),
                    'min_spending': round(min(amounts), 2),
                    'max_spending': round(max(amounts), 2),