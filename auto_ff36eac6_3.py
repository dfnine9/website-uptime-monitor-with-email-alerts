```python
"""
Personal Finance Visualization Script

This module creates interactive visualizations for personal finance data analysis.
It generates sample spending data and creates various charts to display:
- Spending patterns over time
- Category distribution (pie chart)
- Monthly spending trends
- Weekly spending patterns

The script uses matplotlib for static visualizations and includes interactive
elements where possible. All data is synthetically generated for demonstration.

Usage: python script.py

Dependencies: matplotlib, numpy (falls back to manual calculations if not available)
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import random
import calendar
import json

def generate_sample_data():
    """Generate sample financial data for visualization."""
    try:
        categories = ['Food & Dining', 'Transportation', 'Shopping', 'Entertainment', 
                     'Bills & Utilities', 'Healthcare', 'Travel', 'Education', 'Other']
        
        # Generate 90 days of sample transactions
        transactions = []
        start_date = datetime.now() - timedelta(days=90)
        
        for i in range(300):  # ~3-4 transactions per day on average
            date = start_date + timedelta(days=random.randint(0, 89))
            category = random.choice(categories)
            
            # Different spending patterns by category
            if category == 'Food & Dining':
                amount = random.uniform(5, 80)
            elif category == 'Transportation':
                amount = random.uniform(3, 50)
            elif category == 'Bills & Utilities':
                amount = random.uniform(50, 300)
            elif category == 'Shopping':
                amount = random.uniform(10, 200)
            elif category == 'Travel':
                amount = random.uniform(100, 1000)
            else:
                amount = random.uniform(5, 150)
            
            transactions.append({
                'date': date,
                'category': category,
                'amount': round(amount, 2),
                'description': f"{category} expense"
            })
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'])
        return transactions
        
    except Exception as e:
        print(f"Error generating sample data: {e}")
        return []

def create_category_distribution_chart(transactions):
    """Create a pie chart showing spending distribution by category."""
    try:
        category_totals = {}
        for transaction in transactions:
            category = transaction['category']
            amount = transaction['amount']
            category_totals[category] = category_totals.get(category, 0) + amount
        
        if not category_totals:
            print("No data available for category distribution chart")
            return
        
        # Create pie chart
        plt.figure(figsize=(10, 8))
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        colors = plt.cm.Set3(range(len(categories)))
        
        wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                          colors=colors, startangle=90)
        
        plt.title('Spending Distribution by Category', fontsize=16, fontweight='bold')
        
        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
        
        # Print category totals
        print("\nCategory Spending Summary:")
        print("-" * 40)
        for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            print(f"{category}: ${total:.2f}")
        
    except Exception as e:
        print(f"Error creating category distribution chart: {e}")

def create_monthly_trends_chart(transactions):
    """Create a line chart showing monthly spending trends."""
    try:
        monthly_totals = {}
        
        for transaction in transactions:
            month_key = transaction['date'].strftime('%Y-%m')
            amount = transaction['amount']
            monthly_totals[month_key] = monthly_totals.get(month_key, 0) + amount
        
        if not monthly_totals:
            print("No data available for monthly trends chart")
            return
        
        # Sort by month
        sorted_months = sorted(monthly_totals.keys())
        amounts = [monthly_totals[month] for month in sorted_months]
        
        # Convert month strings to datetime objects for better plotting
        month_dates = [datetime.strptime(month, '%Y-%m') for month in sorted_months]
        
        plt.figure(figsize=(12, 6))
        plt.plot(month_dates, amounts, marker='o', linewidth=2, markersize=8, color='#2E86C1')
        plt.fill_between(month_dates, amounts, alpha=0.3, color='#2E86C1')
        
        plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Total Spending ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Format x-axis to show month names
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        # Add value annotations on points
        for i, (date, amount) in enumerate(zip(month_dates, amounts)):
            plt.annotate(f'${amount:.0f}', (date, amount), 
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        plt.tight_layout()
        plt.show()
        
        # Print monthly summary
        print("\nMonthly Spending Summary:")
        print("-" * 30)
        for month, total in zip(sorted_months, amounts):
            month_name = datetime.strptime(month, '%Y-%m').strftime('%B %Y')
            print(f"{month_name}: ${total:.2f}")
        
    except Exception as e:
        print(f"Error creating monthly trends chart: {e}")

def create_daily_spending_pattern(transactions):
    """Create a bar chart showing spending patterns by day of week."""
    try:
        daily_totals = {i: 0 for i in range(7)}  # 0 = Monday, 6 = Sunday
        daily_counts = {i: 0 for i in range(7)}
        
        for transaction in transactions:
            day_of_week = transaction['date'].weekday()
            daily_totals[day_of_week] += transaction['amount']
            daily_counts[day_of_week] += 1
        
        # Calculate average spending per day
        daily_averages = {}
        for day in range(7):
            if daily_counts[day] > 0:
                daily_averages[day] = daily_totals[day] / daily_counts[day]
            else:
                daily_averages[day] = 0
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        averages = [daily_averages[i] for i in range(7)]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(days, averages, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                                             '#FECA57', '#FF9FF3', '#54A0FF'])
        
        plt.title('Average Daily Spending Patterns', fontsize=16, fontweight='bold')
        plt.xlabel('Day of Week', fontsize=12)
        plt.ylabel('Average Spending ($)', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, avg in zip(bars, averages):