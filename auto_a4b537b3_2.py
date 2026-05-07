```python
"""
Personal Finance Analysis Engine

A comprehensive monthly spending analysis tool that processes financial transactions
to calculate category totals, identify trends, compare monthly performance, and
detect unusual spending patterns or spikes.

Features:
- Category-based spending aggregation
- Month-over-month trend analysis
- Statistical anomaly detection for unusual transactions
- Spending spike identification using standard deviation thresholds
- Summary reporting with actionable insights

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
import math


class FinanceAnalysisEngine:
    def __init__(self):
        self.transactions = []
        self.monthly_summaries = defaultdict(lambda: defaultdict(float))
        
    def load_sample_data(self):
        """Generate sample transaction data for demonstration"""
        import random
        
        categories = ['Food', 'Transportation', 'Shopping', 'Bills', 'Entertainment', 'Healthcare']
        
        # Generate 6 months of sample data
        for month_offset in range(6):
            base_date = datetime.now() - timedelta(days=30 * month_offset)
            
            # Generate 20-50 transactions per month
            for _ in range(random.randint(20, 50)):
                transaction = {
                    'date': base_date - timedelta(days=random.randint(0, 29)),
                    'amount': round(random.uniform(5.0, 500.0), 2),
                    'category': random.choice(categories),
                    'description': f"Sample transaction {random.randint(1000, 9999)}"
                }
                
                # Add some occasional large transactions (potential spikes)
                if random.random() < 0.05:
                    transaction['amount'] = round(random.uniform(800.0, 2000.0), 2)
                    
                self.transactions.append(transaction)
    
    def categorize_by_month(self):
        """Group transactions by month and category"""
        try:
            for transaction in self.transactions:
                month_key = transaction['date'].strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                self.monthly_summaries[month_key][category] += amount
                
        except Exception as e:
            print(f"Error categorizing transactions: {e}")
            
    def calculate_monthly_totals(self):
        """Calculate total spending by month"""
        monthly_totals = {}
        
        try:
            for month, categories in self.monthly_summaries.items():
                monthly_totals[month] = sum(categories.values())
                
            return monthly_totals
            
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def identify_trends(self):
        """Identify spending trends across months"""
        try:
            monthly_totals = self.calculate_monthly_totals()
            sorted_months = sorted(monthly_totals.keys())
            
            if len(sorted_months) < 2:
                return "Insufficient data for trend analysis"
            
            trends = {}
            
            # Calculate month-over-month changes
            for i in range(1, len(sorted_months)):
                current_month = sorted_months[i]
                previous_month = sorted_months[i-1]
                
                current_total = monthly_totals[current_month]
                previous_total = monthly_totals[previous_month]
                
                if previous_total > 0:
                    change_percent = ((current_total - previous_total) / previous_total) * 100
                    trends[current_month] = {
                        'change_percent': round(change_percent, 2),
                        'change_amount': round(current_total - previous_total, 2),
                        'current_total': current_total,
                        'previous_total': previous_total
                    }
            
            return trends
            
        except Exception as e:
            print(f"Error identifying trends: {e}")
            return {}
    
    def detect_unusual_transactions(self, threshold_multiplier=2.0):
        """Detect transactions that are unusually large compared to historical averages"""
        try:
            unusual_transactions = []
            
            # Calculate average transaction amount by category
            category_amounts = defaultdict(list)
            for transaction in self.transactions:
                category_amounts[transaction['category']].append(transaction['amount'])
            
            category_stats = {}
            for category, amounts in category_amounts.items():
                if len(amounts) > 1:
                    mean_amount = statistics.mean(amounts)
                    stdev_amount = statistics.stdev(amounts)
                    category_stats[category] = {
                        'mean': mean_amount,
                        'stdev': stdev_amount,
                        'threshold': mean_amount + (threshold_multiplier * stdev_amount)
                    }
            
            # Identify unusual transactions
            for transaction in self.transactions:
                category = transaction['category']
                amount = transaction['amount']
                
                if category in category_stats:
                    threshold = category_stats[category]['threshold']
                    if amount > threshold:
                        unusual_transactions.append({
                            'date': transaction['date'].strftime('%Y-%m-%d'),
                            'amount': amount,
                            'category': category,
                            'description': transaction['description'],
                            'threshold': round(threshold, 2),
                            'deviation': round(amount - category_stats[category]['mean'], 2)
                        })
            
            return unusual_transactions
            
        except Exception as e:
            print(f"Error detecting unusual transactions: {e}")
            return []
    
    def identify_spending_spikes(self):
        """Identify months with spending spikes using statistical analysis"""
        try:
            monthly_totals = self.calculate_monthly_totals()
            
            if len(monthly_totals) < 3:
                return []
            
            amounts = list(monthly_totals.values())
            mean_spending = statistics.mean(amounts)
            stdev_spending = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            spike_threshold = mean_spending + (1.5 * stdev_spending)
            
            spikes = []
            for month, amount in monthly_totals.items():
                if amount > spike_threshold:
                    spikes.append({
                        'month': month,
                        'amount': round(amount, 2),
                        'threshold': round(spike_threshold, 2),
                        'deviation_percent': round(((amount - mean_spending) / mean_spending) * 100, 2)
                    })
            
            return sorted(spikes, key=lambda x: x['amount'], reverse=True)
            
        except Exception as e:
            print(f"Error identifying spending spikes: {e}")
            return []
    
    def generate_category_insights(self):
        """Generate insights about spending patterns by category"""
        try:
            category_trends = defaultdict(list)
            
            # Collect monthly spending by category
            sorted_months = sorted(self.monthly_summaries.keys())
            
            for month in sorted_months:
                for category, amount in self.monthly_summaries[month].items():
                    category_trends[category].append(amount)
            
            insights = {}
            for category, amounts in category_trends.items():
                if len(amounts) >= 2:
                    recent_avg = statistics.mean(amounts[-3:]) if len(amounts) >= 3 else amounts[-1]
                    overall_avg = statistics.mean(amounts)
                    
                    trend_direction = "increasing" if recent_avg > overall_avg else "decreasing"
                    volatility = statistics.stdev(amounts) if len(amounts) > 1 else 0
                    
                    insights[category] = {
                        'recent_average': round(recent_avg, 2),
                        'overall_average': round(overall_avg, 2),
                        'trend': trend_direction,
                        'volatility': round(volatility, 2),
                        'total_months': len(amounts)
                    }
            
            return insights
            
        except Exception as e