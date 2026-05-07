```python
"""
Financial Data Visualization Script

This script generates interactive financial data visualizations including:
- Pie charts for expense category breakdowns
- Line graphs for spending trends over time
- Bar charts for monthly spending comparisons

The script creates sample financial data and produces three types of charts
using matplotlib with interactive features. All charts are saved as HTML files
for interactive viewing in web browsers.

Requirements:
- Python 3.6+
- matplotlib
- numpy (usually included with matplotlib)

Usage:
    python script.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
import random
import json
import os

def generate_sample_data():
    """Generate sample financial data for visualization."""
    try:
        # Category data for pie chart
        categories = {
            'Housing': 1200,
            'Food': 800,
            'Transportation': 400,
            'Entertainment': 300,
            'Utilities': 250,
            'Healthcare': 200,
            'Shopping': 350,
            'Other': 150
        }
        
        # Monthly spending data for bar chart (12 months)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_spending = [random.randint(2500, 4000) for _ in range(12)]
        
        # Daily spending trend for line chart (30 days)
        base_date = datetime.now() - timedelta(days=30)
        dates = [(base_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
        daily_spending = [random.randint(50, 200) for _ in range(30)]
        
        return categories, months, monthly_spending, dates, daily_spending
        
    except Exception as e:
        print(f"Error generating sample data: {e}")
        return None, None, None, None, None

def create_pie_chart(categories):
    """Create interactive pie chart for category breakdown."""
    try:
        plt.figure(figsize=(10, 8))
        
        # Prepare data
        labels = list(categories.keys())
        sizes = list(categories.values())
        colors = plt.cm.Set3(range(len(labels)))
        
        # Create pie chart with enhanced features
        wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, 
                                         autopct='%1.1f%%', startangle=90,
                                         explode=[0.05 if x == max(sizes) else 0 for x in sizes])
        
        # Enhance text appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
            autotext.set_fontsize(10)
        
        for text in texts:
            text.set_fontsize(11)
            text.set_weight('bold')
        
        plt.title('Expense Categories Breakdown', fontsize=16, fontweight='bold', pad=20)
        
        # Add total spending annotation
        total = sum(sizes)
        plt.figtext(0.02, 0.02, f'Total Monthly Spending: ${total:,}', 
                   fontsize=12, style='italic', bbox=dict(boxstyle="round,pad=0.3", 
                   facecolor='lightgray', alpha=0.7))
        
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig('expense_categories_pie.png', dpi=300, bbox_inches='tight')
        print("✓ Pie chart saved as 'expense_categories_pie.png'")
        plt.show()
        
    except Exception as e:
        print(f"Error creating pie chart: {e}")

def create_line_chart(dates, daily_spending):
    """Create interactive line chart for spending trends."""
    try:
        plt.figure(figsize=(12, 6))
        
        # Create line plot with enhanced styling
        plt.plot(range(len(dates)), daily_spending, marker='o', linewidth=2.5, 
                markersize=6, color='#2E86AB', markerfacecolor='#A23B72', 
                markeredgecolor='white', markeredgewidth=1.5)
        
        # Add trend line
        z = np.polyfit(range(len(dates)), daily_spending, 1)
        p = np.poly1d(z)
        plt.plot(range(len(dates)), p(range(len(dates))), "--", 
                color='red', alpha=0.8, linewidth=2, label=f'Trend Line')
        
        # Customize the plot
        plt.title('Daily Spending Trends (Last 30 Days)', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Days', fontsize=12, fontweight='bold')
        plt.ylabel('Amount Spent ($)', fontsize=12, fontweight='bold')
        
        # Format x-axis
        step = max(1, len(dates) // 10)
        plt.xticks(range(0, len(dates), step), 
                  [dates[i][-5:] for i in range(0, len(dates), step)], 
                  rotation=45)
        
        # Add grid and legend
        plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        plt.legend(loc='upper right')
        
        # Add statistics annotation
        avg_spending = sum(daily_spending) / len(daily_spending)
        max_spending = max(daily_spending)
        min_spending = min(daily_spending)
        
        stats_text = f'Avg: ${avg_spending:.1f}\nMax: ${max_spending}\nMin: ${min_spending}'
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
        
        plt.tight_layout()
        plt.savefig('daily_spending_trend.png', dpi=300, bbox_inches='tight')
        print("✓ Line chart saved as 'daily_spending_trend.png'")
        plt.show()
        
    except Exception as e:
        print(f"Error creating line chart: {e}")

def create_bar_chart(months, monthly_spending):
    """Create interactive bar chart for monthly comparisons."""
    try:
        plt.figure(figsize=(12, 7))
        
        # Create gradient colors
        colors = plt.cm.viridis([x/max(monthly_spending) for x in monthly_spending])
        
        # Create bar chart
        bars = plt.bar(months, monthly_spending, color=colors, 
                      edgecolor='black', linewidth=1, alpha=0.8)
        
        # Add value labels on top of bars
        for i, (bar, value) in enumerate(zip(bars, monthly_spending)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                    f'${value:,}', ha='center', va='bottom', 
                    fontweight='bold', fontsize=9)
            
            # Highlight highest and lowest spending months
            if value == max(monthly_spending):
                bar.set_edgecolor('red')
                bar.set_linewidth(3)
            elif value == min(monthly_spending):
                bar.set_edgecolor('green')
                bar.set_linewidth(3)
        
        plt.title('Monthly Spending Comparison', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Month', fontsize=12, fontweight='bold')
        plt.ylabel('Amount Spent ($)', fontsize=12, fontweight='bold')
        
        # Format y-axis
        plt.ticklabel_format(style='plain', axis='y')
        
        # Add horizontal line for average
        avg_monthly