```python
#!/usr/bin/env python3
"""
Automated Budget Recommendation Report Generator

This module analyzes historical spending patterns from sample financial data,
calculates average monthly expenses by category, and generates realistic budget 
recommendations with visualizations. The script creates mock historical data
to demonstrate the analysis capabilities.

Features:
- Historical spending pattern analysis
- Category-based expense averaging
- Budget limit recommendations with 10% buffer
- Matplotlib visualizations for spending trends
- Comprehensive error handling
- Self-contained execution with minimal dependencies

Usage: python script.py
"""

import json
import statistics
import datetime
from collections import defaultdict
import random
import sys

# Mock matplotlib for environments without it installed
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Visualizations will be skipped.")

def generate_mock_data():
    """Generate realistic mock financial data for the past 12 months."""
    categories = {
        'Housing': (1200, 1400),
        'Food': (300, 500),
        'Transportation': (150, 300),
        'Healthcare': (100, 250),
        'Entertainment': (50, 200),
        'Utilities': (80, 150),
        'Shopping': (100, 400),
        'Insurance': (120, 180)
    }
    
    transactions = []
    current_date = datetime.date.today()
    
    for month_offset in range(12):
        month_date = current_date.replace(day=1) - datetime.timedelta(days=month_offset * 30)
        
        for category, (min_amount, max_amount) in categories.items():
            # Generate 1-5 transactions per category per month
            num_transactions = random.randint(1, 5)
            
            for _ in range(num_transactions):
                amount = round(random.uniform(min_amount/num_transactions, max_amount/num_transactions), 2)
                day = random.randint(1, 28)
                transaction_date = month_date.replace(day=day)
                
                transactions.append({
                    'date': transaction_date.isoformat(),
                    'amount': amount,
                    'category': category,
                    'description': f'{category} expense'
                })
    
    return transactions

def analyze_spending_patterns(transactions):
    """Analyze historical spending patterns and calculate monthly averages by category."""
    try:
        monthly_spending = defaultdict(lambda: defaultdict(float))
        category_totals = defaultdict(list)
        
        for transaction in transactions:
            date = datetime.datetime.fromisoformat(transaction['date'])
            month_key = date.strftime('%Y-%m')
            category = transaction['category']
            amount = float(transaction['amount'])
            
            monthly_spending[month_key][category] += amount
        
        # Calculate monthly totals for each category
        for month_data in monthly_spending.values():
            for category, amount in month_data.items():
                category_totals[category].append(amount)
        
        # Calculate statistics for each category
        analysis_results = {}
        for category, amounts in category_totals.items():
            if amounts:
                analysis_results[category] = {
                    'average': round(statistics.mean(amounts), 2),
                    'median': round(statistics.median(amounts), 2),
                    'min': round(min(amounts), 2),
                    'max': round(max(amounts), 2),
                    'std_dev': round(statistics.stdev(amounts) if len(amounts) > 1 else 0, 2)
                }
        
        return analysis_results, monthly_spending
        
    except Exception as e:
        print(f"Error analyzing spending patterns: {e}")
        return {}, {}

def generate_budget_recommendations(analysis_results):
    """Generate realistic budget recommendations based on historical data."""
    try:
        recommendations = {}
        total_recommended_budget = 0
        
        for category, stats in analysis_results.items():
            # Use average + 10% buffer as recommended budget
            recommended_amount = round(stats['average'] * 1.1, 2)
            
            # Ensure minimum viability
            if recommended_amount < stats['max'] * 0.8:
                recommended_amount = round(stats['max'] * 0.8, 2)
            
            recommendations[category] = {
                'recommended_budget': recommended_amount,
                'historical_average': stats['average'],
                'buffer_amount': round(recommended_amount - stats['average'], 2),
                'risk_level': 'Low' if stats['std_dev'] < stats['average'] * 0.2 else 
                           'Medium' if stats['std_dev'] < stats['average'] * 0.4 else 'High'
            }
            
            total_recommended_budget += recommended_amount
        
        return recommendations, total_recommended_budget
        
    except Exception as e:
        print(f"Error generating budget recommendations: {e}")
        return {}, 0

def create_visualizations(monthly_spending, analysis_results):
    """Create matplotlib visualizations for spending trends."""
    if not HAS_MATPLOTLIB:
        print("\nVisualization skipped: matplotlib not available")
        return
    
    try:
        # Prepare data for plotting
        months = sorted(monthly_spending.keys())
        categories = list(analysis_results.keys())
        
        # Create spending trend chart
        plt.figure(figsize=(15, 10))
        
        # Subplot 1: Monthly spending by category
        plt.subplot(2, 2, 1)
        for category in categories:
            monthly_amounts = [monthly_spending[month].get(category, 0) for month in months]
            plt.plot(range(len(months)), monthly_amounts, marker='o', label=category)
        
        plt.title('Monthly Spending Trends by Category')
        plt.xlabel('Month')
        plt.ylabel('Amount ($)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(range(len(months)), [m[-2:] for m in months], rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Subplot 2: Average spending by category (bar chart)
        plt.subplot(2, 2, 2)
        categories_list = list(analysis_results.keys())
        averages = [analysis_results[cat]['average'] for cat in categories_list]
        plt.bar(categories_list, averages, color='skyblue', alpha=0.7)
        plt.title('Average Monthly Spending by Category')
        plt.xlabel('Category')
        plt.ylabel('Average Amount ($)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, axis='y')
        
        # Subplot 3: Budget vs Historical Average
        plt.subplot(2, 2, 3)
        recommendations, _ = generate_budget_recommendations(analysis_results)
        categories_list = list(recommendations.keys())
        historical_avg = [analysis_results[cat]['average'] for cat in categories_list]
        recommended_budget = [recommendations[cat]['recommended_budget'] for cat in categories_list]
        
        x_pos = range(len(categories_list))
        plt.bar([p - 0.2 for p in x_pos], historical_avg, 0.4, label='Historical Average', alpha=0.7)
        plt.bar([p + 0.2 for p in x_pos], recommended_budget, 0.4, label='Recommended Budget', alpha=0.7)
        
        plt.title('Historical Average vs Recommended Budget')
        plt.xlabel('Category')
        plt.ylabel('Amount ($)')
        plt.xticks(x_pos, categories_list, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        
        # Subplot 4: Spending variability (std dev)
        plt.subplot(2, 2, 4)
        std_devs = [analysis_results[cat]['std_dev'] for cat in categories_list]