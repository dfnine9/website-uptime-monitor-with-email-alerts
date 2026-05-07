```python
"""
Financial Spending Report Visualization Generator

This module generates comprehensive monthly spending reports with visualizations
including bar charts, pie charts, and trend analysis. It reads categorized
spending data from CSV files and creates professional financial reports.

Features:
- Monthly spending breakdown by category
- Trend analysis over time
- Category distribution visualization
- Automated report generation with PNG exports

Usage: python script.py

Requirements: matplotlib, seaborn, pandas (automatically handled)
"""

import csv
import os
import sys
from datetime import datetime
from collections import defaultdict
import subprocess
import importlib.util

def install_and_import(package):
    """Install and import a package if not available"""
    try:
        return importlib.import_module(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return importlib.import_module(package)

# Import required packages
plt = install_and_import('matplotlib.pyplot')
sns = install_and_import('seaborn')
pd = install_and_import('pandas')

def create_sample_data():
    """Create sample spending data if no CSV file exists"""
    sample_data = [
        ['Date', 'Category', 'Amount', 'Description'],
        ['2024-01-15', 'Food', '45.50', 'Grocery shopping'],
        ['2024-01-16', 'Transportation', '12.00', 'Bus fare'],
        ['2024-01-17', 'Entertainment', '25.00', 'Movie tickets'],
        ['2024-01-20', 'Food', '38.75', 'Restaurant dinner'],
        ['2024-02-01', 'Housing', '1200.00', 'Rent payment'],
        ['2024-02-03', 'Utilities', '85.50', 'Electricity bill'],
        ['2024-02-05', 'Food', '52.30', 'Groceries'],
        ['2024-02-10', 'Transportation', '15.00', 'Gas'],
        ['2024-02-14', 'Entertainment', '40.00', 'Concert ticket'],
        ['2024-03-01', 'Housing', '1200.00', 'Rent payment'],
        ['2024-03-05', 'Food', '67.80', 'Grocery shopping'],
        ['2024-03-08', 'Healthcare', '150.00', 'Doctor visit'],
        ['2024-03-12', 'Transportation', '45.00', 'Car maintenance'],
        ['2024-03-15', 'Entertainment', '30.00', 'Streaming services']
    ]
    
    with open('spending_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(sample_data)
    
    print("Created sample spending_data.csv file")

def load_spending_data(filename='spending_data.csv'):
    """Load spending data from CSV file"""
    try:
        if not os.path.exists(filename):
            print(f"CSV file '{filename}' not found. Creating sample data...")
            create_sample_data()
        
        df = pd.read_csv(filename)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        
        # Remove rows with invalid amounts
        df = df.dropna(subset=['Amount'])
        
        print(f"Successfully loaded {len(df)} spending records")
        return df
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def generate_monthly_bar_chart(df):
    """Generate monthly spending bar chart"""
    try:
        # Group by month and sum amounts
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_totals = df.groupby('Month')['Amount'].sum()
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(monthly_totals)), monthly_totals.values, 
                      color='skyblue', alpha=0.8)
        
        plt.title('Monthly Spending Overview', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Amount Spent ($)', fontsize=12)
        plt.xticks(range(len(monthly_totals)), 
                  [str(month) for month in monthly_totals.index], rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, monthly_totals.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                    f'${value:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('monthly_spending_bar_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Generated monthly_spending_bar_chart.png")
        return True
        
    except Exception as e:
        print(f"Error generating bar chart: {e}")
        return False

def generate_category_pie_chart(df):
    """Generate category spending pie chart"""
    try:
        category_totals = df.groupby('Category')['Amount'].sum()
        
        plt.figure(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(category_totals)))
        
        wedges, texts, autotexts = plt.pie(category_totals.values, 
                                          labels=category_totals.index,
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          startangle=90)
        
        plt.title('Spending by Category', fontsize=16, fontweight='bold')
        
        # Add legend with amounts
        legend_labels = [f'{cat}: ${amt:.2f}' for cat, amt in category_totals.items()]
        plt.legend(wedges, legend_labels, title="Categories", 
                  loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        plt.savefig('category_pie_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Generated category_pie_chart.png")
        return True
        
    except Exception as e:
        print(f"Error generating pie chart: {e}")
        return False

def generate_trend_analysis(df):
    """Generate spending trend analysis"""
    try:
        # Daily spending trend
        daily_spending = df.groupby(df['Date'].dt.date)['Amount'].sum()
        
        # Monthly category trends
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_category = df.groupby(['Month', 'Category'])['Amount'].sum().unstack(fill_value=0)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Daily trend
        ax1.plot(daily_spending.index, daily_spending.values, 
                marker='o', linestyle='-', alpha=0.7, color='darkblue')
        ax1.set_title('Daily Spending Trend', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Amount ($)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Monthly category trends
        for category in monthly_category.columns:
            ax2.plot(range(len(monthly_category)), monthly_category[category], 
                    marker='o', label=category, linewidth=2)
        
        ax2.set_title('Monthly Category Spending Trends', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Amount ($)')
        ax2.set_xticks