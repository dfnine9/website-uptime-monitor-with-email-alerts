```python
"""
Budget Recommendation Engine

This module implements a comprehensive budget analysis tool that:
1. Compares actual spending against the 50/30/20 budgeting rule
2. Identifies overspending categories and patterns
3. Suggests realistic budget adjustments based on spending history
4. Provides actionable recommendations for budget optimization

The 50/30/20 rule allocates:
- 50% for needs (housing, utilities, groceries, minimum debt payments)
- 30% for wants (entertainment, dining out, hobbies, non-essential purchases)
- 20% for savings and debt repayment beyond minimums

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import random

class BudgetRecommendationEngine:
    def __init__(self):
        self.needs_categories = {
            'housing', 'utilities', 'groceries', 'transportation', 
            'insurance', 'minimum_debt_payments', 'healthcare'
        }
        self.wants_categories = {
            'dining_out', 'entertainment', 'shopping', 'hobbies',
            'subscriptions', 'personal_care', 'miscellaneous'
        }
        self.savings_categories = {
            'emergency_fund', 'retirement', 'investments', 
            'extra_debt_payments', 'savings_goals'
        }

    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate realistic sample spending data for demonstration."""
        try:
            monthly_income = 5000
            
            # Generate 6 months of spending history
            spending_history = []
            for month in range(6):
                month_data = {
                    'month': (datetime.now() - timedelta(days=30*month)).strftime('%Y-%m'),
                    'income': monthly_income + random.randint(-200, 200),
                    'needs': {
                        'housing': random.randint(1200, 1400),
                        'utilities': random.randint(150, 250),
                        'groceries': random.randint(300, 500),
                        'transportation': random.randint(200, 350),
                        'insurance': random.randint(150, 200),
                        'minimum_debt_payments': random.randint(200, 300),
                        'healthcare': random.randint(50, 150)
                    },
                    'wants': {
                        'dining_out': random.randint(200, 400),
                        'entertainment': random.randint(100, 300),
                        'shopping': random.randint(150, 350),
                        'hobbies': random.randint(50, 200),
                        'subscriptions': random.randint(50, 100),
                        'personal_care': random.randint(50, 150),
                        'miscellaneous': random.randint(100, 200)
                    },
                    'savings': {
                        'emergency_fund': random.randint(0, 200),
                        'retirement': random.randint(100, 300),
                        'investments': random.randint(0, 150),
                        'extra_debt_payments': random.randint(0, 100),
                        'savings_goals': random.randint(50, 200)
                    }
                }
                spending_history.append(month_data)
            
            return {
                'monthly_income': monthly_income,
                'spending_history': spending_history
            }
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}

    def calculate_averages(self, spending_history: List[Dict]) -> Dict[str, float]:
        """Calculate average spending across all categories."""
        try:
            averages = {'income': 0, 'needs': {}, 'wants': {}, 'savings': {}}
            
            if not spending_history:
                return averages
                
            # Calculate income average
            incomes = [month['income'] for month in spending_history]
            averages['income'] = statistics.mean(incomes)
            
            # Calculate category averages
            for category_type in ['needs', 'wants', 'savings']:
                category_totals = {}
                for month in spending_history:
                    for subcategory, amount in month[category_type].items():
                        if subcategory not in category_totals:
                            category_totals[subcategory] = []
                        category_totals[subcategory].append(amount)
                
                for subcategory, amounts in category_totals.items():
                    averages[category_type][subcategory] = statistics.mean(amounts)
            
            return averages
        except Exception as e:
            print(f"Error calculating averages: {e}")
            return {'income': 0, 'needs': {}, 'wants': {}, 'savings': {}}

    def analyze_50_30_20_compliance(self, averages: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze compliance with the 50/30/20 rule."""
        try:
            income = averages['income']
            if income <= 0:
                return {}
                
            # Calculate totals
            total_needs = sum(averages['needs'].values())
            total_wants = sum(averages['wants'].values())
            total_savings = sum(averages['savings'].values())
            
            # Calculate percentages
            needs_percentage = (total_needs / income) * 100
            wants_percentage = (total_wants / income) * 100
            savings_percentage = (total_savings / income) * 100
            
            # Calculate ideal amounts
            ideal_needs = income * 0.50
            ideal_wants = income * 0.30
            ideal_savings = income * 0.20
            
            # Calculate variances
            needs_variance = total_needs - ideal_needs
            wants_variance = total_wants - ideal_wants
            savings_variance = total_savings - ideal_savings
            
            return {
                'income': income,
                'actual': {
                    'needs': total_needs,
                    'wants': total_wants,
                    'savings': total_savings
                },
                'percentages': {
                    'needs': needs_percentage,
                    'wants': wants_percentage,
                    'savings': savings_percentage
                },
                'ideal': {
                    'needs': ideal_needs,
                    'wants': ideal_wants,
                    'savings': ideal_savings
                },
                'variances': {
                    'needs': needs_variance,
                    'wants': wants_variance,
                    'savings': savings_variance
                }
            }
        except Exception as e:
            print(f"Error analyzing 50/30/20 compliance: {e}")
            return {}

    def identify_problem_categories(self, averages: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Identify specific categories with overspending issues."""
        try:
            problems = {'overspending': [], 'underfunding': []}
            income = analysis.get('income', 0)
            
            if income <= 0:
                return problems
                
            # Define reasonable percentage thresholds for subcategories
            needs_thresholds = {
                'housing': 0.30,  # 30% max for housing
                'transportation': 0.15,  # 15% max for transportation
                'groceries': 0.10,  # 10% max for groceries
            }
            
            wants_thresholds = {
                'dining_out': 0.08,  # 8% max for dining out
                'entertainment': 0.06,  # 6% max for entertainment
                'shopping': 0.08,  # 8% max for shopping
            }
            
            # Check needs categories
            for category, amount in averages['needs'].items():
                percentage = (amount / income) * 100
                threshold = needs_thresholds.get(category, 0.05) * 100  # Default 5%
                if percentage > threshold:
                    problems['overspending'].append(f"Needs: {category} ({percentage:.1f}% vs