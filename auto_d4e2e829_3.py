```python
"""
Budget Recommendation Engine

This module analyzes historical spending patterns and generates personalized budget 
recommendations for different spending categories based on income and spending trends.

The engine:
1. Analyzes spending patterns across categories
2. Calculates trend-based adjustments
3. Applies income-based scaling
4. Generates realistic budget limits with safety margins

Features:
- Trend analysis using linear regression
- Income-based budget scaling
- Category-wise recommendations
- Overspending alerts
- Savings goal integration
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random


class BudgetRecommendationEngine:
    def __init__(self):
        self.categories = [
            'housing', 'food', 'transportation', 'entertainment', 
            'healthcare', 'utilities', 'shopping', 'savings'
        ]
        self.spending_history = []
        self.income_history = []
        
    def generate_sample_data(self, months: int = 12) -> None:
        """Generate sample spending and income data for demonstration"""
        base_income = 5000
        
        for i in range(months):
            # Generate monthly income with slight variation
            monthly_income = base_income + random.randint(-500, 1000)
            self.income_history.append({
                'month': i + 1,
                'income': monthly_income
            })
            
            # Generate spending data with realistic patterns
            monthly_spending = {
                'month': i + 1,
                'housing': random.randint(1200, 1500),
                'food': random.randint(400, 600),
                'transportation': random.randint(200, 400),
                'entertainment': random.randint(150, 300),
                'healthcare': random.randint(100, 250),
                'utilities': random.randint(150, 250),
                'shopping': random.randint(200, 500),
                'savings': random.randint(300, 800)
            }
            
            # Add some seasonal variations
            if i in [10, 11]:  # Holiday months
                monthly_spending['shopping'] += random.randint(200, 400)
                monthly_spending['entertainment'] += random.randint(100, 200)
            
            self.spending_history.append(monthly_spending)
    
    def calculate_spending_trends(self) -> Dict[str, float]:
        """Calculate spending trends for each category using linear regression"""
        trends = {}
        
        try:
            for category in self.categories:
                if category == 'savings':
                    continue
                    
                values = [month[category] for month in self.spending_history]
                months = list(range(1, len(values) + 1))
                
                # Simple linear regression
                n = len(values)
                sum_x = sum(months)
                sum_y = sum(values)
                sum_xy = sum(x * y for x, y in zip(months, values))
                sum_x2 = sum(x * x for x in months)
                
                if n * sum_x2 - sum_x * sum_x != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    trends[category] = slope
                else:
                    trends[category] = 0.0
                    
        except Exception as e:
            print(f"Error calculating trends: {e}")
            trends = {cat: 0.0 for cat in self.categories if cat != 'savings'}
            
        return trends
    
    def calculate_category_averages(self) -> Dict[str, float]:
        """Calculate average spending for each category"""
        averages = {}
        
        try:
            for category in self.categories:
                values = [month[category] for month in self.spending_history]
                averages[category] = statistics.mean(values)
        except Exception as e:
            print(f"Error calculating averages: {e}")
            averages = {cat: 0.0 for cat in self.categories}
            
        return averages
    
    def get_income_trend(self) -> Tuple[float, float]:
        """Calculate average income and income trend"""
        try:
            incomes = [month['income'] for month in self.income_history]
            avg_income = statistics.mean(incomes)
            
            # Calculate income trend
            months = list(range(1, len(incomes) + 1))
            n = len(incomes)
            sum_x = sum(months)
            sum_y = sum(incomes)
            sum_xy = sum(x * y for x, y in zip(months, incomes))
            sum_x2 = sum(x * x for x in months)
            
            if n * sum_x2 - sum_x * sum_x != 0:
                income_slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            else:
                income_slope = 0.0
                
            return avg_income, income_slope
            
        except Exception as e:
            print(f"Error calculating income trend: {e}")
            return 5000.0, 0.0
    
    def apply_income_scaling(self, base_budget: Dict[str, float], 
                           avg_income: float) -> Dict[str, float]:
        """Scale budget recommendations based on income level"""
        try:
            # Define income brackets and scaling factors
            if avg_income < 3000:
                scale_factor = 0.8
            elif avg_income < 5000:
                scale_factor = 1.0
            elif avg_income < 7500:
                scale_factor = 1.2
            else:
                scale_factor = 1.5
            
            scaled_budget = {}
            for category, amount in base_budget.items():
                if category == 'housing':
                    # Housing should be max 30% of income
                    max_housing = avg_income * 0.30
                    scaled_budget[category] = min(amount * scale_factor, max_housing)
                elif category == 'savings':
                    # Encourage higher savings rate for higher income
                    min_savings = avg_income * 0.20
                    scaled_budget[category] = max(amount * scale_factor, min_savings)
                else:
                    scaled_budget[category] = amount * scale_factor
            
            return scaled_budget
            
        except Exception as e:
            print(f"Error applying income scaling: {e}")
            return base_budget
    
    def generate_recommendations(self) -> Dict:
        """Generate personalized budget recommendations"""
        try:
            # Calculate base metrics
            spending_trends = self.calculate_spending_trends()
            category_averages = self.calculate_category_averages()
            avg_income, income_trend = self.get_income_trend()
            
            # Generate base budget recommendations
            base_recommendations = {}
            
            for category in self.categories:
                if category == 'savings':
                    continue
                    
                avg_spending = category_averages[category]
                trend = spending_trends.get(category, 0)
                
                # Adjust for trend (if increasing, add buffer; if decreasing, optimize)
                if trend > 0:
                    # Increasing trend - add 10% buffer
                    recommended = avg_spending * 1.10
                else:
                    # Decreasing or stable trend - slight optimization
                    recommended = avg_spending * 0.95
                
                base_recommendations[category] = max(recommended, avg_spending * 0.8)
            
            # Calculate recommended savings
            total_expenses = sum(base_recommendations.values())
            recommended_savings = max(avg_income * 0.20, avg_income - total_expenses)
            base_recommendations['savings'] = recommended_savings
            
            # Apply income-based scaling
            final_recommendations = self.apply_income_scaling(
                base_recommendations, avg_income
            )
            
            # Generate insights and alerts
            insights = self.generate_insights(
                spending_trends, category_averages, avg_income