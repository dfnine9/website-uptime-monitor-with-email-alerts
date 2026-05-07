```python
"""
Transaction Data Analysis Module

This module processes categorized financial transactions to generate comprehensive 
spending insights including:
- Monthly spending totals by category
- Trend analysis over time periods
- Anomaly detection for unusual expenses
- Statistical summaries and patterns

The module uses statistical methods to identify spending patterns and flag 
transactions that deviate significantly from normal spending behavior.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math


class TransactionAnalyzer:
    """Analyzes financial transactions for spending patterns and anomalies."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.category_stats = defaultdict(list)
    
    def load_sample_data(self):
        """Generate sample transaction data for demonstration."""
        import random
        
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
        
        # Generate 6 months of sample data
        base_date = datetime(2024, 1, 1)
        
        for month in range(6):
            for day in range(1, 29):  # Avoid month-end complications
                current_date = base_date + timedelta(days=month*30 + day)
                
                # Generate 1-3 transactions per day
                for _ in range(random.randint(1, 3)):
                    category = random.choice(categories)
                    
                    # Different spending patterns by category
                    if category == 'Food':
                        amount = random.uniform(10, 150)
                    elif category == 'Transportation':
                        amount = random.uniform(5, 80)
                    elif category == 'Entertainment':
                        amount = random.uniform(20, 200)
                    elif category == 'Utilities':
                        amount = random.uniform(50, 300)
                    elif category == 'Shopping':
                        amount = random.uniform(25, 500)
                    else:  # Healthcare
                        amount = random.uniform(30, 400)
                    
                    # Add some anomalies (5% chance of unusually high spending)
                    if random.random() < 0.05:
                        amount *= random.uniform(3, 8)
                    
                    self.transactions.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'amount': round(amount, 2),
                        'category': category,
                        'description': f'{category} expense'
                    })
    
    def process_transactions(self):
        """Process transactions to calculate monthly totals and category statistics."""
        try:
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                # Monthly totals by category
                self.monthly_totals[month_key][category] += amount
                
                # Category statistics for anomaly detection
                self.category_stats[category].append(amount)
                
        except Exception as e:
            print(f"Error processing transactions: {e}")
            return False
        return True
    
    def calculate_monthly_insights(self):
        """Calculate and display monthly spending insights."""
        try:
            print("=" * 60)
            print("MONTHLY SPENDING ANALYSIS")
            print("=" * 60)
            
            for month in sorted(self.monthly_totals.keys()):
                print(f"\n📅 Month: {month}")
                print("-" * 30)
                
                monthly_data = self.monthly_totals[month]
                total_month = sum(monthly_data.values())
                
                # Sort categories by spending amount
                sorted_categories = sorted(monthly_data.items(), key=lambda x: x[1], reverse=True)
                
                for category, amount in sorted_categories:
                    percentage = (amount / total_month) * 100 if total_month > 0 else 0
                    print(f"  {category:<15}: ${amount:>8.2f} ({percentage:>5.1f}%)")
                
                print(f"  {'TOTAL':<15}: ${total_month:>8.2f}")
                
        except Exception as e:
            print(f"Error calculating monthly insights: {e}")
    
    def analyze_trends(self):
        """Analyze spending trends across months."""
        try:
            print("\n" + "=" * 60)
            print("SPENDING TREND ANALYSIS")
            print("=" * 60)
            
            # Calculate total spending per month
            monthly_totals_list = []
            months = sorted(self.monthly_totals.keys())
            
            for month in months:
                total = sum(self.monthly_totals[month].values())
                monthly_totals_list.append(total)
            
            if len(monthly_totals_list) >= 2:
                # Calculate trend
                avg_spending = statistics.mean(monthly_totals_list)
                first_half = monthly_totals_list[:len(monthly_totals_list)//2]
                second_half = monthly_totals_list[len(monthly_totals_list)//2:]
                
                if len(first_half) > 0 and len(second_half) > 0:
                    early_avg = statistics.mean(first_half)
                    recent_avg = statistics.mean(second_half)
                    
                    trend_direction = "increasing" if recent_avg > early_avg else "decreasing"
                    trend_magnitude = abs(recent_avg - early_avg)
                    trend_percentage = (trend_magnitude / early_avg) * 100 if early_avg > 0 else 0
                    
                    print(f"📈 Average Monthly Spending: ${avg_spending:.2f}")
                    print(f"📊 Spending Trend: {trend_direction.title()} by ${trend_magnitude:.2f} ({trend_percentage:.1f}%)")
                
                # Category trends
                print("\n🔍 Category Trend Analysis:")
                all_categories = set()
                for month_data in self.monthly_totals.values():
                    all_categories.update(month_data.keys())
                
                for category in sorted(all_categories):
                    category_amounts = []
                    for month in months:
                        amount = self.monthly_totals[month].get(category, 0)
                        category_amounts.append(amount)
                    
                    if len(category_amounts) >= 2:
                        first_val = statistics.mean(category_amounts[:len(category_amounts)//2])
                        second_val = statistics.mean(category_amounts[len(category_amounts)//2:])
                        
                        if first_val > 0:
                            change = ((second_val - first_val) / first_val) * 100
                            direction = "↗️" if change > 5 else "↘️" if change < -5 else "➡️"
                            print(f"  {category:<15}: {direction} {change:>+6.1f}%")
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
    
    def detect_anomalies(self, threshold_multiplier=2.5):
        """Detect anomalous transactions using statistical methods."""
        try:
            print("\n" + "=" * 60)
            print("ANOMALY DETECTION")
            print("=" * 60)
            
            anomalies = []
            
            for category, amounts in self.category_stats.items():
                if len(amounts) < 5:  # Need sufficient data
                    continue
                
                mean_amount = statistics.mean(amounts)
                stdev_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
                
                # Find transactions that are unusually high
                threshold = mean_amount + (threshold_multiplier * stdev_amount)
                
                for transaction in self.transactions:
                    if (transaction['category'] == category and 
                        transaction['amount