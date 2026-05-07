```python
"""
Financial Data Visualization Generator

This module creates interactive HTML charts and graphs for financial analysis including:
- Spending breakdowns by category (pie charts)
- Monthly spending trends (line charts)
- Comparative analysis across time periods (bar charts)

The script generates sample financial data and creates interactive visualizations
using HTML5 Canvas and Chart.js CDN. All visualizations are saved as a single
HTML file that can be opened in any web browser.

Requirements: Python 3.6+ (uses only standard library)
Usage: python script.py
Output: Creates 'financial_dashboard.html' with interactive charts
"""

import json
import random
import datetime
from typing import Dict, List, Tuple
import calendar


class FinancialDataGenerator:
    """Generates realistic sample financial data for visualization."""
    
    def __init__(self):
        self.categories = [
            'Groceries', 'Utilities', 'Transportation', 'Entertainment',
            'Healthcare', 'Dining Out', 'Shopping', 'Insurance',
            'Education', 'Home Maintenance', 'Subscriptions', 'Travel'
        ]
        
    def generate_monthly_data(self, months: int = 12) -> List[Dict]:
        """Generate monthly spending data for specified number of months."""
        data = []
        base_date = datetime.datetime.now() - datetime.timedelta(days=30 * months)
        
        for i in range(months):
            month_date = base_date + datetime.timedelta(days=30 * i)
            month_data = {
                'month': month_date.strftime('%Y-%m'),
                'month_name': month_date.strftime('%B %Y'),
                'categories': {}
            }
            
            total_budget = random.uniform(3000, 5000)
            remaining_budget = total_budget
            
            for category in self.categories[:-1]:
                if remaining_budget <= 0:
                    break
                    
                # Assign realistic spending ranges per category
                if category == 'Groceries':
                    amount = random.uniform(400, 800)
                elif category == 'Utilities':
                    amount = random.uniform(150, 300)
                elif category == 'Transportation':
                    amount = random.uniform(200, 500)
                elif category == 'Entertainment':
                    amount = random.uniform(100, 400)
                elif category == 'Healthcare':
                    amount = random.uniform(50, 300)
                else:
                    amount = random.uniform(50, min(remaining_budget * 0.3, 300))
                
                amount = min(amount, remaining_budget)
                month_data['categories'][category] = round(amount, 2)
                remaining_budget -= amount
            
            # Assign remaining budget to last category if any
            if remaining_budget > 0:
                month_data['categories'][self.categories[-1]] = round(remaining_budget, 2)
            
            month_data['total'] = round(sum(month_data['categories'].values()), 2)
            data.append(month_data)
            
        return data


class ChartGenerator:
    """Generates HTML/JavaScript code for interactive charts."""
    
    @staticmethod
    def generate_pie_chart(data: Dict, chart_id: str, title: str) -> str:
        """Generate pie chart HTML/JS code."""
        labels = list(data.keys())
        values = list(data.values())
        colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
            '#4BC0C0', '#FF6384', '#36A2EB', '#FFCE56'
        ]
        
        return f"""
        <canvas id="{chart_id}" width="400" height="400"></canvas>
        <script>
            var ctx_{chart_id} = document.getElementById('{chart_id}').getContext('2d');
            var chart_{chart_id} = new Chart(ctx_{chart_id}, {{
                type: 'pie',
                data: {{
                    labels: {json.dumps(labels)},
                    datasets: [{{
                        data: {json.dumps(values)},
                        backgroundColor: {json.dumps(colors[:len(labels)])},
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '{title}',
                            font: {{ size: 16, weight: 'bold' }}
                        }},
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        </script>
        """
    
    @staticmethod
    def generate_line_chart(monthly_data: List[Dict], chart_id: str, title: str) -> str:
        """Generate line chart for monthly trends."""
        months = [item['month_name'] for item in monthly_data]
        totals = [item['total'] for item in monthly_data]
        
        return f"""
        <canvas id="{chart_id}" width="800" height="400"></canvas>
        <script>
            var ctx_{chart_id} = document.getElementById('{chart_id}').getContext('2d');
            var chart_{chart_id} = new Chart(ctx_{chart_id}, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(months)},
                    datasets: [{{
                        label: 'Total Spending',
                        data: {json.dumps(totals)},
                        borderColor: '#36A2EB',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '{title}',
                            font: {{ size: 16, weight: 'bold' }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return '$' + value.toLocaleString();
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        </script>
        """
    
    @staticmethod
    def generate_comparative_bar_chart(data1: Dict, data2: Dict, chart_id: str, title: str, labels: Tuple[str, str]) -> str:
        """Generate comparative bar chart for two time periods."""
        categories = list(set(data1.keys()) | set(data2.keys()))
        values1 = [data1.get(cat, 0) for cat in categories]
        values2 = [data2.get(cat, 0) for cat in categories]
        
        return f"""
        <canvas id="{chart_id}" width="800" height="400"></canvas>
        <script>
            var ctx_{chart_id} = document.getElementById('{chart_id}').getContext('2d');
            var chart_{chart_id} = new Chart(ctx_{chart_id}, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(categories)},
                    datasets: [{{
                        label: '{labels[0]}',
                        data: {json.dumps(values1)},
                        backgroundColor: 'rgba(255, 99, 132, 0.8)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }}, {{
                        label: '{labels[1]}',
                        data: {json.dumps(values2)},
                        backgroundColor: 'rgba(54, 162, 235, 0.8)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }}]
                }},