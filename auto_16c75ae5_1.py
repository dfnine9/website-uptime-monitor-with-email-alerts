```python
#!/usr/bin/env python3
"""
Monthly Spending Analyzer

This script analyzes categorized transaction data to calculate monthly spending patterns,
identify trends, and generate comprehensive statistical summaries. It provides:
- Total spending per category
- Percentage breakdowns by category
- Month-over-month spending comparisons
- Trend analysis and insights

The script uses sample transaction data but can be easily modified to read from CSV files
or other data sources. All calculations are performed using Python's standard library.

Usage: python script.py
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import calendar


def generate_sample_data():
    """Generate sample transaction data for demonstration purposes."""
    import random
    
    categories = ['Groceries', 'Utilities', 'Entertainment', 'Transportation', 'Dining', 'Shopping', 'Healthcare']
    transactions = []
    
    # Generate 6 months of sample data
    base_date = datetime(2023, 6, 1)
    for month_offset in range(6):
        current_month = base_date.replace(month=base_date.month + month_offset)
        
        # Generate 15-30 transactions per month
        num_transactions = random.randint(15, 30)
        
        for _ in range(num_transactions):
            day = random.randint(1, 28)  # Avoid month-end issues
            transaction_date = current_month.replace(day=day)
            
            category = random.choice(categories)
            
            # Category-specific amount ranges
            amount_ranges = {
                'Groceries': (25, 150),
                'Utilities': (80, 250),
                'Entertainment': (15, 100),
                'Transportation': (20, 80),
                'Dining': (12, 65),
                'Shopping': (30, 200),
                'Healthcare': (50, 300)
            }
            
            min_amt, max_amt = amount_ranges[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            transactions.append({
                'date': transaction_date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': amount,
                'description': f'{category} purchase'
            })
    
    return transactions


class SpendingAnalyzer:
    """Analyzes spending patterns from transaction data."""
    
    def __init__(self, transactions):
        """Initialize with transaction data."""
        self.transactions = transactions
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
        self.monthly_totals = defaultdict(float)
        self._process_transactions()
    
    def _process_transactions(self):
        """Process transactions into monthly and category summaries."""
        for transaction in self.transactions:
            try:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                category = transaction['category']
                amount = float(transaction['amount'])
                
                self.monthly_data[month_key][category] += amount
                self.category_totals[category] += amount
                self.monthly_totals[month_key] += amount
                
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping invalid transaction: {e}")
                continue
    
    def calculate_category_summary(self):
        """Calculate total spending and percentages by category."""
        total_spent = sum(self.category_totals.values())
        
        summary = {}
        for category, amount in self.category_totals.items():
            percentage = (amount / total_spent * 100) if total_spent > 0 else 0
            summary[category] = {
                'total': amount,
                'percentage': percentage
            }
        
        return summary, total_spent
    
    def calculate_monthly_trends(self):
        """Calculate month-over-month changes and trends."""
        sorted_months = sorted(self.monthly_totals.keys())
        trends = {}
        
        for i, month in enumerate(sorted_months):
            if i > 0:
                prev_month = sorted_months[i-1]
                current_amount = self.monthly_totals[month]
                prev_amount = self.monthly_totals[prev_month]
                
                change = current_amount - prev_amount
                change_percent = (change / prev_amount * 100) if prev_amount > 0 else 0
                
                trends[month] = {
                    'amount': current_amount,
                    'change': change,
                    'change_percent': change_percent
                }
            else:
                trends[month] = {
                    'amount': self.monthly_totals[month],
                    'change': 0,
                    'change_percent': 0
                }
        
        return trends
    
    def identify_spending_patterns(self):
        """Identify spending patterns and insights."""
        patterns = {
            'highest_category': max(self.category_totals, key=self.category_totals.get),
            'lowest_category': min(self.category_totals, key=self.category_totals.get),
            'most_volatile_category': None,
            'average_monthly_spending': statistics.mean(self.monthly_totals.values()),
            'spending_variability': statistics.stdev(self.monthly_totals.values()) if len(self.monthly_totals) > 1 else 0
        }
        
        # Calculate category volatility
        category_volatility = {}
        for category in self.category_totals.keys():
            monthly_amounts = []
            for month in self.monthly_data:
                monthly_amounts.append(self.monthly_data[month][category])
            
            if len(monthly_amounts) > 1:
                category_volatility[category] = statistics.stdev(monthly_amounts)
            else:
                category_volatility[category] = 0
        
        patterns['most_volatile_category'] = max(category_volatility, key=category_volatility.get)
        
        return patterns
    
    def generate_report(self):
        """Generate comprehensive spending analysis report."""
        try:
            print("=" * 60)
            print("MONTHLY SPENDING ANALYSIS REPORT")
            print("=" * 60)
            
            # Category Summary
            category_summary, total_spent = self.calculate_category_summary()
            print(f"\n📊 SPENDING BY CATEGORY (Total: ${total_spent:,.2f})")
            print("-" * 50)
            
            sorted_categories = sorted(category_summary.items(), 
                                     key=lambda x: x[1]['total'], reverse=True)
            
            for category, data in sorted_categories:
                print(f"{category:15} ${data['total']:8,.2f} ({data['percentage']:5.1f}%)")
            
            # Monthly Trends
            trends = self.calculate_monthly_trends()
            print(f"\n📈 MONTHLY SPENDING TRENDS")
            print("-" * 50)
            
            for month, data in sorted(trends.items()):
                month_name = datetime.strptime(month, '%Y-%m').strftime('%B %Y')
                change_symbol = "↗️" if data['change'] > 0 else "↘️" if data['change'] < 0 else "➡️"
                
                print(f"{month_name:12} ${data['amount']:8,.2f} "
                      f"{change_symbol} {data['change']:+7.2f} ({data['change_percent']:+5.1f}%)")
            
            # Patterns and Insights
            patterns = self.identify_spending_patterns()
            print(f"\n🔍 SPENDING INSIGHTS")
            print("-" * 50)
            print(f"Highest Spending Category:    {patterns['highest_category']}")
            print(f"Lowest Spending Category:     {patterns['lowest_category']}")
            print(f"Most Variable Category:       {patterns['most_volatile_category']}")
            print(f"Average Monthly Spending:     ${patterns['average_monthly_spending']:,.