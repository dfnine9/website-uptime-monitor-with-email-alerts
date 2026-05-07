```python
"""
Transaction Analysis and Visualization Script

This module processes categorized financial transactions to generate comprehensive
monthly spending summaries. It calculates category totals, percentages, and creates
visualization charts to help understand spending patterns.

Features:
- Monthly spending summary generation
- Category-wise total and percentage calculations
- Data validation and error handling
- Visualization charts using matplotlib
- Self-contained with minimal dependencies

Usage:
    python script.py

The script generates sample transaction data and produces:
1. Monthly spending summaries printed to stdout
2. Category totals and percentages
3. Visualization charts (pie chart and bar chart)
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import random

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Charts will not be generated.")

def generate_sample_data() -> List[Dict[str, Any]]:
    """Generate sample transaction data for demonstration."""
    categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
    transactions = []
    
    # Generate transactions for last 6 months
    base_date = datetime.now() - timedelta(days=180)
    
    for i in range(150):
        date = base_date + timedelta(days=random.randint(0, 180))
        transaction = {
            'date': date.strftime('%Y-%m-%d'),
            'amount': round(random.uniform(10, 500), 2),
            'category': random.choice(categories),
            'description': f"Transaction {i+1}"
        }
        transactions.append(transaction)
    
    return transactions

def parse_transaction_date(date_str: str) -> datetime:
    """Parse transaction date string to datetime object."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            raise ValueError(f"Unable to parse date: {date_str}")

def process_transactions(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Process transactions and group by month and category.
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Dictionary with monthly data organized by category
    """
    monthly_data = defaultdict(lambda: defaultdict(float))
    
    try:
        for transaction in transactions:
            if not all(key in transaction for key in ['date', 'amount', 'category']):
                print(f"Warning: Skipping invalid transaction: {transaction}")
                continue
                
            date = parse_transaction_date(transaction['date'])
            month_key = date.strftime('%Y-%m')
            category = transaction['category']
            amount = float(transaction['amount'])
            
            monthly_data[month_key][category] += amount
            
    except (ValueError, TypeError) as e:
        print(f"Error processing transaction: {e}")
        
    return dict(monthly_data)

def calculate_category_totals(monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """Calculate total spending by category across all months."""
    category_totals = defaultdict(float)
    
    for month_data in monthly_data.values():
        for category, amount in month_data.items():
            category_totals[category] += amount
            
    return dict(category_totals)

def calculate_percentages(category_totals: Dict[str, float]) -> Dict[str, float]:
    """Calculate percentage of total spending for each category."""
    total_spending = sum(category_totals.values())
    
    if total_spending == 0:
        return {}
        
    percentages = {
        category: (amount / total_spending) * 100
        for category, amount in category_totals.items()
    }
    
    return percentages

def print_monthly_summary(monthly_data: Dict[str, Dict[str, float]]) -> None:
    """Print monthly spending summaries to stdout."""
    print("\n" + "="*60)
    print("MONTHLY SPENDING SUMMARIES")
    print("="*60)
    
    for month in sorted(monthly_data.keys()):
        month_data = monthly_data[month]
        month_total = sum(month_data.values())
        
        print(f"\n{month}:")
        print("-" * 40)
        
        for category in sorted(month_data.keys()):
            amount = month_data[category]
            percentage = (amount / month_total) * 100 if month_total > 0 else 0
            print(f"  {category:<15}: ${amount:>8.2f} ({percentage:>5.1f}%)")
            
        print(f"  {'TOTAL':<15}: ${month_total:>8.2f}")

def print_category_summary(category_totals: Dict[str, float], percentages: Dict[str, float]) -> None:
    """Print category totals and percentages to stdout."""
    print("\n" + "="*60)
    print("CATEGORY TOTALS AND PERCENTAGES")
    print("="*60)
    
    total_spending = sum(category_totals.values())
    
    print(f"\nTotal Spending: ${total_spending:.2f}")
    print("\nCategory Breakdown:")
    print("-" * 40)
    
    # Sort by amount (descending)
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    for category, amount in sorted_categories:
        percentage = percentages.get(category, 0)
        print(f"  {category:<15}: ${amount:>8.2f} ({percentage:>5.1f}%)")

def create_visualizations(category_totals: Dict[str, float]) -> None:
    """Create and display visualization charts."""
    if not MATPLOTLIB_AVAILABLE:
        print("\nVisualization skipped: matplotlib not available")
        return
        
    try:
        # Sort categories by amount
        sorted_items = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        categories, amounts = zip(*sorted_items)
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Pie chart
        ax1.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Spending by Category (Pie Chart)')
        
        # Bar chart
        bars = ax2.bar(categories, amounts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'])
        ax2.set_title('Spending by Category (Bar Chart)')
        ax2.set_ylabel('Amount ($)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.0f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
        
        print("\nVisualization charts displayed successfully!")
        
    except Exception as e:
        print(f"Error creating visualizations: {e}")

def main():
    """Main function to orchestrate the transaction analysis."""
    try:
        print("Transaction Analysis and Visualization")
        print("Generating sample transaction data...")
        
        # Generate or load transaction data
        transactions = generate_sample_data()
        print(f"Loaded {len(transactions)} transactions")
        
        # Process transactions
        print("Processing transactions...")
        monthly_data = process_transactions(transactions)
        
        if not monthly_data:
            print("No valid transactions found to process.")