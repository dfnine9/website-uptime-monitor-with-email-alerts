```python
"""
Automated Monthly Financial Report Generator

This module generates comprehensive monthly spending reports with insights, category breakdowns,
budget recommendations, and actionable expense optimization suggestions based on historical
spending patterns. It simulates financial data analysis and provides intelligent recommendations
for personal finance management.

Features:
- Monthly spending analysis and categorization
- Historical pattern recognition and trend analysis
- Budget recommendations based on spending habits
- Actionable expense optimization suggestions
- Comprehensive report generation with insights

Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class ExpenseData:
    """Simulates expense data for demonstration purposes."""
    
    CATEGORIES = [
        'Housing', 'Transportation', 'Food & Dining', 'Shopping', 'Entertainment',
        'Bills & Utilities', 'Healthcare', 'Travel', 'Education', 'Insurance',
        'Groceries', 'Gas', 'Subscriptions', 'Miscellaneous'
    ]
    
    @staticmethod
    def generate_monthly_data(months=12):
        """Generate simulated expense data for specified number of months."""
        data = []
        base_date = datetime.now() - timedelta(days=30*months)
        
        for month in range(months):
            month_date = base_date + timedelta(days=30*month)
            month_expenses = []
            
            # Generate 20-50 transactions per month
            num_transactions = random.randint(20, 50)
            
            for _ in range(num_transactions):
                category = random.choice(ExpenseData.CATEGORIES)
                
                # Category-based amount ranges
                amount_ranges = {
                    'Housing': (800, 2500),
                    'Transportation': (50, 400),
                    'Food & Dining': (15, 150),
                    'Shopping': (25, 300),
                    'Entertainment': (20, 200),
                    'Bills & Utilities': (50, 300),
                    'Healthcare': (30, 500),
                    'Travel': (100, 1000),
                    'Education': (50, 500),
                    'Insurance': (100, 400),
                    'Groceries': (30, 200),
                    'Gas': (40, 120),
                    'Subscriptions': (10, 50),
                    'Miscellaneous': (10, 100)
                }
                
                min_amt, max_amt = amount_ranges.get(category, (10, 100))
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                expense = {
                    'date': month_date.strftime('%Y-%m-%d'),
                    'category': category,
                    'amount': amount,
                    'description': f'{category} expense'
                }
                month_expenses.append(expense)
            
            data.extend(month_expenses)
        
        return data


class FinancialAnalyzer:
    """Analyzes financial data and generates insights."""
    
    def __init__(self, expense_data):
        self.expenses = expense_data
        self.monthly_totals = self._calculate_monthly_totals()
        self.category_analysis = self._analyze_categories()
    
    def _calculate_monthly_totals(self):
        """Calculate total spending per month."""
        monthly_totals = defaultdict(float)
        
        for expense in self.expenses:
            month_key = expense['date'][:7]  # YYYY-MM format
            monthly_totals[month_key] += expense['amount']
        
        return dict(monthly_totals)
    
    def _analyze_categories(self):
        """Analyze spending by category."""
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        
        for expense in self.expenses:
            category = expense['category']
            category_totals[category] += expense['amount']
            category_counts[category] += 1
        
        category_analysis = {}
        for category in category_totals:
            category_analysis[category] = {
                'total': round(category_totals[category], 2),
                'count': category_counts[category],
                'average': round(category_totals[category] / category_counts[category], 2)
            }
        
        return category_analysis
    
    def get_spending_trends(self):
        """Analyze spending trends over time."""
        try:
            monthly_amounts = list(self.monthly_totals.values())
            
            if len(monthly_amounts) < 2:
                return {"trend": "insufficient_data", "change": 0}
            
            recent_avg = statistics.mean(monthly_amounts[-3:])  # Last 3 months
            previous_avg = statistics.mean(monthly_amounts[:-3]) if len(monthly_amounts) > 3 else monthly_amounts[0]
            
            change_percent = ((recent_avg - previous_avg) / previous_avg) * 100 if previous_avg > 0 else 0
            
            trend = "increasing" if change_percent > 5 else "decreasing" if change_percent < -5 else "stable"
            
            return {
                "trend": trend,
                "change_percent": round(change_percent, 1),
                "recent_average": round(recent_avg, 2),
                "previous_average": round(previous_avg, 2)
            }
        except Exception as e:
            return {"trend": "error", "error": str(e), "change": 0}
    
    def identify_top_categories(self, limit=5):
        """Identify top spending categories."""
        try:
            sorted_categories = sorted(
                self.category_analysis.items(),
                key=lambda x: x[1]['total'],
                reverse=True
            )
            return sorted_categories[:limit]
        except Exception as e:
            print(f"Error identifying top categories: {e}")
            return []
    
    def calculate_budget_recommendations(self):
        """Generate budget recommendations based on historical data."""
        try:
            recommendations = {}
            monthly_amounts = list(self.monthly_totals.values())
            
            if not monthly_amounts:
                return recommendations
            
            avg_monthly_spending = statistics.mean(monthly_amounts)
            std_dev = statistics.stdev(monthly_amounts) if len(monthly_amounts) > 1 else 0
            
            # Overall budget recommendation
            recommendations['total_monthly_budget'] = round(avg_monthly_spending + std_dev, 2)
            
            # Category-based recommendations
            recommendations['categories'] = {}
            total_category_spending = sum(cat['total'] for cat in self.category_analysis.values())
            
            for category, data in self.category_analysis.items():
                monthly_avg = data['total'] / len(self.monthly_totals)
                percentage = (data['total'] / total_category_spending) * 100
                
                recommendations['categories'][category] = {
                    'monthly_budget': round(monthly_avg * 1.1, 2),  # 10% buffer
                    'percentage_of_total': round(percentage, 1),
                    'priority': 'high' if percentage > 20 else 'medium' if percentage > 10 else 'low'
                }
            
            return recommendations
        except Exception as e:
            print(f"Error calculating budget recommendations: {e}")
            return {}
    
    def generate_optimization_suggestions(self):
        """Generate actionable expense optimization suggestions."""
        suggestions = []
        
        try:
            # Analyze top spending categories
            top_categories = self.identify_top_categories(3)
            
            for category, data in top_categories:
                if data['total'] > 1000:  # Significant spending
                    if category == 'Food & Dining':
                        suggestions.append({
                            'category': category,
                            'suggestion': 'Consider meal planning and cooking at home more often',
                            'potential_savings': round(data['total'] * 0.3, 2),
                            'priority': 'high'
                        })
                    elif category == 'Shopping':
                        suggestions.append({
                            'category': category,
                            'suggestion':