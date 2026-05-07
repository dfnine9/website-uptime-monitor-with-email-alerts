```python
"""
Transaction Analysis Script

This module analyzes categorized transaction data to identify spending patterns,
calculate monthly totals per category, and detect trends over time periods.

The script processes transaction data with the following structure:
- Transaction ID
- Date (YYYY-MM-DD format)
- Amount (positive for expenses, negative for income)
- Category (e.g., 'Food', 'Transportation', 'Entertainment')
- Description

Features:
- Monthly spending totals by category
- Trend analysis over time periods
- Pattern identification (peak spending months, category growth)
- Summary statistics and insights
"""

import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from statistics import mean, median
import sys


def generate_sample_data():
    """Generate sample transaction data for demonstration."""
    import random
    
    categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
    transactions = []
    
    # Generate 12 months of sample data
    base_date = datetime(2023, 1, 1)
    
    for month in range(12):
        current_month = base_date.replace(month=month + 1)
        
        # Generate 15-30 transactions per month
        for _ in range(random.randint(15, 30)):
            day = random.randint(1, 28)
            transaction_date = current_month.replace(day=day)
            
            category = random.choice(categories)
            
            # Vary amounts by category
            if category == 'Food':
                amount = round(random.uniform(5, 150), 2)
            elif category == 'Transportation':
                amount = round(random.uniform(20, 200), 2)
            elif category == 'Entertainment':
                amount = round(random.uniform(10, 300), 2)
            elif category == 'Utilities':
                amount = round(random.uniform(50, 250), 2)
            elif category == 'Shopping':
                amount = round(random.uniform(25, 500), 2)
            else:  # Healthcare
                amount = round(random.uniform(30, 800), 2)
            
            transactions.append({
                'id': f'TXN_{len(transactions) + 1:04d}',
                'date': transaction_date.strftime('%Y-%m-%d'),
                'amount': amount,
                'category': category,
                'description': f'{category} purchase'
            })
    
    return transactions


def parse_date(date_string):
    """Parse date string into datetime object with error handling."""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(date_string, '%m/%d/%Y')
        except ValueError:
            raise ValueError(f"Unable to parse date: {date_string}")


def calculate_monthly_totals(transactions):
    """Calculate monthly spending totals by category."""
    monthly_data = defaultdict(lambda: defaultdict(float))
    
    for transaction in transactions:
        try:
            date = parse_date(transaction['date'])
            month_key = f"{date.year}-{date.month:02d}"
            category = transaction['category']
            amount = float(transaction['amount'])
            
            # Only count positive amounts as expenses
            if amount > 0:
                monthly_data[month_key][category] += amount
                
        except (ValueError, KeyError) as e:
            print(f"Warning: Skipping invalid transaction: {e}")
            continue
    
    return dict(monthly_data)


def detect_trends(monthly_data):
    """Detect spending trends over time periods."""
    trends = {}
    category_totals = defaultdict(list)
    
    # Organize data by category across months
    for month, categories in monthly_data.items():
        for category, amount in categories.items():
            category_totals[category].append((month, amount))
    
    # Calculate trends for each category
    for category, data in category_totals.items():
        if len(data) >= 3:  # Need at least 3 months for trend analysis
            amounts = [amount for _, amount in data]
            
            # Calculate trend metrics
            avg_spending = mean(amounts)
            median_spending = median(amounts)
            max_spending = max(amounts)
            min_spending = min(amounts)
            
            # Simple trend calculation (comparing first half vs second half)
            mid_point = len(amounts) // 2
            first_half_avg = mean(amounts[:mid_point]) if mid_point > 0 else 0
            second_half_avg = mean(amounts[mid_point:]) if mid_point < len(amounts) else 0
            
            trend_direction = "increasing" if second_half_avg > first_half_avg else "decreasing"
            trend_percentage = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
            
            trends[category] = {
                'average': avg_spending,
                'median': median_spending,
                'max': max_spending,
                'min': min_spending,
                'trend_direction': trend_direction,
                'trend_percentage': abs(trend_percentage),
                'data_points': len(amounts)
            }
    
    return trends


def identify_patterns(monthly_data, trends):
    """Identify spending patterns and insights."""
    patterns = {}
    
    # Find peak spending months
    monthly_totals = {}
    for month, categories in monthly_data.items():
        monthly_totals[month] = sum(categories.values())
    
    peak_month = max(monthly_totals, key=monthly_totals.get) if monthly_totals else None
    lowest_month = min(monthly_totals, key=monthly_totals.get) if monthly_totals else None
    
    # Find top spending categories
    category_totals = defaultdict(float)
    for month_data in monthly_data.values():
        for category, amount in month_data.items():
            category_totals[category] += amount
    
    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Identify volatile categories (high variance)
    volatile_categories = []
    for category, trend_data in trends.items():
        if trend_data['trend_percentage'] > 50:  # More than 50% change
            volatile_categories.append((category, trend_data['trend_percentage']))
    
    patterns['peak_month'] = peak_month
    patterns['lowest_month'] = lowest_month
    patterns['peak_amount'] = monthly_totals.get(peak_month, 0) if peak_month else 0
    patterns['lowest_amount'] = monthly_totals.get(lowest_month, 0) if lowest_month else 0
    patterns['top_categories'] = top_categories
    patterns['volatile_categories'] = sorted(volatile_categories, key=lambda x: x[1], reverse=True)
    patterns['total_months_analyzed'] = len(monthly_data)
    
    return patterns


def print_analysis_results(monthly_data, trends, patterns):
    """Print comprehensive analysis results."""
    print("=" * 60)
    print("TRANSACTION SPENDING ANALYSIS REPORT")
    print("=" * 60)
    
    # Monthly totals summary
    print("\n📊 MONTHLY SPENDING TOTALS BY CATEGORY")
    print("-" * 40)
    
    sorted_months = sorted(monthly_data.keys())
    for month in sorted_months:
        print(f"\n{month}:")
        categories = monthly_data[month]
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        for category, amount in sorted_categories:
            print(f"  {category:<15}: ${amount:>8.2f}")
        
        month_total = sum(categories.values())
        print(f"  {'TOTAL':<15}: ${month_total:>8.2f}")
    
    # Trend analysis
    print("\n📈 SPENDING TRENDS ANALYSIS")
    print("-" * 40)