```python
"""
Personal Finance Visualization System

This module creates a comprehensive visualization system for analyzing personal finance data.
It generates multiple chart types including bar charts, pie charts, and trend lines to show:
- Monthly spending patterns and comparisons
- Category-wise expense breakdowns
- Income vs expense trends over time
- Budget variance analysis

The system uses matplotlib for static visualizations and includes sample data generation
for demonstration purposes. All charts are saved as PNG files and displayed.

Usage: python script.py
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import random
import json
from collections import defaultdict
import os

def generate_sample_data():
    """Generate realistic sample financial data for demonstration."""
    try:
        categories = ['Housing', 'Food', 'Transportation', 'Utilities', 'Entertainment', 
                     'Healthcare', 'Shopping', 'Education', 'Insurance', 'Savings']
        
        # Generate 12 months of data
        data = []
        base_date = datetime.now() - timedelta(days=365)
        
        for month in range(12):
            current_date = base_date + timedelta(days=30*month)
            monthly_data = {
                'date': current_date.strftime('%Y-%m'),
                'income': random.randint(4000, 6000),
                'expenses': {}
            }
            
            total_expenses = 0
            for category in categories:
                if category == 'Housing':
                    amount = random.randint(1200, 1800)
                elif category == 'Food':
                    amount = random.randint(400, 800)
                elif category == 'Transportation':
                    amount = random.randint(200, 500)
                elif category == 'Utilities':
                    amount = random.randint(100, 300)
                elif category == 'Savings':
                    amount = random.randint(300, 1000)
                else:
                    amount = random.randint(50, 400)
                
                monthly_data['expenses'][category] = amount
                total_expenses += amount
            
            monthly_data['total_expenses'] = total_expenses
            monthly_data['net_income'] = monthly_data['income'] - total_expenses
            data.append(monthly_data)
        
        return data
    except Exception as e:
        print(f"Error generating sample data: {e}")
        return []

def create_monthly_spending_bar_chart(data):
    """Create bar chart showing monthly spending patterns."""
    try:
        months = [item['date'] for item in data]
        total_expenses = [item['total_expenses'] for item in data]
        incomes = [item['income'] for item in data]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x_pos = range(len(months))
        width = 0.35
        
        bars1 = ax.bar([x - width/2 for x in x_pos], incomes, width, 
                      label='Income', color='green', alpha=0.7)
        bars2 = ax.bar([x + width/2 for x in x_pos], total_expenses, width,
                      label='Expenses', color='red', alpha=0.7)
        
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Monthly Income vs Expenses Comparison')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(months, rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:,.0f}', ha='center', va='bottom', fontsize=8)
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:,.0f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('monthly_spending_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Monthly spending bar chart created: monthly_spending_comparison.png")
        
    except Exception as e:
        print(f"Error creating monthly spending chart: {e}")

def create_category_pie_chart(data):
    """Create pie chart showing category-wise expense breakdown."""
    try:
        # Aggregate expenses by category across all months
        category_totals = defaultdict(int)
        
        for month_data in data:
            for category, amount in month_data['expenses'].items():
                category_totals[category] += amount
        
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        
        # Create color scheme
        colors = plt.cm.Set3(range(len(categories)))
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Main pie chart
        wedges, texts, autotexts = ax1.pie(amounts, labels=categories, autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        ax1.set_title('Annual Expense Breakdown by Category')
        
        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
            autotext.set_fontsize(8)
        
        # Create a detailed breakdown chart
        sorted_data = sorted(zip(categories, amounts), key=lambda x: x[1], reverse=True)
        top_categories = [item[0] for item in sorted_data[:6]]
        top_amounts = [item[1] for item in sorted_data[:6]]
        
        bars = ax2.barh(top_categories, top_amounts, color=colors[:6])
        ax2.set_xlabel('Total Amount ($)')
        ax2.set_title('Top 6 Expense Categories')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2,
                    f'${width:,.0f}', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('category_expense_breakdown.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Category breakdown pie chart created: category_expense_breakdown.png")
        
    except Exception as e:
        print(f"Error creating category pie chart: {e}")

def create_trend_analysis(data):
    """Create trend line charts showing financial patterns over time."""
    try:
        dates = [datetime.strptime(item['date'], '%Y-%m') for item in data]
        incomes = [item['income'] for item in data]
        expenses = [item['total_expenses'] for item in data]
        net_incomes = [item['net_income'] for item in data]
        savings_amounts = [item['expenses'].get('Savings', 0) for item in data]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Trend 1: Income vs Expenses over time
        ax1.plot(dates, incomes, marker='o', linewidth=2, label='Income', color='green')
        ax1.plot(dates, expenses, marker='s', linewidth=2, label='Expenses', color='red')
        ax1.set_title('Income vs Expenses Trend')
        ax1.set_ylabel('Amount ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax