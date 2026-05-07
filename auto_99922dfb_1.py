```python
#!/usr/bin/env python3
"""
Financial Data Visualization Module

This module generates spending charts, category breakdowns, and monthly trend analysis
using matplotlib for data visualization. It creates sample financial data and produces
three types of visualizations:

1. Monthly spending trends over time
2. Spending breakdown by category (pie chart)
3. Category spending comparison (bar chart)

The module is self-contained and only requires matplotlib beyond the standard library.
All charts are saved as PNG files and results are printed to stdout.

Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Wedge
except ImportError:
    print("Error: matplotlib is required but not installed")
    print("Install with: pip install matplotlib")
    sys.exit(1)


class FinancialDataGenerator:
    """Generates sample financial data for visualization."""
    
    CATEGORIES = [
        'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
        'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
        'Personal Care', 'Gifts & Donations'
    ]
    
    def __init__(self):
        self.data = []
    
    def generate_sample_data(self, months=12):
        """Generate sample spending data for the specified number of months."""
        try:
            start_date = datetime.now() - timedelta(days=months * 30)
            
            for i in range(months * 30):
                current_date = start_date + timedelta(days=i)
                
                # Generate 0-5 transactions per day
                num_transactions = random.randint(0, 5)
                
                for _ in range(num_transactions):
                    transaction = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'category': random.choice(self.CATEGORIES),
                        'amount': round(random.uniform(5.0, 500.0), 2),
                        'description': f"Transaction on {current_date.strftime('%Y-%m-%d')}"
                    }
                    self.data.append(transaction)
            
            print(f"Generated {len(self.data)} sample transactions")
            return self.data
            
        except Exception as e:
            print(f"Error generating sample data: {str(e)}")
            return []


class SpendingVisualizer:
    """Creates various spending visualizations using matplotlib."""
    
    def __init__(self, data):
        self.data = data
        self.setup_style()
    
    def setup_style(self):
        """Configure matplotlib style settings."""
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def prepare_monthly_data(self):
        """Aggregate spending data by month."""
        try:
            monthly_totals = defaultdict(float)
            
            for transaction in self.data:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                monthly_totals[month_key] += transaction['amount']
            
            # Sort by date
            sorted_months = sorted(monthly_totals.items())
            return sorted_months
            
        except Exception as e:
            print(f"Error preparing monthly data: {str(e)}")
            return []
    
    def prepare_category_data(self):
        """Aggregate spending data by category."""
        try:
            category_totals = defaultdict(float)
            
            for transaction in self.data:
                category_totals[transaction['category']] += transaction['amount']
            
            # Sort by amount (descending)
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            return sorted_categories
            
        except Exception as e:
            print(f"Error preparing category data: {str(e)}")
            return []
    
    def create_monthly_trend_chart(self):
        """Create a line chart showing monthly spending trends."""
        try:
            monthly_data = self.prepare_monthly_data()
            if not monthly_data:
                print("No monthly data available for trend chart")
                return
            
            months = [datetime.strptime(month, '%Y-%m') for month, _ in monthly_data]
            amounts = [amount for _, amount in monthly_data]
            
            plt.figure(figsize=(14, 8))
            plt.plot(months, amounts, marker='o', linewidth=2, markersize=8, color='#2E86AB')
            plt.fill_between(months, amounts, alpha=0.3, color='#2E86AB')
            
            plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Total Spending ($)', fontsize=12)
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.xticks(rotation=45)
            
            # Add value labels on points
            for month, amount in zip(months, amounts):
                plt.annotate(f'${amount:.0f}', (month, amount), 
                           textcoords="offset points", xytext=(0,10), ha='center')
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("✓ Monthly trend chart saved as 'monthly_trends.png'")
            print(f"  - Tracked {len(monthly_data)} months")
            print(f"  - Total spending: ${sum(amounts):.2f}")
            print(f"  - Average monthly: ${sum(amounts)/len(amounts):.2f}")
            
        except Exception as e:
            print(f"Error creating monthly trend chart: {str(e)}")
    
    def create_category_pie_chart(self):
        """Create a pie chart showing spending breakdown by category."""
        try:
            category_data = self.prepare_category_data()
            if not category_data:
                print("No category data available for pie chart")
                return
            
            categories = [cat for cat, _ in category_data]
            amounts = [amount for _, amount in category_data]
            
            # Create color palette
            colors = plt.cm.Set3(range(len(categories)))
            
            plt.figure(figsize=(12, 10))
            wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%',
                                              startangle=90, colors=colors)
            
            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.title('Spending Breakdown by Category', fontsize=16, fontweight='bold', pad=20)
            plt.axis('equal')
            
            # Add legend with amounts
            legend_labels = [f'{cat}: ${amount:.2f}' for cat, amount in category_data]
            plt.legend(wedges, legend_labels, title="Categories", loc="center left", 
                      bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            plt.savefig('category_breakdown.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("✓ Category pie chart saved as 'category_breakdown.png'")
            print(f"  - {len(categories)} categories tracked")
            print(f"  - Top category: {categories[0]} (${amounts[0]:.2f})")
            
        except Exception as e:
            print(f"Error creating category pie chart: