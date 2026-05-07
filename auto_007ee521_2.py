```python
#!/usr/bin/env python3
"""
Budget Recommendation Engine

This module analyzes historical spending patterns and provides personalized budget 
recommendations using the 50/30/20 rule (50% needs, 30% wants, 20% savings/debt).
It suggests category-specific budget limits and identifies potential savings opportunities.

The engine processes spending data, categorizes expenses, applies budgeting rules,
and generates actionable recommendations for financial optimization.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random


class BudgetRecommendationEngine:
    """Analyzes spending patterns and generates budget recommendations."""
    
    def __init__(self):
        self.spending_categories = {
            'needs': ['housing', 'utilities', 'groceries', 'transportation', 'insurance', 'healthcare'],
            'wants': ['entertainment', 'dining_out', 'shopping', 'hobbies', 'subscriptions'],
            'savings': ['savings', 'investments', 'debt_payment', 'emergency_fund']
        }
        
        self.category_benchmarks = {
            'housing': 0.25,  # 25% of income
            'transportation': 0.15,
            'groceries': 0.12,
            'utilities': 0.08,
            'entertainment': 0.08,
            'dining_out': 0.06,
            'shopping': 0.05,
            'healthcare': 0.05,
            'insurance': 0.04,
            'subscriptions': 0.03,
            'hobbies': 0.02
        }

    def generate_sample_data(self, months: int = 6) -> List[Dict]:
        """Generate sample spending data for demonstration."""
        categories = [cat for cats in self.spending_categories.values() for cat in cats]
        spending_data = []
        
        base_income = 5000
        
        for month in range(months):
            date = datetime.now() - timedelta(days=30 * month)
            monthly_data = {
                'month': date.strftime('%Y-%m'),
                'income': base_income + random.randint(-500, 500),
                'expenses': {}
            }
            
            # Generate realistic spending patterns
            for category in categories:
                if category == 'housing':
                    amount = random.uniform(1200, 1400)
                elif category == 'groceries':
                    amount = random.uniform(400, 600)
                elif category == 'transportation':
                    amount = random.uniform(300, 500)
                elif category == 'utilities':
                    amount = random.uniform(200, 300)
                elif category == 'entertainment':
                    amount = random.uniform(200, 400)
                elif category == 'dining_out':
                    amount = random.uniform(150, 350)
                else:
                    amount = random.uniform(50, 200)
                
                monthly_data['expenses'][category] = round(amount, 2)
            
            spending_data.append(monthly_data)
        
        return spending_data

    def analyze_spending_patterns(self, data: List[Dict]) -> Dict:
        """Analyze historical spending patterns."""
        try:
            analysis = {
                'average_income': 0,
                'average_expenses': {},
                'spending_trends': {},
                'total_expenses': 0
            }
            
            if not data:
                raise ValueError("No spending data provided")
            
            # Calculate averages
            incomes = [month['income'] for month in data]
            analysis['average_income'] = statistics.mean(incomes)
            
            # Aggregate expenses by category
            all_categories = set()
            for month in data:
                all_categories.update(month['expenses'].keys())
            
            for category in all_categories:
                amounts = [month['expenses'].get(category, 0) for month in data]
                analysis['average_expenses'][category] = statistics.mean(amounts)
                
                # Calculate trend (simple slope)
                if len(amounts) > 1:
                    x_vals = list(range(len(amounts)))
                    trend = sum((x - statistics.mean(x_vals)) * (y - statistics.mean(amounts)) 
                              for x, y in zip(x_vals, amounts)) / sum((x - statistics.mean(x_vals))**2 for x in x_vals)
                    analysis['spending_trends'][category] = trend
                else:
                    analysis['spending_trends'][category] = 0
            
            analysis['total_expenses'] = sum(analysis['average_expenses'].values())
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}

    def apply_50_30_20_rule(self, income: float) -> Dict[str, float]:
        """Apply the 50/30/20 budgeting rule."""
        try:
            return {
                'needs': income * 0.50,
                'wants': income * 0.30,
                'savings': income * 0.20
            }
        except Exception as e:
            print(f"Error applying 50/30/20 rule: {e}")
            return {'needs': 0, 'wants': 0, 'savings': 0}

    def categorize_expenses(self, expenses: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Categorize expenses into needs, wants, and savings."""
        try:
            categorized = {'needs': {}, 'wants': {}, 'savings': {}}
            
            for expense, amount in expenses.items():
                for category_type, categories in self.spending_categories.items():
                    if expense in categories:
                        categorized[category_type][expense] = amount
                        break
                else:
                    # Default to wants if category not found
                    categorized['wants'][expense] = amount
            
            return categorized
            
        except Exception as e:
            print(f"Error categorizing expenses: {e}")
            return {'needs': {}, 'wants': {}, 'savings': {}}

    def suggest_category_limits(self, income: float, current_expenses: Dict[str, float]) -> Dict[str, Dict]:
        """Suggest spending limits for each category."""
        try:
            suggestions = {}
            budget_allocation = self.apply_50_30_20_rule(income)
            categorized_expenses = self.categorize_expenses(current_expenses)
            
            for category_type in ['needs', 'wants', 'savings']:
                total_budget = budget_allocation[category_type]
                current_total = sum(categorized_expenses[category_type].values())
                
                suggestions[category_type] = {
                    'budget_limit': total_budget,
                    'current_spending': current_total,
                    'difference': total_budget - current_total,
                    'categories': {}
                }
                
                # Distribute budget among subcategories
                for subcategory, current_amount in categorized_expenses[category_type].items():
                    benchmark_pct = self.category_benchmarks.get(subcategory, 0.02)
                    suggested_limit = income * benchmark_pct
                    
                    suggestions[category_type]['categories'][subcategory] = {
                        'suggested_limit': suggested_limit,
                        'current_spending': current_amount,
                        'difference': suggested_limit - current_amount,
                        'percentage_of_income': (current_amount / income) * 100
                    }
            
            return suggestions
            
        except Exception as e:
            print(f"Error suggesting category limits: {e}")
            return {}

    def identify_savings_opportunities(self, analysis: Dict, suggestions: Dict) -> List[Dict]:
        """Identify areas where spending can be reduced."""
        try:
            opportunities = []
            
            for category_type, data in suggestions.items():
                if category_type == 'savings':
                    continue
                    
                for subcategory, details in data['categories'].items():
                    current = details['current_spending']
                    suggested = details['suggested_limit']
                    trend = analysis['spending_trends'].get(