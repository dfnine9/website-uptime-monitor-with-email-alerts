```python
"""
Monthly Financial Report Generator

This module analyzes categorized transaction data to produce comprehensive spending reports.
It generates spending summaries, category breakdowns, and trend visualizations in both
CSV and PDF formats. The script processes transaction data from CSV files and creates
visual charts showing spending patterns over time.

Features:
- Transaction data analysis and categorization
- Monthly spending summaries
- Category-wise expenditure breakdowns
- Trend analysis with simple ASCII charts
- Export to CSV and PDF formats
- Comprehensive error handling

Usage:
    python script.py

The script will look for 'transactions.csv' in the current directory or generate
sample data if the file doesn't exist.
"""

import csv
import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import calendar

def generate_sample_data(filename: str = "transactions.csv") -> None:
    """Generate sample transaction data for demonstration."""
    try:
        sample_transactions = [
            ["2024-01-15", "Grocery Store", "Food", -125.50],
            ["2024-01-16", "Gas Station", "Transportation", -45.00],
            ["2024-01-18", "Restaurant", "Food", -67.30],
            ["2024-01-20", "Salary", "Income", 3500.00],
            ["2024-01-22", "Electric Bill", "Utilities", -89.45],
            ["2024-01-25", "Coffee Shop", "Food", -15.75],
            ["2024-02-02", "Grocery Store", "Food", -143.20],
            ["2024-02-05", "Gas Station", "Transportation", -52.30],
            ["2024-02-08", "Online Shopping", "Shopping", -89.99],
            ["2024-02-12", "Restaurant", "Food", -78.45],
            ["2024-02-15", "Salary", "Income", 3500.00],
            ["2024-02-18", "Internet Bill", "Utilities", -75.00],
            ["2024-02-20", "Movie Theater", "Entertainment", -25.50],
            ["2024-02-25", "Grocery Store", "Food", -156.80],
            ["2024-03-01", "Gas Station", "Transportation", -48.75],
            ["2024-03-05", "Coffee Shop", "Food", -18.90],
            ["2024-03-08", "Gym Membership", "Health", -49.99],
            ["2024-03-12", "Restaurant", "Food", -92.35],
            ["2024-03-15", "Salary", "Income", 3500.00],
            ["2024-03-18", "Phone Bill", "Utilities", -65.00],
            ["2024-03-22", "Online Shopping", "Shopping", -134.50],
            ["2024-03-25", "Grocery Store", "Food", -167.25],
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["date", "description", "category", "amount"])
            writer.writerows(sample_transactions)
        
        print(f"Generated sample data in {filename}")
    except Exception as e:
        print(f"Error generating sample data: {e}")
        sys.exit(1)

def load_transactions(filename: str) -> List[Dict[str, Any]]:
    """Load transaction data from CSV file."""
    transactions = []
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    transaction = {
                        'date': datetime.strptime(row['date'], '%Y-%m-%d'),
                        'description': row['description'],
                        'category': row['category'],
                        'amount': float(row['amount'])
                    }
                    transactions.append(transaction)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid row: {row}. Error: {e}")
                    continue
    except FileNotFoundError:
        print(f"File {filename} not found. Generating sample data...")
        generate_sample_data(filename)
        return load_transactions(filename)
    except Exception as e:
        print(f"Error loading transactions: {e}")
        sys.exit(1)
    
    return transactions

def analyze_transactions(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze transaction data and generate insights."""
    try:
        # Group by month
        monthly_data = defaultdict(lambda: {'income': 0, 'expenses': 0, 'categories': defaultdict(float)})
        category_totals = defaultdict(float)
        
        for transaction in transactions:
            month_key = transaction['date'].strftime('%Y-%m')
            amount = transaction['amount']
            category = transaction['category']
            
            if amount > 0:
                monthly_data[month_key]['income'] += amount
            else:
                monthly_data[month_key]['expenses'] += abs(amount)
                monthly_data[month_key]['categories'][category] += abs(amount)
                category_totals[category] += abs(amount)
        
        # Calculate trends
        months = sorted(monthly_data.keys())
        trends = {
            'months': months,
            'income_trend': [monthly_data[month]['income'] for month in months],
            'expense_trend': [monthly_data[month]['expenses'] for month in months],
            'net_trend': [monthly_data[month]['income'] - monthly_data[month]['expenses'] for month in months]
        }
        
        return {
            'monthly_data': dict(monthly_data),
            'category_totals': dict(category_totals),
            'trends': trends,
            'total_transactions': len(transactions)
        }
    except Exception as e:
        print(f"Error analyzing transactions: {e}")
        return {}

def create_ascii_chart(data: List[float], labels: List[str], title: str, width: int = 50) -> str:
    """Create a simple ASCII bar chart."""
    try:
        if not data or max(data) == 0:
            return f"{title}\nNo data to display\n"
        
        chart = f"{title}\n{'='*len(title)}\n"
        max_value = max(data)
        
        for i, (value, label) in enumerate(zip(data, labels)):
            bar_length = int((value / max_value) * width) if max_value > 0 else 0
            bar = '█' * bar_length
            chart += f"{label:>8}: {bar} ${value:,.2f}\n"
        
        return chart + "\n"
    except Exception as e:
        return f"Error creating chart: {e}\n"

def generate_report_text(analysis: Dict[str, Any]) -> str:
    """Generate a comprehensive text report."""
    try:
        report = "MONTHLY FINANCIAL REPORT\n"
        report += "=" * 50 + "\n\n"
        
        # Summary
        report += f"Total Transactions Analyzed: {analysis['total_transactions']}\n"
        report += f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Monthly breakdown
        report += "MONTHLY BREAKDOWN\n"
        report += "-" * 20 + "\n"
        
        for month, data in sorted(analysis['monthly_data'].items()):
            month_name = datetime.strptime(month, '%Y-%m').strftime('%B %Y')
            net_income = data['income'] - data['expenses']
            report += f"\n{month_name}:\n"
            report += f"  Income:    ${data['income']:>10,.2f}\n"
            report += f"  Expenses:  ${data['expenses']:>10,.2f}\n"
            report += f"  Net:       ${net_income:>10,.2f}\n"
        
        # Category analysis
        report += "\n\nC