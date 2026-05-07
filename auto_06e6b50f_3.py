```python
"""
Personal Budget Recommendation System

This module analyzes historical spending patterns and generates personalized monthly
budget suggestions based on variations of the 50/30/20 rule (needs/wants/savings).
It processes spending data, calculates category-specific limits, and outputs
recommendations in both JSON and PDF formats.

The system:
1. Analyzes historical spending patterns from input data
2. Applies intelligent variations of the 50/30/20 budgeting rule
3. Generates personalized category-specific spending limits
4. Outputs recommendations in JSON format and simulated PDF structure
5. Provides actionable insights for budget optimization

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import sys

class BudgetRecommendationSystem:
    def __init__(self):
        self.spending_categories = {
            'housing': 'needs',
            'utilities': 'needs', 
            'groceries': 'needs',
            'transportation': 'needs',
            'insurance': 'needs',
            'healthcare': 'needs',
            'dining': 'wants',
            'entertainment': 'wants',
            'shopping': 'wants',
            'subscriptions': 'wants',
            'travel': 'wants',
            'hobbies': 'wants',
            'savings': 'savings',
            'investments': 'savings',
            'emergency_fund': 'savings',
            'retirement': 'savings'
        }
        
    def generate_sample_data(self) -> List[Dict]:
        """Generate sample historical spending data for demonstration"""
        sample_months = []
        for i in range(6):  # 6 months of data
            month_data = {
                'month': (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m'),
                'income': 5000 + (i * 100),  # Varying income
                'expenses': {
                    'housing': 1200 + (i * 20),
                    'utilities': 200 + (i * 10),
                    'groceries': 400 + (i * 15),
                    'transportation': 300 + (i * 5),
                    'insurance': 150,
                    'healthcare': 100 + (i * 5),
                    'dining': 250 + (i * 20),
                    'entertainment': 180 + (i * 15),
                    'shopping': 220 + (i * 25),
                    'subscriptions': 80 + (i * 5),
                    'travel': 200 + (i * 50),
                    'hobbies': 120 + (i * 10),
                    'savings': 500 + (i * 30),
                    'investments': 300 + (i * 20),
                    'emergency_fund': 200,
                    'retirement': 400
                }
            }
            sample_months.append(month_data)
        return sample_months
    
    def analyze_spending_patterns(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Analyze historical spending to identify patterns and averages"""
        try:
            if not historical_data:
                raise ValueError("No historical data provided")
            
            analysis = {
                'avg_income': 0,
                'category_averages': {},
                'category_trends': {},
                'spending_volatility': {},
                'total_avg_expenses': 0
            }
            
            # Calculate averages
            incomes = [month['income'] for month in historical_data]
            analysis['avg_income'] = statistics.mean(incomes)
            
            # Analyze each category
            for category in self.spending_categories.keys():
                category_amounts = []
                for month in historical_data:
                    if category in month['expenses']:
                        category_amounts.append(month['expenses'][category])
                
                if category_amounts:
                    analysis['category_averages'][category] = statistics.mean(category_amounts)
                    analysis['spending_volatility'][category] = statistics.stdev(category_amounts) if len(category_amounts) > 1 else 0
                    
                    # Calculate trend (simple slope)
                    if len(category_amounts) > 1:
                        x_values = list(range(len(category_amounts)))
                        slope = self._calculate_trend_slope(x_values, category_amounts)
                        analysis['category_trends'][category] = slope
            
            analysis['total_avg_expenses'] = sum(analysis['category_averages'].values())
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}
    
    def _calculate_trend_slope(self, x_values: List[int], y_values: List[float]) -> float:
        """Calculate simple linear regression slope"""
        try:
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            return slope
        except ZeroDivisionError:
            return 0.0
    
    def apply_budget_rule_variation(self, income: float, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Apply intelligent variation of 50/30/20 rule based on spending analysis"""
        try:
            # Base 50/30/20 allocation
            base_needs = income * 0.50
            base_wants = income * 0.30
            base_savings = income * 0.20
            
            # Adjust based on actual spending patterns
            actual_needs = sum(analysis['category_averages'].get(cat, 0) 
                             for cat, type_ in self.spending_categories.items() if type_ == 'needs')
            actual_wants = sum(analysis['category_averages'].get(cat, 0) 
                             for cat, type_ in self.spending_categories.items() if type_ == 'wants')
            actual_savings = sum(analysis['category_averages'].get(cat, 0) 
                               for cat, type_ in self.spending_categories.items() if type_ == 'savings')
            
            # Calculate adjustment factors
            needs_ratio = actual_needs / base_needs if base_needs > 0 else 1
            wants_ratio = actual_wants / base_wants if base_wants > 0 else 1
            savings_ratio = actual_savings / base_savings if base_savings > 0 else 1
            
            # Apply intelligent adjustments
            if needs_ratio > 1.2:  # High needs spending
                adjusted_needs = min(income * 0.65, actual_needs * 1.1)  # Cap at 65%
                adjusted_wants = income * 0.25
                adjusted_savings = income - adjusted_needs - adjusted_wants
            elif savings_ratio < 0.5:  # Low savings
                adjusted_savings = income * 0.25  # Increase savings target
                adjusted_needs = min(income * 0.55, actual_needs * 1.05)
                adjusted_wants = income - adjusted_needs - adjusted_savings
            else:  # Balanced spending
                adjusted_needs = income * 0.50
                adjusted_wants = income * 0.30
                adjusted_savings = income * 0.20
            
            return {
                'needs': max(0, adjusted_needs),
                'wants': max(0, adjusted_wants), 
                'savings': max(0, adjusted_savings)
            }
            
        except Exception as e:
            print(f"Error applying budget rule: {e}")
            # Return default 50/30/20 if error
            return {
                'needs': income * 0.50,
                'wants': income * 0.30,
                'savings': income * 0.20
            }
    
    def generate_category_limits(self, budget_allocation: Dict[str, float