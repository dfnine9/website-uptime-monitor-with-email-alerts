```python
"""
Interactive Spending Breakdown Chart Generator

This module creates interactive spending breakdown charts using matplotlib to visualize
monthly category totals. It generates bar charts, pie charts, and trend lines with
export capabilities for financial data analysis.

Features:
- Bar charts showing spending by category
- Pie charts for category distribution
- Trend lines showing spending patterns over time
- Export capabilities to PNG and CSV formats
- Sample data generation for demonstration
- Interactive matplotlib features

Dependencies: matplotlib, pandas (simulated with standard library for data handling)
"""

import json
import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict
import os

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.widgets import Button
except ImportError:
    print("Error: matplotlib not found. Please install with: pip install matplotlib")
    exit(1)

class SpendingAnalyzer:
    """Analyzes and visualizes spending data with interactive charts."""
    
    def __init__(self):
        self.spending_data = []
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                          'Healthcare', 'Shopping', 'Housing', 'Education']
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                      '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
    
    def generate_sample_data(self, months=12):
        """Generate sample spending data for demonstration."""
        try:
            start_date = datetime.now() - timedelta(days=months*30)
            
            for i in range(months * 25):  # ~25 transactions per month
                date = start_date + timedelta(days=random.randint(0, months*30))
                category = random.choice(self.categories)
                amount = round(random.uniform(10, 500), 2)
                
                self.spending_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'category': category,
                    'amount': amount,
                    'description': f'{category} expense'
                })
            
            print(f"Generated {len(self.spending_data)} sample transactions")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            self.spending_data = []
    
    def process_monthly_data(self):
        """Process spending data into monthly category totals."""
        try:
            monthly_totals = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.spending_data:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_totals[month_key][category] += amount
            
            return dict(monthly_totals)
            
        except Exception as e:
            print(f"Error processing monthly data: {e}")
            return {}
    
    def create_bar_chart(self, monthly_data):
        """Create interactive bar chart showing monthly spending by category."""
        try:
            fig, ax = plt.subplots(figsize=(15, 8))
            
            months = sorted(monthly_data.keys())
            categories = self.categories
            
            # Prepare data for stacked bar chart
            bottom = [0] * len(months)
            
            for i, category in enumerate(categories):
                values = []
                for month in months:
                    values.append(monthly_data.get(month, {}).get(category, 0))
                
                ax.bar(months, values, bottom=bottom, label=category, 
                      color=self.colors[i % len(self.colors)])
                
                # Update bottom for stacking
                bottom = [b + v for b, v in zip(bottom, values)]
            
            ax.set_title('Monthly Spending Breakdown by Category', fontsize=16, fontweight='bold')
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Amount ($)', fontsize=12)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Add export button
            ax_button = plt.axes([0.02, 0.02, 0.1, 0.04])
            button = Button(ax_button, 'Export PNG')
            button.on_clicked(lambda x: self.export_chart(fig, 'bar_chart'))
            
            return fig
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            return None
    
    def create_pie_chart(self, monthly_data):
        """Create pie chart showing overall category distribution."""
        try:
            # Calculate total spending by category
            category_totals = defaultdict(float)
            
            for month_data in monthly_data.values():
                for category, amount in month_data.items():
                    category_totals[category] += amount
            
            if not category_totals:
                print("No data available for pie chart")
                return None
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            categories = list(category_totals.keys())
            amounts = list(category_totals.values())
            colors = self.colors[:len(categories)]
            
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, colors=colors,
                                            autopct='%1.1f%%', startangle=90)
            
            ax.set_title('Overall Spending Distribution by Category', 
                        fontsize=16, fontweight='bold')
            
            # Add export button
            ax_button = plt.axes([0.02, 0.02, 0.1, 0.04])
            button = Button(ax_button, 'Export PNG')
            button.on_clicked(lambda x: self.export_chart(fig, 'pie_chart'))
            
            return fig
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return None
    
    def create_trend_chart(self, monthly_data):
        """Create trend lines showing spending patterns over time."""
        try:
            fig, ax = plt.subplots(figsize=(15, 8))
            
            months = sorted(monthly_data.keys())
            month_dates = [datetime.strptime(m, '%Y-%m') for m in months]
            
            for i, category in enumerate(self.categories):
                values = []
                for month in months:
                    values.append(monthly_data.get(month, {}).get(category, 0))
                
                if any(v > 0 for v in values):  # Only plot if there's data
                    ax.plot(month_dates, values, marker='o', linewidth=2,
                           label=category, color=self.colors[i % len(self.colors)])
            
            ax.set_title('Spending Trends by Category Over Time', 
                        fontsize=16, fontweight='bold')
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Amount ($)', fontsize=12)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            plt.xticks(rotation=45)
            
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Add export button
            ax_button = plt.axes([0.02, 0.02, 0.1, 0.04])
            button = Button(ax_button, 'Export PNG')
            button.on_clicked(lambda x: self.export_chart(fig, 'trend_chart'))