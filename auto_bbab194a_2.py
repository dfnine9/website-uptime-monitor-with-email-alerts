```python
"""
Transaction Data Analysis Script

This script processes categorized financial transaction data to generate comprehensive
monthly spending insights. It calculates category totals, identifies spending trends,
and creates visualizations to help understand spending patterns.

Features:
- Processes transaction data with date, amount, and category information
- Calculates monthly spending totals by category
- Identifies spending trends over time
- Generates visualizations using matplotlib
- Provides summary statistics and insights

Usage: python script.py

Dependencies: matplotlib (for visualization)
Note: Sample data is generated internally for demonstration purposes.
"""

import json
import csv
import io
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import calendar
import statistics

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Visualizations will be skipped.")

def generate_sample_data():
    """Generate sample transaction data for analysis."""
    import random
    
    categories = ['Groceries', 'Utilities', 'Entertainment', 'Transportation', 
                  'Healthcare', 'Dining', 'Shopping', 'Bills', 'Gas', 'Insurance']
    
    transactions = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(500):
        # Generate random date within the year
        days_offset = random.randint(0, 365)
        transaction_date = start_date + timedelta(days=days_offset)
        
        # Generate random amount based on category
        category = random.choice(categories)
        if category in ['Groceries', 'Utilities', 'Bills']:
            amount = round(random.uniform(50, 300), 2)
        elif category in ['Entertainment', 'Dining']:
            amount = round(random.uniform(15, 150), 2)
        elif category in ['Transportation', 'Gas']:
            amount = round(random.uniform(25, 100), 2)
        else:
            amount = round(random.uniform(10, 200), 2)
        
        transactions.append({
            'date': transaction_date.strftime('%Y-%m-%d'),
            'amount': amount,
            'category': category,
            'description': f"{category} transaction {i+1}"
        })
    
    return transactions

def parse_date(date_string):
    """Parse date string in various formats."""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(date_string, '%m/%d/%Y')
        except ValueError:
            try:
                return datetime.strptime(date_string, '%d/%m/%Y')
            except ValueError:
                raise ValueError(f"Unable to parse date: {date_string}")

def process_transactions(transactions):
    """Process transaction data and calculate insights."""
    try:
        monthly_data = defaultdict(lambda: defaultdict(float))
        category_totals = defaultdict(float)
        monthly_totals = defaultdict(float)
        
        for transaction in transactions:
            try:
                date = parse_date(transaction['date'])
                amount = float(transaction['amount'])
                category = transaction['category']
                
                month_key = date.strftime('%Y-%m')
                monthly_data[month_key][category] += amount
                category_totals[category] += amount
                monthly_totals[month_key] += amount
                
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping invalid transaction: {e}")
                continue
        
        return monthly_data, category_totals, monthly_totals
    
    except Exception as e:
        print(f"Error processing transactions: {e}")
        return {}, {}, {}

def calculate_trends(monthly_data):
    """Calculate spending trends for each category."""
    trends = {}
    
    try:
        for category in set().union(*[data.keys() for data in monthly_data.values()]):
            amounts = []
            months = sorted(monthly_data.keys())
            
            for month in months:
                amounts.append(monthly_data[month].get(category, 0))
            
            if len(amounts) > 1:
                # Calculate simple trend (positive = increasing, negative = decreasing)
                trend = (amounts[-1] - amounts[0]) / len(amounts) if amounts[0] != 0 else 0
                avg_amount = statistics.mean(amounts)
                trends[category] = {
                    'trend': trend,
                    'average': avg_amount,
                    'total_months': len(amounts),
                    'amounts': amounts
                }
        
        return trends
    
    except Exception as e:
        print(f"Error calculating trends: {e}")
        return {}

def print_summary(category_totals, monthly_totals, trends):
    """Print summary statistics."""
    try:
        print("\n" + "="*60)
        print("SPENDING ANALYSIS SUMMARY")
        print("="*60)
        
        # Category totals
        print("\nTOP SPENDING CATEGORIES:")
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        for i, (category, total) in enumerate(sorted_categories[:10], 1):
            percentage = (total / sum(category_totals.values())) * 100
            print(f"{i:2d}. {category:<15} ${total:>8.2f} ({percentage:5.1f}%)")
        
        # Monthly overview
        print("\nMONTHLY SPENDING OVERVIEW:")
        sorted_months = sorted(monthly_totals.items())
        for month, total in sorted_months[-6:]:  # Last 6 months
            month_name = datetime.strptime(month, '%Y-%m').strftime('%B %Y')
            print(f"{month_name:<15} ${total:>8.2f}")
        
        # Trends
        print("\nSPENDING TRENDS:")
        trend_categories = sorted(trends.items(), key=lambda x: abs(x[1]['trend']), reverse=True)
        for category, trend_data in trend_categories[:5]:
            trend_direction = "↑" if trend_data['trend'] > 0 else "↓" if trend_data['trend'] < 0 else "→"
            print(f"{category:<15} {trend_direction} ${trend_data['average']:>7.2f} avg/month")
        
        # Overall statistics
        total_spent = sum(category_totals.values())
        avg_monthly = sum(monthly_totals.values()) / len(monthly_totals) if monthly_totals else 0
        print(f"\nTOTAL SPENT: ${total_spent:.2f}")
        print(f"AVERAGE MONTHLY: ${avg_monthly:.2f}")
        print(f"ANALYSIS PERIOD: {len(monthly_totals)} months")
        
    except Exception as e:
        print(f"Error printing summary: {e}")

def create_visualizations(monthly_data, category_totals, monthly_totals):
    """Create visualizations using matplotlib."""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available. Skipping visualizations.")
        return
    
    try:
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Transaction Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Category totals pie chart
        categories = list(category_totals.keys())[:8]  # Top 8 categories
        amounts = [category_totals[cat] for cat in categories]
        other_amount = sum(category_totals.values()) - sum(amounts)
        
        if other_amount > 0:
            categories.append('Other')
            amounts.append(other_amount)
        
        ax1.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Spending by Category')