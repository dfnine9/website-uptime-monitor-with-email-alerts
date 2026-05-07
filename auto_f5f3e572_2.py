```python
"""
Personal Budget Recommendation Engine

This module analyzes historical spending data to generate personalized budget suggestions,
spending limits per category, and savings opportunities. It uses statistical analysis
of spending patterns and income to provide actionable financial recommendations.

Features:
- Analyzes historical spending patterns by category
- Generates personalized budget allocations based on income
- Identifies spending anomalies and potential savings opportunities
- Provides category-specific spending limits with buffer zones
- Calculates recommended emergency fund targets

The engine uses the 50/30/20 budgeting rule as a baseline and adjusts based on
individual spending patterns and income levels.
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random


class BudgetRecommendationEngine:
    """Analyzes spending data and generates personalized budget recommendations."""
    
    def __init__(self):
        self.spending_categories = [
            'housing', 'transportation', 'food', 'utilities', 'healthcare',
            'entertainment', 'shopping', 'education', 'personal_care', 'miscellaneous'
        ]
        
    def generate_sample_data(self, months: int = 6) -> Tuple[float, List[Dict]]:
        """Generate sample historical spending data for demonstration."""
        try:
            # Generate sample monthly income
            base_income = random.uniform(3500, 8000)
            income = base_income + random.uniform(-200, 200)
            
            # Generate historical spending data
            spending_data = []
            for month in range(months):
                monthly_data = {
                    'month': (datetime.now() - timedelta(days=30 * month)).strftime('%Y-%m'),
                    'income': income + random.uniform(-300, 300),
                    'expenses': {}
                }
                
                # Generate category spending with realistic patterns
                total_expenses = 0
                for category in self.spending_categories:
                    if category == 'housing':
                        amount = random.uniform(0.25, 0.35) * income
                    elif category == 'transportation':
                        amount = random.uniform(0.10, 0.20) * income
                    elif category == 'food':
                        amount = random.uniform(0.10, 0.15) * income
                    elif category == 'utilities':
                        amount = random.uniform(0.05, 0.10) * income
                    else:
                        amount = random.uniform(0.02, 0.08) * income
                    
                    # Add some randomness
                    amount *= random.uniform(0.7, 1.3)
                    monthly_data['expenses'][category] = round(amount, 2)
                    total_expenses += amount
                
                monthly_data['total_expenses'] = round(total_expenses, 2)
                spending_data.append(monthly_data)
                
            return income, spending_data
            
        except Exception as e:
            print(f"Error generating sample data: {str(e)}")
            raise
    
    def analyze_spending_patterns(self, spending_data: List[Dict]) -> Dict:
        """Analyze historical spending to identify patterns and trends."""
        try:
            analysis = {
                'category_averages': {},
                'category_trends': {},
                'spending_volatility': {},
                'total_average': 0,
                'savings_rate': 0
            }
            
            # Calculate averages and volatility for each category
            for category in self.spending_categories:
                amounts = [month['expenses'].get(category, 0) for month in spending_data]
                if amounts:
                    analysis['category_averages'][category] = statistics.mean(amounts)
                    analysis['spending_volatility'][category] = statistics.stdev(amounts) if len(amounts) > 1 else 0
                    
                    # Simple trend calculation (last 3 months vs first 3 months)
                    if len(amounts) >= 6:
                        recent_avg = statistics.mean(amounts[:3])
                        older_avg = statistics.mean(amounts[-3:])
                        trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
                        analysis['category_trends'][category] = trend
            
            # Calculate overall metrics
            total_expenses = [month['total_expenses'] for month in spending_data]
            total_income = [month['income'] for month in spending_data]
            
            if total_expenses and total_income:
                analysis['total_average'] = statistics.mean(total_expenses)
                avg_income = statistics.mean(total_income)
                analysis['savings_rate'] = (avg_income - analysis['total_average']) / avg_income
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {str(e)}")
            raise
    
    def generate_budget_recommendations(self, income: float, analysis: Dict) -> Dict:
        """Generate personalized budget recommendations based on analysis."""
        try:
            recommendations = {
                'monthly_income': income,
                'category_limits': {},
                'savings_target': 0,
                'emergency_fund_target': 0,
                'budget_allocation': {},
                'optimization_suggestions': []
            }
            
            # Base budget allocations (50/30/20 rule adapted)
            base_allocations = {
                'housing': 0.28,
                'transportation': 0.15,
                'food': 0.12,
                'utilities': 0.08,
                'healthcare': 0.05,
                'entertainment': 0.08,
                'shopping': 0.07,
                'education': 0.03,
                'personal_care': 0.04,
                'miscellaneous': 0.05,
                'savings': 0.20
            }
            
            # Adjust allocations based on historical patterns
            total_historical_spending = sum(analysis['category_averages'].values())
            spending_ratio = min(total_historical_spending / income, 0.85)  # Cap at 85%
            
            for category in self.spending_categories:
                historical_avg = analysis['category_averages'].get(category, 0)
                base_amount = income * base_allocations[category]
                
                # Blend historical average with base recommendation
                if historical_avg > 0:
                    recommended_amount = (historical_avg * 0.7) + (base_amount * 0.3)
                else:
                    recommended_amount = base_amount
                
                # Add buffer for volatile categories
                volatility = analysis['spending_volatility'].get(category, 0)
                if volatility > recommended_amount * 0.2:  # High volatility
                    recommended_amount *= 1.15  # Add 15% buffer
                
                recommendations['category_limits'][category] = round(recommended_amount, 2)
                recommendations['budget_allocation'][category] = round(
                    recommended_amount / income * 100, 1
                )
            
            # Calculate savings target
            total_allocated = sum(recommendations['category_limits'].values())
            recommendations['savings_target'] = max(income - total_allocated, income * 0.10)
            recommendations['emergency_fund_target'] = total_allocated * 6  # 6 months expenses
            
            # Generate optimization suggestions
            recommendations['optimization_suggestions'] = self._generate_suggestions(
                income, analysis, recommendations
            )
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            raise
    
    def _generate_suggestions(self, income: float, analysis: Dict, recommendations: Dict) -> List[str]:
        """Generate personalized optimization suggestions."""
        suggestions = []
        
        try:
            # High spending categories
            for category, amount in recommendations['category_limits'].items():
                percentage = (amount / income) * 100
                
                if category == 'housing' and percentage > 30:
                    suggestions.append(f"Housing costs ({percentage:.1f}%) exceed recommended 30%. Consider refinancing or finding more affordable housing.")
                
                elif category == 'transportation' and percentage > 20:
                    suggestions.append(f"Transportation costs ({percentage:.1f}%) are high. Consider public