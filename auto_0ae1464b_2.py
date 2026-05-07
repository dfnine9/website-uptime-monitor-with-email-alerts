```python
"""
Monthly Spending Report Generator

This module generates comprehensive monthly spending reports with data aggregation
by category and time period. It includes summary statistics, trend analysis, and
visualization of spending patterns.

Features:
- Data aggregation by category and time period
- Summary statistics (mean, median, std dev, totals)
- Trend analysis with percentage changes
- Monthly and yearly comparisons
- Category-wise spending breakdown
- Configurable date ranges and categories

Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from typing import Dict, List, Tuple, Any


class SpendingReportGenerator:
    """Generates monthly spending reports with trend analysis."""
    
    def __init__(self):
        self.transactions = []
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                          'Shopping', 'Healthcare', 'Education', 'Miscellaneous']
    
    def generate_sample_data(self, months: int = 12) -> List[Dict]:
        """Generate sample transaction data for demonstration."""
        transactions = []
        base_date = datetime.now() - timedelta(days=months * 30)
        
        for i in range(months * 30):
            # Generate 0-5 transactions per day
            daily_transactions = random.randint(0, 5)
            current_date = base_date + timedelta(days=i)
            
            for _ in range(daily_transactions):
                transaction = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'amount': round(random.uniform(5.0, 500.0), 2),
                    'category': random.choice(self.categories),
                    'description': f"Transaction on {current_date.strftime('%Y-%m-%d')}"
                }
                transactions.append(transaction)
        
        return transactions
    
    def load_data(self, data: List[Dict] = None) -> None:
        """Load transaction data."""
        if data is None:
            self.transactions = self.generate_sample_data()
        else:
            self.transactions = data
    
    def aggregate_by_month(self) -> Dict[str, Dict[str, float]]:
        """Aggregate spending data by month and category."""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        for transaction in self.transactions:
            try:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = float(transaction['amount'])
                
                monthly_data[month_key][category] += amount
                monthly_data[month_key]['TOTAL'] += amount
            except (ValueError, KeyError) as e:
                print(f"Error processing transaction: {e}")
                continue
        
        return dict(monthly_data)
    
    def calculate_summary_stats(self, data: Dict[str, float]) -> Dict[str, float]:
        """Calculate summary statistics for given data."""
        values = [v for v in data.values() if isinstance(v, (int, float))]
        
        if not values:
            return {'mean': 0, 'median': 0, 'std_dev': 0, 'min': 0, 'max': 0, 'total': 0}
        
        try:
            return {
                'mean': round(statistics.mean(values), 2),
                'median': round(statistics.median(values), 2),
                'std_dev': round(statistics.stdev(values) if len(values) > 1 else 0, 2),
                'min': round(min(values), 2),
                'max': round(max(values), 2),
                'total': round(sum(values), 2)
            }
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {'mean': 0, 'median': 0, 'std_dev': 0, 'min': 0, 'max': 0, 'total': 0}
    
    def calculate_trends(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Calculate month-over-month trends."""
        trends = {}
        months = sorted(monthly_data.keys())
        
        for i in range(1, len(months)):
            current_month = months[i]
            previous_month = months[i-1]
            trends[current_month] = {}
            
            for category in self.categories + ['TOTAL']:
                current_amount = monthly_data[current_month].get(category, 0)
                previous_amount = monthly_data[previous_month].get(category, 0)
                
                if previous_amount > 0:
                    change = ((current_amount - previous_amount) / previous_amount) * 100
                    trends[current_month][category] = round(change, 2)
                else:
                    trends[current_month][category] = 0.0
        
        return trends
    
    def generate_category_summary(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Generate summary statistics by category across all months."""
        category_summary = {}
        
        for category in self.categories:
            category_amounts = []
            for month_data in monthly_data.values():
                if category in month_data:
                    category_amounts.append(month_data[category])
            
            if category_amounts:
                category_summary[category] = self.calculate_summary_stats({
                    f'month_{i}': amount for i, amount in enumerate(category_amounts)
                })
            else:
                category_summary[category] = {'mean': 0, 'median': 0, 'std_dev': 0, 'min': 0, 'max': 0, 'total': 0}
        
        return category_summary
    
    def print_monthly_breakdown(self, monthly_data: Dict[str, Dict[str, float]]) -> None:
        """Print detailed monthly breakdown."""
        print("\n" + "="*80)
        print("MONTHLY SPENDING BREAKDOWN")
        print("="*80)
        
        for month in sorted(monthly_data.keys()):
            print(f"\n{month}:")
            print("-" * 40)
            
            month_data = monthly_data[month]
            for category in sorted(month_data.keys()):
                if category != 'TOTAL':
                    amount = month_data[category]
                    percentage = (amount / month_data.get('TOTAL', 1)) * 100
                    print(f"  {category:<15}: ${amount:>8.2f} ({percentage:>5.1f}%)")
            
            print(f"  {'TOTAL':<15}: ${month_data.get('TOTAL', 0):>8.2f}")
    
    def print_trend_analysis(self, trends: Dict[str, Dict[str, float]]) -> None:
        """Print trend analysis."""
        print("\n" + "="*80)
        print("MONTH-OVER-MONTH TREND ANALYSIS")
        print("="*80)
        
        for month in sorted(trends.keys()):
            print(f"\n{month} vs Previous Month:")
            print("-" * 40)
            
            for category in self.categories + ['TOTAL']:
                if category in trends[month]:
                    change = trends[month][category]
                    direction = "↑" if change > 0 else "↓" if change < 0 else "→"
                    print(f"  {category:<15}: {direction} {change:>6.1f}%")
    
    def print_category_summary(self, category_summary: Dict[str, Dict[str, float]]) -> None:
        """Print category summary statistics."""
        print("\n" + "="*80)
        print("CATEGORY SUMMARY STATISTICS")
        print("="*80)
        
        print(f"{'Category':<15} {'Mean':<10} {'Median':<10}