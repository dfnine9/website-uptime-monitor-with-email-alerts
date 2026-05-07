```python
"""
Monthly Spending Report Generator

A self-contained Python script that generates interactive spending reports with visualizations.
Creates sample spending data and produces charts showing:
- Spending by category (pie chart)
- Monthly spending trends (line chart)
- Budget variance analysis (bar chart)

Uses matplotlib for visualizations and includes comprehensive error handling.
Run with: python script.py
"""

import json
import random
import datetime
from typing import Dict, List, Any
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch
except ImportError:
    print("Error: matplotlib is required but not installed")
    print("Install with: pip install matplotlib")
    sys.exit(1)


class SpendingReportGenerator:
    """Generates monthly spending reports with interactive visualizations."""
    
    def __init__(self):
        self.categories = [
            "Food & Dining", "Transportation", "Shopping", "Entertainment",
            "Bills & Utilities", "Healthcare", "Travel", "Education", "Other"
        ]
        self.months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate realistic sample spending data for demonstration."""
        try:
            spending_data = {}
            budgets = {
                "Food & Dining": 800,
                "Transportation": 400,
                "Shopping": 600,
                "Entertainment": 300,
                "Bills & Utilities": 1200,
                "Healthcare": 200,
                "Travel": 500,
                "Education": 150,
                "Other": 250
            }
            
            # Generate 12 months of data
            for i, month in enumerate(self.months):
                monthly_spending = {}
                for category in self.categories:
                    # Add some randomness but keep it realistic
                    base_amount = budgets[category]
                    variation = random.uniform(0.7, 1.3)
                    monthly_spending[category] = round(base_amount * variation, 2)
                
                spending_data[month] = {
                    "spending": monthly_spending,
                    "budget": budgets.copy()
                }
            
            return spending_data
            
        except Exception as e:
            print(f"Error generating sample data: {str(e)}")
            return {}
    
    def create_category_pie_chart(self, monthly_data: Dict[str, float], month: str) -> None:
        """Create a pie chart showing spending by category for a specific month."""
        try:
            categories = list(monthly_data.keys())
            amounts = list(monthly_data.values())
            
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(range(len(categories)))
            
            wedges, texts, autotexts = plt.pie(
                amounts, 
                labels=categories, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors
            )
            
            plt.title(f'Spending by Category - {month}', fontsize=16, fontweight='bold')
            
            # Make percentage labels more readable
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.axis('equal')
            plt.tight_layout()
            plt.show()
            
            print(f"✓ Category breakdown chart generated for {month}")
            
        except Exception as e:
            print(f"Error creating pie chart: {str(e)}")
    
    def create_trends_chart(self, spending_data: Dict[str, Any]) -> None:
        """Create a line chart showing spending trends over time."""
        try:
            months = list(spending_data.keys())
            
            # Calculate total spending per month
            monthly_totals = []
            monthly_budgets = []
            
            for month in months:
                total_spent = sum(spending_data[month]["spending"].values())
                total_budget = sum(spending_data[month]["budget"].values())
                monthly_totals.append(total_spent)
                monthly_budgets.append(total_budget)
            
            plt.figure(figsize=(14, 8))
            
            # Create x-axis positions
            x_positions = range(len(months))
            
            # Plot spending and budget lines
            plt.plot(x_positions, monthly_totals, marker='o', linewidth=3, 
                    label='Actual Spending', color='#e74c3c', markersize=8)
            plt.plot(x_positions, monthly_budgets, marker='s', linewidth=2, 
                    linestyle='--', label='Budget', color='#27ae60', markersize=6)
            
            # Fill area between lines
            plt.fill_between(x_positions, monthly_totals, monthly_budgets, 
                           alpha=0.3, color='gray')
            
            plt.title('Monthly Spending Trends vs Budget', fontsize=16, fontweight='bold')
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            
            # Set x-axis labels
            plt.xticks(x_positions, months, rotation=45)
            
            plt.legend(fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
            print("✓ Monthly trends chart generated")
            
        except Exception as e:
            print(f"Error creating trends chart: {str(e)}")
    
    def create_variance_chart(self, spending_data: Dict[str, Any]) -> None:
        """Create a bar chart showing budget variance analysis."""
        try:
            # Calculate average variance by category
            category_variances = {category: [] for category in self.categories}
            
            for month_data in spending_data.values():
                spending = month_data["spending"]
                budget = month_data["budget"]
                
                for category in self.categories:
                    variance = spending[category] - budget[category]
                    variance_percent = (variance / budget[category]) * 100
                    category_variances[category].append(variance_percent)
            
            # Calculate average variance for each category
            avg_variances = {}
            for category, variances in category_variances.items():
                avg_variances[category] = sum(variances) / len(variances)
            
            categories = list(avg_variances.keys())
            variances = list(avg_variances.values())
            
            # Create color mapping (red for over budget, green for under)
            colors = ['#e74c3c' if v > 0 else '#27ae60' for v in variances]
            
            plt.figure(figsize=(14, 8))
            bars = plt.bar(categories, variances, color=colors, alpha=0.7, edgecolor='black')
            
            # Add a horizontal line at 0
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            plt.title('Budget Variance Analysis (Average % Over/Under Budget)', 
                     fontsize=16, fontweight='bold')
            plt.xlabel('Category', fontsize=12)
            plt.ylabel('Variance (%)', fontsize=12)
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, variance in zip(bars, variances):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + (1 if height >= 0 else -3),
                        f'{variance:.1f}%', ha='center', va='bottom' if height >= 0 else 'top',
                        fontweight='bold')
            
            # Add legend
            legend_elements = [
                Patch(facecolor='#e74c3c', alpha=0.7, label='Over Budget'),