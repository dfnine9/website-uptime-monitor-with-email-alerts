```python
#!/usr/bin/env python3
"""
Budget Recommendation Engine

This module creates a comprehensive budget analysis system that:
1. Compares actual spending against predefined budget categories
2. Identifies overspending areas and calculates variance percentages
3. Generates actionable savings recommendations based on spending patterns
4. Produces a formatted report with insights and recommendations

The engine analyzes spending data, calculates budget variance, identifies trends,
and provides specific recommendations to help users optimize their financial habits.
"""

import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import random


class BudgetRecommendationEngine:
    """
    A comprehensive budget analysis and recommendation system.
    """
    
    def __init__(self):
        self.budget_categories = {
            'Housing': 1200.00,
            'Food': 400.00,
            'Transportation': 300.00,
            'Utilities': 150.00,
            'Entertainment': 200.00,
            'Healthcare': 100.00,
            'Shopping': 250.00,
            'Savings': 500.00,
            'Miscellaneous': 100.00
        }
        
        # Sample actual spending data (in real implementation, this would come from external source)
        self.actual_spending = {}
        self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate realistic sample spending data for demonstration."""
        try:
            # Simulate actual spending with some variance from budget
            variance_factors = {
                'Housing': 1.05,      # Slightly over
                'Food': 1.25,         # Significantly over
                'Transportation': 0.85,  # Under budget
                'Utilities': 1.15,    # Over budget
                'Entertainment': 1.45,  # Way over budget
                'Healthcare': 0.90,   # Under budget
                'Shopping': 1.35,     # Over budget
                'Savings': 0.60,      # Under target
                'Miscellaneous': 1.80  # Way over
            }
            
            for category, budget in self.budget_categories.items():
                factor = variance_factors.get(category, 1.0)
                # Add some randomness to make it more realistic
                random_factor = random.uniform(0.95, 1.05)
                self.actual_spending[category] = round(budget * factor * random_factor, 2)
                
        except Exception as e:
            print(f"Error generating sample data: {e}")
            sys.exit(1)
    
    def calculate_variance(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate variance between actual spending and budget for each category.
        
        Returns:
            Dict containing variance data for each category
        """
        try:
            variance_data = {}
            
            for category in self.budget_categories:
                budget = self.budget_categories[category]
                actual = self.actual_spending.get(category, 0)
                
                variance_amount = actual - budget
                variance_percentage = (variance_amount / budget) * 100 if budget > 0 else 0
                
                variance_data[category] = {
                    'budget': budget,
                    'actual': actual,
                    'variance_amount': variance_amount,
                    'variance_percentage': variance_percentage,
                    'over_budget': variance_amount > 0
                }
            
            return variance_data
            
        except Exception as e:
            print(f"Error calculating variance: {e}")
            return {}
    
    def identify_overspending_categories(self, variance_data: Dict) -> List[Tuple[str, float, float]]:
        """
        Identify categories where spending exceeds budget.
        
        Args:
            variance_data: Variance analysis data
            
        Returns:
            List of tuples (category, overspend_amount, overspend_percentage)
        """
        try:
            overspending = []
            
            for category, data in variance_data.items():
                if data['over_budget']:
                    overspending.append((
                        category,
                        data['variance_amount'],
                        data['variance_percentage']
                    ))
            
            # Sort by overspend percentage (highest first)
            overspending.sort(key=lambda x: x[2], reverse=True)
            return overspending
            
        except Exception as e:
            print(f"Error identifying overspending: {e}")
            return []
    
    def generate_savings_recommendations(self, variance_data: Dict, overspending: List) -> List[Dict[str, Any]]:
        """
        Generate actionable savings recommendations based on spending analysis.
        
        Args:
            variance_data: Variance analysis data
            overspending: List of overspending categories
            
        Returns:
            List of recommendation dictionaries
        """
        try:
            recommendations = []
            
            # Category-specific recommendations
            category_tips = {
                'Food': [
                    "Plan meals in advance and create shopping lists",
                    "Cook more meals at home instead of dining out",
                    "Buy generic brands and shop sales",
                    "Consider bulk buying for non-perishables"
                ],
                'Entertainment': [
                    "Look for free community events and activities",
                    "Use streaming services instead of movie theaters",
                    "Take advantage of happy hour specials",
                    "Explore outdoor activities like hiking"
                ],
                'Shopping': [
                    "Implement a 24-hour waiting period before purchases",
                    "Unsubscribe from promotional emails",
                    "Use cashback apps and compare prices",
                    "Focus on needs vs wants evaluation"
                ],
                'Transportation': [
                    "Consider carpooling or public transportation",
                    "Combine errands into single trips",
                    "Maintain your vehicle for better fuel efficiency",
                    "Walk or bike for short distances"
                ],
                'Utilities': [
                    "Adjust thermostat settings for energy savings",
                    "Switch to LED bulbs and unplug devices",
                    "Consider bundling services for discounts",
                    "Use programmable thermostats"
                ],
                'Miscellaneous': [
                    "Track all small purchases for awareness",
                    "Set up automatic transfers to savings",
                    "Review subscriptions and cancel unused ones",
                    "Use the envelope method for discretionary spending"
                ]
            }
            
            for category, overspend_amount, overspend_percentage in overspending:
                if overspend_percentage > 10:  # Focus on significant overspending
                    tips = category_tips.get(category, ["Review spending patterns and set stricter limits"])
                    
                    target_reduction = min(overspend_amount * 0.75, overspend_amount)  # Aim to reduce 75% of overspend
                    
                    recommendations.append({
                        'category': category,
                        'overspend_amount': overspend_amount,
                        'overspend_percentage': overspend_percentage,
                        'target_reduction': target_reduction,
                        'priority': 'High' if overspend_percentage > 30 else 'Medium',
                        'actionable_tips': tips[:3],  # Top 3 tips
                        'potential_monthly_savings': target_reduction
                    })
            
            # Add general recommendations
            total_overspend = sum(data['variance_amount'] for data in variance_data.values() if data['over_budget'])
            if total_overspend > 0:
                recommendations.append({
                    'category': 'General',
                    'overspend_amount': total_overspend,
                    'priority': 'High',
                    'actionable_tips': [
                        "Set up budget alerts on your banking app",
                        "Review and adjust budget categories monthly",
                        "Use the 50/30/20 rule (needs/wants/savings)",
                        "Consider using budgeting apps for tracking"
                    ],
                    'potential_monthly_savings': total_overspend * 0.60
                })
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []