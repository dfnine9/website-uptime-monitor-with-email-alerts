```python
"""
Personal Budget Recommendation Engine

This module analyzes historical spending data to generate personalized monthly budget 
recommendations with category-wise percentage allocations and spending limits based on 
income patterns. It uses statistical analysis to identify spending trends and provides 
data-driven budget suggestions following common financial planning principles.

Features:
- Analyzes historical transaction data
- Calculates income patterns and spending trends
- Generates percentage-based category allocations
- Provides monthly spending limits per category
- Includes emergency fund recommendations
- Handles various data formats and edge cases

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
import random


class BudgetRecommendationEngine:
    """
    A comprehensive budget recommendation system that analyzes spending patterns
    and generates personalized monthly budget allocations.
    """
    
    def __init__(self):
        self.essential_categories = {
            'housing': {'min': 25, 'max': 35, 'priority': 1},
            'utilities': {'min': 5, 'max': 10, 'priority': 1},
            'groceries': {'min': 10, 'max': 15, 'priority': 1},
            'transportation': {'min': 10, 'max': 20, 'priority': 1},
            'insurance': {'min': 5, 'max': 10, 'priority': 1},
        }
        
        self.discretionary_categories = {
            'dining_out': {'min': 5, 'max': 15, 'priority': 2},
            'entertainment': {'min': 5, 'max': 10, 'priority': 2},
            'shopping': {'min': 5, 'max': 15, 'priority': 2},
            'personal_care': {'min': 2, 'max': 5, 'priority': 2},
            'subscriptions': {'min': 1, 'max': 5, 'priority': 2},
        }
        
        self.savings_categories = {
            'emergency_fund': {'min': 10, 'max': 20, 'priority': 1},
            'retirement': {'min': 10, 'max': 15, 'priority': 1},
            'investments': {'min': 5, 'max': 20, 'priority': 2},
        }

    def generate_sample_data(self, months=12):
        """Generate realistic sample spending data for demonstration."""
        try:
            categories = list(self.essential_categories.keys()) + list(self.discretionary_categories.keys())
            data = []
            base_income = random.uniform(4000, 8000)
            
            for month in range(months):
                date = datetime.now() - timedelta(days=30 * month)
                monthly_income = base_income * random.uniform(0.9, 1.1)
                
                # Generate expenses
                for category in categories:
                    if category in self.essential_categories:
                        base_pct = (self.essential_categories[category]['min'] + 
                                  self.essential_categories[category]['max']) / 2
                    else:
                        base_pct = (self.discretionary_categories[category]['min'] + 
                                  self.discretionary_categories[category]['max']) / 2
                    
                    amount = monthly_income * (base_pct / 100) * random.uniform(0.7, 1.3)
                    
                    data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'category': category,
                        'amount': round(amount, 2),
                        'type': 'expense'
                    })
                
                # Add income record
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'category': 'income',
                    'amount': round(monthly_income, 2),
                    'type': 'income'
                })
            
            return data
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []

    def analyze_income_patterns(self, data):
        """Analyze income patterns from historical data."""
        try:
            incomes = [item['amount'] for item in data if item['type'] == 'income']
            
            if not incomes:
                raise ValueError("No income data found")
            
            return {
                'average_monthly_income': round(statistics.mean(incomes), 2),
                'median_monthly_income': round(statistics.median(incomes), 2),
                'income_stability': round(1 - (statistics.stdev(incomes) / statistics.mean(incomes)), 2),
                'min_income': round(min(incomes), 2),
                'max_income': round(max(incomes), 2)
            }
            
        except Exception as e:
            print(f"Error analyzing income patterns: {e}")
            return {
                'average_monthly_income': 5000,
                'median_monthly_income': 5000,
                'income_stability': 0.8,
                'min_income': 4500,
                'max_income': 5500
            }

    def analyze_spending_patterns(self, data):
        """Analyze historical spending patterns by category."""
        try:
            spending_by_category = defaultdict(list)
            
            for item in data:
                if item['type'] == 'expense':
                    spending_by_category[item['category']].append(item['amount'])
            
            patterns = {}
            for category, amounts in spending_by_category.items():
                if amounts:
                    patterns[category] = {
                        'average_monthly': round(statistics.mean(amounts), 2),
                        'median_monthly': round(statistics.median(amounts), 2),
                        'volatility': round(statistics.stdev(amounts) if len(amounts) > 1 else 0, 2),
                        'trend': self._calculate_trend(amounts)
                    }
            
            return patterns
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}

    def _calculate_trend(self, amounts):
        """Calculate spending trend (increasing, decreasing, stable)."""
        try:
            if len(amounts) < 2:
                return 'stable'
            
            recent_avg = statistics.mean(amounts[:len(amounts)//2])
            older_avg = statistics.mean(amounts[len(amounts)//2:])
            
            change_pct = (recent_avg - older_avg) / older_avg * 100
            
            if change_pct > 5:
                return 'increasing'
            elif change_pct < -5:
                return 'decreasing'
            else:
                return 'stable'
                
        except Exception as e:
            return 'stable'

    def generate_budget_recommendations(self, income_analysis, spending_patterns):
        """Generate personalized budget recommendations."""
        try:
            monthly_income = income_analysis['average_monthly_income']
            recommendations = {}
            
            # Start with essential categories
            total_allocated = 0
            
            for category, constraints in self.essential_categories.items():
                historical_spending = spending_patterns.get(category, {})
                
                if historical_spending:
                    # Base recommendation on historical average but constrain within limits
                    historical_pct = (historical_spending['average_monthly'] / monthly_income) * 100
                    recommended_pct = max(constraints['min'], 
                                        min(constraints['max'], historical_pct))
                else:
                    # Use middle of recommended range if no historical data
                    recommended_pct = (constraints['min'] + constraints['max']) / 2
                
                amount = monthly_income * (recommended_pct / 100)
                
                recommendations[category] = {
                    'percentage': round(recommended_pct, 1),
                    'monthly_limit': round(amount, 2),
                    'category_type': 'essential',
                    'historical_average': historical_spending.get('average_monthly', 0),
                    'trend': historical_spending.get('trend', 'stable')