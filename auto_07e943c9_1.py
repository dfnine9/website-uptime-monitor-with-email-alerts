```python
"""
Spending Pattern Analyzer Module

This module analyzes spending patterns from transaction data by:
- Detecting spending trends over time
- Identifying high-spending periods
- Calculating category-wise spending percentages
- Flagging unusual transactions and spending spikes

The module uses statistical analysis to identify anomalies and provides
comprehensive insights into spending behavior patterns.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Any
import random


class SpendingAnalyzer:
    """Analyzes spending patterns and detects anomalies in transaction data."""
    
    def __init__(self):
        self.transactions = []
        self.daily_totals = defaultdict(float)
        self.category_totals = defaultdict(float)
        
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        categories = ['Food', 'Transportation', 'Shopping', 'Entertainment', 'Utilities', 'Healthcare']
        
        # Generate 90 days of transaction data
        base_date = datetime.now() - timedelta(days=90)
        
        for i in range(300):  # 300 transactions over 90 days
            transaction_date = base_date + timedelta(days=random.randint(0, 89))
            category = random.choice(categories)
            
            # Create realistic spending patterns
            if category == 'Food':
                amount = random.uniform(10, 100)
            elif category == 'Transportation':
                amount = random.uniform(5, 50)
            elif category == 'Shopping':
                amount = random.uniform(20, 300)
            elif category == 'Entertainment':
                amount = random.uniform(15, 150)
            elif category == 'Utilities':
                amount = random.uniform(50, 200)
            else:  # Healthcare
                amount = random.uniform(25, 500)
            
            # Add some spending spikes randomly
            if random.random() < 0.05:  # 5% chance of spike
                amount *= random.uniform(3, 8)
            
            transaction = {
                'date': transaction_date.strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'category': category,
                'description': f'{category} purchase'
            }
            
            self.transactions.append(transaction)
    
    def process_transactions(self) -> None:
        """Process transactions to calculate daily and category totals."""
        try:
            for transaction in self.transactions:
                date = transaction['date']
                amount = transaction['amount']
                category = transaction['category']
                
                self.daily_totals[date] += amount
                self.category_totals[category] += amount
                
        except KeyError as e:
            print(f"Error processing transaction: Missing key {e}")
        except (ValueError, TypeError) as e:
            print(f"Error processing transaction amount: {e}")
    
    def detect_spending_trends(self) -> Dict[str, Any]:
        """Detect overall spending trends over time."""
        try:
            if not self.daily_totals:
                return {'trend': 'No data available'}
            
            # Sort dates and calculate weekly averages
            sorted_dates = sorted(self.daily_totals.keys())
            daily_amounts = [self.daily_totals[date] for date in sorted_dates]
            
            # Calculate trend using simple linear regression
            n = len(daily_amounts)
            if n < 2:
                return {'trend': 'Insufficient data'}
            
            x_values = list(range(n))
            x_mean = statistics.mean(x_values)
            y_mean = statistics.mean(daily_amounts)
            
            numerator = sum((x_values[i] - x_mean) * (daily_amounts[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator
            
            # Determine trend direction
            if slope > 1:
                trend_direction = 'Increasing'
            elif slope < -1:
                trend_direction = 'Decreasing'
            else:
                trend_direction = 'Stable'
            
            # Calculate weekly averages for pattern analysis
            weekly_averages = []
            for i in range(0, len(daily_amounts), 7):
                week_data = daily_amounts[i:i+7]
                if week_data:
                    weekly_averages.append(statistics.mean(week_data))
            
            return {
                'trend': trend_direction,
                'slope': round(slope, 2),
                'average_daily_spending': round(statistics.mean(daily_amounts), 2),
                'weekly_averages': [round(avg, 2) for avg in weekly_averages[-4:]],  # Last 4 weeks
                'total_days_analyzed': n
            }
            
        except Exception as e:
            return {'error': f'Error detecting trends: {str(e)}'}
    
    def identify_high_spending_periods(self) -> List[Dict[str, Any]]:
        """Identify periods of unusually high spending."""
        try:
            if not self.daily_totals:
                return []
            
            daily_amounts = list(self.daily_totals.values())
            mean_spending = statistics.mean(daily_amounts)
            
            if len(daily_amounts) > 1:
                std_spending = statistics.stdev(daily_amounts)
            else:
                std_spending = 0
            
            threshold = mean_spending + (1.5 * std_spending)
            
            high_spending_days = []
            for date, amount in self.daily_totals.items():
                if amount > threshold:
                    high_spending_days.append({
                        'date': date,
                        'amount': round(amount, 2),
                        'deviation_from_mean': round(amount - mean_spending, 2),
                        'percentage_above_mean': round(((amount - mean_spending) / mean_spending) * 100, 1)
                    })
            
            # Sort by amount descending
            high_spending_days.sort(key=lambda x: x['amount'], reverse=True)
            
            return high_spending_days[:10]  # Return top 10
            
        except Exception as e:
            print(f"Error identifying high spending periods: {e}")
            return []
    
    def calculate_category_percentages(self) -> Dict[str, float]:
        """Calculate percentage of spending by category."""
        try:
            if not self.category_totals:
                return {}
            
            total_spending = sum(self.category_totals.values())
            
            if total_spending == 0:
                return {}
            
            percentages = {}
            for category, amount in self.category_totals.items():
                percentage = (amount / total_spending) * 100
                percentages[category] = round(percentage, 1)
            
            return dict(sorted(percentages.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            print(f"Error calculating category percentages: {e}")
            return {}
    
    def flag_unusual_transactions(self) -> List[Dict[str, Any]]:
        """Flag individual transactions that appear unusual."""
        try:
            unusual_transactions = []
            
            # Group transactions by category for comparison
            category_amounts = defaultdict(list)
            for transaction in self.transactions:
                category_amounts[transaction['category']].append(transaction['amount'])
            
            # Calculate thresholds for each category
            category_thresholds = {}
            for category, amounts in category_amounts.items():
                if len(amounts) > 1:
                    mean_amount = statistics.mean(amounts)
                    std_amount = statistics.stdev(amounts)
                    category_thresholds[category] = mean_amount + (2 * std_amount)
                else:
                    category_thresholds[category] = amounts[0