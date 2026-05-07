```python
#!/usr/bin/env python3
"""
Spending Analysis Engine

A comprehensive financial analysis tool that processes spending data to:
- Calculate monthly and weekly spending patterns
- Identify spending trends over time
- Detect anomalies in spending behavior
- Generate statistical insights and visualizations

The engine uses numpy for statistical computations and matplotlib for
data visualization, providing actionable insights into spending habits.

Usage: python script.py
"""

import sys
import json
import datetime
from typing import Dict, List, Tuple, Any
import statistics
import random
import math

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from collections import defaultdict, Counter
except ImportError as e:
    print(f"Error: Required library not found - {e}")
    print("Please install: pip install numpy matplotlib")
    sys.exit(1)


class SpendingAnalyzer:
    """Main spending analysis engine with pattern detection and visualization."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(float)
        self.weekly_data = defaultdict(float)
        self.category_data = defaultdict(float)
        
    def load_sample_data(self) -> None:
        """Generate realistic sample spending data for analysis."""
        try:
            categories = ['Groceries', 'Gas', 'Restaurants', 'Shopping', 'Bills', 
                         'Entertainment', 'Healthcare', 'Travel', 'Subscriptions']
            
            base_date = datetime.datetime.now() - datetime.timedelta(days=365)
            
            for i in range(500):  # Generate 500 transactions over past year
                date = base_date + datetime.timedelta(days=random.randint(0, 365))
                category = random.choice(categories)
                
                # Create realistic spending patterns
                if category == 'Groceries':
                    amount = random.normalvariate(75, 25)
                elif category == 'Gas':
                    amount = random.normalvariate(45, 15)
                elif category == 'Bills':
                    amount = random.normalvariate(200, 50)
                elif category == 'Restaurants':
                    amount = random.normalvariate(35, 15)
                else:
                    amount = random.normalvariate(60, 30)
                
                # Add some seasonal variation
                month_factor = 1.0 + 0.2 * math.sin(2 * math.pi * date.month / 12)
                amount *= month_factor
                
                # Ensure positive amounts
                amount = max(5.0, amount)
                
                self.transactions.append({
                    'date': date,
                    'amount': round(amount, 2),
                    'category': category,
                    'description': f"{category} purchase"
                })
                
            self.transactions.sort(key=lambda x: x['date'])
            print(f"Generated {len(self.transactions)} sample transactions")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def process_data(self) -> None:
        """Process raw transactions into monthly and weekly aggregations."""
        try:
            for transaction in self.transactions:
                date = transaction['date']
                amount = transaction['amount']
                category = transaction['category']
                
                # Monthly aggregation
                month_key = date.strftime('%Y-%m')
                self.monthly_data[month_key] += amount
                
                # Weekly aggregation (ISO week)
                year, week, _ = date.isocalendar()
                week_key = f"{year}-W{week:02d}"
                self.weekly_data[week_key] += amount
                
                # Category aggregation
                self.category_data[category] += amount
                
            print(f"Processed {len(self.transactions)} transactions")
            print(f"Monthly periods: {len(self.monthly_data)}")
            print(f"Weekly periods: {len(self.weekly_data)}")
            
        except Exception as e:
            print(f"Error processing data: {e}")
            raise
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate comprehensive statistical insights."""
        try:
            monthly_amounts = list(self.monthly_data.values())
            weekly_amounts = list(self.weekly_data.values())
            all_amounts = [t['amount'] for t in self.transactions]
            
            stats = {
                'total_spending': sum(all_amounts),
                'transaction_count': len(self.transactions),
                'average_transaction': statistics.mean(all_amounts),
                'median_transaction': statistics.median(all_amounts),
                'monthly_stats': {
                    'mean': statistics.mean(monthly_amounts),
                    'median': statistics.median(monthly_amounts),
                    'std_dev': statistics.stdev(monthly_amounts) if len(monthly_amounts) > 1 else 0,
                    'min': min(monthly_amounts),
                    'max': max(monthly_amounts)
                },
                'weekly_stats': {
                    'mean': statistics.mean(weekly_amounts),
                    'median': statistics.median(weekly_amounts),
                    'std_dev': statistics.stdev(weekly_amounts) if len(weekly_amounts) > 1 else 0,
                    'min': min(weekly_amounts),
                    'max': max(weekly_amounts)
                }
            }
            
            return stats
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {}
    
    def detect_anomalies(self, z_threshold: float = 2.0) -> Dict[str, List]:
        """Detect spending anomalies using Z-score analysis."""
        try:
            monthly_amounts = list(self.monthly_data.values())
            weekly_amounts = list(self.weekly_data.values())
            
            anomalies = {'monthly': [], 'weekly': [], 'transactions': []}
            
            if len(monthly_amounts) > 1:
                monthly_mean = statistics.mean(monthly_amounts)
                monthly_std = statistics.stdev(monthly_amounts)
                
                for month, amount in self.monthly_data.items():
                    if monthly_std > 0:
                        z_score = abs(amount - monthly_mean) / monthly_std
                        if z_score > z_threshold:
                            anomalies['monthly'].append({
                                'period': month,
                                'amount': amount,
                                'z_score': z_score,
                                'type': 'high' if amount > monthly_mean else 'low'
                            })
            
            if len(weekly_amounts) > 1:
                weekly_mean = statistics.mean(weekly_amounts)
                weekly_std = statistics.stdev(weekly_amounts)
                
                for week, amount in self.weekly_data.items():
                    if weekly_std > 0:
                        z_score = abs(amount - weekly_mean) / weekly_std
                        if z_score > z_threshold:
                            anomalies['weekly'].append({
                                'period': week,
                                'amount': amount,
                                'z_score': z_score,
                                'type': 'high' if amount > weekly_mean else 'low'
                            })
            
            # Transaction-level anomalies
            all_amounts = [t['amount'] for t in self.transactions]
            if len(all_amounts) > 1:
                tx_mean = statistics.mean(all_amounts)
                tx_std = statistics.stdev(all_amounts)
                
                for transaction in self.transactions:
                    if tx_std > 0:
                        z_score = abs(transaction['amount'] - tx_mean) / tx_std
                        if z_score > z_threshold:
                            anomalies['transactions'].append({
                                'date': transaction['date'].strftime('%Y-%m-%d'),
                                'amount': transaction['amount'],
                                'category': transaction['category'],
                                'z_score': z_score
                            })
            
            return anomalies
            
        except Exception as e:
            print(f"Error detecting anom