```python
"""
Personal Finance Spending Pattern Analyzer

This module analyzes spending patterns by comparing monthly category totals,
identifying spending trends over time, and detecting anomalies or budget overruns
using statistical analysis.

Features:
- Monthly category spending comparison
- Trend analysis using linear regression
- Anomaly detection using statistical methods (Z-score and IQR)
- Budget overrun detection
- Comprehensive reporting with visualizations in text format

Dependencies: Python standard library only
"""

import json
import statistics
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random
import math


class SpendingAnalyzer:
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        
    def load_sample_data(self):
        """Generate sample transaction data for demonstration"""
        categories = ['Groceries', 'Transportation', 'Entertainment', 'Utilities', 
                     'Healthcare', 'Shopping', 'Restaurants', 'Gas', 'Insurance']
        
        # Generate 12 months of sample data
        base_date = datetime.date(2024, 1, 1)
        
        for month in range(12):
            current_date = datetime.date(2024, month + 1, 1)
            
            # Generate 15-30 transactions per month
            num_transactions = random.randint(15, 30)
            
            for _ in range(num_transactions):
                category = random.choice(categories)
                
                # Create realistic spending patterns with some categories having trends
                base_amount = {
                    'Groceries': 250 + month * 10,  # Increasing trend
                    'Transportation': 150 - month * 2,  # Decreasing trend
                    'Entertainment': 200 + random.randint(-50, 50),  # Volatile
                    'Utilities': 120 + random.randint(-20, 20),
                    'Healthcare': random.randint(50, 300),
                    'Shopping': random.randint(50, 400),
                    'Restaurants': 180 + random.randint(-30, 30),
                    'Gas': 80 + random.randint(-20, 40),
                    'Insurance': 200 if random.random() < 0.3 else 0  # Periodic
                }.get(category, 100)
                
                # Add some noise
                amount = abs(base_amount + random.randint(-30, 30))
                
                # Random day in month
                try:
                    day = random.randint(1, 28)
                    transaction_date = datetime.date(2024, month + 1, day)
                except ValueError:
                    transaction_date = current_date
                
                self.transactions.append({
                    'date': transaction_date.isoformat(),
                    'category': category,
                    'amount': round(amount, 2),
                    'description': f'{category} purchase'
                })
        
        # Set sample budgets
        self.budgets = {
            'Groceries': 300,
            'Transportation': 180,
            'Entertainment': 250,
            'Utilities': 150,
            'Healthcare': 200,
            'Shopping': 300,
            'Restaurants': 200,
            'Gas': 120,
            'Insurance': 250
        }
    
    def get_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly totals by category"""
        monthly_totals = defaultdict(lambda: defaultdict(float))
        
        for transaction in self.transactions:
            try:
                date = datetime.datetime.fromisoformat(transaction['date']).date()
                month_key = f"{date.year}-{date.month:02d}"
                category = transaction['category']
                amount = float(transaction['amount'])
                
                monthly_totals[month_key][category] += amount
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping invalid transaction: {e}")
                continue
                
        return dict(monthly_totals)
    
    def calculate_trends(self, monthly_totals: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
        """Calculate spending trends for each category using linear regression"""
        trends = {}
        
        # Get all categories
        all_categories = set()
        for month_data in monthly_totals.values():
            all_categories.update(month_data.keys())
        
        for category in all_categories:
            monthly_amounts = []
            months = sorted(monthly_totals.keys())
            
            for month in months:
                amount = monthly_totals[month].get(category, 0)
                monthly_amounts.append(amount)
            
            if len(monthly_amounts) < 2:
                continue
                
            # Simple linear regression
            n = len(monthly_amounts)
            x_values = list(range(n))
            
            try:
                # Calculate slope (trend)
                x_mean = statistics.mean(x_values)
                y_mean = statistics.mean(monthly_amounts)
                
                numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, monthly_amounts))
                denominator = sum((x - x_mean) ** 2 for x in x_values)
                
                if denominator == 0:
                    slope = 0
                else:
                    slope = numerator / denominator
                
                # Calculate correlation coefficient
                if len(monthly_amounts) > 1:
                    std_x = statistics.stdev(x_values) if len(x_values) > 1 else 0
                    std_y = statistics.stdev(monthly_amounts) if len(monthly_amounts) > 1 else 0
                    
                    if std_x > 0 and std_y > 0:
                        correlation = numerator / (n * std_x * std_y)
                    else:
                        correlation = 0
                else:
                    correlation = 0
                
                trends[category] = {
                    'slope': round(slope, 2),
                    'correlation': round(correlation, 3),
                    'average_monthly': round(y_mean, 2),
                    'trend_direction': 'Increasing' if slope > 5 else 'Decreasing' if slope < -5 else 'Stable',
                    'monthly_data': monthly_amounts
                }
                
            except statistics.StatisticsError:
                trends[category] = {
                    'slope': 0,
                    'correlation': 0,
                    'average_monthly': 0,
                    'trend_direction': 'Insufficient Data',
                    'monthly_data': monthly_amounts
                }
        
        return trends
    
    def detect_anomalies(self, monthly_totals: Dict[str, Dict[str, float]]) -> Dict[str, List[Dict[str, Any]]]:
        """Detect spending anomalies using Z-score and IQR methods"""
        anomalies = defaultdict(list)
        
        # Get all categories
        all_categories = set()
        for month_data in monthly_totals.values():
            all_categories.update(month_data.keys())
        
        for category in all_categories:
            amounts = []
            month_amount_pairs = []
            
            for month in sorted(monthly_totals.keys()):
                amount = monthly_totals[month].get(category, 0)
                amounts.append(amount)
                month_amount_pairs.append((month, amount))
            
            if len(amounts) < 3:
                continue
                
            try:
                # Z-score method
                mean_amount = statistics.mean(amounts)
                std_amount = statistics.stdev(amounts)
                
                # IQR method
                sorted_amounts = sorted(amounts)
                q1_idx = len(sorted_amounts) // 4
                q3_idx = 3 * len(sorted_amounts) // 4
                
                if q1_idx < len(sorted_amounts) and q3_idx < len(sorted_amounts):
                    q1 = sorted_amounts[