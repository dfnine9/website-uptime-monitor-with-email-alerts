```python
"""
Personal Finance Transaction Analysis Module

This module analyzes categorized transaction data to provide comprehensive spending insights.
It generates monthly spending trends, category percentage breakdowns, identifies unusual
spending patterns, and performs comparative analysis across different time periods.

Features:
- Monthly spending trend analysis
- Category-wise spending breakdown with percentages
- Unusual spending pattern detection using statistical analysis
- Time period comparison (month-over-month, year-over-year)
- Summary statistics and insights

The module uses only standard library modules for maximum portability and compatibility.
"""

import json
import statistics
import calendar
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random
import math


class TransactionAnalyzer:
    """Analyzes transaction data to generate spending insights."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
        
    def load_sample_data(self) -> List[Dict]:
        """Generate sample transaction data for demonstration."""
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                     'Healthcare', 'Shopping', 'Education', 'Insurance', 'Travel']
        
        transactions = []
        start_date = datetime(2023, 1, 1)
        
        # Generate 12 months of sample data
        for month in range(12):
            month_date = start_date + timedelta(days=30 * month)
            
            # Generate 20-40 transactions per month
            for _ in range(random.randint(20, 40)):
                category = random.choice(categories)
                
                # Different spending patterns by category
                if category == 'Food':
                    amount = random.uniform(15, 120)
                elif category == 'Transportation':
                    amount = random.uniform(25, 200)
                elif category == 'Utilities':
                    amount = random.uniform(80, 300)
                elif category == 'Healthcare':
                    amount = random.uniform(50, 500)
                else:
                    amount = random.uniform(20, 250)
                
                # Add some unusual spending patterns randomly
                if random.random() < 0.05:  # 5% chance of unusual spending
                    amount *= random.uniform(3, 8)
                
                transaction_date = month_date + timedelta(days=random.randint(0, 29))
                
                transactions.append({
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'amount': round(amount, 2),
                    'category': category,
                    'description': f'{category} purchase'
                })
        
        return sorted(transactions, key=lambda x: x['date'])
    
    def load_transactions(self, transactions: List[Dict] = None):
        """Load transaction data."""
        try:
            if transactions is None:
                self.transactions = self.load_sample_data()
            else:
                self.transactions = transactions
            
            # Process transactions into monthly and category data
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = float(transaction['amount'])
                
                self.monthly_data[month_key][category] += amount
                self.category_totals[category] += amount
                
        except Exception as e:
            print(f"Error loading transactions: {e}")
            raise
    
    def analyze_monthly_trends(self) -> Dict[str, Any]:
        """Analyze monthly spending trends."""
        try:
            monthly_totals = {}
            monthly_category_data = {}
            
            for month, categories in self.monthly_data.items():
                monthly_totals[month] = sum(categories.values())
                monthly_category_data[month] = dict(categories)
            
            # Calculate trend statistics
            amounts = list(monthly_totals.values())
            if len(amounts) > 1:
                trend_direction = "increasing" if amounts[-1] > amounts[0] else "decreasing"
                avg_change = (amounts[-1] - amounts[0]) / len(amounts)
            else:
                trend_direction = "insufficient data"
                avg_change = 0
            
            return {
                'monthly_totals': monthly_totals,
                'monthly_category_data': monthly_category_data,
                'average_monthly_spending': statistics.mean(amounts) if amounts else 0,
                'trend_direction': trend_direction,
                'average_monthly_change': round(avg_change, 2),
                'highest_month': max(monthly_totals.items(), key=lambda x: x[1]) if monthly_totals else None,
                'lowest_month': min(monthly_totals.items(), key=lambda x: x[1]) if monthly_totals else None
            }
        except Exception as e:
            print(f"Error analyzing monthly trends: {e}")
            return {}
    
    def analyze_category_percentages(self) -> Dict[str, Any]:
        """Analyze spending by category with percentages."""
        try:
            total_spending = sum(self.category_totals.values())
            
            if total_spending == 0:
                return {'error': 'No spending data available'}
            
            category_percentages = {}
            for category, amount in self.category_totals.items():
                percentage = (amount / total_spending) * 100
                category_percentages[category] = {
                    'amount': round(amount, 2),
                    'percentage': round(percentage, 2)
                }
            
            # Sort by spending amount
            sorted_categories = sorted(category_percentages.items(), 
                                     key=lambda x: x[1]['amount'], reverse=True)
            
            return {
                'total_spending': round(total_spending, 2),
                'category_breakdown': dict(sorted_categories),
                'top_category': sorted_categories[0] if sorted_categories else None,
                'number_of_categories': len(category_percentages)
            }
        except Exception as e:
            print(f"Error analyzing category percentages: {e}")
            return {}
    
    def detect_unusual_patterns(self) -> Dict[str, Any]:
        """Detect unusual spending patterns using statistical analysis."""
        try:
            unusual_transactions = []
            category_stats = {}
            
            # Calculate statistics for each category
            for category in self.category_totals.keys():
                category_amounts = [
                    float(t['amount']) for t in self.transactions 
                    if t['category'] == category
                ]
                
                if len(category_amounts) > 1:
                    mean_amount = statistics.mean(category_amounts)
                    stdev_amount = statistics.stdev(category_amounts)
                    
                    category_stats[category] = {
                        'mean': round(mean_amount, 2),
                        'stdev': round(stdev_amount, 2),
                        'threshold': round(mean_amount + (2 * stdev_amount), 2)
                    }
            
            # Find unusual transactions (more than 2 standard deviations from mean)
            for transaction in self.transactions:
                category = transaction['category']
                amount = float(transaction['amount'])
                
                if category in category_stats:
                    threshold = category_stats[category]['threshold']
                    if amount > threshold:
                        unusual_transactions.append({
                            'date': transaction['date'],
                            'amount': amount,
                            'category': category,
                            'description': transaction['description'],
                            'deviation_factor': round(amount / category_stats[category]['mean'], 2)
                        })
            
            # Sort by deviation factor
            unusual_transactions.sort(key=lambda x: x['deviation_factor'], reverse=True)
            
            return {
                'category_statistics': category_stats,
                'unusual_transactions': unusual_transactions[:10],  # Top 10 most unusual
                'total_unusual_count': len(unusual_transactions),
                'unusual_spending_total': round(sum(t['amount