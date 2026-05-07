```python
#!/usr/bin/env python3
"""
Interactive Financial Data Visualization Module

This module generates interactive Plotly charts for financial analysis including:
- Monthly spending trends over time
- Category breakdown pie charts
- Budget vs actual spending comparisons
- Comprehensive financial dashboard

The module creates sample financial data and generates three types of visualizations:
1. Line chart showing spending trends by month
2. Pie chart showing spending breakdown by category
3. Bar chart comparing budgeted vs actual spending

All charts are interactive and can be saved as HTML files for viewing in a web browser.
"""

import json
import datetime
import random
from typing import Dict, List, Any, Tuple
import sys


class FinancialDataGenerator:
    """Generates sample financial data for visualization purposes."""
    
    def __init__(self):
        self.categories = [
            'Housing', 'Transportation', 'Food', 'Healthcare', 
            'Entertainment', 'Shopping', 'Utilities', 'Insurance'
        ]
        self.months = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
    
    def generate_monthly_data(self) -> Dict[str, List[float]]:
        """Generate monthly spending data for each category."""
        try:
            monthly_data = {}
            base_amounts = {
                'Housing': 1500, 'Transportation': 400, 'Food': 600,
                'Healthcare': 200, 'Entertainment': 300, 'Shopping': 250,
                'Utilities': 150, 'Insurance': 100
            }
            
            for category in self.categories:
                monthly_data[category] = []
                base_amount = base_amounts[category]
                
                for month in range(12):
                    # Add seasonal variation and random fluctuation
                    seasonal_factor = 1 + 0.1 * random.sin(month * 3.14159 / 6)
                    random_factor = random.uniform(0.8, 1.2)
                    amount = base_amount * seasonal_factor * random_factor
                    monthly_data[category].append(round(amount, 2))
            
            return monthly_data
        except Exception as e:
            print(f"Error generating monthly data: {e}")
            return {}
    
    def generate_budget_data(self) -> Dict[str, float]:
        """Generate budget allocations for each category."""
        try:
            budget_data = {
                'Housing': 1600, 'Transportation': 450, 'Food': 650,
                'Healthcare': 250, 'Entertainment': 350, 'Shopping': 300,
                'Utilities': 180, 'Insurance': 120
            }
            return budget_data
        except Exception as e:
            print(f"Error generating budget data: {e}")
            return {}


class PlotlyChartGenerator:
    """Generates interactive Plotly charts using only built-in libraries."""
    
    def __init__(self):
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FCEA2B', '#FF9FF3', '#54A0FF', '#5F27CD'
        ]
    
    def create_line_chart_html(self, monthly_data: Dict[str, List[float]], months: List[str]) -> str:
        """Create HTML for interactive line chart showing monthly spending trends."""
        try:
            traces = []
            for i, (category, values) in enumerate(monthly_data.items()):
                color = self.colors[i % len(self.colors)]
                trace = f"""
                {{
                    x: {json.dumps(months)},
                    y: {json.dumps(values)},
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: '{category}',
                    line: {{color: '{color}', width: 3}},
                    marker: {{size: 8}}
                }}"""
                traces.append(trace)
            
            traces_str = ','.join(traces)
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Monthly Spending Trends</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <div id="monthlyTrends" style="width:100%;height:600px;"></div>
                <script>
                    var data = [{traces_str}];
                    var layout = {{
                        title: {{
                            text: 'Monthly Spending Trends',
                            font: {{size: 24}}
                        }},
                        xaxis: {{
                            title: 'Month',
                            gridcolor: '#E5E5E5'
                        }},
                        yaxis: {{
                            title: 'Amount ($)',
                            gridcolor: '#E5E5E5'
                        }},
                        plot_bgcolor: '#F8F9FA',
                        paper_bgcolor: '#FFFFFF',
                        hovermode: 'x unified'
                    }};
                    Plotly.newPlot('monthlyTrends', data, layout);
                </script>
            </body>
            </html>"""
            
            return html
        except Exception as e:
            print(f"Error creating line chart: {e}")
            return ""
    
    def create_pie_chart_html(self, category_totals: Dict[str, float]) -> str:
        """Create HTML for interactive pie chart showing category breakdown."""
        try:
            labels = list(category_totals.keys())
            values = list(category_totals.values())
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Spending by Category</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <div id="categoryBreakdown" style="width:100%;height:600px;"></div>
                <script>
                    var data = [{{
                        values: {json.dumps(values)},
                        labels: {json.dumps(labels)},
                        type: 'pie',
                        textinfo: 'label+percent',
                        textposition: 'outside',
                        marker: {{
                            colors: {json.dumps(self.colors[:len(labels)])}
                        }},
                        hole: 0.3
                    }}];
                    var layout = {{
                        title: {{
                            text: 'Annual Spending by Category',
                            font: {{size: 24}}
                        }},
                        paper_bgcolor: '#FFFFFF',
                        showlegend: true
                    }};
                    Plotly.newPlot('categoryBreakdown', data, layout);
                </script>
            </body>
            </html>"""
            
            return html
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return ""
    
    def create_budget_comparison_html(self, actual_totals: Dict[str, float], 
                                    budget_data: Dict[str, float]) -> str:
        """Create HTML for budget vs actual comparison bar chart."""
        try:
            categories = list(budget_data.keys())
            actual_values = [actual_totals.get(cat, 0) for cat in categories]
            budget_values = [budget_data[cat] for cat in categories]
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Budget vs Actual Spending</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <div id="budgetComparison" style="width:100%;height:600px;"></div>
                <script>
                    var trace1 = {{
                        x: {json.dumps(categories)},
                        y: {json.dumps(budget_values)},
                        name: