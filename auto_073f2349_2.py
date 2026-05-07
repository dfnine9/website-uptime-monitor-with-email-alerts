```python
#!/usr/bin/env python3
"""
Financial Data Visualization Tool

This module creates interactive financial visualizations including:
- Spending by category (pie chart)
- Monthly spending trends (line chart)
- Budget vs actual comparisons (bar chart)
- Savings opportunities analysis (horizontal bar chart)

Dependencies: matplotlib, pandas (uses sample data if unavailable)
Usage: python script.py
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
import random
from collections import defaultdict

def generate_sample_data():
    """Generate sample financial data for demonstration"""
    categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping']
    months = []
    current_date = datetime(2024, 1, 1)
    
    for i in range(12):
        month_date = current_date + timedelta(days=30*i)
        months.append(month_date.strftime('%Y-%m'))
    
    # Generate spending data
    spending_data = []
    budgets = {
        'Housing': 1200, 'Food': 400, 'Transportation': 300, 
        'Entertainment': 200, 'Utilities': 150, 'Healthcare': 100, 'Shopping': 250
    }
    
    for month in months:
        for category in categories:
            base_amount = budgets[category]
            actual_amount = base_amount * (0.8 + random.random() * 0.4)  # 80-120% of budget
            spending_data.append({
                'month': month,
                'category': category,
                'budgeted': base_amount,
                'actual': round(actual_amount, 2)
            })
    
    return spending_data, budgets

def create_spending_by_category_chart(data):
    """Create pie chart showing spending by category"""
    try:
        category_totals = defaultdict(float)
        for item in data:
            category_totals[item['category']] += item['actual']
        
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        
        plt.figure(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(categories)))
        wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                          colors=colors, startangle=90)
        
        plt.title('Total Spending by Category', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        # Add legend with dollar amounts
        legend_labels = [f'{cat}: ${amt:,.2f}' for cat, amt in zip(categories, amounts)]
        plt.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        print("✓ Spending by Category chart created")
        return plt.gcf()
        
    except Exception as e:
        print(f"Error creating category chart: {e}")
        return None

def create_monthly_trends_chart(data):
    """Create line chart showing monthly spending trends"""
    try:
        monthly_totals = defaultdict(float)
        for item in data:
            monthly_totals[item['month']] += item['actual']
        
        months = sorted(monthly_totals.keys())
        amounts = [monthly_totals[month] for month in months]
        
        plt.figure(figsize=(12, 6))
        plt.plot(months, amounts, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        plt.fill_between(months, amounts, alpha=0.3, color='#2E86AB')
        
        plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Total Spending ($)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        print("✓ Monthly Trends chart created")
        return plt.gcf()
        
    except Exception as e:
        print(f"Error creating trends chart: {e}")
        return None

def create_budget_vs_actual_chart(data, budgets):
    """Create bar chart comparing budget vs actual spending"""
    try:
        category_actual = defaultdict(float)
        for item in data:
            category_actual[item['category']] += item['actual']
        
        categories = list(budgets.keys())
        budget_amounts = [budgets[cat] * 12 for cat in categories]  # Annual budget
        actual_amounts = [category_actual[cat] for cat in categories]
        
        x = range(len(categories))
        width = 0.35
        
        plt.figure(figsize=(14, 8))
        bars1 = plt.bar([i - width/2 for i in x], budget_amounts, width, 
                       label='Budgeted', color='#A8DADC', alpha=0.8)
        bars2 = plt.bar([i + width/2 for i in x], actual_amounts, width, 
                       label='Actual', color='#F1FAEE', alpha=0.8)
        
        plt.title('Budget vs Actual Spending (Annual)', fontsize=16, fontweight='bold')
        plt.xlabel('Category', fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        plt.xticks(x, categories, rotation=45, ha='right')
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis as currency
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        print("✓ Budget vs Actual chart created")
        return plt.gcf()
        
    except Exception as e:
        print(f"Error creating budget comparison chart: {e}")
        return None

def create_savings_opportunities_chart(data, budgets):
    """Create horizontal bar chart showing savings opportunities"""
    try:
        category_actual = defaultdict(float)
        for item in data:
            category_actual[item['category']] += item['actual']
        
        opportunities = []
        for category in budgets.keys():
            annual_budget = budgets[category] * 12
            annual_actual = category_actual[category]
            difference = annual_actual - annual_budget
            opportunities.append({
                'category': category,
                'difference': difference,
                'percentage': (difference / annual_budget) * 100 if annual_budget > 0 else 0
            })
        
        # Sort by overspending (highest first)
        opportunities.sort(key=lambda x: x['difference'], reverse=True)
        
        categories = [item['category'] for item in opportunities]
        differences = [item['difference'] for item in opportunities]
        colors = ['#E63946' if diff > 0 else '#2A9D8F' for diff in differences]
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(categories, differences, color=colors, alpha=0.7)
        
        plt.title('Savings Opportunities (Over/Under Budget)', fontsize=16, fontweight='bold')
        plt.xlabel('Difference from Budget ($)', fontsize=12)
        plt