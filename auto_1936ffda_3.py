```python
"""
Automated Budget Analysis and Recommendation System

This module analyzes spending patterns from sample financial data and generates
comprehensive budget recommendations including:
- Suggested budget allocations per category based on historical spending
- Identification of overspending areas compared to recommended limits
- Actionable recommendations for expense optimization
- Trend analysis and seasonal spending patterns

The system uses statistical analysis to provide data-driven insights for
personal or business financial planning.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
import random


class BudgetAnalyzer:
    def __init__(self):
        self.spending_data = []
        self.category_limits = {
            'housing': 0.30,      # 30% of income
            'food': 0.15,         # 15% of income
            'transportation': 0.15, # 15% of income
            'utilities': 0.10,    # 10% of income
            'entertainment': 0.05, # 5% of income
            'healthcare': 0.05,   # 5% of income
            'shopping': 0.10,     # 10% of income
            'savings': 0.20,      # 20% of income
            'other': 0.05         # 5% of income
        }
    
    def generate_sample_data(self, months=12):
        """Generate realistic sample spending data for demonstration"""
        categories = list(self.category_limits.keys())
        base_income = 5000
        
        for month in range(months):
            date = datetime.now() - timedelta(days=30 * month)
            monthly_income = base_income + random.uniform(-500, 1000)
            
            for category in categories:
                if category == 'savings':
                    continue  # Handle savings separately
                
                # Add some randomness to spending patterns
                base_amount = monthly_income * self.category_limits[category]
                actual_amount = base_amount * random.uniform(0.7, 1.3)
                
                self.spending_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'category': category,
                    'amount': round(actual_amount, 2),
                    'income': monthly_income,
                    'description': f'{category.title()} expenses for {date.strftime("%B %Y")}'
                })
    
    def calculate_category_spending(self):
        """Calculate total and average spending by category"""
        category_totals = defaultdict(list)
        
        for transaction in self.spending_data:
            category_totals[transaction['category']].append(transaction['amount'])
        
        category_stats = {}
        for category, amounts in category_totals.items():
            category_stats[category] = {
                'total': sum(amounts),
                'average': statistics.mean(amounts),
                'median': statistics.median(amounts),
                'transactions': len(amounts)
            }
        
        return category_stats
    
    def identify_overspending(self, average_income):
        """Identify categories where spending exceeds recommended limits"""
        category_stats = self.calculate_category_spending()
        overspending_areas = []
        
        for category, stats in category_stats.items():
            recommended_amount = average_income * self.category_limits[category]
            if stats['average'] > recommended_amount:
                overage_amount = stats['average'] - recommended_amount
                overage_percentage = (overage_amount / recommended_amount) * 100
                
                overspending_areas.append({
                    'category': category,
                    'current_spending': stats['average'],
                    'recommended_limit': recommended_amount,
                    'overage_amount': overage_amount,
                    'overage_percentage': overage_percentage
                })
        
        return sorted(overspending_areas, key=lambda x: x['overage_percentage'], reverse=True)
    
    def generate_budget_recommendations(self, average_income):
        """Generate specific budget recommendations based on analysis"""
        recommendations = []
        category_stats = self.calculate_category_spending()
        overspending_areas = self.identify_overspending(average_income)
        
        # High-level recommendations
        if overspending_areas:
            total_overage = sum(area['overage_amount'] for area in overspending_areas)
            recommendations.append({
                'type': 'critical',
                'title': 'Reduce Overall Overspending',
                'description': f'You are overspending by ${total_overage:.2f} per month across multiple categories.',
                'action': 'Focus on the top 3 overspending categories for immediate impact.'
            })
        
        # Category-specific recommendations
        for area in overspending_areas[:3]:  # Top 3 overspending areas
            category = area['category']
            
            if category == 'food':
                recommendations.append({
                    'type': 'actionable',
                    'title': f'Optimize {category.title()} Spending',
                    'description': f'Reduce food expenses by ${area["overage_amount"]:.2f}/month',
                    'action': 'Try meal planning, bulk cooking, and limit dining out to 2x per week.'
                })
            elif category == 'entertainment':
                recommendations.append({
                    'type': 'actionable',
                    'title': f'Optimize {category.title()} Spending',
                    'description': f'Reduce entertainment expenses by ${area["overage_amount"]:.2f}/month',
                    'action': 'Use free activities, streaming services instead of theaters, happy hour specials.'
                })
            elif category == 'shopping':
                recommendations.append({
                    'type': 'actionable',
                    'title': f'Optimize {category.title()} Spending',
                    'description': f'Reduce shopping expenses by ${area["overage_amount"]:.2f}/month',
                    'action': 'Implement 24-hour rule before purchases, use shopping lists, compare prices.'
                })
            else:
                recommendations.append({
                    'type': 'actionable',
                    'title': f'Optimize {category.title()} Spending',
                    'description': f'Reduce {category} expenses by ${area["overage_amount"]:.2f}/month',
                    'action': f'Review {category} subscriptions and find alternatives or negotiate better rates.'
                })
        
        # Savings recommendations
        current_savings_rate = self.calculate_savings_rate(average_income)
        target_savings_rate = 0.20  # 20%
        
        if current_savings_rate < target_savings_rate:
            savings_deficit = (target_savings_rate - current_savings_rate) * average_income
            recommendations.append({
                'type': 'savings',
                'title': 'Increase Emergency Fund Savings',
                'description': f'Current savings rate: {current_savings_rate*100:.1f}%. Target: {target_savings_rate*100:.0f}%',
                'action': f'Increase monthly savings by ${savings_deficit:.2f} through expense reduction.'
            })
        
        return recommendations
    
    def calculate_savings_rate(self, average_income):
        """Calculate current savings rate based on spending patterns"""
        category_stats = self.calculate_category_spending()
        total_spending = sum(stats['average'] for stats in category_stats.values())
        savings_amount = average_income - total_spending
        return max(0, savings_amount / average_income)
    
    def calculate_trend_analysis(self):
        """Analyze spending trends over time"""
        monthly_spending = defaultdict(lambda: defaultdict(float))
        
        for transaction in self.spending_data:
            month_key = transaction['date'][:7]  # YYYY-MM format
            monthly_spending[month_key][transaction['category']] += transaction['amount']
        
        trends = {}
        for category in self.category_limits.keys():
            if category == 'savings':
                continue
            
            amounts = []
            months = sorted(monthly_spending.keys())
            for month in months:
                amounts.append(monthly_spending[month][category])
            
            if len(amounts)