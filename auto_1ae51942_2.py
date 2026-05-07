```python
"""
Monthly Spending Report Visualization Generator

This module generates comprehensive monthly spending reports with multiple chart types:
- Bar charts showing spending by category
- Pie charts displaying spending distribution
- Trend graphs tracking spending over time
- Exports reports as PDF files

Uses matplotlib for visualization and reportlab for PDF generation.
Includes sample data generation for demonstration purposes.

Usage: python script.py
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import random
from typing import Dict, List, Tuple

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_pdf import PdfPages
except ImportError:
    print("Error: matplotlib is required. Install with: pip install matplotlib")
    sys.exit(1)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    print("Warning: reportlab not available. Using matplotlib PDF backend only.")


class SpendingDataGenerator:
    """Generates sample spending data for demonstration."""
    
    CATEGORIES = [
        "Food & Dining", "Transportation", "Entertainment", "Shopping", 
        "Utilities", "Healthcare", "Travel", "Education", "Groceries", "Other"
    ]
    
    @staticmethod
    def generate_monthly_data(months: int = 12) -> Dict:
        """Generate sample spending data for specified number of months."""
        data = {
            "transactions": [],
            "monthly_totals": {},
            "category_totals": {}
        }
        
        base_date = datetime.now() - timedelta(days=30 * months)
        
        for month in range(months):
            month_date = base_date + timedelta(days=30 * month)
            month_key = month_date.strftime("%Y-%m")
            monthly_spending = 0
            
            # Generate 15-30 transactions per month
            num_transactions = random.randint(15, 30)
            
            for _ in range(num_transactions):
                category = random.choice(SpendingDataGenerator.CATEGORIES)
                
                # Generate realistic amounts based on category
                if category == "Food & Dining":
                    amount = random.uniform(15, 150)
                elif category == "Transportation":
                    amount = random.uniform(20, 200)
                elif category == "Utilities":
                    amount = random.uniform(50, 300)
                elif category == "Groceries":
                    amount = random.uniform(30, 200)
                elif category == "Travel":
                    amount = random.uniform(100, 1000)
                else:
                    amount = random.uniform(10, 500)
                
                transaction_date = month_date + timedelta(days=random.randint(0, 29))
                
                transaction = {
                    "date": transaction_date.strftime("%Y-%m-%d"),
                    "category": category,
                    "amount": round(amount, 2),
                    "description": f"{category} expense"
                }
                
                data["transactions"].append(transaction)
                monthly_spending += amount
                
                # Update category totals
                if category not in data["category_totals"]:
                    data["category_totals"][category] = 0
                data["category_totals"][category] += amount
            
            data["monthly_totals"][month_key] = round(monthly_spending, 2)
        
        return data


class SpendingReportGenerator:
    """Generates visual spending reports with charts and PDF export."""
    
    def __init__(self, data: Dict):
        """Initialize with spending data."""
        self.data = data
        self.charts_created = []
        
    def create_category_bar_chart(self) -> str:
        """Create bar chart showing spending by category."""
        try:
            plt.figure(figsize=(12, 8))
            categories = list(self.data["category_totals"].keys())
            amounts = list(self.data["category_totals"].values())
            
            # Sort by amount for better visualization
            sorted_data = sorted(zip(categories, amounts), key=lambda x: x[1], reverse=True)
            categories, amounts = zip(*sorted_data)
            
            bars = plt.bar(categories, amounts, color='steelblue', alpha=0.8)
            plt.title('Spending by Category', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Category', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:.0f}', ha='center', va='bottom')
            
            plt.tight_layout()
            chart_path = 'category_bar_chart.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.charts_created.append(chart_path)
            print(f"✓ Created category bar chart: {chart_path}")
            return chart_path
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            return None
    
    def create_category_pie_chart(self) -> str:
        """Create pie chart showing spending distribution."""
        try:
            plt.figure(figsize=(10, 10))
            categories = list(self.data["category_totals"].keys())
            amounts = list(self.data["category_totals"].values())
            
            # Create colors
            colors = plt.cm.Set3(range(len(categories)))
            
            # Create pie chart
            wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%',
                                              colors=colors, startangle=90)
            
            plt.title('Spending Distribution by Category', fontsize=16, fontweight='bold', pad=20)
            
            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.axis('equal')
            chart_path = 'category_pie_chart.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.charts_created.append(chart_path)
            print(f"✓ Created category pie chart: {chart_path}")
            return chart_path
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return None
    
    def create_monthly_trend_chart(self) -> str:
        """Create line chart showing monthly spending trends."""
        try:
            plt.figure(figsize=(12, 8))
            
            months = sorted(self.data["monthly_totals"].keys())
            amounts = [self.data["monthly_totals"][month] for month in months]
            
            # Convert month strings to datetime for better x-axis formatting
            month_dates = [datetime.strptime(month, "%Y-%m") for month in months]
            
            plt.plot(month_dates, amounts, marker='o', linewidth=2, markersize=8, 
                    color='darkgreen', markerfacecolor='lightgreen')
            
            plt.title('Monthly Spending Trend', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Total Spending ($)', fontsize=12)
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.xticks(rotation=45)
            
            # Add grid
            plt.grid(True, alpha=0.3)
            
            # Add value labels
            for date, amount in