```python
"""
Personal Finance Data Analysis Module

This module provides comprehensive analysis of monthly spending data including:
- Monthly spending totals by category
- Spending trend identification across time periods
- Statistical insights (averages, percentages, distributions)
- Transaction pattern analysis

The module uses sample data for demonstration but can be easily adapted
to work with real financial data from CSV files or APIs.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import random


class SpendingAnalyzer:
    """Analyzes spending patterns and generates financial insights."""
    
    def __init__(self):
        self.transactions = []
        self.categories = {}
        
    def generate_sample_data(self):
        """Generate sample transaction data for demonstration."""
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                     'Shopping', 'Healthcare', 'Education', 'Insurance']
        
        # Generate 6 months of sample data
        start_date = datetime.now() - timedelta(days=180)
        
        for i in range(200):  # 200 sample transactions
            date = start_date + timedelta(days=random.randint(0, 180))
            category = random.choice(categories)
            
            # Different spending patterns by category
            if category == 'Food':
                amount = round(random.uniform(15, 80), 2)
            elif category == 'Utilities':
                amount = round(random.uniform(50, 200), 2)
            elif category == 'Transportation':
                amount = round(random.uniform(20, 150), 2)
            else:
                amount = round(random.uniform(10, 300), 2)
            
            self.transactions.append({
                'date': date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': amount,
                'description': f'{category} transaction {i+1}'
            })
    
    def calculate_monthly_totals(self):
        """Calculate total spending by category for each month."""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        try:
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_key][category] += amount
                
            return dict(monthly_data)
            
        except (KeyError, ValueError) as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def identify_spending_trends(self, monthly_data):
        """Identify spending trends across months."""
        trends = {}
        
        try:
            # Calculate month-over-month changes
            sorted_months = sorted(monthly_data.keys())
            
            for category in set().union(*[month_data.keys() for month_data in monthly_data.values()]):
                category_amounts = []
                for month in sorted_months:
                    amount = monthly_data[month].get(category, 0)
                    category_amounts.append(amount)
                
                if len(category_amounts) >= 2:
                    # Calculate trend (positive = increasing, negative = decreasing)
                    first_half = sum(category_amounts[:len(category_amounts)//2])
                    second_half = sum(category_amounts[len(category_amounts)//2:])
                    
                    if first_half > 0:
                        trend_percent = ((second_half - first_half) / first_half) * 100
                    else:
                        trend_percent = 0
                    
                    trends[category] = {
                        'trend_percent': round(trend_percent, 2),
                        'direction': 'increasing' if trend_percent > 5 else 'decreasing' if trend_percent < -5 else 'stable',
                        'monthly_amounts': category_amounts
                    }
            
            return trends
            
        except Exception as e:
            print(f"Error identifying trends: {e}")
            return {}
    
    def calculate_statistics(self):
        """Calculate comprehensive statistical insights."""
        stats = {}
        
        try:
            if not self.transactions:
                return stats
            
            # Basic statistics
            amounts = [t['amount'] for t in self.transactions]
            total_spending = sum(amounts)
            
            stats['total_transactions'] = len(self.transactions)
            stats['total_spending'] = round(total_spending, 2)
            stats['average_transaction'] = round(statistics.mean(amounts), 2)
            stats['median_transaction'] = round(statistics.median(amounts), 2)
            
            if len(amounts) > 1:
                stats['std_deviation'] = round(statistics.stdev(amounts), 2)
            
            # Category analysis
            category_totals = defaultdict(float)
            category_counts = defaultdict(int)
            
            for transaction in self.transactions:
                category = transaction['category']
                amount = transaction['amount']
                category_totals[category] += amount
                category_counts[category] += 1
            
            # Category percentages
            category_percentages = {}
            for category, total in category_totals.items():
                percentage = (total / total_spending) * 100
                category_percentages[category] = round(percentage, 2)
            
            stats['category_percentages'] = category_percentages
            stats['category_averages'] = {
                category: round(total / category_counts[category], 2)
                for category, total in category_totals.items()
            }
            
            # Top spending categories
            stats['top_categories'] = dict(
                sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            )
            
            return stats
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {}
    
    def print_analysis_report(self):
        """Print comprehensive analysis report to stdout."""
        try:
            print("=" * 60)
            print("PERSONAL FINANCE ANALYSIS REPORT")
            print("=" * 60)
            
            # Generate and analyze data
            self.generate_sample_data()
            monthly_data = self.calculate_monthly_totals()
            trends = self.identify_spending_trends(monthly_data)
            stats = self.calculate_statistics()
            
            # Overall Statistics
            print("\n📊 OVERALL STATISTICS")
            print("-" * 30)
            print(f"Total Transactions: {stats.get('total_transactions', 0)}")
            print(f"Total Spending: ${stats.get('total_spending', 0):,.2f}")
            print(f"Average Transaction: ${stats.get('average_transaction', 0):.2f}")
            print(f"Median Transaction: ${stats.get('median_transaction', 0):.2f}")
            if 'std_deviation' in stats:
                print(f"Standard Deviation: ${stats['std_deviation']:.2f}")
            
            # Monthly Breakdown
            print("\n📅 MONTHLY SPENDING BY CATEGORY")
            print("-" * 40)
            for month in sorted(monthly_data.keys()):
                print(f"\n{month}:")
                month_total = sum(monthly_data[month].values())
                for category, amount in sorted(monthly_data[month].items(), key=lambda x: x[1], reverse=True):
                    print(f"  {category:15}: ${amount:8.2f}")
                print(f"  {'TOTAL':15}: ${month_total:8.2f}")
            
            # Category Analysis
            print("\n🏷️ CATEGORY ANALYSIS")
            print("-" * 30)
            print("Spending by Category (% of total):")
            for category, percentage in sorted(stats.get('category_percentages', {}).items(), 
                                             key=lambda x: x[1], reverse=True):
                amount = stats.get('top_categories', {}).get(category, 0)
                print(f"  {category:15}: {percentage:5.1f}% (${amount: