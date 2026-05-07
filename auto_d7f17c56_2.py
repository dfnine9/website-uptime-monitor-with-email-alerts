```python
#!/usr/bin/env python3
"""
HTML Transaction Dashboard Generator

This module creates a responsive web dashboard for transaction data analysis.
It generates interactive charts, filters, and date range selectors using only
standard library dependencies plus httpx and anthropic for data processing.

The dashboard includes:
- Transaction overview with summary statistics
- Interactive charts (bar, line, pie) using Chart.js
- Date range filtering
- Category and amount filtering
- Responsive design with Bootstrap CSS
- Export functionality

Usage: python script.py
"""

import json
import datetime
import random
import os
from typing import Dict, List, Any, Optional
import html


class TransactionDashboard:
    """Generate HTML dashboard for transaction data with interactive features."""
    
    def __init__(self):
        self.transactions = []
        self.categories = set()
        
    def generate_sample_data(self, num_transactions: int = 100) -> List[Dict[str, Any]]:
        """Generate sample transaction data for demonstration."""
        try:
            categories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Utilities', 'Healthcare', 'Education']
            transactions = []
            
            for i in range(num_transactions):
                date = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365))
                category = random.choice(categories)
                amount = round(random.uniform(10, 500), 2)
                description = f"{category} transaction #{i+1}"
                
                transaction = {
                    'id': i + 1,
                    'date': date.strftime('%Y-%m-%d'),
                    'category': category,
                    'amount': amount,
                    'description': description,
                    'type': 'expense' if amount > 0 else 'income'
                }
                transactions.append(transaction)
                
            return transactions
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []
    
    def calculate_statistics(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics from transaction data."""
        try:
            if not transactions:
                return {}
                
            total_amount = sum(t['amount'] for t in transactions)
            avg_amount = total_amount / len(transactions) if transactions else 0
            max_amount = max(t['amount'] for t in transactions) if transactions else 0
            min_amount = min(t['amount'] for t in transactions) if transactions else 0
            
            category_totals = {}
            for transaction in transactions:
                category = transaction['category']
                category_totals[category] = category_totals.get(category, 0) + transaction['amount']
            
            monthly_totals = {}
            for transaction in transactions:
                month = transaction['date'][:7]  # YYYY-MM
                monthly_totals[month] = monthly_totals.get(month, 0) + transaction['amount']
            
            return {
                'total_transactions': len(transactions),
                'total_amount': round(total_amount, 2),
                'average_amount': round(avg_amount, 2),
                'max_amount': max_amount,
                'min_amount': min_amount,
                'category_totals': category_totals,
                'monthly_totals': monthly_totals
            }
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {}
    
    def generate_chart_data(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data structures for Chart.js charts."""
        try:
            chart_data = {}
            
            # Category pie chart data
            if 'category_totals' in stats:
                categories = list(stats['category_totals'].keys())
                amounts = list(stats['category_totals'].values())
                
                chart_data['category_chart'] = {
                    'labels': categories,
                    'datasets': [{
                        'data': amounts,
                        'backgroundColor': [
                            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                        ][:len(categories)]
                    }]
                }
            
            # Monthly trend line chart data
            if 'monthly_totals' in stats:
                months = sorted(stats['monthly_totals'].keys())
                amounts = [stats['monthly_totals'][month] for month in months]
                
                chart_data['monthly_chart'] = {
                    'labels': months,
                    'datasets': [{
                        'label': 'Monthly Spending',
                        'data': amounts,
                        'borderColor': '#36A2EB',
                        'backgroundColor': 'rgba(54, 162, 235, 0.1)',
                        'fill': True
                    }]
                }
            
            return chart_data
            
        except Exception as e:
            print(f"Error generating chart data: {e}")
            return {}
    
    def generate_html_dashboard(self, transactions: List[Dict[str, Any]], 
                              stats: Dict[str, Any], chart_data: Dict[str, Any]) -> str:
        """Generate complete HTML dashboard with embedded CSS and JavaScript."""
        try:
            # Escape data for safe HTML embedding
            transactions_json = html.escape(json.dumps(transactions))
            chart_data_json = html.escape(json.dumps(chart_data))
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transaction Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .dashboard-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
        }}
        .stat-card {{
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        .filter-section {{
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }}
        .transaction-table {{
            max-height: 400px;
            overflow-y: auto;
        }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <div class="container">
            <h1 class="text-center">Transaction Dashboard</h1>
            <p class="text-center mb-0">Interactive financial data analysis</p>
        </div>
    </div>

    <div class="container mt-4">
        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-md-3 mb-3">
                <div class="card stat-card h-100">
                    <div class="card-body text-center">
                        <h5 class="card-title text-primary">Total Transactions</h5>
                        <h2 class="text-dark">{stats.get('total_transactions', 0)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card stat-card h-100">
                    <div class="card-body text-center">
                        <h5 class="card-title text-success">Total Amount</h5