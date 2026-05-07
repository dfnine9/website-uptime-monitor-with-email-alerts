```python
#!/usr/bin/env python3
"""
Personal Budget Recommendation System

This module implements a comprehensive budget analysis and recommendation system that:
- Analyzes historical spending patterns across different categories
- Generates personalized budget suggestions based on income and spending history
- Provides overspending alerts and recommendations
- Tracks monthly trends and identifies anomalies
- Offers actionable insights for financial optimization

The system uses statistical analysis to understand spending behavior and provides
data-driven recommendations for budget allocation and expense management.
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import re


class BudgetRecommendationSystem:
    """Main class for budget analysis and recommendations."""
    
    def __init__(self):
        self.categories = [
            'Housing', 'Transportation', 'Food', 'Healthcare', 'Entertainment',
            'Shopping', 'Utilities', 'Insurance', 'Savings', 'Debt', 'Other'
        ]
        self.transactions = []
        self.monthly_income = 0
        self.spending_patterns = {}
        
    def add_transaction(self, amount: float, category: str, date: str, description: str = ""):
        """Add a transaction to the system."""
        try:
            transaction = {
                'amount': float(amount),
                'category': category.title(),
                'date': datetime.strptime(date, '%Y-%m-%d'),
                'description': description
            }
            self.transactions.append(transaction)
            return True
        except (ValueError, TypeError) as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def set_monthly_income(self, income: float):
        """Set the user's monthly income."""
        try:
            self.monthly_income = float(income)
            return True
        except (ValueError, TypeError):
            print("Error: Invalid income amount")
            return False
    
    def analyze_spending_patterns(self) -> Dict:
        """Analyze spending patterns across categories and time periods."""
        try:
            if not self.transactions:
                return {}
            
            # Group transactions by month and category
            monthly_spending = {}
            category_totals = {cat: [] for cat in self.categories}
            
            for transaction in self.transactions:
                month_key = transaction['date'].strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                if month_key not in monthly_spending:
                    monthly_spending[month_key] = {cat: 0 for cat in self.categories}
                
                if category in self.categories:
                    monthly_spending[month_key][category] += amount
                    category_totals[category].append(amount)
                else:
                    monthly_spending[month_key]['Other'] += amount
                    category_totals['Other'].append(amount)
            
            # Calculate statistics for each category
            patterns = {}
            for category, amounts in category_totals.items():
                if amounts:
                    patterns[category] = {
                        'average_monthly': sum(amounts) / len(set(t['date'].strftime('%Y-%m') for t in self.transactions)),
                        'median': statistics.median(amounts),
                        'std_dev': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                        'max': max(amounts),
                        'min': min(amounts),
                        'total_transactions': len(amounts)
                    }
            
            self.spending_patterns = patterns
            return patterns
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}
    
    def generate_budget_recommendations(self) -> Dict:
        """Generate personalized budget recommendations based on spending patterns."""
        try:
            if not self.spending_patterns or self.monthly_income <= 0:
                return {}
            
            recommendations = {}
            total_recommended = 0
            
            # Standard budget allocation percentages (50/30/20 rule adjusted)
            standard_allocations = {
                'Housing': 0.30,
                'Transportation': 0.15,
                'Food': 0.12,
                'Healthcare': 0.05,
                'Entertainment': 0.08,
                'Shopping': 0.05,
                'Utilities': 0.08,
                'Insurance': 0.04,
                'Savings': 0.20,
                'Debt': 0.10,
                'Other': 0.03
            }
            
            for category in self.categories:
                if category in self.spending_patterns:
                    current_avg = self.spending_patterns[category]['average_monthly']
                    standard_amount = self.monthly_income * standard_allocations.get(category, 0.03)
                    
                    # Adjust recommendation based on spending history
                    if current_avg > standard_amount * 1.2:
                        # High spending category - recommend gradual reduction
                        recommended = current_avg * 0.9
                    elif current_avg < standard_amount * 0.5:
                        # Low spending category - can increase if desired
                        recommended = min(standard_amount, current_avg * 1.1)
                    else:
                        # Reasonable spending - use average of current and standard
                        recommended = (current_avg + standard_amount) / 2
                else:
                    # No spending history - use standard allocation
                    recommended = self.monthly_income * standard_allocations.get(category, 0.03)
                
                recommendations[category] = {
                    'recommended_amount': round(recommended, 2),
                    'current_average': round(self.spending_patterns.get(category, {}).get('average_monthly', 0), 2),
                    'standard_allocation': round(self.monthly_income * standard_allocations.get(category, 0.03), 2)
                }
                total_recommended += recommended
            
            # Adjust if total exceeds income
            if total_recommended > self.monthly_income:
                adjustment_factor = self.monthly_income / total_recommended
                for category in recommendations:
                    recommendations[category]['recommended_amount'] *= adjustment_factor
                    recommendations[category]['recommended_amount'] = round(recommendations[category]['recommended_amount'], 2)
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating budget recommendations: {e}")
            return {}
    
    def check_overspending_alerts(self, current_month_spending: Dict[str, float] = None) -> List[Dict]:
        """Check for overspending alerts in current month."""
        try:
            if current_month_spending is None:
                # Use current month's data from transactions
                current_month = datetime.now().strftime('%Y-%m')
                current_month_spending = {cat: 0 for cat in self.categories}
                
                for transaction in self.transactions:
                    if transaction['date'].strftime('%Y-%m') == current_month:
                        category = transaction['category']
                        if category in self.categories:
                            current_month_spending[category] += transaction['amount']
                        else:
                            current_month_spending['Other'] += transaction['amount']
            
            recommendations = self.generate_budget_recommendations()
            alerts = []
            
            for category, spent in current_month_spending.items():
                if spent > 0 and category in recommendations:
                    recommended = recommendations[category]['recommended_amount']
                    if spent > recommended * 1.1:  # 10% threshold
                        overspend_amount = spent - recommended
                        overspend_percentage = ((spent - recommended) / recommended) * 100
                        
                        alerts.append({
                            'category': category,
                            'spent': round(spent, 2),
                            'recommended': round(recommended, 2),
                            'overspend_amount': round(overspend_amount, 2),
                            'overspend_percentage': round(overspend_percentage, 1),
                            'severity': 'HIGH' if overspend_percentage > 50 else 'MEDIUM' if overspend_percentage > 25 else 'LOW'
                        })
            
            return sorted(alerts, key=lambda x: x['overspend_percentage'],