```python
"""
Personal Finance Data Analysis Module

This module analyzes personal spending patterns from transaction data.
It calculates monthly spending by category, identifies top expense categories,
tracks spending trends over time, and detects unusual transactions or spending spikes.

Features:
- Monthly spending analysis by category
- Top expense category identification
- Spending trend analysis over time
- Anomaly detection for unusual transactions
- Statistical analysis of spending patterns

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math


class SpendingAnalyzer:
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
        
    def generate_sample_data(self):
        """Generate realistic sample transaction data for analysis"""
        import random
        
        categories = [
            'Groceries', 'Restaurants', 'Transportation', 'Utilities', 
            'Entertainment', 'Shopping', 'Healthcare', 'Insurance',
            'Gas', 'Coffee', 'Subscriptions', 'Rent'
        ]
        
        base_date = datetime(2024, 1, 1)
        
        for i in range(500):
            # Generate random date within last 12 months
            days_offset = random.randint(0, 365)
            transaction_date = base_date + timedelta(days=days_offset)
            
            category = random.choice(categories)
            
            # Category-specific amount ranges for realism
            if category == 'Rent':
                amount = random.uniform(1200, 2000)
            elif category == 'Groceries':
                amount = random.uniform(20, 200)
            elif category == 'Utilities':
                amount = random.uniform(80, 300)
            elif category == 'Coffee':
                amount = random.uniform(3, 15)
            elif category == 'Gas':
                amount = random.uniform(30, 80)
            else:
                amount = random.uniform(10, 500)
            
            # Occasionally add anomalous transactions
            if random.random() < 0.05:  # 5% chance of anomaly
                amount *= random.uniform(3, 10)
            
            self.transactions.append({
                'date': transaction_date,
                'category': category,
                'amount': round(amount, 2),
                'description': f"{category} purchase"
            })
    
    def process_transactions(self):
        """Process transactions into monthly and category data structures"""
        try:
            for transaction in self.transactions:
                date = transaction['date']
                month_key = f"{date.year}-{date.month:02d}"
                category = transaction['category']
                amount = transaction['amount']
                
                self.monthly_data[month_key][category] += amount
                self.category_totals[category] += amount
                
        except Exception as e:
            print(f"Error processing transactions: {e}")
            raise
    
    def calculate_monthly_patterns(self):
        """Calculate and display monthly spending patterns by category"""
        print("=" * 60)
        print("MONTHLY SPENDING PATTERNS BY CATEGORY")
        print("=" * 60)
        
        try:
            for month in sorted(self.monthly_data.keys()):
                print(f"\nMonth: {month}")
                print("-" * 30)
                
                month_data = self.monthly_data[month]
                total_month = sum(month_data.values())
                
                # Sort categories by spending amount
                sorted_categories = sorted(month_data.items(), key=lambda x: x[1], reverse=True)
                
                for category, amount in sorted_categories:
                    percentage = (amount / total_month) * 100 if total_month > 0 else 0
                    print(f"{category:<15}: ${amount:>8.2f} ({percentage:>5.1f}%)")
                
                print(f"{'TOTAL':<15}: ${total_month:>8.2f}")
                
        except Exception as e:
            print(f"Error calculating monthly patterns: {e}")
    
    def identify_top_categories(self):
        """Identify and display top expense categories"""
        print("\n" + "=" * 60)
        print("TOP EXPENSE CATEGORIES (Overall)")
        print("=" * 60)
        
        try:
            total_spending = sum(self.category_totals.values())
            sorted_categories = sorted(self.category_totals.items(), key=lambda x: x[1], reverse=True)
            
            print(f"{'Rank':<4} {'Category':<15} {'Amount':<12} {'Percentage':<10}")
            print("-" * 50)
            
            for rank, (category, amount) in enumerate(sorted_categories, 1):
                percentage = (amount / total_spending) * 100 if total_spending > 0 else 0
                print(f"{rank:<4} {category:<15} ${amount:<11.2f} {percentage:<9.1f}%")
            
            print(f"\nTotal Spending: ${total_spending:.2f}")
            
        except Exception as e:
            print(f"Error identifying top categories: {e}")
    
    def analyze_spending_trends(self):
        """Analyze spending trends over time"""
        print("\n" + "=" * 60)
        print("SPENDING TRENDS OVER TIME")
        print("=" * 60)
        
        try:
            # Calculate monthly totals
            monthly_totals = {}
            for month, categories in self.monthly_data.items():
                monthly_totals[month] = sum(categories.values())
            
            sorted_months = sorted(monthly_totals.keys())
            
            if len(sorted_months) < 2:
                print("Insufficient data for trend analysis")
                return
            
            print(f"{'Month':<10} {'Total Spending':<15} {'Change':<15} {'Trend'}")
            print("-" * 60)
            
            previous_amount = None
            for month in sorted_months:
                current_amount = monthly_totals[month]
                
                if previous_amount is not None:
                    change = current_amount - previous_amount
                    change_pct = (change / previous_amount) * 100 if previous_amount > 0 else 0
                    
                    trend_indicator = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                    change_str = f"${change:+.2f} ({change_pct:+.1f}%)"
                else:
                    change_str = "N/A"
                    trend_indicator = "🟦"
                
                print(f"{month:<10} ${current_amount:<14.2f} {change_str:<15} {trend_indicator}")
                previous_amount = current_amount
            
            # Calculate overall trend
            if len(sorted_months) >= 3:
                amounts = [monthly_totals[month] for month in sorted_months]
                avg_change = statistics.mean([amounts[i] - amounts[i-1] for i in range(1, len(amounts))])
                
                print(f"\nAverage monthly change: ${avg_change:+.2f}")
                if avg_change > 0:
                    print("Overall trend: INCREASING spending 📈")
                elif avg_change < 0:
                    print("Overall trend: DECREASING spending 📉")
                else:
                    print("Overall trend: STABLE spending ➡️")
                    
        except Exception as e:
            print(f"Error analyzing spending trends: {e}")
    
    def detect_anomalous_transactions(self):
        """Detect unusual transactions or spending spikes"""
        print("\n" + "=" * 60)
        print("ANOMALOUS TRANSACTION DETECTION")
        print("=" * 60)
        
        try:
            # Group transactions by category for statistical analysis
            category_amounts = defaultdict(list)
            for transaction in self.transactions:
                category_amounts[transaction['category']].append(transaction['amount'])
            
            anom