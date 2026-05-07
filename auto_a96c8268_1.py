```python
"""
Personal Finance Spending Insights Module

This module analyzes spending data to generate comprehensive insights including:
- Category totals and percentages
- Monthly spending trends
- Top merchants by spending volume
- Visual charts (pie charts for categories, bar charts for trends)

The module processes financial transaction data and creates visualizations
to help users understand their spending patterns and make informed decisions.

Usage:
    python script.py

Dependencies:
    - matplotlib (for visualization)
    - datetime (standard library)
    - json (standard library)
    - random (standard library - for demo data)
"""

import json
import datetime
from collections import defaultdict, Counter
import random

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
except ImportError:
    print("Error: matplotlib is required but not installed.")
    print("Please install with: pip install matplotlib")
    exit(1)


class SpendingAnalyzer:
    """Analyzes spending data and generates insights with visualizations."""
    
    def __init__(self):
        self.transactions = []
        self.category_totals = defaultdict(float)
        self.monthly_totals = defaultdict(float)
        self.merchant_totals = defaultdict(float)
    
    def load_sample_data(self):
        """Generate sample transaction data for demonstration."""
        categories = ['Food & Dining', 'Transportation', 'Shopping', 'Entertainment', 
                     'Bills & Utilities', 'Healthcare', 'Travel', 'Gas']
        merchants = ['Amazon', 'Uber', 'Starbucks', 'Target', 'Shell', 'Netflix', 
                    'Walmart', 'McDonald\'s', 'CVS', 'Home Depot']
        
        # Generate 100 random transactions over the last 6 months
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=180)
        
        for _ in range(100):
            random_days = random.randint(0, 180)
            transaction_date = start_date + datetime.timedelta(days=random_days)
            
            transaction = {
                'date': transaction_date.strftime('%Y-%m-%d'),
                'amount': round(random.uniform(5.0, 500.0), 2),
                'category': random.choice(categories),
                'merchant': random.choice(merchants),
                'description': f'Transaction at {random.choice(merchants)}'
            }
            self.transactions.append(transaction)
        
        print(f"Generated {len(self.transactions)} sample transactions")
    
    def calculate_category_totals(self):
        """Calculate total spending by category."""
        try:
            self.category_totals.clear()
            for transaction in self.transactions:
                category = transaction.get('category', 'Unknown')
                amount = float(transaction.get('amount', 0))
                self.category_totals[category] += amount
            
            # Sort by spending amount (descending)
            self.category_totals = dict(sorted(
                self.category_totals.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
        except (ValueError, KeyError) as e:
            print(f"Error calculating category totals: {e}")
    
    def calculate_monthly_trends(self):
        """Calculate spending trends by month."""
        try:
            self.monthly_totals.clear()
            for transaction in self.transactions:
                date_str = transaction.get('date', '')
                amount = float(transaction.get('amount', 0))
                
                # Parse date and create month-year key
                transaction_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                month_key = transaction_date.strftime('%Y-%m')
                
                self.monthly_totals[month_key] += amount
            
            # Sort by date
            self.monthly_totals = dict(sorted(self.monthly_totals.items()))
            
        except (ValueError, KeyError) as e:
            print(f"Error calculating monthly trends: {e}")
    
    def calculate_top_merchants(self, top_n=10):
        """Calculate top merchants by spending volume."""
        try:
            self.merchant_totals.clear()
            for transaction in self.transactions:
                merchant = transaction.get('merchant', 'Unknown')
                amount = float(transaction.get('amount', 0))
                self.merchant_totals[merchant] += amount
            
            # Get top N merchants
            top_merchants = dict(sorted(
                self.merchant_totals.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n])
            
            return top_merchants
            
        except (ValueError, KeyError) as e:
            print(f"Error calculating top merchants: {e}")
            return {}
    
    def create_category_pie_chart(self):
        """Create pie chart for category breakdown."""
        try:
            if not self.category_totals:
                print("No category data available for pie chart")
                return
            
            plt.figure(figsize=(10, 8))
            categories = list(self.category_totals.keys())
            amounts = list(self.category_totals.values())
            
            # Create pie chart with percentages
            plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
            plt.title('Spending by Category', fontsize=16, fontweight='bold')
            plt.axis('equal')
            
            # Add total spending to title
            total_spending = sum(amounts)
            plt.suptitle(f'Total Spending: ${total_spending:,.2f}', fontsize=12)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error creating category pie chart: {e}")
    
    def create_monthly_bar_chart(self):
        """Create bar chart for monthly spending patterns."""
        try:
            if not self.monthly_totals:
                print("No monthly data available for bar chart")
                return
            
            plt.figure(figsize=(12, 6))
            months = list(self.monthly_totals.keys())
            amounts = list(self.monthly_totals.values())
            
            # Convert month strings to datetime objects for better formatting
            month_dates = [datetime.datetime.strptime(month, '%Y-%m') for month in months]
            
            plt.bar(month_dates, amounts, color='skyblue', edgecolor='navy', alpha=0.7)
            plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold')
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            
            # Format x-axis to show month names
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.xticks(rotation=45)
            
            # Add value labels on bars
            for i, amount in enumerate(amounts):
                plt.text(month_dates[i], amount + max(amounts) * 0.01, 
                        f'${amount:,.0f}', ha='center', va='bottom', fontsize=10)
            
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error creating monthly bar chart: {e}")
    
    def print_insights(self):
        """Print comprehensive spending insights to stdout."""
        try:
            print("\n" + "="*60)
            print("SPENDING INSIGHTS REPORT")
            print("="*60)
            
            # Category breakdown
            print("\n📊 CATEGORY BREAKDOWN:")
            print("-" * 30)
            total_spending = sum(self.category_totals.values())
            
            for category, amount in self.category_totals.items():
                percentage = (amount / total_spending) * 100 if total_spending > 0 else 0
                print(f"{category:<20}: ${amount:>8,.2f}