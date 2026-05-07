```python
"""
Data Visualization Module for Financial Transaction Analysis

This module generates comprehensive charts and graphs from categorized transaction data:
- Spending by category pie charts
- Monthly spending trends line graphs  
- Top merchants bar charts

Uses matplotlib for visualization with sample transaction data.
Self-contained with minimal dependencies.

Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch
except ImportError:
    print("Error: matplotlib is required but not installed")
    print("Install with: pip install matplotlib")
    sys.exit(1)

class TransactionVisualizer:
    """Generates visualizations from categorized transaction data"""
    
    def __init__(self, transactions_data=None):
        """Initialize with transaction data or generate sample data"""
        self.transactions = transactions_data or self._generate_sample_data()
        
    def _generate_sample_data(self):
        """Generate realistic sample transaction data for demonstration"""
        categories = ['Food & Dining', 'Transportation', 'Shopping', 'Entertainment', 
                     'Utilities', 'Healthcare', 'Groceries', 'Gas', 'Education']
        merchants = {
            'Food & Dining': ['Restaurant A', 'Cafe B', 'Fast Food C', 'Diner D'],
            'Transportation': ['Gas Station', 'Uber', 'Metro Card', 'Parking'],
            'Shopping': ['Amazon', 'Target', 'Walmart', 'Best Buy'],
            'Entertainment': ['Netflix', 'Movie Theater', 'Concert Hall', 'Gaming'],
            'Utilities': ['Electric Co', 'Water Dept', 'Internet ISP', 'Phone Co'],
            'Healthcare': ['Pharmacy', 'Doctor Office', 'Dental Care', 'Insurance'],
            'Groceries': ['Grocery Store A', 'Market B', 'Organic Foods', 'Supermarket'],
            'Gas': ['Shell', 'Exxon', 'BP', 'Chevron'],
            'Education': ['University', 'Online Course', 'Books Store', 'Supplies']
        }
        
        transactions = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(500):  # Generate 500 sample transactions
            category = random.choice(categories)
            merchant = random.choice(merchants[category])
            amount = round(random.uniform(5, 500), 2)
            date = start_date + timedelta(days=random.randint(0, 365))
            
            transactions.append({
                'date': date.strftime('%Y-%m-%d'),
                'amount': amount,
                'category': category,
                'merchant': merchant,
                'description': f'{merchant} - {category}'
            })
        
        return sorted(transactions, key=lambda x: x['date'])
    
    def create_category_pie_chart(self):
        """Generate pie chart showing spending by category"""
        try:
            category_totals = defaultdict(float)
            
            for transaction in self.transactions:
                category_totals[transaction['category']] += transaction['amount']
            
            if not category_totals:
                print("No category data available for pie chart")
                return
            
            # Sort categories by spending amount
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            categories = [item[0] for item in sorted_categories]
            amounts = [item[1] for item in sorted_categories]
            
            # Create pie chart
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(range(len(categories)))
            wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                             colors=colors, startangle=90)
            
            # Enhance text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
            
            plt.title('Spending by Category', fontsize=16, fontweight='bold', pad=20)
            plt.axis('equal')
            
            # Add total spending info
            total_spending = sum(amounts)
            plt.figtext(0.02, 0.02, f'Total Spending: ${total_spending:,.2f}', 
                       fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            plt.savefig('spending_by_category.png', dpi=300, bbox_inches='tight')
            print("✓ Category pie chart saved as 'spending_by_category.png'")
            print(f"  Total categories: {len(categories)}")
            print(f"  Total spending: ${total_spending:,.2f}")
            plt.show()
            
        except Exception as e:
            print(f"Error creating category pie chart: {e}")
    
    def create_monthly_trends_chart(self):
        """Generate line graph showing monthly spending trends"""
        try:
            monthly_totals = defaultdict(float)
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                monthly_totals[month_key] += transaction['amount']
            
            if not monthly_totals:
                print("No monthly data available for trends chart")
                return
            
            # Sort by month
            sorted_months = sorted(monthly_totals.items())
            months = [datetime.strptime(item[0], '%Y-%m') for item in sorted_months]
            amounts = [item[1] for item in sorted_months]
            
            # Create line chart
            plt.figure(figsize=(12, 6))
            plt.plot(months, amounts, marker='o', linewidth=2, markersize=6, color='#2E86AB')
            plt.fill_between(months, amounts, alpha=0.3, color='#2E86AB')
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.xticks(rotation=45)
            
            # Formatting
            plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Add trend statistics
            avg_spending = sum(amounts) / len(amounts)
            max_spending = max(amounts)
            max_month = months[amounts.index(max_spending)].strftime('%Y-%m')
            
            plt.figtext(0.02, 0.02, 
                       f'Avg: ${avg_spending:,.2f} | Peak: ${max_spending:,.2f} ({max_month})', 
                       fontsize=10)
            
            plt.tight_layout()
            plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
            print("✓ Monthly trends chart saved as 'monthly_trends.png'")
            print(f"  Months analyzed: {len(months)}")
            print(f"  Average monthly spending: ${avg_spending:,.2f}")
            plt.show()
            
        except Exception as e:
            print(f"Error creating monthly trends chart: {e}")
    
    def create_top_merchants_chart(self, top_n=10):
        """Generate bar chart showing top merchants by spending"""
        try:
            merchant_totals = defaultdict(float)
            
            for transaction in self.transactions:
                merchant_totals[transaction['merchant']] += transaction['amount']
            
            if not merchant_totals:
                print("No merchant data available for bar chart")
                return
            
            # Get top N merchants
            sorted_merchants = sorted(merchant_totals.items(),