```python
#!/usr/bin/env python3
"""
Financial Data Visualization Component

This module generates interactive charts for financial analysis including:
- Spending by category pie charts
- Monthly trend lines
- Budget vs actual comparisons

Uses matplotlib for static charts and plotly for interactive visualizations.
Generates sample financial data for demonstration purposes.

Usage: python script.py
"""

import json
import random
import datetime
from typing import Dict, List, Any
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available, skipping static charts")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available, skipping interactive charts")


class FinancialDataGenerator:
    """Generates sample financial data for visualization."""
    
    CATEGORIES = ['Food', 'Transportation', 'Housing', 'Entertainment', 'Healthcare', 'Shopping', 'Utilities']
    
    @staticmethod
    def generate_spending_data() -> Dict[str, float]:
        """Generate spending by category data."""
        return {
            category: round(random.uniform(200, 1500), 2)
            for category in FinancialDataGenerator.CATEGORIES
        }
    
    @staticmethod
    def generate_monthly_trends(months: int = 12) -> Dict[str, List[Any]]:
        """Generate monthly spending trends."""
        end_date = datetime.date.today()
        dates = []
        spending = []
        
        for i in range(months):
            month_date = end_date - datetime.timedelta(days=30 * i)
            dates.append(month_date)
            spending.append(round(random.uniform(2000, 5000), 2))
        
        return {
            'dates': list(reversed(dates)),
            'spending': list(reversed(spending))
        }
    
    @staticmethod
    def generate_budget_comparison() -> Dict[str, Dict[str, float]]:
        """Generate budget vs actual spending comparison."""
        comparison = {}
        for category in FinancialDataGenerator.CATEGORIES:
            budget = round(random.uniform(300, 1000), 2)
            actual = round(budget * random.uniform(0.7, 1.3), 2)
            comparison[category] = {'budget': budget, 'actual': actual}
        
        return comparison


class MatplotlibCharts:
    """Static chart generation using matplotlib."""
    
    @staticmethod
    def create_spending_pie_chart(spending_data: Dict[str, float]) -> None:
        """Create a pie chart showing spending by category."""
        try:
            categories = list(spending_data.keys())
            amounts = list(spending_data.values())
            
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(range(len(categories)))
            
            wedges, texts, autotexts = plt.pie(
                amounts, 
                labels=categories, 
                autopct='%1.1f%%',
                colors=colors,
                explode=[0.05] * len(categories)
            )
            
            plt.title('Spending by Category', fontsize=16, fontweight='bold')
            plt.axis('equal')
            
            # Add legend with amounts
            legend_labels = [f'{cat}: ${amt:.2f}' for cat, amt in spending_data.items()]
            plt.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            plt.savefig('spending_pie_chart.png', dpi=300, bbox_inches='tight')
            plt.show()
            
        except Exception as e:
            print(f"Error creating matplotlib pie chart: {e}")
    
    @staticmethod
    def create_monthly_trend_line(trend_data: Dict[str, List[Any]]) -> None:
        """Create a line chart showing monthly spending trends."""
        try:
            plt.figure(figsize=(12, 6))
            
            plt.plot(trend_data['dates'], trend_data['spending'], 
                    marker='o', linewidth=2, markersize=6, color='#2E86AB')
            
            plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold')
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Spending ($)', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Format x-axis dates
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.xticks(rotation=45)
            
            # Add value labels on points
            for date, spending in zip(trend_data['dates'], trend_data['spending']):
                plt.annotate(f'${spending:.0f}', 
                           (date, spending), 
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center',
                           fontsize=9)
            
            plt.tight_layout()
            plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
            plt.show()
            
        except Exception as e:
            print(f"Error creating matplotlib trend chart: {e}")
    
    @staticmethod
    def create_budget_comparison(budget_data: Dict[str, Dict[str, float]]) -> None:
        """Create a bar chart comparing budget vs actual spending."""
        try:
            categories = list(budget_data.keys())
            budgets = [budget_data[cat]['budget'] for cat in categories]
            actuals = [budget_data[cat]['actual'] for cat in categories]
            
            x = range(len(categories))
            width = 0.35
            
            plt.figure(figsize=(12, 8))
            
            bars1 = plt.bar([i - width/2 for i in x], budgets, width, 
                           label='Budget', color='#A8DADC', alpha=0.8)
            bars2 = plt.bar([i + width/2 for i in x], actuals, width, 
                           label='Actual', color='#457B9D', alpha=0.8)
            
            plt.xlabel('Category', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.title('Budget vs Actual Spending Comparison', fontsize=16, fontweight='bold')
            plt.xticks(x, categories, rotation=45, ha='right')
            plt.legend()
            plt.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    plt.annotate(f'${height:.0f}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom',
                               fontsize=9)
            
            plt.tight_layout()
            plt.savefig('budget_comparison.png', dpi=300, bbox_inches='tight')
            plt.show()
            
        except Exception as e:
            print(f"Error creating matplotlib budget comparison: {e}")


class PlotlyCharts:
    """Interactive chart generation using plotly."""
    
    @staticmethod
    def create_interactive_spending_pie(spending_data: Dict[str, float]) -> None:
        """Create an interactive pie chart showing spending by category."""
        try:
            fig = go.Figure(data=[go.Pie(
                labels=list(spending_