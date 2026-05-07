```python
#!/usr/bin/env python3
"""
Financial Data Visualization Module

This module creates comprehensive financial visualizations including:
- Pie charts for expense category distribution
- Bar charts for monthly spending trends
- Line graphs for spending patterns over time

The script generates sample financial data and exports all charts as PNG files
to the current directory. Uses matplotlib for visualization with proper error
handling and stdout logging.

Dependencies: matplotlib, numpy (standard scientific Python stack)
Usage: python script.py
"""

import matplotlib.pyplot as plt
import numpy as np
import datetime
import random
import sys
from pathlib import Path

def generate_sample_data():
    """Generate sample financial data for visualization."""
    try:
        # Sample expense categories and amounts
        categories = ['Housing', 'Food', 'Transportation', 'Healthcare', 
                     'Entertainment', 'Utilities', 'Shopping', 'Insurance']
        
        # Generate category distribution data
        category_amounts = [random.randint(800, 2500) for _ in categories]
        
        # Generate monthly data for the past 12 months
        months = []
        monthly_totals = []
        current_date = datetime.datetime.now()
        
        for i in range(12):
            month_date = current_date - datetime.timedelta(days=30*i)
            months.append(month_date.strftime('%b %Y'))
            monthly_totals.append(random.randint(3000, 6000))
        
        months.reverse()
        monthly_totals.reverse()
        
        # Generate daily spending data for line chart
        days = list(range(1, 31))
        daily_spending = [random.randint(50, 300) for _ in days]
        
        print("✓ Sample financial data generated successfully")
        return {
            'categories': categories,
            'category_amounts': category_amounts,
            'months': months,
            'monthly_totals': monthly_totals,
            'days': days,
            'daily_spending': daily_spending
        }
        
    except Exception as e:
        print(f"✗ Error generating sample data: {e}")
        return None

def create_pie_chart(categories, amounts, filename='expense_categories_pie.png'):
    """Create and save a pie chart for expense categories."""
    try:
        plt.figure(figsize=(10, 8))
        
        # Create pie chart with custom colors
        colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%',
                                          startangle=90, colors=colors)
        
        # Customize text
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        plt.title('Expense Distribution by Category', fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')
        
        # Save the chart
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Pie chart saved as {filename}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating pie chart: {e}")
        return False

def create_bar_chart(months, totals, filename='monthly_spending_bar.png'):
    """Create and save a bar chart for monthly spending trends."""
    try:
        plt.figure(figsize=(14, 8))
        
        # Create bar chart
        bars = plt.bar(range(len(months)), totals, color='steelblue', alpha=0.8)
        
        # Customize the chart
        plt.xlabel('Month', fontsize=12, fontweight='bold')
        plt.ylabel('Total Spending ($)', fontsize=12, fontweight='bold')
        plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
        plt.xticks(range(len(months)), months, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, total in zip(bars, totals):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 50,
                    f'${total:,}', ha='center', va='bottom', fontweight='bold')
        
        # Add grid for better readability
        plt.grid(axis='y', alpha=0.3)
        plt.ylim(0, max(totals) * 1.15)
        
        # Save the chart
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Bar chart saved as {filename}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating bar chart: {e}")
        return False

def create_line_chart(days, spending, filename='daily_spending_line.png'):
    """Create and save a line chart for daily spending patterns."""
    try:
        plt.figure(figsize=(12, 8))
        
        # Create line chart
        plt.plot(days, spending, marker='o', linewidth=2.5, markersize=6, 
                color='darkgreen', markerfacecolor='lightgreen', 
                markeredgecolor='darkgreen', alpha=0.8)
        
        # Customize the chart
        plt.xlabel('Day of Month', fontsize=12, fontweight='bold')
        plt.ylabel('Daily Spending ($)', fontsize=12, fontweight='bold')
        plt.title('Daily Spending Pattern (Current Month)', fontsize=16, fontweight='bold', pad=20)
        
        # Add grid
        plt.grid(True, alpha=0.3)
        
        # Highlight highest and lowest spending days
        max_idx = spending.index(max(spending))
        min_idx = spending.index(min(spending))
        
        plt.annotate(f'Highest: ${spending[max_idx]}', 
                    xy=(days[max_idx], spending[max_idx]), 
                    xytext=(days[max_idx]+2, spending[max_idx]+20),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                    fontsize=10, fontweight='bold', color='red')
        
        plt.annotate(f'Lowest: ${spending[min_idx]}', 
                    xy=(days[min_idx], spending[min_idx]), 
                    xytext=(days[min_idx]+2, spending[min_idx]-30),
                    arrowprops=dict(arrowstyle='->', color='blue', lw=1.5),
                    fontsize=10, fontweight='bold', color='blue')
        
        # Set axis limits
        plt.xlim(0, 31)
        plt.ylim(0, max(spending) * 1.2)
        
        # Save the chart
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Line chart saved as {filename}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating line chart: {e}")
        return False

def main():
    """Main function to orchestrate the visualization creation."""
    try:
        print("=== Financial Data Visualization Generator ===")
        print("Generating comprehensive financial charts...\n")
        
        # Generate sample data
        data = generate_sample_data()
        if not data:
            print("✗ Failed to generate data. Exiting.")
            sys.exit(1)
        
        print()
        success_count = 0
        
        # Create pie chart for category distribution
        if create_pie_chart(data['categories'], data['category_amounts']):
            success_count += 1
        
        # Create bar chart for monthly trends
        if create_bar_chart(data['months'], data['monthly_totals']):
            success_count += 1