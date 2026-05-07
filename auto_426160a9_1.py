```python
#!/usr/bin/env python3
"""
Monthly Spending Visualization Module

This module generates comprehensive monthly spending breakdowns with interactive visualizations.
Features include:
- Pie charts for category distribution analysis
- Bar charts for spending trends over time
- Data export capabilities
- Error handling for robust operation

Dependencies: matplotlib, plotly (will attempt installation if missing)
Usage: python script.py
"""

import sys
import subprocess
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import calendar

def install_package(package_name: str) -> bool:
    """Install a package using pip with error handling."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}: {e}")
        return False

def ensure_dependencies():
    """Ensure required packages are installed."""
    required_packages = ['matplotlib', 'plotly']
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            if not install_package(package):
                print(f"Warning: Could not install {package}. Some features may not work.")

# Ensure dependencies are available
ensure_dependencies()

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available - pie charts disabled")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Plotly not available - interactive charts disabled")

class SpendingData:
    """Handles generation and management of spending data."""
    
    CATEGORIES = [
        'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
        'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
        'Personal Care', 'Gifts & Donations', 'Business Services', 'Other'
    ]
    
    def __init__(self, months: int = 12):
        self.months = months
        self.data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> List[Dict[str, Any]]:
        """Generate realistic sample spending data."""
        data = []
        base_date = datetime.now() - timedelta(days=30 * self.months)
        
        for month_offset in range(self.months):
            current_date = base_date + timedelta(days=30 * month_offset)
            month_data = {
                'date': current_date,
                'month_year': current_date.strftime('%Y-%m'),
                'month_name': current_date.strftime('%B %Y'),
                'categories': {}
            }
            
            # Generate spending for each category with realistic variations
            total_budget = random.uniform(2000, 5000)
            remaining_budget = total_budget
            
            for i, category in enumerate(self.CATEGORIES):
                if i == len(self.CATEGORIES) - 1:  # Last category gets remaining budget
                    amount = max(0, remaining_budget)
                else:
                    # Assign percentage of remaining budget
                    percentage = random.uniform(0.05, 0.25)
                    amount = remaining_budget * percentage
                    remaining_budget -= amount
                
                month_data['categories'][category] = round(amount, 2)
            
            month_data['total'] = sum(month_data['categories'].values())
            data.append(month_data)
        
        return data
    
    def get_category_totals(self) -> Dict[str, float]:
        """Calculate total spending by category across all months."""
        totals = {category: 0 for category in self.CATEGORIES}
        
        for month_data in self.data:
            for category, amount in month_data['categories'].items():
                totals[category] += amount
        
        return totals
    
    def get_monthly_totals(self) -> Tuple[List[str], List[float]]:
        """Get monthly total spending amounts."""
        months = [item['month_name'] for item in self.data]
        totals = [item['total'] for item in self.data]
        return months, totals
    
    def get_trend_data(self, category: str) -> Tuple[List[str], List[float]]:
        """Get spending trend for a specific category."""
        months = [item['month_name'] for item in self.data]
        amounts = [item['categories'].get(category, 0) for item in self.data]
        return months, amounts

class SpendingVisualizer:
    """Creates various visualizations for spending data."""
    
    def __init__(self, spending_data: SpendingData):
        self.data = spending_data
        self.output_dir = "spending_reports"
    
    def create_matplotlib_charts(self) -> bool:
        """Create charts using matplotlib."""
        if not MATPLOTLIB_AVAILABLE:
            return False
        
        try:
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Monthly Spending Analysis', fontsize=16, fontweight='bold')
            
            # 1. Category Distribution Pie Chart
            category_totals = self.data.get_category_totals()
            categories = list(category_totals.keys())
            amounts = list(category_totals.values())
            
            # Filter out zero amounts
            non_zero_data = [(cat, amt) for cat, amt in zip(categories, amounts) if amt > 0]
            if non_zero_data:
                categories, amounts = zip(*non_zero_data)
            
            colors = plt.cm.Set3(range(len(categories)))
            wedges, texts, autotexts = ax1.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            ax1.set_title('Spending by Category (Total)', fontweight='bold')
            
            # Adjust text properties
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            # 2. Monthly Spending Trend
            months, monthly_totals = self.data.get_monthly_totals()
            ax2.plot(range(len(months)), monthly_totals, marker='o', linewidth=2, markersize=6)
            ax2.set_title('Monthly Spending Trend', fontweight='bold')
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Amount ($)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
            
            # Set x-axis labels
            ax2.set_xticks(range(len(months)))
            ax2.set_xticklabels([m.split()[0][:3] for m in months], rotation=45)
            
            # 3. Top Categories Bar Chart
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            top_categories = sorted_categories[:6]  # Top 6 categories
            
            cat_names, cat_amounts = zip(*top_categories)
            bars = ax3.bar(range(len(cat_names)), cat_amounts, color=colors[:len(cat_names)])
            ax3.set_title('Top Spending Categories', fontweight='bold')
            ax3.set_xlabel('Category')
            ax3.set_ylabel('Total Amount ($)')
            ax3.set_xticks(range(len(cat_names)))
            ax3.set_xticklabels([name.replace(' & ', '\n&\n') for name in cat_names], 
                               rotation=45, ha