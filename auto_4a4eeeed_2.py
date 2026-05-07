```python
"""
Interactive Financial Dashboard Generator

This module creates a self-contained HTML dashboard with JavaScript charts for financial data visualization.
The dashboard displays spending by category, monthly trends, budget progress bars, and alert notifications
using Chart.js for responsive data visualization.

Features:
- Category-based spending analysis with pie charts
- Monthly spending trends with line charts
- Budget progress tracking with progress bars
- Alert notifications for budget overruns
- Fully responsive web interface
- Self-contained HTML file generation

Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os


def generate_sample_data() -> Dict[str, Any]:
    """Generate sample financial data for dashboard demonstration."""
    try:
        categories = ["Food", "Transportation", "Entertainment", "Utilities", "Healthcare", "Shopping", "Other"]
        
        # Generate monthly data for the last 12 months
        months = []
        monthly_data = []
        current_date = datetime.now()
        
        for i in range(11, -1, -1):
            month_date = current_date - timedelta(days=30*i)
            months.append(month_date.strftime("%b %Y"))
            monthly_total = random.randint(2000, 4000)
            monthly_data.append(monthly_total)
        
        # Generate category spending
        category_spending = {}
        total_spending = sum(monthly_data[-3:]) / 3  # Average of last 3 months
        
        for category in categories:
            category_spending[category] = random.randint(100, int(total_spending/3))
        
        # Generate budget data
        budgets = {}
        alerts = []
        
        for category in categories:
            budget = random.randint(int(category_spending[category] * 0.8), int(category_spending[category] * 1.5))
            budgets[category] = budget
            
            if category_spending[category] > budget * 0.9:
                alerts.append({
                    "type": "warning" if category_spending[category] <= budget else "danger",
                    "category": category,
                    "message": f"{category} spending is {'over budget' if category_spending[category] > budget else 'approaching budget limit'}"
                })
        
        return {
            "months": months,
            "monthly_spending": monthly_data,
            "category_spending": category_spending,
            "budgets": budgets,
            "alerts": alerts
        }
    
    except Exception as e:
        print(f"Error generating sample data: {str(e)}")
        return {}


def create_html_dashboard(data: Dict[str, Any]) -> str:
    """Create the complete HTML dashboard with embedded JavaScript and CSS."""
    try:
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .dashboard {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            padding: 25px;
            border-left: 5px solid #3498db;
        }}
        
        .card h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin-bottom: 20px;
        }}
        
        .alerts {{
            margin-bottom: 30px;
        }}
        
        .alert {{
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid;
        }}
        
        .alert-warning {{
            background-color: #fff3cd;
            border-color: #ffc107;
            color: #856404;
        }}
        
        .alert-danger {{
            background-color: #f8d7da;
            border-color: #dc3545;
            color: #721c24;
        }}
        
        .budget-item {{
            margin-bottom: 15px;
        }}
        
        .budget-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-weight: 500;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        
        .progress-safe {{ background-color: #28a745; }}
        .progress-warning {{ background-color: #ffc107; }}
        .progress-danger {{ background-color: #dc3545; }}
        
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>💰 Financial Dashboard</h1>
            <p>Track your spending, monitor budgets, and stay financially healthy</p>
        </div>
        
        <div class="content">
            <!-- Alerts Section -->
            <div class="alerts">
                <h3>🚨 Budget Alerts</h3>
                <div id="alertsContainer">
                    <!-- Alerts will be inserted here -->
                </div>
            </div>
            
            <div class="grid">
                <!-- Monthly Trends Chart -->
                <div class="card">
                    <h3>📈 Monthly Spending Trends</h3>
                    <div class="chart-container">
                        <canvas id="monthlyChart"></canvas>
                    </div>
                </div>
                
                <!-- Category Pie Chart -->
                <div class="card">
                    <h3>🥧 Spending by Category</h3>
                    <div class="chart-container">
                        <canvas id