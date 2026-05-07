```python
"""
Budget Recommendation Generator

This module analyzes historical spending patterns and generates personalized budget
recommendations with savings goals and monthly spending limits for each category.

Features:
- Analyzes spending trends across multiple categories
- Applies configurable savings percentage rules
- Generates monthly spending limits based on historical data
- Provides actionable budget recommendations
- Includes error handling for data validation

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class BudgetRecommendationGenerator:
    def __init__(self):
        self.categories = [
            'Housing', 'Food', 'Transportation', 'Utilities', 'Healthcare',
            'Entertainment', 'Shopping', 'Education', 'Insurance', 'Miscellaneous'
        ]
        self.savings_rules = {
            'emergency_fund': 0.20,  # 20% for emergency fund
            'retirement': 0.15,      # 15% for retirement
            'short_term_goals': 0.10 # 10% for short-term goals
        }
    
    def generate_sample_data(self) -> List[Dict]:
        """Generate sample historical spending data for demonstration."""
        import random
        
        sample_data = []
        base_amounts = {
            'Housing': 1500, 'Food': 600, 'Transportation': 400,
            'Utilities': 200, 'Healthcare': 300, 'Entertainment': 250,
            'Shopping': 300, 'Education': 150, 'Insurance': 180,
            'Miscellaneous': 200
        }
        
        # Generate 12 months of data
        for month in range(1, 13):
            monthly_data = {
                'month': f"2023-{month:02d}",
                'expenses': {}
            }
            
            for category in self.categories:
                # Add some variance to base amounts (±30%)
                variance = random.uniform(0.7, 1.3)
                amount = round(base_amounts[category] * variance, 2)
                monthly_data['expenses'][category] = amount
            
            sample_data.append(monthly_data)
        
        return sample_data
    
    def analyze_spending_patterns(self, historical_data: List[Dict]) -> Dict[str, Dict]:
        """
        Analyze historical spending to identify patterns and trends.
        
        Args:
            historical_data: List of monthly spending records
            
        Returns:
            Dictionary with analysis results for each category
        """
        try:
            analysis = {}
            
            for category in self.categories:
                amounts = []
                for month_data in historical_data:
                    if category in month_data.get('expenses', {}):
                        amounts.append(month_data['expenses'][category])
                
                if amounts:
                    analysis[category] = {
                        'average': round(statistics.mean(amounts), 2),
                        'median': round(statistics.median(amounts), 2),
                        'min': min(amounts),
                        'max': max(amounts),
                        'std_dev': round(statistics.stdev(amounts) if len(amounts) > 1 else 0, 2),
                        'trend': self._calculate_trend(amounts)
                    }
                else:
                    analysis[category] = {
                        'average': 0, 'median': 0, 'min': 0, 'max': 0,
                        'std_dev': 0, 'trend': 'stable'
                    }
            
            return analysis
            
        except Exception as e:
            raise ValueError(f"Error analyzing spending patterns: {str(e)}")
    
    def _calculate_trend(self, amounts: List[float]) -> str:
        """Calculate spending trend (increasing, decreasing, or stable)."""
        if len(amounts) < 3:
            return 'stable'
        
        # Compare first third with last third of data
        first_third = amounts[:len(amounts)//3]
        last_third = amounts[-len(amounts)//3:]
        
        first_avg = statistics.mean(first_third)
        last_avg = statistics.mean(last_third)
        
        change_percent = (last_avg - first_avg) / first_avg * 100
        
        if change_percent > 10:
            return 'increasing'
        elif change_percent < -10:
            return 'decreasing'
        else:
            return 'stable'
    
    def calculate_total_income_estimate(self, analysis: Dict[str, Dict]) -> float:
        """Estimate total income based on spending patterns."""
        total_expenses = sum(cat_data['average'] for cat_data in analysis.values())
        # Assume income is 20% higher than expenses (basic financial health)
        estimated_income = total_expenses * 1.2
        return round(estimated_income, 2)
    
    def generate_savings_recommendations(self, estimated_income: float) -> Dict[str, float]:
        """Generate savings recommendations based on income and rules."""
        try:
            savings_recommendations = {}
            
            for goal, percentage in self.savings_rules.items():
                amount = estimated_income * percentage
                savings_recommendations[goal] = round(amount, 2)
            
            return savings_recommendations
            
        except Exception as e:
            raise ValueError(f"Error generating savings recommendations: {str(e)}")
    
    def generate_monthly_limits(self, analysis: Dict[str, Dict], 
                              estimated_income: float,
                              savings_total: float) -> Dict[str, float]:
        """
        Generate recommended monthly spending limits for each category.
        
        Args:
            analysis: Spending pattern analysis
            estimated_income: Estimated monthly income
            savings_total: Total monthly savings target
            
        Returns:
            Dictionary with recommended monthly limits per category
        """
        try:
            available_for_expenses = estimated_income - savings_total
            current_total_expenses = sum(cat_data['average'] for cat_data in analysis.values())
            
            # Calculate adjustment factor to fit within budget
            adjustment_factor = available_for_expenses / current_total_expenses if current_total_expenses > 0 else 1
            
            monthly_limits = {}
            
            for category, data in analysis.items():
                # Base limit on historical average, adjusted for budget constraints
                base_limit = data['average'] * adjustment_factor
                
                # Apply trend-based adjustments
                if data['trend'] == 'increasing':
                    # Reduce limit for increasing trend categories
                    adjusted_limit = base_limit * 0.9
                elif data['trend'] == 'decreasing':
                    # Maintain current level for decreasing trends
                    adjusted_limit = base_limit * 1.05
                else:
                    # Stable trend
                    adjusted_limit = base_limit
                
                # Ensure minimum reasonable amounts
                if category in ['Housing', 'Food', 'Utilities']:
                    minimum_amount = data['average'] * 0.8  # Essential categories
                    adjusted_limit = max(adjusted_limit, minimum_amount)
                
                monthly_limits[category] = round(adjusted_limit, 2)
            
            return monthly_limits
            
        except Exception as e:
            raise ValueError(f"Error generating monthly limits: {str(e)}")
    
    def generate_recommendations_report(self, analysis: Dict[str, Dict],
                                      estimated_income: float,
                                      savings_recommendations: Dict[str, float],
                                      monthly_limits: Dict[str, float]) -> str:
        """Generate a comprehensive budget recommendations report."""
        try:
            report = []
            report.append("=" * 60)
            report.append("PERSONALIZED BUDGET RECOMMENDATIONS")
            report.append("=" * 60)
            report.append("")
            
            # Income and savings overview
            total_savings = sum(savings_recommendations.values())
            total_expenses = sum(monthly_limits.values())
            
            report.append("FINANCIAL OVERVIEW")
            report.append("-" * 20)
            report.append(f"Estimated Monthly Income: ${estimated_income:,.2f}")
            report.append(f"Total Recommended Savings: ${total_savings:,.2f