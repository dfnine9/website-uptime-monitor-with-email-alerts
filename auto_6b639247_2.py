```python
"""
Expense Visualization Component

This module provides a comprehensive expense tracking and visualization system using matplotlib.
It generates various charts and graphs showing expense breakdowns, spending trends, and category 
comparisons with export functionality for reports.

Features:
- Pie charts for expense category breakdowns
- Line charts for spending trends over time
- Bar charts for category comparisons
- Monthly/weekly spending analysis
- Export functionality to PNG, PDF, and CSV formats
- Sample data generation for demonstration

Dependencies: matplotlib, pandas (standard data science stack)
Usage: python script.py
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import random
import json
import csv
import os
from typing import Dict, List, Tuple, Optional
import sys

class ExpenseVisualizer:
    """
    A comprehensive expense visualization system that creates various charts
    and graphs for expense analysis with export capabilities.
    """
    
    def __init__(self):
        """Initialize the ExpenseVisualizer with sample data."""
        self.expenses = self._generate_sample_data()
        self.categories = self._get_categories()
        self.output_dir = "expense_reports"
        self._ensure_output_directory()
    
    def _ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
        except Exception as e:
            print(f"Warning: Could not create output directory: {e}")
    
    def _generate_sample_data(self) -> List[Dict]:
        """Generate sample expense data for demonstration."""
        try:
            categories = [
                "Food & Dining", "Transportation", "Shopping", "Entertainment",
                "Bills & Utilities", "Healthcare", "Travel", "Education",
                "Business", "Personal Care"
            ]
            
            expenses = []
            start_date = datetime.now() - timedelta(days=90)
            
            for i in range(150):  # Generate 150 sample transactions
                date = start_date + timedelta(days=random.randint(0, 90))
                category = random.choice(categories)
                
                # Different spending patterns by category
                amount_ranges = {
                    "Food & Dining": (5, 100),
                    "Transportation": (10, 200),
                    "Shopping": (20, 500),
                    "Entertainment": (15, 150),
                    "Bills & Utilities": (50, 300),
                    "Healthcare": (30, 500),
                    "Travel": (100, 1000),
                    "Education": (50, 800),
                    "Business": (25, 400),
                    "Personal Care": (10, 150)
                }
                
                min_amt, max_amt = amount_ranges[category]
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                expenses.append({
                    "date": date,
                    "category": category,
                    "amount": amount,
                    "description": f"{category} expense #{i+1}"
                })
            
            return sorted(expenses, key=lambda x: x["date"])
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []
    
    def _get_categories(self) -> List[str]:
        """Extract unique categories from expenses."""
        try:
            return list(set(expense["category"] for expense in self.expenses))
        except Exception as e:
            print(f"Error extracting categories: {e}")
            return []
    
    def create_category_breakdown_pie(self, save_path: Optional[str] = None) -> None:
        """Create a pie chart showing expense breakdown by category."""
        try:
            # Calculate total spending by category
            category_totals = {}
            for expense in self.expenses:
                category = expense["category"]
                amount = expense["amount"]
                category_totals[category] = category_totals.get(category, 0) + amount
            
            # Prepare data for pie chart
            categories = list(category_totals.keys())
            amounts = list(category_totals.values())
            
            # Create pie chart
            plt.figure(figsize=(12, 8))
            colors = plt.cm.Set3(range(len(categories)))
            wedges, texts, autotexts = plt.pie(
                amounts, 
                labels=categories,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors
            )
            
            plt.title('Expense Breakdown by Category', fontsize=16, fontweight='bold')
            
            # Add total amount to legend
            total_amount = sum(amounts)
            plt.figtext(0.02, 0.02, f'Total Expenses: ${total_amount:,.2f}', 
                       fontsize=12, fontweight='bold')
            
            plt.axis('equal')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Category breakdown pie chart saved to: {save_path}")
            
            plt.show()
            
        except Exception as e:
            print(f"Error creating category breakdown pie chart: {e}")
    
    def create_spending_trend_line(self, save_path: Optional[str] = None) -> None:
        """Create a line chart showing spending trends over time."""
        try:
            # Group expenses by date
            daily_spending = {}
            for expense in self.expenses:
                date_str = expense["date"].strftime("%Y-%m-%d")
                daily_spending[date_str] = daily_spending.get(date_str, 0) + expense["amount"]
            
            # Sort dates and prepare data
            dates = sorted(daily_spending.keys())
            amounts = [daily_spending[date] for date in dates]
            date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
            
            # Create line chart
            plt.figure(figsize=(14, 8))
            plt.plot(date_objects, amounts, marker='o', linewidth=2, markersize=4)
            
            # Calculate and plot trend line
            if len(date_objects) > 1:
                x_numeric = [(date - date_objects[0]).days for date in date_objects]
                z = np.polyfit(x_numeric, amounts, 1) if 'np' in globals() else None
                if z is not None:
                    trend_line = [z[0] * x + z[1] for x in x_numeric]
                    plt.plot(date_objects, trend_line, '--r', alpha=0.8, label='Trend')
            
            plt.title('Daily Spending Trends', fontsize=16, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.xticks(rotation=45)
            
            # Add statistics
            avg_spending = sum(amounts) / len(amounts)
            max_spending = max(amounts)
            min_spending = min(amounts)
            
            stats_text = f'Avg: ${avg_spending:.2f}\nMax: ${max_spending:.2f}\nMin: ${min_spending:.2f}'
            plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Spending trend line chart saved to: {save_path}")
            
            plt.