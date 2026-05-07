```python
#!/usr/bin/env python3
"""
Interactive Financial Data Visualization Tool

This module generates interactive visualizations for financial expense analysis including:
- Monthly spending breakdown charts
- Category trends over time
- Top expense categories analysis
- Exportable HTML and CSV reports

Dependencies: matplotlib, plotly (will attempt to install if missing)
Usage: python script.py
"""

import sys
import subprocess
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import csv
import os

def install_package(package_name: str) -> bool:
    """Install a package using pip if not available."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}")
        return False

# Try to import required packages, install if missing
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
except ImportError:
    print("Installing matplotlib...")
    if install_package("matplotlib"):
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    else:
        sys.exit(1)

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
except ImportError:
    print("Installing plotly...")
    if install_package("plotly"):
        import plotly.graph_objects as go
        import plotly.express as px
        from plotly.subplots import make_subplots
    else:
        sys.exit(1)

class FinancialDataGenerator:
    """Generates sample financial data for visualization."""
    
    def __init__(self):
        self.categories = [
            "Food & Dining", "Shopping", "Transportation", "Bills & Utilities",
            "Entertainment", "Healthcare", "Travel", "Education", "Investment",
            "Insurance", "Groceries", "Gas", "Home & Garden"
        ]
        
    def generate_sample_data(self, months: int = 12) -> List[Dict[str, Any]]:
        """Generate sample financial transaction data."""
        data = []
        start_date = datetime.now() - timedelta(days=months * 30)
        
        for i in range(months * 50):  # ~50 transactions per month
            transaction_date = start_date + timedelta(
                days=random.randint(0, months * 30)
            )
            
            category = random.choice(self.categories)
            
            # Category-based spending ranges
            spending_ranges = {
                "Food & Dining": (10, 150),
                "Shopping": (20, 300),
                "Transportation": (15, 200),
                "Bills & Utilities": (50, 400),
                "Entertainment": (10, 100),
                "Healthcare": (25, 500),
                "Travel": (100, 1500),
                "Education": (50, 800),
                "Investment": (100, 2000),
                "Insurance": (100, 600),
                "Groceries": (30, 200),
                "Gas": (25, 80),
                "Home & Garden": (20, 400)
            }
            
            min_amount, max_amount = spending_ranges.get(category, (10, 100))
            amount = round(random.uniform(min_amount, max_amount), 2)
            
            data.append({
                "date": transaction_date,
                "category": category,
                "amount": amount,
                "description": f"{category} expense"
            })
        
        return sorted(data, key=lambda x: x["date"])

class FinancialVisualizer:
    """Creates interactive visualizations for financial data."""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.processed_data = self._process_data()
        
    def _process_data(self) -> Dict[str, Any]:
        """Process raw transaction data for visualization."""
        try:
            # Monthly spending breakdown
            monthly_spending = {}
            category_trends = {}
            category_totals = {}
            
            for transaction in self.data:
                month_key = transaction["date"].strftime("%Y-%m")
                category = transaction["category"]
                amount = transaction["amount"]
                
                # Monthly totals
                if month_key not in monthly_spending:
                    monthly_spending[month_key] = 0
                monthly_spending[month_key] += amount
                
                # Category trends over time
                if category not in category_trends:
                    category_trends[category] = {}
                if month_key not in category_trends[category]:
                    category_trends[category][month_key] = 0
                category_trends[category][month_key] += amount
                
                # Category totals
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += amount
            
            return {
                "monthly_spending": monthly_spending,
                "category_trends": category_trends,
                "category_totals": category_totals
            }
            
        except Exception as e:
            print(f"Error processing data: {e}")
            return {"monthly_spending": {}, "category_trends": {}, "category_totals": {}}
    
    def create_monthly_spending_chart(self) -> None:
        """Create interactive monthly spending breakdown chart."""
        try:
            monthly_data = self.processed_data["monthly_spending"]
            
            if not monthly_data:
                print("No monthly data available")
                return
            
            months = sorted(monthly_data.keys())
            amounts = [monthly_data[month] for month in months]
            
            # Plotly interactive chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=months,
                y=amounts,
                mode='lines+markers',
                name='Monthly Spending',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8, color='#e74c3c')
            ))
            
            fig.update_layout(
                title="Monthly Spending Breakdown",
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                hovermode='x unified',
                template='plotly_white'
            )
            
            fig.write_html("monthly_spending.html")
            print("✓ Monthly spending chart saved as 'monthly_spending.html'")
            
            # Also create matplotlib version
            plt.figure(figsize=(12, 6))
            plt.plot(months, amounts, marker='o', linewidth=2, markersize=6)
            plt.title("Monthly Spending Breakdown")
            plt.xlabel("Month")
            plt.ylabel("Amount ($)")
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig("monthly_spending.png", dpi=300, bbox_inches='tight')
            plt.close()
            print("✓ Monthly spending chart saved as 'monthly_spending.png'")
            
        except Exception as e:
            print(f"Error creating monthly spending chart: {e}")
    
    def create_category_trends_chart(self) -> None:
        """Create interactive category trends over time chart."""
        try:
            category_data = self.processed_data["category_trends"]
            
            if not category_data:
                print("No category data available")
                return
            
            # Get all unique months
            all_months = set()
            for category_months in category_data.values():
                all_months.update(category_months.keys())
            all_months = sorted(list(all_months))
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Category Trends Over Time", "Top Categories Comparison"),
                vertical_spacing=0.1
            )
            
            # Top 5 categories by total spending
            top_categories = sorted(
                self.processed_data["category_totals"].items(),
                key=lambda x: x