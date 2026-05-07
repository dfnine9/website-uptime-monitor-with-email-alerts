```python
"""
Personal Spending Analysis Engine

A comprehensive tool for analyzing personal spending patterns that:
- Calculates monthly and weekly spending totals by category
- Identifies spending trends over time
- Detects unusual transactions based on statistical analysis
- Monitors budget threshold breaches
- Provides actionable insights for financial management

The engine processes transaction data and generates detailed reports
including anomaly detection, trend analysis, and budget compliance monitoring.
"""

import json
import statistics
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import math


class SpendingAnalysisEngine:
    def __init__(self):
        self.transactions = []
        self.categories = set()
        self.budgets = {}
        
    def add_transaction(self, date: str, amount: float, category: str, description: str = ""):
        """Add a transaction to the analysis dataset."""
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            transaction = {
                'date': parsed_date,
                'amount': abs(amount),  # Ensure positive for spending
                'category': category.lower(),
                'description': description
            }
            self.transactions.append(transaction)
            self.categories.add(category.lower())
        except ValueError as e:
            print(f"Error adding transaction: Invalid date format. Use YYYY-MM-DD. {e}")
    
    def set_budget(self, category: str, monthly_limit: float):
        """Set monthly budget limit for a category."""
        self.budgets[category.lower()] = monthly_limit
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        for transaction in self.transactions:
            month_key = transaction['date'].strftime("%Y-%m")
            category = transaction['category']
            monthly_data[month_key][category] += transaction['amount']
        
        return dict(monthly_data)
    
    def calculate_weekly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate weekly spending totals by category."""
        weekly_data = defaultdict(lambda: defaultdict(float))
        
        for transaction in self.transactions:
            # Get Monday of the week as the week identifier
            monday = transaction['date'] - timedelta(days=transaction['date'].weekday())
            week_key = monday.strftime("%Y-W%U")
            category = transaction['category']
            weekly_data[week_key][category] += transaction['amount']
        
        return dict(weekly_data)
    
    def identify_spending_trends(self) -> Dict[str, Dict[str, Any]]:
        """Identify spending trends by category over time."""
        monthly_totals = self.calculate_monthly_totals()
        trends = {}
        
        for category in self.categories:
            category_monthly = []
            months = []
            
            for month, categories in monthly_totals.items():
                amount = categories.get(category, 0)
                category_monthly.append(amount)
                months.append(month)
            
            if len(category_monthly) >= 2:
                # Calculate trend direction
                recent_months = category_monthly[-3:] if len(category_monthly) >= 3 else category_monthly
                if len(recent_months) >= 2:
                    trend_direction = "increasing" if recent_months[-1] > recent_months[0] else "decreasing"
                    if recent_months[-1] == recent_months[0]:
                        trend_direction = "stable"
                else:
                    trend_direction = "insufficient_data"
                
                # Calculate average and variance
                avg_spending = statistics.mean(category_monthly)
                variance = statistics.variance(category_monthly) if len(category_monthly) > 1 else 0
                
                trends[category] = {
                    'direction': trend_direction,
                    'average_monthly': round(avg_spending, 2),
                    'variance': round(variance, 2),
                    'latest_month': round(category_monthly[-1], 2),
                    'data_points': len(category_monthly)
                }
        
        return trends
    
    def detect_unusual_transactions(self, threshold_multiplier: float = 2.0) -> List[Dict[str, Any]]:
        """Detect transactions that are unusually large for their category."""
        unusual_transactions = []
        
        # Group transactions by category
        category_amounts = defaultdict(list)
        for transaction in self.transactions:
            category_amounts[transaction['category']].append(transaction['amount'])
        
        # Calculate thresholds for each category
        category_thresholds = {}
        for category, amounts in category_amounts.items():
            if len(amounts) >= 3:  # Need at least 3 transactions for meaningful statistics
                mean_amount = statistics.mean(amounts)
                std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
                threshold = mean_amount + (threshold_multiplier * std_dev)
                category_thresholds[category] = threshold
        
        # Find unusual transactions
        for transaction in self.transactions:
            category = transaction['category']
            if category in category_thresholds:
                if transaction['amount'] > category_thresholds[category]:
                    unusual_transactions.append({
                        'date': transaction['date'].strftime("%Y-%m-%d"),
                        'amount': transaction['amount'],
                        'category': category,
                        'description': transaction['description'],
                        'threshold': round(category_thresholds[category], 2),
                        'deviation': round(transaction['amount'] - category_thresholds[category], 2)
                    })
        
        return sorted(unusual_transactions, key=lambda x: x['deviation'], reverse=True)
    
    def check_budget_breaches(self) -> Dict[str, Dict[str, Any]]:
        """Check for budget threshold breaches by category."""
        monthly_totals = self.calculate_monthly_totals()
        breaches = {}
        
        for month, categories in monthly_totals.items():
            month_breaches = {}
            
            for category, amount in categories.items():
                if category in self.budgets:
                    budget_limit = self.budgets[category]
                    if amount > budget_limit:
                        month_breaches[category] = {
                            'spent': round(amount, 2),
                            'budget': budget_limit,
                            'overspend': round(amount - budget_limit, 2),
                            'percentage_over': round(((amount - budget_limit) / budget_limit) * 100, 2)
                        }
            
            if month_breaches:
                breaches[month] = month_breaches
        
        return breaches
    
    def generate_insights(self) -> Dict[str, Any]:
        """Generate actionable insights from the spending analysis."""
        insights = {
            'summary': {},
            'recommendations': [],
            'alerts': []
        }
        
        # Overall spending summary
        total_spending = sum(t['amount'] for t in self.transactions)
        insights['summary']['total_transactions'] = len(self.transactions)
        insights['summary']['total_spending'] = round(total_spending, 2)
        insights['summary']['average_transaction'] = round(total_spending / len(self.transactions), 2) if self.transactions else 0
        
        # Category analysis
        category_totals = defaultdict(float)
        for transaction in self.transactions:
            category_totals[transaction['category']] += transaction['amount']
        
        top_category = max(category_totals.items(), key=lambda x: x[1]) if category_totals else None
        if top_category:
            insights['summary']['top_spending_category'] = {
                'category': top_category[0],
                'amount': round(top_category[1], 2),
                'percentage': round((top_category[1] / total_spending) * 100, 2)
            }
        
        # Recommendations based on trends
        trends = self.identify_spending_trends()
        for