```python
"""
Financial Data Visualization Module

This module provides functionality to generate various types of financial charts
including pie charts for spending distribution, bar charts for monthly trends,
and line graphs for expense tracking over time using matplotlib.

Features:
- Pie charts for categorical spending analysis
- Bar charts for monthly/periodic comparisons
- Line graphs for time series expense tracking
- Error handling for data validation and chart generation
- Sample data generation for demonstration purposes

Usage:
    python script.py

Dependencies:
    - matplotlib (for chart generation)
    - datetime (standard library)
    - random (standard library)
"""

import matplotlib.pyplot as plt
import datetime
import random
from typing import Dict, List, Tuple, Optional

class FinancialChartGenerator:
    """
    A class to generate various financial visualization charts.
    """
    
    def __init__(self):
        """Initialize the chart generator with default settings."""
        plt.style.use('default')
        
    def generate_sample_data(self) -> Tuple[Dict[str, float], Dict[str, List[float]], List[datetime.date], List[float]]:
        """
        Generate sample financial data for demonstration.
        
        Returns:
            Tuple containing:
            - spending_categories: Dict of category names to amounts
            - monthly_data: Dict of categories to monthly values
            - dates: List of dates for time series
            - expenses: List of expense amounts over time
        """
        try:
            # Sample spending categories
            spending_categories = {
                'Housing': 2500.00,
                'Food': 800.00,
                'Transportation': 600.00,
                'Entertainment': 400.00,
                'Healthcare': 300.00,
                'Shopping': 500.00,
                'Utilities': 250.00,
                'Other': 150.00
            }
            
            # Sample monthly data for 12 months
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            monthly_data = {}
            for category in ['Housing', 'Food', 'Transportation', 'Entertainment']:
                base_amount = spending_categories[category]
                monthly_data[category] = [
                    base_amount + random.uniform(-100, 100) for _ in months
                ]
            
            # Sample time series data for expense tracking
            start_date = datetime.date(2023, 1, 1)
            dates = []
            expenses = []
            
            for i in range(365):
                current_date = start_date + datetime.timedelta(days=i)
                dates.append(current_date)
                # Generate realistic daily expenses with some variation
                base_expense = 50 + random.uniform(-20, 30)
                # Add weekly and monthly patterns
                weekly_factor = 1.2 if current_date.weekday() >= 5 else 1.0
                monthly_factor = 1.1 if current_date.day <= 5 else 1.0
                expense = base_expense * weekly_factor * monthly_factor
                expenses.append(max(0, expense))
            
            return spending_categories, monthly_data, dates, expenses
            
        except Exception as e:
            print(f"Error generating sample data: {str(e)}")
            raise
    
    def create_pie_chart(self, data: Dict[str, float], title: str = "Spending Distribution") -> None:
        """
        Create a pie chart for spending distribution.
        
        Args:
            data: Dictionary with category names as keys and amounts as values
            title: Chart title
        """
        try:
            if not data:
                raise ValueError("Data dictionary cannot be empty")
            
            # Prepare data
            categories = list(data.keys())
            amounts = list(data.values())
            
            # Validate data
            if any(amount < 0 for amount in amounts):
                raise ValueError("All amounts must be non-negative")
            
            # Create pie chart
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(range(len(categories)))
            
            wedges, texts, autotexts = plt.pie(
                amounts, 
                labels=categories, 
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            
            # Enhance appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
            
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            plt.axis('equal')
            
            # Add total amount
            total = sum(amounts)
            plt.figtext(0.5, 0.02, f'Total: ${total:,.2f}', 
                       ha='center', fontsize=12, style='italic')
            
            plt.tight_layout()
            plt.show()
            print(f"✓ Pie chart '{title}' generated successfully")
            
        except Exception as e:
            print(f"Error creating pie chart: {str(e)}")
            raise
    
    def create_bar_chart(self, monthly_data: Dict[str, List[float]], title: str = "Monthly Spending Trends") -> None:
        """
        Create a bar chart for monthly trends comparison.
        
        Args:
            monthly_data: Dictionary with categories as keys and monthly amounts as values
            title: Chart title
        """
        try:
            if not monthly_data:
                raise ValueError("Monthly data dictionary cannot be empty")
            
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            # Validate data structure
            for category, values in monthly_data.items():
                if len(values) != 12:
                    raise ValueError(f"Category '{category}' must have exactly 12 monthly values")
                if any(val < 0 for val in values):
                    raise ValueError(f"All values for '{category}' must be non-negative")
            
            # Create bar chart
            plt.figure(figsize=(14, 8))
            
            # Set up bar positions
            categories = list(monthly_data.keys())
            x_pos = range(len(months))
            bar_width = 0.8 / len(categories)
            
            # Plot bars for each category
            for i, category in enumerate(categories):
                x_positions = [x + (i - len(categories)/2 + 0.5) * bar_width for x in x_pos]
                plt.bar(x_positions, monthly_data[category], 
                       bar_width, label=category, alpha=0.8)
            
            # Customize chart
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            plt.xticks(x_pos, months)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, alpha=0.3, axis='y')
            
            # Format y-axis to show currency
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            plt.tight_layout()
            plt.show()
            print(f"✓ Bar chart '{title}' generated successfully")
            
        except Exception as e:
            print(f"Error creating bar chart: {str(e)}")
            raise
    
    def create_line_graph(self, dates: List[datetime.date], expenses: List[float], 
                         title: str = "Expense Tracking Over Time") -> None:
        """
        Create a line graph for expense tracking over time.
        
        Args:
            dates: List of dates
            expenses: List of corresponding expense amounts
            title: Chart title
        """
        try:
            if not dates or not expenses:
                raise ValueError("Dates and expenses lists cannot be empty")
            
            if len(dates) != len(expenses):