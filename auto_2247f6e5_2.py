```python
"""
Budget Recommendation Engine

This module analyzes historical spending patterns and generates personalized budget 
suggestions with alerts for overspending in specific categories. It uses statistical
analysis of spending data to recommend optimal budget allocations and monitors
current spending against those recommendations.

Features:
- Analyzes historical spending patterns across categories
- Generates personalized budget recommendations based on income and spending history
- Provides overspending alerts when current spending exceeds recommended limits
- Calculates spending trends and seasonal patterns
- Offers actionable budget optimization suggestions
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sys


class BudgetRecommendationEngine:
    def __init__(self, monthly_income: float):
        self.monthly_income = monthly_income
        self.spending_history = []
        self.current_month_spending = {}
        self.budget_recommendations = {}
        self.categories = [
            'housing', 'transportation', 'food', 'utilities', 'healthcare',
            'entertainment', 'shopping', 'savings', 'debt_payment', 'miscellaneous'
        ]
    
    def add_spending_record(self, date: str, category: str, amount: float, description: str = ""):
        """Add a spending record to the history"""
        try:
            record = {
                'date': datetime.strptime(date, '%Y-%m-%d'),
                'category': category.lower(),
                'amount': abs(amount),  # Ensure positive amount
                'description': description
            }
            self.spending_history.append(record)
            return True
        except ValueError as e:
            print(f"Error adding spending record: Invalid date format. Use YYYY-MM-DD")
            return False
        except Exception as e:
            print(f"Error adding spending record: {e}")
            return False
    
    def analyze_historical_patterns(self) -> Dict[str, Dict]:
        """Analyze historical spending patterns by category"""
        try:
            if not self.spending_history:
                return {}
            
            category_analysis = {}
            
            for category in self.categories:
                category_spending = [
                    record['amount'] for record in self.spending_history 
                    if record['category'] == category
                ]
                
                if category_spending:
                    analysis = {
                        'total_spent': sum(category_spending),
                        'average_monthly': sum(category_spending) / max(1, len(set(
                            record['date'].strftime('%Y-%m') for record in self.spending_history
                            if record['category'] == category
                        ))),
                        'median_transaction': statistics.median(category_spending),
                        'max_transaction': max(category_spending),
                        'transaction_count': len(category_spending),
                        'spending_trend': self._calculate_trend(category)
                    }
                    category_analysis[category] = analysis
            
            return category_analysis
        
        except Exception as e:
            print(f"Error analyzing historical patterns: {e}")
            return {}
    
    def _calculate_trend(self, category: str) -> str:
        """Calculate spending trend for a category over the last 3 months"""
        try:
            recent_months = []
            current_date = datetime.now()
            
            for i in range(3):
                month_start = current_date.replace(day=1) - timedelta(days=i*30)
                month_key = month_start.strftime('%Y-%m')
                
                month_spending = sum(
                    record['amount'] for record in self.spending_history
                    if record['category'] == category and 
                    record['date'].strftime('%Y-%m') == month_key
                )
                recent_months.append(month_spending)
            
            if len(recent_months) < 2:
                return "insufficient_data"
            
            if recent_months[0] > recent_months[-1] * 1.1:
                return "increasing"
            elif recent_months[0] < recent_months[-1] * 0.9:
                return "decreasing"
            else:
                return "stable"
                
        except Exception:
            return "unknown"
    
    def generate_budget_recommendations(self) -> Dict[str, float]:
        """Generate personalized budget recommendations based on 50/30/20 rule and historical data"""
        try:
            historical_analysis = self.analyze_historical_patterns()
            
            # Base budget framework (50/30/20 rule)
            needs_budget = self.monthly_income * 0.50  # Housing, utilities, food, transportation
            wants_budget = self.monthly_income * 0.30  # Entertainment, shopping, misc
            savings_budget = self.monthly_income * 0.20  # Savings and debt payment
            
            recommendations = {}
            
            # Essential categories (needs)
            essential_categories = ['housing', 'utilities', 'food', 'transportation', 'healthcare']
            essential_total = sum(
                historical_analysis.get(cat, {}).get('average_monthly', 0) 
                for cat in essential_categories
            )
            
            if essential_total > 0:
                for category in essential_categories:
                    if category in historical_analysis:
                        historical_avg = historical_analysis[category]['average_monthly']
                        # Scale based on available needs budget
                        recommendations[category] = min(
                            historical_avg * 1.1,  # 10% buffer
                            (historical_avg / essential_total) * needs_budget
                        )
                    else:
                        # Default allocations for categories with no history
                        defaults = {
                            'housing': needs_budget * 0.6,
                            'utilities': needs_budget * 0.15,
                            'food': needs_budget * 0.15,
                            'transportation': needs_budget * 0.08,
                            'healthcare': needs_budget * 0.02
                        }
                        recommendations[category] = defaults.get(category, 0)
            
            # Discretionary categories (wants)
            discretionary_categories = ['entertainment', 'shopping', 'miscellaneous']
            discretionary_total = sum(
                historical_analysis.get(cat, {}).get('average_monthly', 0) 
                for cat in discretionary_categories
            )
            
            if discretionary_total > 0:
                for category in discretionary_categories:
                    if category in historical_analysis:
                        historical_avg = historical_analysis[category]['average_monthly']
                        recommendations[category] = min(
                            historical_avg,
                            (historical_avg / discretionary_total) * wants_budget
                        )
                    else:
                        recommendations[category] = wants_budget / len(discretionary_categories)
            else:
                for category in discretionary_categories:
                    recommendations[category] = wants_budget / len(discretionary_categories)
            
            # Savings and debt payment
            if 'savings' in historical_analysis:
                recommendations['savings'] = max(
                    historical_analysis['savings']['average_monthly'],
                    savings_budget * 0.7
                )
            else:
                recommendations['savings'] = savings_budget * 0.7
            
            if 'debt_payment' in historical_analysis:
                recommendations['debt_payment'] = historical_analysis['debt_payment']['average_monthly']
            else:
                recommendations['debt_payment'] = savings_budget * 0.3
            
            self.budget_recommendations = recommendations
            return recommendations
            
        except Exception as e:
            print(f"Error generating budget recommendations: {e}")
            return {}
    
    def update_current_month_spending(self, category: str, amount: float):
        """Update current month spending for a category"""
        try:
            category = category.lower()
            if category not in self.current_month_spending:
                self.current_month_spending[category] = 0
            self.current_month_spending[category] += abs(amount)
        except Exception as e:
            print(f"Error updating current month spending: {e}")
    
    def check_overspending_alerts(self) -> List[Dict]:
        """Check for overspending in any category and generate alerts"""
        alerts = []