```python
"""
Personal Finance Data Analysis Module

This module provides comprehensive analysis of personal spending patterns including:
- Monthly spending pattern calculation
- Top expense category identification
- Spending trend analysis over time
- Statistical detection of unusual spending behavior

The module uses statistical methods including moving averages, standard deviation analysis,
and Z-score calculations to identify spending anomalies and patterns.

Usage: python script.py
"""

import json
import statistics
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random


class SpendingAnalyzer:
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(list)
        self.category_data = defaultdict(list)
        
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration"""
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare', 'Education']
        
        # Generate 12 months of sample data
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(500):  # 500 sample transactions
            date = base_date + timedelta(days=random.randint(0, 365))
            category = random.choice(categories)
            
            # Create realistic spending patterns
            base_amounts = {
                'Food': (20, 150),
                'Transportation': (15, 80),
                'Entertainment': (25, 200),
                'Utilities': (50, 300),
                'Shopping': (30, 500),
                'Healthcare': (40, 800),
                'Education': (100, 2000)
            }
            
            min_amt, max_amt = base_amounts[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            # Add some seasonal variation
            if category == 'Utilities' and date.month in [12, 1, 2]:
                amount *= 1.5  # Higher utility bills in winter
            
            # Occasionally add unusual spending (5% chance)
            if random.random() < 0.05:
                amount *= random.uniform(2.0, 4.0)
            
            transaction = {
                'date': date.strftime('%Y-%m-%d'),
                'amount': amount,
                'category': category,
                'description': f"{category} purchase"
            }
            
            self.transactions.append(transaction)
    
    def process_transactions(self) -> None:
        """Process transactions into monthly and category groupings"""
        try:
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                
                self.monthly_data[month_key].append(transaction['amount'])
                self.category_data[transaction['category']].append(transaction['amount'])
                
        except Exception as e:
            print(f"Error processing transactions: {e}")
            raise
    
    def calculate_monthly_patterns(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending patterns and statistics"""
        try:
            monthly_stats = {}
            
            for month, amounts in self.monthly_data.items():
                if amounts:
                    monthly_stats[month] = {
                        'total': round(sum(amounts), 2),
                        'average_transaction': round(statistics.mean(amounts), 2),
                        'median_transaction': round(statistics.median(amounts), 2),
                        'transaction_count': len(amounts),
                        'std_deviation': round(statistics.stdev(amounts) if len(amounts) > 1 else 0, 2)
                    }
            
            return monthly_stats
            
        except Exception as e:
            print(f"Error calculating monthly patterns: {e}")
            return {}
    
    def identify_top_categories(self, top_n: int = 5) -> List[Tuple[str, float, int]]:
        """Identify top expense categories by total spending"""
        try:
            category_totals = []
            
            for category, amounts in self.category_data.items():
                total_spent = sum(amounts)
                transaction_count = len(amounts)
                category_totals.append((category, round(total_spent, 2), transaction_count))
            
            # Sort by total spending (descending)
            category_totals.sort(key=lambda x: x[1], reverse=True)
            
            return category_totals[:top_n]
            
        except Exception as e:
            print(f"Error identifying top categories: {e}")
            return []
    
    def analyze_spending_trends(self) -> Dict[str, Any]:
        """Analyze spending trends over time"""
        try:
            # Sort months chronologically
            sorted_months = sorted(self.monthly_data.keys())
            monthly_totals = [sum(self.monthly_data[month]) for month in sorted_months]
            
            if len(monthly_totals) < 2:
                return {"error": "Insufficient data for trend analysis"}
            
            # Calculate trend metrics
            avg_monthly_spend = statistics.mean(monthly_totals)
            trend_direction = "increasing" if monthly_totals[-1] > monthly_totals[0] else "decreasing"
            
            # Calculate month-over-month changes
            monthly_changes = []
            for i in range(1, len(monthly_totals)):
                change_pct = ((monthly_totals[i] - monthly_totals[i-1]) / monthly_totals[i-1]) * 100
                monthly_changes.append(round(change_pct, 2))
            
            # Calculate 3-month moving average for recent months
            moving_averages = []
            for i in range(2, len(monthly_totals)):
                ma = statistics.mean(monthly_totals[i-2:i+1])
                moving_averages.append(round(ma, 2))
            
            return {
                'average_monthly_spending': round(avg_monthly_spend, 2),
                'trend_direction': trend_direction,
                'latest_month_spending': round(monthly_totals[-1], 2),
                'highest_month': max(monthly_totals),
                'lowest_month': min(monthly_totals),
                'monthly_changes_pct': monthly_changes,
                'recent_3month_moving_avg': moving_averages[-3:] if len(moving_averages) >= 3 else moving_averages
            }
            
        except Exception as e:
            print(f"Error analyzing spending trends: {e}")
            return {}
    
    def detect_unusual_spending(self, z_threshold: float = 2.0) -> Dict[str, List]:
        """Detect unusual spending behavior using statistical analysis"""
        try:
            unusual_transactions = []
            unusual_monthly_spending = []
            
            # Detect unusual individual transactions by category
            for category, amounts in self.category_data.items():
                if len(amounts) > 3:  # Need sufficient data for statistical analysis
                    mean_amount = statistics.mean(amounts)
                    std_dev = statistics.stdev(amounts)
                    
                    if std_dev > 0:  # Avoid division by zero
                        for i, amount in enumerate(amounts):
                            z_score = abs((amount - mean_amount) / std_dev)
                            if z_score > z_threshold:
                                # Find the actual transaction
                                for transaction in self.transactions:
                                    if (transaction['category'] == category and 
                                        transaction['amount'] == amount):
                                        unusual_transactions.append({
                                            'date': transaction['date'],
                                            'category': category,
                                            'amount': amount,
                                            'z_score': round(z_score, 2),
                                            'category_average': round(mean_amount, 2)
                                        })
                                        break
            
            # Detect unusual monthly spending
            monthly_totals = [sum(amounts) for amounts in self.monthly_data.values()]
            if len(monthly_totals) > 3:
                mean_