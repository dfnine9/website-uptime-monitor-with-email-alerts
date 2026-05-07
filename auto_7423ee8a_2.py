```python
"""
Budget Recommendation Engine

A comprehensive personal finance tool that analyzes historical spending patterns to generate
personalized monthly budget recommendations. The engine:

1. Analyzes spending patterns across different categories
2. Calculates income-to-expense ratios
3. Generates category-specific spending limits based on historical data and best practices
4. Recommends savings goals using the 50/30/20 rule as a baseline
5. Provides actionable budget insights and recommendations

The engine uses statistical analysis of historical data to identify spending trends,
seasonal variations, and areas for potential optimization. It applies financial best
practices while personalizing recommendations based on individual spending patterns.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import sys


class BudgetRecommendationEngine:
    def __init__(self):
        self.spending_categories = [
            'housing', 'transportation', 'food', 'utilities', 'healthcare',
            'entertainment', 'shopping', 'education', 'insurance', 'debt_payments',
            'savings', 'investments', 'miscellaneous'
        ]
        
        # Standard budget allocation percentages (50/30/20 rule adapted)
        self.standard_allocations = {
            'housing': 0.30,
            'transportation': 0.15,
            'food': 0.12,
            'utilities': 0.08,
            'healthcare': 0.05,
            'entertainment': 0.08,
            'shopping': 0.05,
            'education': 0.03,
            'insurance': 0.04,
            'debt_payments': 0.10,
            'savings': 0.15,
            'investments': 0.05,
            'miscellaneous': 0.05
        }

    def generate_sample_data(self) -> Tuple[List[Dict], float]:
        """Generate realistic sample financial data for demonstration"""
        import random
        
        # Sample monthly income
        monthly_income = 5500.0
        
        # Generate 12 months of spending data
        spending_data = []
        base_date = datetime.now() - timedelta(days=365)
        
        for month in range(12):
            month_date = base_date + timedelta(days=month * 30)
            monthly_spending = {
                'date': month_date.strftime('%Y-%m-%d'),
                'income': monthly_income + random.uniform(-200, 200),
                'expenses': {}
            }
            
            # Generate expenses with some seasonal variation
            seasonal_factor = 1.0
            if month in [10, 11]:  # Holiday months
                seasonal_factor = 1.2
            elif month in [5, 6, 7]:  # Summer months
                seasonal_factor = 1.1
            
            total_expenses = 0
            for category in self.spending_categories:
                if category in ['savings', 'investments']:
                    continue
                    
                base_amount = monthly_income * self.standard_allocations[category]
                # Add randomness and seasonal variation
                amount = base_amount * seasonal_factor * random.uniform(0.7, 1.3)
                monthly_spending['expenses'][category] = round(amount, 2)
                total_expenses += amount
            
            # Add actual savings based on leftover income
            leftover = monthly_spending['income'] - total_expenses
            monthly_spending['expenses']['savings'] = max(0, round(leftover * 0.7, 2))
            monthly_spending['expenses']['investments'] = max(0, round(leftover * 0.3, 2))
            
            spending_data.append(monthly_spending)
        
        return spending_data, monthly_income

    def analyze_spending_patterns(self, spending_data: List[Dict]) -> Dict:
        """Analyze historical spending patterns to identify trends"""
        try:
            category_stats = {}
            monthly_totals = []
            monthly_incomes = []
            
            for month_data in spending_data:
                monthly_incomes.append(month_data['income'])
                month_total = sum(month_data['expenses'].values())
                monthly_totals.append(month_total)
            
            # Calculate statistics for each category
            for category in self.spending_categories:
                amounts = [month['expenses'].get(category, 0) for month in spending_data]
                amounts = [amt for amt in amounts if amt > 0]  # Filter out zero values
                
                if amounts:
                    category_stats[category] = {
                        'average': round(statistics.mean(amounts), 2),
                        'median': round(statistics.median(amounts), 2),
                        'min': round(min(amounts), 2),
                        'max': round(max(amounts), 2),
                        'std_dev': round(statistics.stdev(amounts) if len(amounts) > 1 else 0, 2),
                        'trend': self._calculate_trend(amounts)
                    }
                else:
                    category_stats[category] = {
                        'average': 0, 'median': 0, 'min': 0, 'max': 0, 'std_dev': 0, 'trend': 'stable'
                    }
            
            analysis = {
                'category_stats': category_stats,
                'avg_monthly_income': round(statistics.mean(monthly_incomes), 2),
                'avg_monthly_expenses': round(statistics.mean(monthly_totals), 2),
                'income_stability': round(statistics.stdev(monthly_incomes), 2),
                'expense_stability': round(statistics.stdev(monthly_totals), 2)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}

    def _calculate_trend(self, amounts: List[float]) -> str:
        """Calculate spending trend over time"""
        try:
            if len(amounts) < 3:
                return 'stable'
            
            # Simple trend calculation using first and last third
            first_third = amounts[:len(amounts)//3]
            last_third = amounts[-len(amounts)//3:]
            
            first_avg = statistics.mean(first_third)
            last_avg = statistics.mean(last_third)
            
            change_percent = ((last_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
            
            if change_percent > 10:
                return 'increasing'
            elif change_percent < -10:
                return 'decreasing'
            else:
                return 'stable'
        except Exception:
            return 'stable'

    def generate_budget_recommendations(self, analysis: Dict) -> Dict:
        """Generate personalized budget recommendations based on analysis"""
        try:
            recommendations = {}
            monthly_income = analysis['avg_monthly_income']
            current_expenses = analysis['avg_monthly_expenses']
            
            # Calculate recommended amounts for each category
            category_recommendations = {}
            total_recommended = 0
            
            for category in self.spending_categories:
                current_avg = analysis['category_stats'][category]['average']
                trend = analysis['category_stats'][category]['trend']
                
                # Base recommendation on standard allocation
                standard_amount = monthly_income * self.standard_allocations[category]
                
                # Adjust based on current spending and trends
                if trend == 'increasing' and category not in ['savings', 'investments']:
                    # If spending is increasing, recommend slightly below current average
                    recommended = min(current_avg * 0.95, standard_amount * 1.1)
                elif trend == 'decreasing':
                    # If decreasing, allow some flexibility
                    recommended = max(current_avg * 1.05, standard_amount * 0.9)
                else:
                    # Stable spending - balance between current and standard
                    recommended = (current_avg + standard_amount) / 2
                
                # Special handling for savings and investments
                if category == 'savings':
                    # Recommend at least 10% for emergency savings
                    recommended = max(recommended, monthly_income * 0.10)
                elif category == 'investments':
                    # Recommend