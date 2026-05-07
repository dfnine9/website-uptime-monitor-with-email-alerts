```python
#!/usr/bin/env python3
"""
Financial Transaction Reporting Module

This module processes categorized transaction data to generate comprehensive monthly
spending summaries. It calculates category totals and percentages, and creates 
visualizations including bar charts, pie charts, and trend lines.

The module generates sample transaction data for demonstration purposes and provides
detailed spending analysis with visual representations of financial patterns.

Dependencies: Standard library only (matplotlib simulation using ASCII charts)
Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

class TransactionReporter:
    """Processes transaction data and generates spending reports with visualizations."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_summaries = defaultdict(dict)
        
    def generate_sample_data(self, months=6):
        """Generate sample transaction data for testing purposes."""
        categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Health & Fitness', 'Travel', 'Education',
            'Groceries', 'Gas', 'Insurance', 'Subscriptions'
        ]
        
        start_date = datetime.now() - timedelta(days=months * 30)
        
        for _ in range(500):  # Generate 500 sample transactions
            transaction_date = start_date + timedelta(days=random.randint(0, months * 30))
            transaction = {
                'id': f'TXN_{random.randint(1000, 9999)}',
                'date': transaction_date.strftime('%Y-%m-%d'),
                'amount': round(random.uniform(5.0, 500.0), 2),
                'category': random.choice(categories),
                'description': f'Transaction in {random.choice(categories)}',
                'month_year': transaction_date.strftime('%Y-%m')
            }
            self.transactions.append(transaction)
    
    def process_transactions(self):
        """Process transactions and calculate monthly summaries."""
        try:
            monthly_data = defaultdict(lambda: {'total': 0, 'categories': defaultdict(float), 'count': 0})
            
            for transaction in self.transactions:
                month_year = transaction['month_year']
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_year]['total'] += amount
                monthly_data[month_year]['categories'][category] += amount
                monthly_data[month_year]['count'] += 1
            
            # Calculate percentages and store summaries
            for month_year, data in monthly_data.items():
                total = data['total']
                category_percentages = {}
                
                for category, amount in data['categories'].items():
                    percentage = (amount / total) * 100 if total > 0 else 0
                    category_percentages[category] = {
                        'amount': round(amount, 2),
                        'percentage': round(percentage, 2)
                    }
                
                self.monthly_summaries[month_year] = {
                    'total_spent': round(total, 2),
                    'transaction_count': data['count'],
                    'categories': category_percentages,
                    'top_category': max(data['categories'].items(), key=lambda x: x[1])[0] if data['categories'] else 'None'
                }
                
        except Exception as e:
            print(f"Error processing transactions: {e}")
            raise
    
    def create_ascii_bar_chart(self, data, title, max_width=50):
        """Create ASCII bar chart visualization."""
        print(f"\n{title}")
        print("=" * len(title))
        
        if not data:
            print("No data available")
            return
            
        max_value = max(data.values()) if data.values() else 1
        
        for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]:
            bar_length = int((value / max_value) * max_width)
            bar = "█" * bar_length
            print(f"{label[:20]:<20} │{bar:<{max_width}} │ ${value:,.2f}")
    
    def create_ascii_pie_chart(self, data, title):
        """Create ASCII representation of pie chart."""
        print(f"\n{title}")
        print("=" * len(title))
        
        if not data:
            print("No data available")
            return
            
        total = sum(data.values())
        
        for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
            percentage = (value / total) * 100 if total > 0 else 0
            dots = int(percentage / 2)  # Scale dots to percentage
            visual = "●" * dots
            print(f"{label[:25]:<25} │ {visual:<50} │ {percentage:5.1f}% (${value:,.2f})")
    
    def create_trend_visualization(self, monthly_totals):
        """Create ASCII trend line visualization."""
        print(f"\nMonthly Spending Trend")
        print("=" * 21)
        
        if not monthly_totals:
            print("No data available")
            return
            
        sorted_months = sorted(monthly_totals.items())
        max_amount = max(monthly_totals.values()) if monthly_totals.values() else 1
        
        for month, amount in sorted_months:
            # Convert month from YYYY-MM to readable format
            try:
                year, month_num = month.split('-')
                month_name = calendar.month_abbr[int(month_num)]
                display_month = f"{month_name} {year}"
            except:
                display_month = month
                
            trend_length = int((amount / max_amount) * 40)
            trend_line = "▓" * trend_length
            print(f"{display_month:<10} │{trend_line:<40} │ ${amount:,.2f}")
    
    def generate_monthly_report(self, month_year=None):
        """Generate detailed report for a specific month or all months."""
        try:
            if month_year:
                months_to_report = [month_year] if month_year in self.monthly_summaries else []
            else:
                months_to_report = sorted(self.monthly_summaries.keys())
            
            if not months_to_report:
                print(f"No data found for {month_year if month_year else 'any month'}")
                return
            
            print("FINANCIAL TRANSACTION ANALYSIS REPORT")
            print("=" * 40)
            
            # Overall summary
            total_all_months = sum(summary['total_spent'] for summary in self.monthly_summaries.values())
            total_transactions = sum(summary['transaction_count'] for summary in self.monthly_summaries.values())
            
            print(f"Report Period: {min(months_to_report)} to {max(months_to_report)}")
            print(f"Total Amount Spent: ${total_all_months:,.2f}")
            print(f"Total Transactions: {total_transactions:,}")
            print(f"Average per Transaction: ${total_all_months/total_transactions:.2f}" if total_transactions > 0 else "Average per Transaction: $0.00")
            
            # Monthly breakdown
            for month in months_to_report:
                summary = self.monthly_summaries[month]
                
                try:
                    year, month_num = month.split('-')
                    month_name = calendar.month_name[int(month_num)]
                    display_month = f"{month_name} {year}"
                except:
                    display_month = month
                
                print(f"\n\n📊 MONTH: {display_month}")
                print("-" * 30)
                print(f"Total Spent: ${summary['total_spent']:,.2f}")
                print(f"Transactions: {summary['transaction_count']}")
                print(f"Top Category: {summary['top_category']}")
                print(f"Avg per Transaction: ${