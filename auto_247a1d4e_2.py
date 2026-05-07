```python
#!/usr/bin/env python3
"""
Transaction Analysis Dashboard Generator

This module creates a responsive HTML dashboard that combines transaction analysis
with interactive charts and visualizations. It generates a self-contained HTML
file with embedded CSS styling and JavaScript interactivity for financial
transaction data analysis.

Features:
- Responsive dashboard layout with CSS Grid/Flexbox
- Interactive charts using Chart.js (CDN)
- Transaction summary statistics
- Trend analysis visualization
- Category breakdown charts
- Mobile-responsive design
- Dark/light theme toggle

Usage:
    python script.py

The script generates 'transaction_dashboard.html' in the current directory.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys


def generate_sample_transactions(count: int = 100) -> List[Dict[str, Any]]:
    """Generate sample transaction data for demonstration purposes."""
    categories = ['Food', 'Transportation', 'Shopping', 'Bills', 'Entertainment', 'Healthcare', 'Income']
    transaction_types = ['debit', 'credit']
    
    transactions = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        transaction_date = base_date + timedelta(days=random.randint(0, 30))
        category = random.choice(categories)
        
        # Income transactions are typically credit, others are typically debit
        if category == 'Income':
            trans_type = 'credit'
            amount = random.uniform(1000, 5000)
        else:
            trans_type = random.choice(transaction_types)
            amount = random.uniform(10, 500)
        
        transactions.append({
            'id': f'txn_{i:04d}',
            'date': transaction_date.strftime('%Y-%m-%d'),
            'amount': round(amount, 2),
            'type': trans_type,
            'category': category,
            'description': f'{category} transaction #{i+1}',
            'merchant': f'Merchant {random.randint(1, 50)}'
        })
    
    return transactions


def analyze_transactions(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze transaction data and return summary statistics."""
    try:
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'credit')
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'debit')
        net_balance = total_income - total_expenses
        
        # Category analysis
        category_totals = {}
        for transaction in transactions:
            category = transaction['category']
            amount = transaction['amount'] if transaction['type'] == 'debit' else 0
            category_totals[category] = category_totals.get(category, 0) + amount
        
        # Daily trends
        daily_totals = {}
        for transaction in transactions:
            date = transaction['date']
            amount = transaction['amount']
            if transaction['type'] == 'debit':
                amount = -amount
            daily_totals[date] = daily_totals.get(date, 0) + amount
        
        return {
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expenses, 2),
            'net_balance': round(net_balance, 2),
            'transaction_count': len(transactions),
            'category_breakdown': category_totals,
            'daily_trends': daily_totals
        }
    except Exception as e:
        print(f"Error analyzing transactions: {e}", file=sys.stderr)
        return {}


def generate_html_dashboard(transactions: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
    """Generate complete HTML dashboard with embedded CSS and JavaScript."""
    
    # Convert data to JSON for JavaScript
    transactions_json = json.dumps(transactions, indent=2)
    analysis_json = json.dumps(analysis, indent=2)
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transaction Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --warning-color: #f59e0b;
            --background-color: #f8fafc;
            --card-background: #ffffff;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
        }}
        
        .dark-theme {{
            --background-color: #0f172a;
            --card-background: #1e293b;
            --text-color: #f1f5f9;
            --border-color: #334155;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
            transition: all 0.3s ease;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px 0;
            border-bottom: 2px solid var(--border-color);
        }}
        
        .header h1 {{
            color: var(--primary-color);
            font-size: 2.5rem;
            font-weight: bold;
        }}
        
        .theme-toggle {{
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s ease;
        }}
        
        .theme-toggle:hover {{
            background: #1d4ed8;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: var(--card-background);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-color);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }}
        
        .card h3 {{
            margin-bottom: 15px;
            color: var(--primary-color);
            font-size: 1.3rem;
        }}
        
        .stat-card {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: var(--secondary-color);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .income {{
            color: var(--success-