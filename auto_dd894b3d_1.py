```python
#!/usr/bin/env python3
"""
Transaction Analysis Module

This module processes categorized financial transactions to provide comprehensive spending analysis.
It calculates spending totals by category, identifies trends over different time periods, and
detects unusual spending patterns or statistical outliers.

Features:
- Category-wise spending totals and averages
- Monthly and weekly trend analysis
- Statistical outlier detection using IQR method
- Spending pattern analysis with variance calculations
- Summary reporting with actionable insights

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random


class TransactionAnalyzer:
    """Analyzes financial transactions for spending patterns and anomalies."""
    
    def __init__(self):
        self.transactions = []
        self.categories = set()
    
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        categories = ['Groceries', 'Restaurants', 'Gas', 'Entertainment', 'Utilities', 
                     'Shopping', 'Healthcare', 'Transportation', 'Education', 'Miscellaneous']
        
        # Generate 6 months of sample data
        base_date = datetime.now() - timedelta(days=180)
        
        for i in range(500):
            date = base_date + timedelta(days=random.randint(0, 180))
            category = random.choice(categories)
            
            # Create realistic spending patterns with some outliers
            if category == 'Groceries':
                amount = random.normalvariate(85, 25)
            elif category == 'Restaurants':
                amount = random.normalvariate(45, 20)
            elif category == 'Gas':
                amount = random.normalvariate(60, 15)
            elif category == 'Utilities':
                amount = random.normalvariate(150, 30)
            else:
                amount = random.normalvariate(75, 35)
            
            # Occasionally add outliers
            if random.random() < 0.05:
                amount *= random.uniform(3, 8)
            
            amount = max(5, abs(amount))  # Ensure positive amounts
            
            transaction = {
                'id': f'txn_{i+1}',
                'date': date.strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'category': category,
                'description': f'{category} purchase #{i+1}'
            }
            self.transactions.append(transaction)
            self.categories.add(category)
    
    def calculate_category_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate spending totals and statistics by category."""
        try:
            category_data = defaultdict(list)
            
            for transaction in self.transactions:
                category_data[transaction['category']].append(transaction['amount'])
            
            results = {}
            for category, amounts in category_data.items():
                results[category] = {
                    'total': sum(amounts),
                    'count': len(amounts),
                    'average': statistics.mean(amounts),
                    'median': statistics.median(amounts),
                    'std_dev': statistics.stdev(amounts) if len(amounts) > 1 else 0
                }
            
            return results
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return {}
    
    def analyze_monthly_trends(self) -> Dict[str, Dict[str, float]]:
        """Analyze spending trends by month."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                monthly_data[month_key][transaction['category']] += transaction['amount']
                monthly_data[month_key]['total'] += transaction['amount']
            
            return dict(monthly_data)
        except Exception as e:
            print(f"Error analyzing monthly trends: {e}")
            return {}
    
    def analyze_weekly_trends(self) -> Dict[str, Dict[str, float]]:
        """Analyze spending trends by week."""
        try:
            weekly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                # Get Monday of the week
                monday = date - timedelta(days=date.weekday())
                week_key = monday.strftime('%Y-W%U')
                weekly_data[week_key][transaction['category']] += transaction['amount']
                weekly_data[week_key]['total'] += transaction['amount']
            
            return dict(weekly_data)
        except Exception as e:
            print(f"Error analyzing weekly trends: {e}")
            return {}
    
    def detect_outliers(self) -> List[Dict[str, Any]]:
        """Detect unusual spending patterns using IQR method."""
        try:
            outliers = []
            category_data = defaultdict(list)
            
            # Group transactions by category
            for transaction in self.transactions:
                category_data[transaction['category']].append(transaction)
            
            for category, transactions in category_data.items():
                if len(transactions) < 4:
                    continue
                
                amounts = [t['amount'] for t in transactions]
                q1 = statistics.quantiles(amounts, n=4)[0]
                q3 = statistics.quantiles(amounts, n=4)[2]
                iqr = q3 - q1
                
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                for transaction in transactions:
                    if transaction['amount'] < lower_bound or transaction['amount'] > upper_bound:
                        outlier_info = transaction.copy()
                        outlier_info['category_avg'] = statistics.mean(amounts)
                        outlier_info['deviation_factor'] = round(
                            transaction['amount'] / statistics.mean(amounts), 2
                        )
                        outliers.append(outlier_info)
            
            return sorted(outliers, key=lambda x: x['deviation_factor'], reverse=True)
        except Exception as e:
            print(f"Error detecting outliers: {e}")
            return []
    
    def generate_insights(self, category_totals: Dict, monthly_trends: Dict, 
                         outliers: List) -> List[str]:
        """Generate actionable insights from the analysis."""
        insights = []
        
        try:
            # Top spending categories
            top_categories = sorted(
                category_totals.items(), 
                key=lambda x: x[1]['total'], 
                reverse=True
            )[:3]
            
            insights.append(f"Top 3 spending categories: {', '.join([cat for cat, _ in top_categories])}")
            
            # Monthly spending trend
            if len(monthly_trends) >= 2:
                months = sorted(monthly_trends.keys())
                recent_total = monthly_trends[months[-1]]['total']
                previous_total = monthly_trends[months[-2]]['total']
                change = ((recent_total - previous_total) / previous_total) * 100
                
                trend = "increased" if change > 0 else "decreased"
                insights.append(f"Monthly spending {trend} by {abs(change):.1f}% last month")
            
            # High variance categories
            high_variance = [
                cat for cat, data in category_totals.items() 
                if data['std_dev'] / data['average'] > 0.5
            ]
            if high_variance:
                insights.append(f"Categories with high spending variance: {', '.join(high_variance)}")
            
            # Outlier summary
            if outliers:
                insights.append(f"Detected {len(outliers)} unusual transactions")
                top_outlier = outliers[0]
                insights.append(
                    f"Largest outlier: ${top_outlier['amount']