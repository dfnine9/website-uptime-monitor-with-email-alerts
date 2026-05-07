```python
"""
Financial Data Analysis and Visualization Script

This module generates synthetic financial spending data and creates comprehensive
visual insights including pie charts for spending categories, bar charts for
monthly trends, and line graphs for spending patterns over time.

The script is self-contained and generates sample data to demonstrate various
matplotlib visualization techniques for financial analysis.

Dependencies: matplotlib, datetime (standard library)
Usage: python script.py
"""

import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

def generate_sample_data():
    """Generate sample financial data for demonstration purposes."""
    categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
    data = []
    
    # Generate 12 months of data
    start_date = datetime(2023, 1, 1)
    
    for month in range(12):
        current_date = start_date.replace(month=month + 1)
        month_name = calendar.month_name[month + 1]
        
        # Generate 20-40 transactions per month
        num_transactions = random.randint(20, 40)
        
        for _ in range(num_transactions):
            category = random.choice(categories)
            # Different spending ranges for different categories
            if category == 'Food':
                amount = random.uniform(15, 150)
            elif category == 'Transportation':
                amount = random.uniform(25, 200)
            elif category == 'Entertainment':
                amount = random.uniform(20, 300)
            elif category == 'Utilities':
                amount = random.uniform(80, 250)
            elif category == 'Shopping':
                amount = random.uniform(30, 500)
            else:  # Healthcare
                amount = random.uniform(50, 800)
            
            # Random day within the month
            day = random.randint(1, 28)
            transaction_date = current_date.replace(day=day)
            
            data.append({
                'date': transaction_date,
                'category': category,
                'amount': round(amount, 2),
                'month': month_name
            })
    
    return data

def analyze_spending_by_category(data):
    """Analyze total spending by category."""
    category_totals = defaultdict(float)
    for transaction in data:
        category_totals[transaction['category']] += transaction['amount']
    return dict(category_totals)

def analyze_monthly_trends(data):
    """Analyze spending trends by month."""
    monthly_totals = defaultdict(float)
    for transaction in data:
        monthly_totals[transaction['month']] += transaction['amount']
    
    # Ensure proper month ordering
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    ordered_monthly = {month: monthly_totals.get(month, 0) for month in month_order}
    return ordered_monthly

def analyze_daily_patterns(data):
    """Analyze spending patterns over time."""
    daily_totals = defaultdict(float)
    for transaction in data:
        date_key = transaction['date'].strftime('%Y-%m-%d')
        daily_totals[date_key] += transaction['amount']
    
    # Sort by date
    sorted_dates = sorted(daily_totals.keys())
    dates = [datetime.strptime(date, '%Y-%m-%d') for date in sorted_dates]
    amounts = [daily_totals[date] for date in sorted_dates]
    
    return dates, amounts

def create_pie_chart(category_data):
    """Create pie chart for spending by category."""
    try:
        plt.figure(figsize=(10, 8))
        
        categories = list(category_data.keys())
        amounts = list(category_data.values())
        
        # Create colors for each slice
        colors = plt.cm.Set3(range(len(categories)))
        
        # Create pie chart
        wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%',
                                          startangle=90, colors=colors)
        
        # Enhance appearance
        plt.setp(autotexts, size=10, weight='bold')
        plt.title('Spending Distribution by Category', fontsize=16, fontweight='bold', pad=20)
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        plt.axis('equal')
        
        # Add total spending information
        total_spending = sum(amounts)
        plt.figtext(0.02, 0.02, f'Total Spending: ${total_spending:,.2f}', 
                   fontsize=12, style='italic')
        
        plt.tight_layout()
        plt.savefig('spending_by_category.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✓ Pie chart for spending by category created successfully")
        
    except Exception as e:
        print(f"Error creating pie chart: {e}")

def create_bar_chart(monthly_data):
    """Create bar chart for monthly spending trends."""
    try:
        plt.figure(figsize=(12, 6))
        
        months = list(monthly_data.keys())
        amounts = list(monthly_data.values())
        
        # Create bar chart
        bars = plt.bar(months, amounts, color='skyblue', edgecolor='navy', linewidth=0.7)
        
        # Enhance appearance
        plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}', ha='center', va='bottom', fontsize=10)
        
        # Add grid for better readability
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✓ Bar chart for monthly trends created successfully")
        
    except Exception as e:
        print(f"Error creating bar chart: {e}")

def create_line_graph(dates, amounts):
    """Create line graph for spending patterns over time."""
    try:
        plt.figure(figsize=(14, 6))
        
        # Create line plot
        plt.plot(dates, amounts, marker='o', linestyle='-', linewidth=2, 
                markersize=4, color='darkgreen', alpha=0.7)
        
        # Enhance appearance
        plt.title('Daily Spending Patterns Over Time', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Daily Spending ($)', fontsize=12)
        
        # Format x-axis dates
        plt.xticks(rotation=45)
        
        # Add grid
        plt.grid(True, alpha=0.3)
        
        # Add trend line (moving average)
        if len(amounts) > 7:
            window_size = 7  # 7-day moving average
            moving_avg = []
            moving_dates = []
            
            for i in range(window_size - 1, len(amounts)):
                avg = sum(amounts[i-window_size+1:i+1]) / window_size
                moving_avg.append(avg)
                moving_dates.append(dates[i])
            
            plt.plot(moving_dates, moving_avg, linestyle='--', linewidth=2,
                    color='red', alpha=0.8, label='7-day Moving Average')
            plt.legend()
        
        plt.tight_