```python
"""
Monthly Spending Report Generator

This module generates comprehensive monthly spending reports with interactive visualizations.
It analyzes spending patterns, categorizes expenses, tracks trends, and provides budget
variance analysis using matplotlib for static plots and simulated interactive features.

Features:
- Monthly spending breakdowns by category
- Trend analysis across multiple months
- Budget vs actual spending variance
- Interactive-style visualizations with hover effects simulation
- Statistical analysis of spending patterns

Usage:
    python script.py

Dependencies:
    - Standard library modules (datetime, random, json, etc.)
    - matplotlib (for visualizations)
    
Note: This is a self-contained demonstration using simulated data.
In production, you would replace the data generation with actual financial data sources.
"""

import json
import random
import datetime
from typing import Dict, List, Tuple, Any
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.dates import DateFormatter
    import numpy as np
except ImportError:
    print("Error: matplotlib not found. Please install with: pip install matplotlib")
    sys.exit(1)

class SpendingAnalyzer:
    """Analyzes spending data and generates comprehensive reports."""
    
    def __init__(self):
        self.categories = [
            "Food & Dining", "Transportation", "Shopping", "Entertainment",
            "Bills & Utilities", "Healthcare", "Travel", "Education",
            "Personal Care", "Home & Garden", "Insurance", "Investments"
        ]
        self.spending_data = []
        self.monthly_budgets = {}
        
    def generate_sample_data(self, months: int = 12) -> None:
        """Generate realistic sample spending data for demonstration."""
        try:
            base_date = datetime.datetime.now().replace(day=1)
            
            # Set monthly budgets
            budget_ranges = {
                "Food & Dining": (400, 600),
                "Transportation": (200, 400),
                "Shopping": (150, 300),
                "Entertainment": (100, 250),
                "Bills & Utilities": (300, 400),
                "Healthcare": (100, 300),
                "Travel": (0, 500),
                "Education": (50, 200),
                "Personal Care": (50, 150),
                "Home & Garden": (100, 250),
                "Insurance": (200, 300),
                "Investments": (500, 1000)
            }
            
            for category, (min_budget, max_budget) in budget_ranges.items():
                self.monthly_budgets[category] = random.randint(min_budget, max_budget)
            
            # Generate spending data
            for month_offset in range(months):
                current_date = base_date - datetime.timedelta(days=30 * month_offset)
                month_str = current_date.strftime("%Y-%m")
                
                for category in self.categories:
                    # Generate realistic spending with some variance
                    budget = self.monthly_budgets[category]
                    actual_spending = budget * random.uniform(0.7, 1.3)
                    
                    # Add seasonal variations
                    if category == "Travel" and current_date.month in [6, 7, 12]:
                        actual_spending *= 1.5
                    elif category == "Shopping" and current_date.month == 12:
                        actual_spending *= 1.4
                    
                    self.spending_data.append({
                        "date": current_date,
                        "month": month_str,
                        "category": category,
                        "amount": round(actual_spending, 2),
                        "budget": budget,
                        "variance": round(actual_spending - budget, 2)
                    })
                    
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate total spending by month and category."""
        try:
            monthly_totals = {}
            
            for record in self.spending_data:
                month = record["month"]
                category = record["category"]
                amount = record["amount"]
                
                if month not in monthly_totals:
                    monthly_totals[month] = {}
                
                if category not in monthly_totals[month]:
                    monthly_totals[month][category] = 0
                
                monthly_totals[month][category] += amount
            
            return monthly_totals
            
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def create_category_breakdown_chart(self, month: str = None) -> None:
        """Create a pie chart showing spending breakdown by category."""
        try:
            if month is None:
                month = max([record["month"] for record in self.spending_data])
            
            monthly_data = [record for record in self.spending_data if record["month"] == month]
            category_totals = {}
            
            for record in monthly_data:
                category = record["category"]
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += record["amount"]
            
            # Create pie chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Pie chart
            colors = plt.cm.Set3(np.linspace(0, 1, len(category_totals)))
            wedges, texts, autotexts = ax1.pie(
                category_totals.values(),
                labels=category_totals.keys(),
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            
            ax1.set_title(f'Spending Breakdown - {month}', fontsize=14, fontweight='bold')
            
            # Bar chart for better comparison
            categories = list(category_totals.keys())
            amounts = list(category_totals.values())
            
            bars = ax2.bar(range(len(categories)), amounts, color=colors)
            ax2.set_xlabel('Categories')
            ax2.set_ylabel('Amount ($)')
            ax2.set_title(f'Category Spending - {month}', fontsize=14, fontweight='bold')
            ax2.set_xticks(range(len(categories)))
            ax2.set_xticklabels(categories, rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'${amount:.0f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.show()
            
            # Print summary
            total_spending = sum(category_totals.values())
            print(f"\n=== Spending Breakdown for {month} ===")
            print(f"Total Spending: ${total_spending:.2f}")
            print("\nTop 5 Categories:")
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            for i, (category, amount) in enumerate(sorted_categories[:5], 1):
                percentage = (amount / total_spending) * 100
                print(f"{i}. {category}: ${amount:.2f} ({percentage:.1f}%)")
                
        except Exception as e:
            print(f"Error creating category breakdown chart: {e}")
    
    def create_spending_trends_chart(self) -> None:
        """Create a line chart showing spending trends over time."""
        try:
            monthly_totals = self.calculate_monthly_totals()
            
            # Calculate total spending per month
            months = sorted(monthly_totals.keys())
            total_by_month = []
            dates = []
            
            for month in months:
                total = sum(monthly_totals[month].values())
                total_by_month.append(total)
                dates.append(datetime.datetime.strptime(month, "%Y-%m"))