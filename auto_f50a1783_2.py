```python
"""
Automated Budget Recommendation System

This module generates personalized budget recommendations using the 50/30/20 rule
(50% needs, 30% wants, 20% savings) combined with historical spending analysis
and category-specific thresholds. It analyzes spending patterns to suggest
realistic budget limits that align with financial best practices while
accommodating individual spending behaviors.

Features:
- Implements 50/30/20 budget allocation rule
- Analyzes historical spending patterns
- Sets category-specific spending thresholds
- Provides actionable budget recommendations
- Includes variance analysis and trend detection
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random


class BudgetRecommendationSystem:
    """
    Automated budget recommendation system using percentage-based allocation
    rules and historical spending analysis.
    """
    
    def __init__(self):
        self.spending_categories = {
            'housing': {'type': 'need', 'max_percent': 30, 'min_percent': 25},
            'transportation': {'type': 'need', 'max_percent': 15, 'min_percent': 10},
            'food': {'type': 'need', 'max_percent': 12, 'min_percent': 8},
            'utilities': {'type': 'need', 'max_percent': 8, 'min_percent': 5},
            'insurance': {'type': 'need', 'max_percent': 5, 'min_percent': 3},
            'healthcare': {'type': 'need', 'max_percent': 8, 'min_percent': 4},
            'entertainment': {'type': 'want', 'max_percent': 8, 'min_percent': 2},
            'dining_out': {'type': 'want', 'max_percent': 6, 'min_percent': 1},
            'shopping': {'type': 'want', 'max_percent': 8, 'min_percent': 2},
            'hobbies': {'type': 'want', 'max_percent': 5, 'min_percent': 1},
            'travel': {'type': 'want', 'max_percent': 8, 'min_percent': 0},
            'emergency_fund': {'type': 'savings', 'max_percent': 10, 'min_percent': 5},
            'retirement': {'type': 'savings', 'max_percent': 15, 'min_percent': 10},
            'investments': {'type': 'savings', 'max_percent': 10, 'min_percent': 0},
            'debt_payment': {'type': 'savings', 'max_percent': 20, 'min_percent': 5}
        }
        
        self.allocation_rules = {
            'needs': 50,
            'wants': 30,
            'savings': 20
        }
    
    def generate_sample_data(self, months: int = 6) -> List[Dict]:
        """Generate sample spending data for demonstration."""
        sample_data = []
        base_income = 5000
        
        for month in range(months):
            date = datetime.now() - timedelta(days=30 * month)
            monthly_income = base_income + random.randint(-500, 500)
            
            spending = {
                'date': date.strftime('%Y-%m'),
                'income': monthly_income,
                'housing': random.randint(1200, 1600),
                'transportation': random.randint(300, 600),
                'food': random.randint(400, 700),
                'utilities': random.randint(150, 300),
                'insurance': random.randint(200, 400),
                'healthcare': random.randint(100, 400),
                'entertainment': random.randint(100, 400),
                'dining_out': random.randint(150, 400),
                'shopping': random.randint(200, 500),
                'hobbies': random.randint(50, 300),
                'travel': random.randint(0, 800),
                'emergency_fund': random.randint(200, 500),
                'retirement': random.randint(400, 800),
                'investments': random.randint(0, 600),
                'debt_payment': random.randint(200, 600)
            }
            sample_data.append(spending)
        
        return sample_data
    
    def analyze_historical_spending(self, historical_data: List[Dict]) -> Dict:
        """Analyze historical spending patterns and calculate averages."""
        try:
            if not historical_data:
                raise ValueError("No historical data provided")
            
            analysis = {
                'average_income': 0,
                'category_averages': {},
                'category_percentages': {},
                'variance_analysis': {},
                'spending_trends': {}
            }
            
            # Calculate average income
            incomes = [month['income'] for month in historical_data]
            analysis['average_income'] = statistics.mean(incomes)
            
            # Analyze each category
            for category in self.spending_categories.keys():
                if category in historical_data[0]:
                    amounts = [month.get(category, 0) for month in historical_data]
                    
                    analysis['category_averages'][category] = statistics.mean(amounts)
                    analysis['category_percentages'][category] = (
                        analysis['category_averages'][category] / analysis['average_income'] * 100
                    )
                    
                    # Variance analysis
                    if len(amounts) > 1:
                        analysis['variance_analysis'][category] = {
                            'std_dev': statistics.stdev(amounts),
                            'min': min(amounts),
                            'max': max(amounts),
                            'volatility': 'high' if statistics.stdev(amounts) > statistics.mean(amounts) * 0.3 else 'low'
                        }
                    
                    # Simple trend analysis (last 3 months vs first 3 months)
                    if len(amounts) >= 6:
                        recent_avg = statistics.mean(amounts[:3])
                        older_avg = statistics.mean(amounts[-3:])
                        trend_direction = 'increasing' if recent_avg > older_avg else 'decreasing'
                        analysis['spending_trends'][category] = {
                            'direction': trend_direction,
                            'change_percent': ((recent_avg - older_avg) / older_avg) * 100
                        }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing historical spending: {e}")
            return {}
    
    def calculate_50_30_20_allocation(self, income: float) -> Dict:
        """Calculate budget allocation based on 50/30/20 rule."""
        try:
            allocation = {}
            
            for category, percentage in self.allocation_rules.items():
                allocation[category] = income * (percentage / 100)
            
            return allocation
            
        except Exception as e:
            print(f"Error calculating 50/30/20 allocation: {e}")
            return {}
    
    def generate_category_recommendations(self, income: float, historical_analysis: Dict) -> Dict:
        """Generate specific category budget recommendations."""
        try:
            recommendations = {}
            total_allocation = self.calculate_50_30_20_allocation(income)
            
            # Group categories by type
            categories_by_type = {'needs': [], 'wants': [], 'savings': []}
            for category, info in self.spending_categories.items():
                categories_by_type[info['type']].append(category)
            
            # Allocate budget for each type
            for budget_type, total_budget in total_allocation.items():
                type_categories = categories_by_type[budget_type]
                
                for category in type_categories:
                    category_info = self.spending_categories[category]
                    historical_avg = historical_analysis.get('category_averages', {}).get(category, 0)
                    historical_percent = historical_analysis.get('category_percentages', {}).get(category, 0)
                    
                    # Calculate