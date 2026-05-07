```python
"""
Financial Data Visualization Module

This module generates interactive charts and graphs for financial data analysis including:
- Pie charts for expense categories
- Line graphs for spending trends over time
- Bar charts comparing monthly budgets to actual spending

Dependencies: matplotlib, plotly (will attempt graceful fallback to basic matplotlib if plotly unavailable)
Usage: python script.py
"""

import sys
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    print("Warning: plotly not available, falling back to matplotlib")


class FinancialDataGenerator:
    """Generates sample financial data for visualization."""
    
    def __init__(self):
        self.categories = ['Food', 'Transportation', 'Housing', 'Entertainment', 'Healthcare', 'Shopping', 'Utilities']
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    def generate_expense_data(self) -> Dict[str, float]:
        """Generate sample expense data by category."""
        try:
            expenses = {}
            for category in self.categories:
                expenses[category] = round(random.uniform(200, 1200), 2)
            return expenses
        except Exception as e:
            print(f"Error generating expense data: {e}")
            return {}
    
    def generate_spending_trends(self) -> Tuple[List[str], List[float]]:
        """Generate spending trend data over time."""
        try:
            base_date = datetime(2024, 1, 1)
            dates = []
            spending = []
            
            for i in range(12):
                current_date = base_date + timedelta(days=i*30)
                dates.append(current_date.strftime('%Y-%m'))
                # Simulate seasonal spending patterns
                base_spending = 2500 + (500 * (i % 4))  # Quarterly variation
                noise = random.uniform(-300, 300)
                spending.append(round(base_spending + noise, 2))
            
            return dates, spending
        except Exception as e:
            print(f"Error generating spending trends: {e}")
            return [], []
    
    def generate_budget_comparison(self) -> Tuple[List[str], List[float], List[float]]:
        """Generate budget vs actual spending comparison."""
        try:
            budgets = []
            actuals = []
            
            for month in self.months:
                budget = round(random.uniform(2800, 3500), 2)
                # Actual spending varies around budget
                variance = random.uniform(-0.2, 0.3)  # -20% to +30%
                actual = round(budget * (1 + variance), 2)
                
                budgets.append(budget)
                actuals.append(actual)
            
            return self.months, budgets, actuals
        except Exception as e:
            print(f"Error generating budget comparison: {e}")
            return [], [], []


class PlotlyVisualizer:
    """Creates interactive visualizations using Plotly."""
    
    def __init__(self):
        if not HAS_PLOTLY:
            raise ImportError("Plotly not available")
    
    def create_expense_pie_chart(self, expenses: Dict[str, float]) -> None:
        """Create interactive pie chart for expense categories."""
        try:
            fig = go.Figure(data=[go.Pie(
                labels=list(expenses.keys()),
                values=list(expenses.values()),
                hole=0.3,
                hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>"
            )])
            
            fig.update_layout(
                title="Expense Categories Distribution",
                font_size=12,
                showlegend=True
            )
            
            fig.show()
            print("✓ Interactive pie chart generated successfully")
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
    
    def create_spending_trend_line(self, dates: List[str], spending: List[float]) -> None:
        """Create interactive line graph for spending trends."""
        try:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=spending,
                mode='lines+markers',
                name='Monthly Spending',
                line=dict(width=3, color='blue'),
                marker=dict(size=8),
                hovertemplate="<b>%{x}</b><br>Spending: $%{y:,.2f}<extra></extra>"
            ))
            
            fig.update_layout(
                title="Spending Trends Over Time",
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                hovermode='x unified',
                showlegend=True
            )
            
            fig.show()
            print("✓ Interactive line chart generated successfully")
            
        except Exception as e:
            print(f"Error creating line chart: {e}")
    
    def create_budget_comparison_bar(self, months: List[str], budgets: List[float], actuals: List[float]) -> None:
        """Create interactive bar chart comparing budgets to actual spending."""
        try:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=months,
                y=budgets,
                name='Budget',
                marker_color='lightblue',
                hovertemplate="<b>%{x}</b><br>Budget: $%{y:,.2f}<extra></extra>"
            ))
            
            fig.add_trace(go.Bar(
                x=months,
                y=actuals,
                name='Actual Spending',
                marker_color='orange',
                hovertemplate="<b>%{x}</b><br>Actual: $%{y:,.2f}<extra></extra>"
            ))
            
            fig.update_layout(
                title="Monthly Budget vs Actual Spending",
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                barmode='group',
                hovermode='x unified',
                showlegend=True
            )
            
            fig.show()
            print("✓ Interactive bar chart generated successfully")
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")


class MatplotlibVisualizer:
    """Creates static visualizations using Matplotlib."""
    
    def __init__(self):
        if not HAS_MATPLOTLIB:
            raise ImportError("Matplotlib not available")
        plt.style.use('default')
    
    def create_expense_pie_chart(self, expenses: Dict[str, float]) -> None:
        """Create pie chart for expense categories."""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            wedges, texts, autotexts = ax.pie(
                expenses.values(),
                labels=expenses.keys(),
                autopct='%1.1f%%',
                startangle=90,
                colors=plt.cm.Set3.colors
            )
            
            ax.set_title('Expense Categories Distribution', fontsize=16, fontweight='bold')
            
            # Add value labels
            for i, (category, amount) in enumerate(expenses.items()):
                autotexts[i].set_text(f'{autotexts[i].get_text()}\n${amount:,.0f}')
            
            plt.tight_layout()
            plt.show()
            print("✓ Pie chart generated successfully")
            
        except Exception as e: