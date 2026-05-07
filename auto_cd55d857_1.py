```python
#!/usr/bin/env python3
"""
Monthly Spending Report Visualization Module

This module generates comprehensive monthly spending reports with various visualizations
including bar charts, pie charts, and trend analysis. It analyzes spending patterns
across different categories and provides insights into financial behavior.

Features:
- Monthly spending breakdown by category
- Trend analysis over time
- Category-wise spending distribution
- Spending pattern analysis
- Statistical summaries

Dependencies: matplotlib, seaborn (will attempt to install if missing)
"""

import sys
import subprocess
import json
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple, Any
import calendar

# Check and install required packages
def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}")
        return False
    return True

# Try to import required packages, install if missing
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Wedge
except ImportError:
    print("matplotlib not found. Installing...")
    if install_package("matplotlib"):
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.patches import Wedge
    else:
        print("Failed to install matplotlib. Exiting.")
        sys.exit(1)

try:
    import seaborn as sns
except ImportError:
    print("seaborn not found. Installing...")
    if install_package("seaborn"):
        import seaborn as sns
    else:
        print("Failed to install seaborn. Exiting.")
        sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("numpy not found. Installing...")
    if install_package("numpy"):
        import numpy as np
    else:
        print("Failed to install numpy. Exiting.")
        sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("pandas not found. Installing...")
    if install_package("pandas"):
        import pandas as pd
    else:
        print("Failed to install pandas. Exiting.")
        sys.exit(1)

class SpendingReportGenerator:
    """Generate comprehensive spending reports with visualizations"""
    
    def __init__(self):
        """Initialize the spending report generator"""
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Education', 'Travel',
            'Personal Care', 'Groceries', 'Gas', 'Insurance'
        ]
        self.colors = sns.color_palette("husl", len(self.categories))
        
    def generate_sample_data(self, months: int = 12) -> pd.DataFrame:
        """Generate sample spending data for demonstration"""
        try:
            data = []
            base_date = datetime.now() - timedelta(days=30*months)
            
            for i in range(months):
                current_date = base_date + timedelta(days=30*i)
                month_year = current_date.strftime("%Y-%m")
                
                for category in self.categories:
                    # Generate realistic spending amounts with some randomness
                    base_amounts = {
                        'Food & Dining': 400,
                        'Transportation': 200,
                        'Shopping': 300,
                        'Entertainment': 150,
                        'Bills & Utilities': 350,
                        'Healthcare': 100,
                        'Education': 50,
                        'Travel': 200,
                        'Personal Care': 80,
                        'Groceries': 450,
                        'Gas': 180,
                        'Insurance': 250
                    }
                    
                    base_amount = base_amounts.get(category, 100)
                    # Add seasonal variation and randomness
                    seasonal_factor = 1 + 0.2 * random.random()
                    if category == 'Travel' and i in [5, 6, 11]:  # Summer and holiday travel
                        seasonal_factor *= 1.5
                    elif category == 'Bills & Utilities' and i in [0, 1, 11]:  # Winter heating
                        seasonal_factor *= 1.3
                    
                    amount = base_amount * seasonal_factor * (0.7 + 0.6 * random.random())
                    
                    data.append({
                        'date': current_date,
                        'month_year': month_year,
                        'category': category,
                        'amount': round(amount, 2)
                    })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return pd.DataFrame()
    
    def create_monthly_bar_chart(self, df: pd.DataFrame) -> None:
        """Create monthly spending bar chart"""
        try:
            plt.figure(figsize=(14, 8))
            
            # Group by month and sum amounts
            monthly_totals = df.groupby('month_year')['amount'].sum().reset_index()
            monthly_totals['date'] = pd.to_datetime(monthly_totals['month_year'])
            monthly_totals = monthly_totals.sort_values('date')
            
            # Create bar chart
            bars = plt.bar(range(len(monthly_totals)), monthly_totals['amount'], 
                          color='steelblue', alpha=0.7, edgecolor='navy', linewidth=1)
            
            # Customize chart
            plt.title('Monthly Spending Overview', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12, fontweight='bold')
            plt.ylabel('Amount ($)', fontsize=12, fontweight='bold')
            
            # Format x-axis labels
            month_labels = [datetime.strptime(month, '%Y-%m').strftime('%b %Y') 
                          for month in monthly_totals['month_year']]
            plt.xticks(range(len(monthly_totals)), month_labels, rotation=45, ha='right')
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'${height:,.0f}', ha='center', va='bottom', fontweight='bold')
            
            # Add grid for better readability
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Format y-axis to show currency
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error creating monthly bar chart: {e}")
    
    def create_category_pie_chart(self, df: pd.DataFrame) -> None:
        """Create category spending pie chart"""
        try:
            plt.figure(figsize=(12, 10))
            
            # Group by category and sum amounts
            category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
            
            # Create pie chart with custom styling
            wedges, texts, autotexts = plt.pie(category_totals.values, 
                                              labels=category_totals.index,
                                              colors=self.colors,
                                              autopct='%1.1f%%',
                                              startangle=90,
                                              explode=[0.05 if i == 0 else 0 for i in range(len(category_totals))])
            
            # Customize text
            plt.setp(autotexts, size=10, weight="bold", color="white")
            plt.setp(texts, size=11, weight="bold")
            
            plt.title('Spending Distribution by Category', fontsize=16, fontweight='bold', pad=20)