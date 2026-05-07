```python
"""
Personal Finance Data Visualization Module

This module provides comprehensive data visualization functions for personal finance analysis.
It generates monthly spending charts, category breakdowns, and trend analysis using matplotlib
and pandas. The module includes sample data generation for demonstration purposes and can be
easily adapted to work with real financial data from CSV files or databases.

Features:
- Monthly spending trend charts
- Category-wise expense breakdown (pie charts and bar charts)
- Year-over-year comparison analysis
- Spending pattern trend analysis
- Interactive data filtering and aggregation

Dependencies: matplotlib, pandas, numpy (all standard data science libraries)
Usage: python script.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings('ignore')

def generate_sample_data(months=12):
    """Generate sample financial data for demonstration purposes."""
    try:
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                     'Healthcare', 'Shopping', 'Rent', 'Insurance', 'Education', 'Miscellaneous']
        
        data = []
        start_date = datetime.now() - timedelta(days=30*months)
        
        for i in range(months * 30):  # Roughly 30 transactions per month
            date = start_date + timedelta(days=i//30*30 + random.randint(0, 29))
            category = random.choice(categories)
            
            # Create realistic spending patterns
            base_amounts = {
                'Rent': random.uniform(800, 1500),
                'Food': random.uniform(10, 150),
                'Transportation': random.uniform(5, 80),
                'Entertainment': random.uniform(15, 200),
                'Utilities': random.uniform(50, 300),
                'Healthcare': random.uniform(20, 500),
                'Shopping': random.uniform(25, 400),
                'Insurance': random.uniform(100, 600),
                'Education': random.uniform(50, 800),
                'Miscellaneous': random.uniform(5, 100)
            }
            
            amount = base_amounts[category]
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': round(amount, 2),
                'description': f"{category} expense"
            })
        
        return pd.DataFrame(data)
    
    except Exception as e:
        print(f"Error generating sample data: {e}")
        return pd.DataFrame()

def create_monthly_spending_chart(df):
    """Create a line chart showing monthly spending trends."""
    try:
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        
        # Group by month and sum amounts
        monthly_spending = df.groupby('month')['amount'].sum().reset_index()
        monthly_spending['month_str'] = monthly_spending['month'].astype(str)
        
        plt.figure(figsize=(12, 6))
        plt.plot(monthly_spending['month_str'], monthly_spending['amount'], 
                marker='o', linewidth=2, markersize=8, color='#2E8B57')
        plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Month', fontsize=12, fontweight='bold')
        plt.ylabel('Total Spending ($)', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Add value labels on points
        for i, v in enumerate(monthly_spending['amount']):
            plt.annotate(f'${v:,.0f}', 
                        (i, v), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center',
                        fontweight='bold')
        
        plt.show()
        
        print("Monthly Spending Summary:")
        print("-" * 40)
        for _, row in monthly_spending.iterrows():
            print(f"{row['month']}: ${row['amount']:,.2f}")
        print(f"\nAverage Monthly Spending: ${monthly_spending['amount'].mean():,.2f}")
        print(f"Highest Month: {monthly_spending.loc[monthly_spending['amount'].idxmax(), 'month']} (${monthly_spending['amount'].max():,.2f})")
        print(f"Lowest Month: {monthly_spending.loc[monthly_spending['amount'].idxmin(), 'month']} (${monthly_spending['amount'].min():,.2f})")
        
    except Exception as e:
        print(f"Error creating monthly spending chart: {e}")

def create_category_breakdown(df):
    """Create pie chart and bar chart showing spending by category."""
    try:
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        # Create subplot with pie chart and bar chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Pie Chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_totals)))
        wedges, texts, autotexts = ax1.pie(category_totals.values, 
                                          labels=category_totals.index,
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          startangle=90)
        ax1.set_title('Spending by Category (Pie Chart)', fontsize=14, fontweight='bold', pad=20)
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Bar Chart
        bars = ax2.bar(category_totals.index, category_totals.values, color=colors)
        ax2.set_title('Spending by Category (Bar Chart)', fontsize=14, fontweight='bold', pad=20)
        ax2.set_xlabel('Category', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Total Amount ($)', fontsize=12, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, category_totals.values):
            height = bar.get_height()
            ax2.annotate(f'${value:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontweight='bold')
        
        plt.tight_layout()
        plt.show()
        
        print("\nCategory Breakdown:")
        print("-" * 40)
        for category, amount in category_totals.items():
            percentage = (amount / category_totals.sum()) * 100
            print(f"{category}: ${amount:,.2f} ({percentage:.1f}%)")
        
        print(f"\nTop 3 Spending Categories:")
        for i, (category, amount) in enumerate(category_totals.head(3).items(), 1):
            print(f"{i}. {category}: ${amount:,.2f}")
        
    except Exception as e:
        print(f"Error creating category breakdown: {e}")

def create_trend_analysis(df):
    """Create advanced trend analysis with moving averages and forecasting."""
    try:
        df['date'] = pd.to_datetime(df['date'])
        
        # Daily spending
        daily_spending = df.groupby('date')['amount'].sum().reset_index()
        daily_spending = daily_spending.set_index('date').resample('D').sum().fillna(0)
        
        # Calculate moving averages
        daily_spending['7_day_ma'] = daily_spending['amount'].rolling(window=7,