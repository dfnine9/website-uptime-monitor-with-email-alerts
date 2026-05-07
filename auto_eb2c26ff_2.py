```python
"""
Financial Analytics Dashboard Generator

This module creates comprehensive visual reports for financial data analysis including:
- Spending breakdown by category (pie chart)
- Monthly spending trends (line chart) 
- Top expense categories (bar chart)
- Export capabilities for all charts

Features:
- Self-contained with minimal dependencies
- Generates sample financial data for demonstration
- Creates interactive charts using matplotlib
- Exports charts as PNG files
- Comprehensive error handling
- Detailed console output

Usage: python script.py
"""

import json
import random
import datetime
from typing import Dict, List, Tuple, Any
import os
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta
    import calendar
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install matplotlib: pip install matplotlib")
    sys.exit(1)

class FinancialReportGenerator:
    """Generate comprehensive financial visual reports with export capabilities."""
    
    def __init__(self):
        """Initialize the report generator with sample data."""
        self.categories = [
            "Food & Dining", "Transportation", "Shopping", "Entertainment",
            "Bills & Utilities", "Healthcare", "Travel", "Education",
            "Groceries", "Gas", "Insurance", "Subscriptions"
        ]
        self.sample_data = self._generate_sample_data()
        
    def _generate_sample_data(self) -> List[Dict[str, Any]]:
        """Generate realistic sample financial data for the last 12 months."""
        data = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(500):  # Generate 500 transactions
            transaction_date = start_date + timedelta(days=random.randint(0, 365))
            category = random.choice(self.categories)
            
            # Different spending patterns by category
            amount_ranges = {
                "Food & Dining": (15, 80),
                "Transportation": (5, 150),
                "Shopping": (20, 300),
                "Entertainment": (10, 120),
                "Bills & Utilities": (50, 400),
                "Healthcare": (30, 500),
                "Travel": (100, 1500),
                "Education": (50, 800),
                "Groceries": (40, 200),
                "Gas": (30, 100),
                "Insurance": (100, 600),
                "Subscriptions": (10, 50)
            }
            
            min_amt, max_amt = amount_ranges.get(category, (10, 100))
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            data.append({
                "date": transaction_date.strftime("%Y-%m-%d"),
                "category": category,
                "amount": amount,
                "description": f"{category} expense"
            })
        
        return sorted(data, key=lambda x: x["date"])
    
    def _ensure_export_directory(self) -> str:
        """Create export directory if it doesn't exist."""
        export_dir = "financial_reports"
        try:
            os.makedirs(export_dir, exist_ok=True)
            return export_dir
        except Exception as e:
            print(f"Warning: Could not create export directory: {e}")
            return "."
    
    def generate_category_breakdown(self, export_dir: str) -> None:
        """Generate and export spending breakdown by category pie chart."""
        try:
            print("Generating category breakdown chart...")
            
            # Calculate spending by category
            category_totals = {}
            for transaction in self.sample_data:
                category = transaction["category"]
                amount = transaction["amount"]
                category_totals[category] = category_totals.get(category, 0) + amount
            
            # Sort by amount (descending)
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            
            # Create pie chart
            plt.figure(figsize=(12, 8))
            categories, amounts = zip(*sorted_categories)
            
            # Generate colors
            colors = plt.cm.Set3(range(len(categories)))
            
            # Create pie chart with percentage labels
            wedges, texts, autotexts = plt.pie(
                amounts, 
                labels=categories, 
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                explode=[0.05 if i == 0 else 0 for i in range(len(categories))]  # Explode largest slice
            )
            
            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            plt.title('Spending Breakdown by Category', fontsize=16, fontweight='bold', pad=20)
            plt.axis('equal')
            
            # Add total spending annotation
            total_spending = sum(amounts)
            plt.figtext(0.02, 0.02, f'Total Spending: ${total_spending:,.2f}', 
                       fontsize=12, fontweight='bold')
            
            # Save chart
            export_path = os.path.join(export_dir, "category_breakdown.png")
            plt.savefig(export_path, dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"✓ Category breakdown chart saved to: {export_path}")
            print(f"✓ Total categories analyzed: {len(categories)}")
            print(f"✓ Total spending: ${total_spending:,.2f}")
            
        except Exception as e:
            print(f"Error generating category breakdown: {e}")
    
    def generate_monthly_trends(self, export_dir: str) -> None:
        """Generate and export monthly spending trends line chart."""
        try:
            print("\nGenerating monthly trends chart...")
            
            # Calculate monthly totals
            monthly_totals = {}
            for transaction in self.sample_data:
                date_obj = datetime.strptime(transaction["date"], "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                amount = transaction["amount"]
                monthly_totals[month_key] = monthly_totals.get(month_key, 0) + amount
            
            # Sort by date
            sorted_months = sorted(monthly_totals.items())
            
            # Prepare data for plotting
            months = [datetime.strptime(month, "%Y-%m") for month, _ in sorted_months]
            amounts = [amount for _, amount in sorted_months]
            
            # Create line chart
            plt.figure(figsize=(14, 8))
            plt.plot(months, amounts, marker='o', linewidth=2, markersize=6, color='#2E86C1')
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            plt.xticks(rotation=45)
            
            # Add grid and labels
            plt.grid(True, alpha=0.3)
            plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12, fontweight='bold')
            plt.ylabel('Amount Spent ($)', fontsize=12, fontweight='bold')
            
            # Format y-axis as currency
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add average line
            avg_spending = sum(amounts) / len(amounts)
            plt.axhline(y=avg_spending, color='red', linestyle='--', alpha=0.7, 
                       label=f'Average: ${avg_spending:,.2f}')
            plt.legend()
            
            # Add annotations for highest/lowest months
            max_idx = amounts.index(max