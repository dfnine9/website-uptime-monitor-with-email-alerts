```python
#!/usr/bin/env python3
"""
Personalized Budget Recommendation System

This module creates personalized budget recommendations based on historical spending patterns,
income data, and financial goals using rule-based algorithms. It analyzes spending categories,
calculates averages, and provides actionable budget suggestions to help users achieve their
financial objectives.

The system uses rule-based algorithms to:
- Analyze historical spending patterns across different categories
- Calculate income-to-expense ratios
- Generate budget recommendations based on financial goals
- Provide alerts for overspending categories
- Suggest reallocation strategies for better financial health

Author: AI Assistant
Date: 2024
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sys


class BudgetRecommendationEngine:
    """Rule-based budget recommendation engine."""
    
    def __init__(self):
        self.spending_categories = {
            'housing': {'priority': 1, 'recommended_max': 0.30},
            'food': {'priority': 2, 'recommended_max': 0.15},
            'transportation': {'priority': 3, 'recommended_max': 0.15},
            'utilities': {'priority': 4, 'recommended_max': 0.10},
            'healthcare': {'priority': 5, 'recommended_max': 0.08},
            'entertainment': {'priority': 6, 'recommended_max': 0.05},
            'shopping': {'priority': 7, 'recommended_max': 0.05},
            'savings': {'priority': 1, 'recommended_min': 0.20},
            'emergency_fund': {'priority': 2, 'recommended_min': 0.10}
        }
    
    def analyze_spending_patterns(self, historical_data: List[Dict]) -> Dict:
        """Analyze historical spending patterns and calculate averages."""
        try:
            category_totals = {}
            monthly_totals = {}
            
            for transaction in historical_data:
                category = transaction['category']
                amount = float(transaction['amount'])
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = f"{date.year}-{date.month:02d}"
                
                # Track category spending
                if category not in category_totals:
                    category_totals[category] = []
                category_totals[category].append(amount)
                
                # Track monthly totals
                if month_key not in monthly_totals:
                    monthly_totals[month_key] = 0
                monthly_totals[month_key] += amount
            
            # Calculate averages
            analysis = {
                'category_averages': {},
                'monthly_average_spending': statistics.mean(monthly_totals.values()) if monthly_totals else 0,
                'spending_trends': {}
            }
            
            for category, amounts in category_totals.items():
                analysis['category_averages'][category] = {
                    'average': statistics.mean(amounts),
                    'median': statistics.median(amounts),
                    'max': max(amounts),
                    'min': min(amounts),
                    'total_transactions': len(amounts)
                }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {str(e)}")
            return {}
    
    def calculate_budget_recommendations(self, 
                                       income: float, 
                                       spending_analysis: Dict, 
                                       financial_goals: Dict) -> Dict:
        """Generate personalized budget recommendations based on rules."""
        try:
            recommendations = {
                'monthly_budget': {},
                'adjustments_needed': [],
                'goal_progress': {},
                'alerts': []
            }
            
            # Rule 1: 50/30/20 rule as baseline
            needs_budget = income * 0.50
            wants_budget = income * 0.30
            savings_budget = income * 0.20
            
            category_averages = spending_analysis.get('category_averages', {})
            
            # Rule 2: Adjust based on historical spending
            for category, config in self.spending_categories.items():
                if category in ['savings', 'emergency_fund']:
                    continue
                    
                max_recommended = config['recommended_max'] * income
                current_avg = category_averages.get(category, {}).get('average', 0)
                
                if current_avg > max_recommended:
                    recommended_amount = max_recommended
                    overspend = current_avg - max_recommended
                    recommendations['adjustments_needed'].append({
                        'category': category,
                        'current_spending': current_avg,
                        'recommended_max': max_recommended,
                        'reduction_needed': overspend,
                        'action': f"Reduce {category} spending by ${overspend:.2f}"
                    })
                    recommendations['alerts'].append(f"ALERT: {category} spending exceeds recommended limit")
                else:
                    recommended_amount = min(current_avg * 1.05, max_recommended)  # Allow 5% buffer
                
                recommendations['monthly_budget'][category] = recommended_amount
            
            # Rule 3: Savings and emergency fund recommendations
            current_savings = category_averages.get('savings', {}).get('average', 0)
            recommended_savings = max(savings_budget * 0.75, income * 0.15)  # At least 15%
            
            if current_savings < recommended_savings:
                shortfall = recommended_savings - current_savings
                recommendations['adjustments_needed'].append({
                    'category': 'savings',
                    'current_amount': current_savings,
                    'recommended_amount': recommended_savings,
                    'increase_needed': shortfall,
                    'action': f"Increase savings by ${shortfall:.2f} per month"
                })
            
            recommendations['monthly_budget']['savings'] = recommended_savings
            recommendations['monthly_budget']['emergency_fund'] = income * 0.05
            
            # Rule 4: Goal-based adjustments
            if financial_goals:
                recommendations['goal_progress'] = self._analyze_goal_progress(
                    financial_goals, income, category_averages
                )
            
            # Rule 5: Balance check
            total_recommended = sum(recommendations['monthly_budget'].values())
            if total_recommended > income:
                excess = total_recommended - income
                recommendations['alerts'].append(f"WARNING: Budget exceeds income by ${excess:.2f}")
                recommendations = self._rebalance_budget(recommendations, income)
            
            return recommendations
            
        except Exception as e:
            print(f"Error calculating budget recommendations: {str(e)}")
            return {}
    
    def _analyze_goal_progress(self, goals: Dict, income: float, spending_data: Dict) -> Dict:
        """Analyze progress toward financial goals."""
        try:
            goal_analysis = {}
            
            for goal_name, goal_info in goals.items():
                target_amount = goal_info.get('target_amount', 0)
                target_date = datetime.strptime(goal_info.get('target_date', '2025-12-31'), '%Y-%m-%d')
                current_amount = goal_info.get('current_amount', 0)
                
                months_remaining = max(1, (target_date - datetime.now()).days / 30)
                amount_needed = target_amount - current_amount
                monthly_required = amount_needed / months_remaining
                
                current_allocation = spending_data.get(goal_name, {}).get('average', 0)
                
                goal_analysis[goal_name] = {
                    'target_amount': target_amount,
                    'current_amount': current_amount,
                    'amount_needed': amount_needed,
                    'months_remaining': int(months_remaining),
                    'monthly_required': monthly_required,
                    'current_monthly_allocation': current_allocation,
                    'adjustment_needed': monthly_required - current_allocation,
                    'feasible': monthly_required <= (income * 0.30)  # Max 30% of income for goals
                }
            
            return goal_analysis
            
        except Exception