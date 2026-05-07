```python
"""
Personal Finance Data Analysis Module

This module provides comprehensive analysis of spending patterns including:
- Category-wise spending breakdown and trends
- Time-based spending pattern analysis
- Anomaly detection for unusual spending behavior
- Budget variance analysis and overrun alerts
- Statistical insights into financial habits

The module uses sample data for demonstration but can be easily adapted
to work with real financial data from CSV files or APIs.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import math


class SpendingAnalyzer:
    """Analyzes spending patterns and detects financial anomalies."""
    
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        self.categories = set()
        
    def add_transaction(self, date: str, amount: float, category: str, description: str = ""):
        """Add a transaction to the analyzer."""
        try:
            transaction = {
                'date': datetime.strptime(date, '%Y-%m-%d'),
                'amount': float(amount),
                'category': category.lower(),
                'description': description
            }
            self.transactions.append(transaction)
            self.categories.add(category.lower())
        except (ValueError, TypeError) as e:
            print(f"Error adding transaction: {e}")
    
    def set_budget(self, category: str, monthly_limit: float):
        """Set monthly budget limit for a category."""
        try:
            self.budgets[category.lower()] = float(monthly_limit)
        except (ValueError, TypeError) as e:
            print(f"Error setting budget: {e}")
    
    def calculate_category_totals(self) -> Dict[str, float]:
        """Calculate total spending by category."""
        category_totals = defaultdict(float)
        
        for transaction in self.transactions:
            category_totals[transaction['category']] += transaction['amount']
        
        return dict(category_totals)
    
    def calculate_monthly_trends(self) -> Dict[str, Dict[str, float]]:
        """Calculate spending trends by month and category."""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        for transaction in self.transactions:
            month_key = transaction['date'].strftime('%Y-%m')
            monthly_data[month_key][transaction['category']] += transaction['amount']
        
        return dict(monthly_data)
    
    def detect_spending_anomalies(self, threshold_multiplier: float = 2.0) -> List[Dict]:
        """Detect unusual spending patterns using statistical analysis."""
        anomalies = []
        
        # Group transactions by category for analysis
        category_amounts = defaultdict(list)
        for transaction in self.transactions:
            category_amounts[transaction['category']].append(transaction['amount'])
        
        for category, amounts in category_amounts.items():
            if len(amounts) < 3:  # Need minimum data for statistical analysis
                continue
                
            try:
                mean_amount = statistics.mean(amounts)
                stdev_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
                threshold = mean_amount + (threshold_multiplier * stdev_amount)
                
                for transaction in self.transactions:
                    if (transaction['category'] == category and 
                        transaction['amount'] > threshold and
                        stdev_amount > 0):
                        
                        anomalies.append({
                            'date': transaction['date'].strftime('%Y-%m-%d'),
                            'category': category,
                            'amount': transaction['amount'],
                            'mean': round(mean_amount, 2),
                            'threshold': round(threshold, 2),
                            'description': transaction['description'],
                            'severity': 'high' if transaction['amount'] > threshold * 1.5 else 'medium'
                        })
            except statistics.StatisticsError as e:
                print(f"Statistical analysis error for category {category}: {e}")
        
        return sorted(anomalies, key=lambda x: x['amount'], reverse=True)
    
    def check_budget_overruns(self) -> Dict[str, Dict]:
        """Check for budget overruns by category and month."""
        monthly_trends = self.calculate_monthly_trends()
        overruns = {}
        
        for month, categories in monthly_trends.items():
            month_overruns = {}
            
            for category, spent in categories.items():
                if category in self.budgets:
                    budget_limit = self.budgets[category]
                    if spent > budget_limit:
                        month_overruns[category] = {
                            'spent': round(spent, 2),
                            'budget': budget_limit,
                            'overrun': round(spent - budget_limit, 2),
                            'percentage_over': round(((spent - budget_limit) / budget_limit) * 100, 1)
                        }
            
            if month_overruns:
                overruns[month] = month_overruns
        
        return overruns
    
    def calculate_spending_velocity(self) -> Dict[str, float]:
        """Calculate average daily spending by category."""
        if not self.transactions:
            return {}
        
        # Get date range
        dates = [t['date'] for t in self.transactions]
        date_range = (max(dates) - min(dates)).days + 1
        
        category_totals = self.calculate_category_totals()
        
        velocity = {}
        for category, total in category_totals.items():
            velocity[category] = round(total / date_range, 2)
        
        return velocity
    
    def generate_insights(self) -> Dict[str, Any]:
        """Generate comprehensive financial insights."""
        insights = {
            'total_transactions': len(self.transactions),
            'date_range': self._get_date_range(),
            'total_spending': sum(t['amount'] for t in self.transactions),
            'average_transaction': round(statistics.mean([t['amount'] for t in self.transactions]), 2) if self.transactions else 0,
            'most_expensive_category': self._get_most_expensive_category(),
            'spending_frequency': self._calculate_spending_frequency()
        }
        
        return insights
    
    def _get_date_range(self) -> Dict[str, str]:
        """Get the date range of transactions."""
        if not self.transactions:
            return {'start': 'N/A', 'end': 'N/A', 'days': 0}
        
        dates = [t['date'] for t in self.transactions]
        start_date = min(dates)
        end_date = max(dates)
        
        return {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'days': (end_date - start_date).days + 1
        }
    
    def _get_most_expensive_category(self) -> Dict[str, Any]:
        """Find the category with highest spending."""
        category_totals = self.calculate_category_totals()
        
        if not category_totals:
            return {'category': 'N/A', 'amount': 0}
        
        max_category = max(category_totals.items(), key=lambda x: x[1])
        return {'category': max_category[0], 'amount': round(max_category[1], 2)}
    
    def _calculate_spending_frequency(self) -> Dict[str, int]:
        """Calculate transaction frequency by category."""
        frequency = Counter(t['category'] for t in self.transactions)
        return dict(frequency)


def generate_sample_data(analyzer: SpendingAnalyzer):
    """Generate sample financial data for demonstration."""
    import random
    
    # Sample categories and their typical ranges
    categories = {
        'groceries': (50, 200),
        'dining': (20, 100),
        'transportation': (30, 150),
        'entertainment': (25, 80),
        'utilities': (80, 300),
        'shopping': (40, 250),
        'healthcare': (50,