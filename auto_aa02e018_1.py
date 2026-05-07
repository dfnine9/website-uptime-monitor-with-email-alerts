```python
"""
Financial Data Visualization Module

This module provides comprehensive data visualization capabilities for financial spending analysis.
It generates matplotlib charts showing:
- Spending patterns by category (pie chart)
- Monthly spending trends (line chart)
- Top expenses analysis (bar chart)
- Export functionality to PNG/PDF formats

Features:
- Self-contained implementation with minimal dependencies
- Robust error handling for data processing and chart generation
- Sample data generation for demonstration purposes
- Multiple export formats (PNG, PDF)
- Customizable chart styling and layouts

Usage:
    python script.py

The script will generate sample financial data and create three types of visualizations,
saving them as both PNG and PDF files in the current directory.
"""

import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
import numpy as np
import random
from datetime import datetime, timedelta
from collections import defaultdict
import os
import sys

class FinancialDataVisualizer:
    """
    A comprehensive financial data visualization tool that creates charts
    for spending analysis and exports them in multiple formats.
    """
    
    def __init__(self):
        """Initialize the visualizer with default settings."""
        self.data = []
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                          'Healthcare', 'Shopping', 'Education', 'Travel', 'Insurance']
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', 
                      '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3']
        
    def generate_sample_data(self, num_transactions=200):
        """
        Generate sample financial transaction data for demonstration.
        
        Args:
            num_transactions (int): Number of sample transactions to generate
            
        Returns:
            list: List of transaction dictionaries
        """
        try:
            self.data = []
            start_date = datetime.now() - timedelta(days=365)
            
            for _ in range(num_transactions):
                transaction_date = start_date + timedelta(days=random.randint(0, 365))
                category = random.choice(self.categories)
                
                # Generate realistic amounts based on category
                amount_ranges = {
                    'Food': (10, 150),
                    'Transportation': (5, 200),
                    'Entertainment': (15, 300),
                    'Utilities': (50, 400),
                    'Healthcare': (20, 1000),
                    'Shopping': (25, 500),
                    'Education': (100, 2000),
                    'Travel': (200, 3000),
                    'Insurance': (100, 800)
                }
                
                min_amt, max_amt = amount_ranges.get(category, (10, 200))
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                transaction = {
                    'date': transaction_date,
                    'category': category,
                    'amount': amount,
                    'description': f"{category} expense {random.randint(1000, 9999)}"
                }
                
                self.data.append(transaction)
            
            print(f"✓ Generated {len(self.data)} sample transactions")
            return self.data
            
        except Exception as e:
            print(f"✗ Error generating sample data: {str(e)}")
            return []
    
    def create_category_spending_chart(self):
        """
        Create a pie chart showing spending distribution by category.
        
        Returns:
            matplotlib.figure.Figure: The generated figure object
        """
        try:
            # Aggregate spending by category
            category_totals = defaultdict(float)
            for transaction in self.data:
                category_totals[transaction['category']] += transaction['amount']
            
            if not category_totals:
                raise ValueError("No data available for category chart")
            
            # Sort categories by spending amount
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            categories, amounts = zip(*sorted_categories)
            
            # Create pie chart
            fig, ax = plt.subplots(figsize=(12, 8))
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%',
                                            colors=self.colors[:len(categories)], startangle=90)
            
            # Enhance styling
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            ax.set_title('Spending Distribution by Category', fontsize=16, fontweight='bold', pad=20)
            
            # Add total spending annotation
            total_spending = sum(amounts)
            ax.text(0, -1.3, f'Total Spending: ${total_spending:,.2f}', 
                   ha='center', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            print("✓ Created category spending pie chart")
            return fig
            
        except Exception as e:
            print(f"✗ Error creating category chart: {str(e)}")
            return None
    
    def create_monthly_trends_chart(self):
        """
        Create a line chart showing monthly spending trends.
        
        Returns:
            matplotlib.figure.Figure: The generated figure object
        """
        try:
            # Aggregate spending by month
            monthly_totals = defaultdict(float)
            for transaction in self.data:
                month_key = transaction['date'].strftime('%Y-%m')
                monthly_totals[month_key] += transaction['amount']
            
            if not monthly_totals:
                raise ValueError("No data available for trends chart")
            
            # Sort by date
            sorted_months = sorted(monthly_totals.items())
            months, amounts = zip(*sorted_months)
            
            # Convert month strings to datetime for better x-axis formatting
            month_dates = [datetime.strptime(month, '%Y-%m') for month in months]
            
            # Create line chart
            fig, ax = plt.subplots(figsize=(14, 8))
            ax.plot(month_dates, amounts, marker='o', linewidth=2, markersize=6, 
                   color='#4ECDC4', markerfacecolor='#FF6B6B', markeredgecolor='white', markeredgewidth=2)
            
            # Fill area under the curve
            ax.fill_between(month_dates, amounts, alpha=0.3, color='#4ECDC4')
            
            # Enhance styling
            ax.set_title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Month', fontsize=12, fontweight='bold')
            ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            # Format y-axis to show currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add trend line
            x_numeric = np.arange(len(month_dates))
            z = np.polyfit(x_numeric, amounts, 1)
            p = np.poly1d(z)
            ax.plot(month_dates, p(x_numeric), "--", alpha=0.7, color='red', linewidth=1)
            
            plt.tight_layout()
            print("✓ Created monthly trends line chart")
            return fig
            
        except Exception as e:
            print(f"✗ Error creating trends chart: {str(e)}")
            return None
    
    def create_top_expenses_chart(self, top_n=10):
        """
        Create a horizontal bar chart showing top individual expenses.
        
        Args:
            top_n (int): Number of top expenses to display
            
        Returns:
            matplotlib.figure.Figure: The generated figure object
        """
        try: