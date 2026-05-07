```python
"""
Transaction Data Analysis Module

This module processes categorized transaction data to:
1. Calculate monthly spending totals by category
2. Identify spending trends over time
3. Detect anomalies or unusual spending patterns

The module generates sample transaction data and performs comprehensive analysis
including statistical anomaly detection using z-scores and trend analysis.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
import random

class TransactionAnalyzer:
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.category_trends = defaultdict(list)
        
    def generate_sample_data(self, num_months=12):
        """Generate sample transaction data for testing"""
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping']
        base_amounts = {'Food': 300, 'Transportation': 200, 'Entertainment': 150, 
                       'Utilities': 120, 'Healthcare': 100, 'Shopping': 250}
        
        transactions = []
        start_date = datetime.now() - timedelta(days=365)
        
        for month in range(num_months):
            month_date = start_date + timedelta(days=30 * month)
            
            for category in categories:
                # Generate 5-15 transactions per category per month
                num_transactions = random.randint(5, 15)
                base_amount = base_amounts[category]
                
                # Add seasonal variation
                seasonal_multiplier = 1.0
                if category == 'Utilities' and month in [11, 0, 1]:  # Winter months
                    seasonal_multiplier = 1.4
                elif category == 'Entertainment' and month in [5, 6, 7]:  # Summer months
                    seasonal_multiplier = 1.3
                
                for _ in range(num_transactions):
                    # Random variation around base amount
                    amount = base_amount * seasonal_multiplier * random.uniform(0.3, 1.8)
                    
                    # Occasionally add anomalous transactions
                    if random.random() < 0.05:  # 5% chance of anomaly
                        amount *= random.uniform(3, 8)
                    
                    transaction_date = month_date + timedelta(days=random.randint(0, 29))
                    
                    transactions.append({
                        'date': transaction_date.strftime('%Y-%m-%d'),
                        'category': category,
                        'amount': round(amount, 2),
                        'description': f'{category} purchase'
                    })
        
        return transactions
    
    def load_transactions(self, transactions=None):
        """Load transaction data"""
        try:
            if transactions is None:
                self.transactions = self.generate_sample_data()
                print("Generated sample transaction data")
            else:
                self.transactions = transactions
                print(f"Loaded {len(self.transactions)} transactions")
        except Exception as e:
            print(f"Error loading transactions: {e}")
            return False
        return True
    
    def calculate_monthly_totals(self):
        """Calculate monthly spending totals by category"""
        try:
            self.monthly_totals.clear()
            
            for transaction in self.transactions:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                category = transaction['category']
                amount = float(transaction['amount'])
                
                self.monthly_totals[month_key][category] += amount
            
            print("\n=== MONTHLY SPENDING TOTALS BY CATEGORY ===")
            for month in sorted(self.monthly_totals.keys()):
                print(f"\nMonth: {month}")
                total_month = 0
                for category, amount in sorted(self.monthly_totals[month].items()):
                    print(f"  {category}: ${amount:.2f}")
                    total_month += amount
                print(f"  TOTAL: ${total_month:.2f}")
                
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
    
    def analyze_spending_trends(self):
        """Identify spending trends over time"""
        try:
            # Organize data by category over time
            category_monthly = defaultdict(list)
            
            for month in sorted(self.monthly_totals.keys()):
                for category in self.monthly_totals[month]:
                    category_monthly[category].append({
                        'month': month,
                        'amount': self.monthly_totals[month][category]
                    })
            
            print("\n=== SPENDING TRENDS ANALYSIS ===")
            
            for category, monthly_data in category_monthly.items():
                if len(monthly_data) < 3:  # Need at least 3 months for trend
                    continue
                    
                amounts = [data['amount'] for data in monthly_data]
                
                # Calculate trend
                avg_amount = statistics.mean(amounts)
                recent_avg = statistics.mean(amounts[-3:]) if len(amounts) >= 3 else avg_amount
                early_avg = statistics.mean(amounts[:3]) if len(amounts) >= 3 else avg_amount
                
                trend_direction = "STABLE"
                if recent_avg > early_avg * 1.15:
                    trend_direction = "INCREASING"
                elif recent_avg < early_avg * 0.85:
                    trend_direction = "DECREASING"
                
                print(f"\n{category}:")
                print(f"  Average monthly: ${avg_amount:.2f}")
                print(f"  Early period avg: ${early_avg:.2f}")
                print(f"  Recent period avg: ${recent_avg:.2f}")
                print(f"  Trend: {trend_direction}")
                
                # Calculate month-over-month changes
                changes = []
                for i in range(1, len(amounts)):
                    if amounts[i-1] > 0:
                        change = ((amounts[i] - amounts[i-1]) / amounts[i-1]) * 100
                        changes.append(change)
                
                if changes:
                    avg_change = statistics.mean(changes)
                    print(f"  Avg monthly change: {avg_change:.1f}%")
                
        except Exception as e:
            print(f"Error analyzing trends: {e}")
    
    def detect_anomalies(self):
        """Detect anomalies or unusual spending patterns"""
        try:
            print("\n=== ANOMALY DETECTION ===")
            
            # Analyze by category
            for category in set(t['category'] for t in self.transactions):
                category_transactions = [t for t in self.transactions if t['category'] == category]
                amounts = [float(t['amount']) for t in category_transactions]
                
                if len(amounts) < 5:  # Need sufficient data
                    continue
                
                mean_amount = statistics.mean(amounts)
                stdev_amount = statistics.stdev(amounts)
                
                # Find anomalies (transactions > 2 standard deviations from mean)
                anomalies = []
                for transaction in category_transactions:
                    amount = float(transaction['amount'])
                    z_score = (amount - mean_amount) / stdev_amount if stdev_amount > 0 else 0
                    
                    if abs(z_score) > 2:  # Anomaly threshold
                        anomalies.append({
                            'date': transaction['date'],
                            'amount': amount,
                            'z_score': z_score,
                            'description': transaction['description']
                        })
                
                if anomalies:
                    print(f"\n{category} - Anomalies detected:")
                    print(f"  Normal range: ${mean_amount - 2*stdev_amount:.2f} - ${mean_amount + 2*stdev_amount:.2f}")
                    for anomaly in sorted(anomalies, key=lambda x: abs(x['z_score']), reverse=True)[:5]: