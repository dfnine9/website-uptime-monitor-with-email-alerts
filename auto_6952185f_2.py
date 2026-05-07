```python
"""
Monthly Transaction Analysis Module

This module provides comprehensive analysis of categorized financial transactions.
It aggregates transaction data, calculates spending totals per category, identifies
spending trends over time, and generates statistical insights including averages,
standard deviations, and growth rates.

Features:
- Transaction categorization and aggregation
- Monthly spending trend analysis
- Statistical insights (mean, std dev, variance)
- Growth rate calculations
- Top spending categories identification
- Anomaly detection for unusual spending patterns

Usage:
    python script.py

The script generates sample transaction data and performs a complete monthly analysis.
"""

import json
import statistics
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
import random


class MonthlyTransactionAnalyzer:
    """Analyzes monthly transaction data and provides comprehensive insights."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
        self.insights = {}
    
    def add_transaction(self, date: str, category: str, amount: float, description: str = ""):
        """Add a transaction to the analyzer."""
        try:
            transaction = {
                'date': datetime.datetime.strptime(date, '%Y-%m-%d'),
                'category': category,
                'amount': abs(amount),  # Use absolute value for spending analysis
                'description': description
            }
            self.transactions.append(transaction)
        except ValueError as e:
            print(f"Error adding transaction: Invalid date format. Expected YYYY-MM-DD. {e}")
        except Exception as e:
            print(f"Error adding transaction: {e}")
    
    def load_sample_data(self):
        """Load sample transaction data for demonstration."""
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare', 'Education']
        
        # Generate 6 months of sample data
        base_date = datetime.datetime(2024, 1, 1)
        
        for month in range(6):
            for _ in range(random.randint(15, 30)):  # 15-30 transactions per month
                date = base_date + datetime.timedelta(days=month*30 + random.randint(0, 29))
                category = random.choice(categories)
                
                # Category-specific amount ranges
                amount_ranges = {
                    'Food': (20, 150),
                    'Transportation': (15, 200),
                    'Entertainment': (25, 300),
                    'Utilities': (50, 250),
                    'Shopping': (30, 500),
                    'Healthcare': (40, 400),
                    'Education': (100, 1000)
                }
                
                min_amt, max_amt = amount_ranges.get(category, (20, 200))
                amount = random.uniform(min_amt, max_amt)
                
                self.add_transaction(
                    date.strftime('%Y-%m-%d'),
                    category,
                    amount,
                    f"Sample {category.lower()} transaction"
                )
    
    def aggregate_monthly_data(self):
        """Aggregate transactions by month and category."""
        try:
            for transaction in self.transactions:
                month_key = transaction['date'].strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                self.monthly_data[month_key][category] += amount
                self.category_totals[category] += amount
                
        except Exception as e:
            print(f"Error aggregating monthly data: {e}")
    
    def calculate_trends(self) -> Dict[str, Any]:
        """Calculate spending trends over time."""
        try:
            trends = {}
            
            # Sort months chronologically
            sorted_months = sorted(self.monthly_data.keys())
            
            for category in self.category_totals.keys():
                monthly_amounts = []
                for month in sorted_months:
                    amount = self.monthly_data[month].get(category, 0)
                    monthly_amounts.append(amount)
                
                if len(monthly_amounts) > 1:
                    # Calculate growth rate
                    first_amount = monthly_amounts[0] if monthly_amounts[0] > 0 else 1
                    last_amount = monthly_amounts[-1]
                    growth_rate = ((last_amount - first_amount) / first_amount) * 100
                    
                    # Calculate average monthly spending
                    avg_monthly = statistics.mean(monthly_amounts)
                    
                    trends[category] = {
                        'monthly_amounts': monthly_amounts,
                        'growth_rate': round(growth_rate, 2),
                        'avg_monthly': round(avg_monthly, 2),
                        'total_spent': round(sum(monthly_amounts), 2),
                        'months_tracked': len(monthly_amounts)
                    }
            
            return trends
        except Exception as e:
            print(f"Error calculating trends: {e}")
            return {}
    
    def generate_statistical_insights(self) -> Dict[str, Any]:
        """Generate comprehensive statistical insights."""
        try:
            insights = {}
            
            # Overall statistics
            total_spending = sum(self.category_totals.values())
            category_percentages = {
                cat: round((amount / total_spending) * 100, 2)
                for cat, amount in self.category_totals.items()
            }
            
            # Monthly spending statistics
            monthly_totals = []
            for month_data in self.monthly_data.values():
                monthly_totals.append(sum(month_data.values()))
            
            if monthly_totals:
                insights['monthly_stats'] = {
                    'avg_monthly_spending': round(statistics.mean(monthly_totals), 2),
                    'median_monthly_spending': round(statistics.median(monthly_totals), 2),
                    'std_dev_monthly': round(statistics.stdev(monthly_totals) if len(monthly_totals) > 1 else 0, 2),
                    'min_month': round(min(monthly_totals), 2),
                    'max_month': round(max(monthly_totals), 2)
                }
            
            # Category statistics
            category_amounts = list(self.category_totals.values())
            if category_amounts:
                insights['category_stats'] = {
                    'total_categories': len(self.category_totals),
                    'avg_per_category': round(statistics.mean(category_amounts), 2),
                    'category_std_dev': round(statistics.stdev(category_amounts) if len(category_amounts) > 1 else 0, 2)
                }
            
            # Top categories
            sorted_categories = sorted(self.category_totals.items(), key=lambda x: x[1], reverse=True)
            insights['top_categories'] = [
                {
                    'category': cat,
                    'amount': round(amount, 2),
                    'percentage': category_percentages[cat]
                }
                for cat, amount in sorted_categories[:5]
            ]
            
            # Anomaly detection (spending > 2 standard deviations)
            if len(monthly_totals) > 1:
                mean_spending = statistics.mean(monthly_totals)
                std_dev = statistics.stdev(monthly_totals)
                threshold = mean_spending + (2 * std_dev)
                
                anomalous_months = []
                for month, month_data in self.monthly_data.items():
                    month_total = sum(month_data.values())
                    if month_total > threshold:
                        anomalous_months.append({
                            'month': month,
                            'amount': round(month_total, 2),
                            'deviation': round(month_total - mean_spending, 2)
                        })
                
                insights['anomalies'] = anomalous_months
            
            insights['summary'] = {
                'total_transactions': len(self.transactions),
                'total_spending': round(total_spending, 2),
                'analysis_