```python
"""
Personal Finance Analysis Script

This script analyzes spending patterns from CSV transaction data to:
- Calculate monthly spending averages by category
- Detect spending anomalies using statistical methods
- Generate budget recommendations based on savings goals
- Provide actionable insights for financial planning

Usage: python script.py

The script expects a CSV file named 'transactions.csv' with columns:
date,amount,category,description

If no file exists, sample data will be generated for demonstration.
"""

import csv
import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
import os


def load_or_generate_data():
    """Load transaction data from CSV or generate sample data if file doesn't exist."""
    filename = 'transactions.csv'
    
    if not os.path.exists(filename):
        print(f"No {filename} found. Generating sample data...")
        generate_sample_data(filename)
    
    transactions = []
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                transactions.append({
                    'date': datetime.strptime(row['date'], '%Y-%m-%d'),
                    'amount': float(row['amount']),
                    'category': row['category'],
                    'description': row['description']
                })
    except Exception as e:
        print(f"Error loading data: {e}")
        return []
    
    return sorted(transactions, key=lambda x: x['date'])


def generate_sample_data(filename):
    """Generate sample transaction data for demonstration."""
    import random
    
    categories = ['Groceries', 'Transportation', 'Entertainment', 'Utilities', 
                 'Dining Out', 'Healthcare', 'Shopping', 'Gas', 'Insurance']
    
    transactions = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(500):
        date = start_date + timedelta(days=random.randint(0, 365))
        category = random.choice(categories)
        
        # Create realistic spending patterns
        base_amounts = {
            'Groceries': (50, 150),
            'Transportation': (20, 80),
            'Entertainment': (30, 120),
            'Utilities': (80, 200),
            'Dining Out': (25, 75),
            'Healthcare': (50, 300),
            'Shopping': (40, 200),
            'Gas': (30, 80),
            'Insurance': (100, 400)
        }
        
        min_amt, max_amt = base_amounts[category]
        amount = round(random.uniform(min_amt, max_amt), 2)
        
        # Add some anomalies (10% chance of high spending)
        if random.random() < 0.1:
            amount *= random.uniform(2, 5)
        
        transactions.append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': amount,
            'category': category,
            'description': f'{category} purchase'
        })
    
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'amount', 'category', 'description'])
        writer.writeheader()
        writer.writerows(transactions)
    
    print(f"Generated {len(transactions)} sample transactions in {filename}")


def analyze_spending_patterns(transactions):
    """Analyze spending patterns by category and month."""
    monthly_spending = defaultdict(lambda: defaultdict(float))
    category_totals = defaultdict(float)
    
    for transaction in transactions:
        month_key = transaction['date'].strftime('%Y-%m')
        category = transaction['category']
        amount = transaction['amount']
        
        monthly_spending[month_key][category] += amount
        category_totals[category] += amount
    
    return monthly_spending, category_totals


def calculate_monthly_averages(monthly_spending):
    """Calculate average monthly spending by category."""
    category_monthly_amounts = defaultdict(list)
    
    for month_data in monthly_spending.values():
        for category, amount in month_data.items():
            category_monthly_amounts[category].append(amount)
    
    averages = {}
    for category, amounts in category_monthly_amounts.items():
        if amounts:
            averages[category] = {
                'average': statistics.mean(amounts),
                'median': statistics.median(amounts),
                'std_dev': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                'min': min(amounts),
                'max': max(amounts)
            }
    
    return averages


def detect_anomalies(transactions, monthly_averages):
    """Detect spending anomalies using statistical methods."""
    anomalies = []
    
    for transaction in transactions:
        category = transaction['category']
        amount = transaction['amount']
        
        if category in monthly_averages:
            avg = monthly_averages[category]['average']
            std_dev = monthly_averages[category]['std_dev']
            
            # Consider anomaly if amount is more than 2 standard deviations from mean
            if std_dev > 0 and abs(amount - avg) > 2 * std_dev:
                anomalies.append({
                    'date': transaction['date'],
                    'category': category,
                    'amount': amount,
                    'expected_range': (avg - 2*std_dev, avg + 2*std_dev),
                    'description': transaction['description']
                })
    
    return sorted(anomalies, key=lambda x: x['date'], reverse=True)


def calculate_budget_recommendations(monthly_averages, category_totals, savings_goal_percent=20):
    """Generate budget recommendations based on spending patterns and savings goals."""
    total_monthly_spending = sum(avg_data['average'] for avg_data in monthly_averages.values())
    
    # Calculate target total budget based on savings goal
    target_total = total_monthly_spending / (1 - savings_goal_percent / 100)
    savings_target = target_total * (savings_goal_percent / 100)
    
    recommendations = {
        'current_monthly_spending': total_monthly_spending,
        'target_monthly_budget': target_total,
        'monthly_savings_target': savings_target,
        'category_recommendations': {}
    }
    
    # Calculate category-wise recommendations
    for category, avg_data in monthly_averages.items():
        current_avg = avg_data['average']
        category_percent = current_avg / total_monthly_spending
        suggested_budget = target_total * category_percent * 0.9  # 10% reduction across categories
        
        recommendations['category_recommendations'][category] = {
            'current_average': current_avg,
            'suggested_budget': suggested_budget,
            'potential_savings': max(0, current_avg - suggested_budget),
            'reduction_percent': max(0, (current_avg - suggested_budget) / current_avg * 100)
        }
    
    return recommendations


def print_analysis_results(monthly_averages, anomalies, recommendations):
    """Print formatted analysis results."""
    print("\n" + "="*80)
    print("PERSONAL FINANCE ANALYSIS REPORT")
    print("="*80)
    
    # Monthly Averages
    print("\n📊 MONTHLY SPENDING AVERAGES BY CATEGORY:")
    print("-" * 60)
    for category, data in sorted(monthly_averages.items(), 
                                key=lambda x: x[1]['average'], reverse=True):
        print(f"{category:20} | Avg: ${data['average']:8.2f} | "
              f"Range: ${data['min']:6.2f} - ${data['max']:8.2f}")
    
    # Anomalies
    print(f"\n🚨 SPENDING ANOMALIES (Last 10):")
    print("-" * 60)
    if anomalies:
        for anomaly in anomalies[:10]:
            expected_min, expected_max = anomaly['expected_range']
            print