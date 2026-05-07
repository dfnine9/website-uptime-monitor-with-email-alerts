```python
#!/usr/bin/env python3
"""
Monthly Spending Reports Data Visualization Module

This module generates comprehensive monthly spending reports with interactive visualizations including:
- Category breakdown pie charts
- Monthly spending trends over time
- Budget vs actual spending comparisons
- Spending pattern analysis

The module creates sample financial data and generates various charts to help analyze spending habits.
Uses matplotlib for static visualizations and includes error handling for robust operation.

Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch
except ImportError:
    print("Error: matplotlib not found. Install with: pip install matplotlib")
    sys.exit(1)

class SpendingReportGenerator:
    """Generates monthly spending reports with visualizations."""
    
    def __init__(self):
        self.categories = [
            'Housing', 'Food', 'Transportation', 'Utilities', 
            'Entertainment', 'Healthcare', 'Shopping', 'Savings'
        ]
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
            '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ]
        
    def generate_sample_data(self, months: int = 12) -> Dict:
        """Generate sample spending data for the specified number of months."""
        try:
            data = {
                'monthly_data': [],
                'budgets': {},
                'transactions': []
            }
            
            # Set budgets for each category
            base_budgets = {
                'Housing': 1200, 'Food': 600, 'Transportation': 400,
                'Utilities': 200, 'Entertainment': 300, 'Healthcare': 250,
                'Shopping': 400, 'Savings': 500
            }
            data['budgets'] = base_budgets
            
            # Generate monthly data
            start_date = datetime.now() - timedelta(days=30 * months)
            
            for month_offset in range(months):
                current_date = start_date + timedelta(days=30 * month_offset)
                month_name = current_date.strftime('%B %Y')
                
                monthly_spending = {}
                monthly_total = 0
                
                for category in self.categories:
                    # Add some randomness to spending (80-120% of budget)
                    variance = random.uniform(0.6, 1.4)
                    amount = base_budgets[category] * variance
                    monthly_spending[category] = round(amount, 2)
                    monthly_total += amount
                
                data['monthly_data'].append({
                    'month': month_name,
                    'date': current_date,
                    'spending': monthly_spending,
                    'total': round(monthly_total, 2)
                })
                
                # Generate individual transactions
                for category in self.categories:
                    num_transactions = random.randint(3, 12)
                    category_total = monthly_spending[category]
                    
                    for _ in range(num_transactions):
                        transaction_amount = category_total / num_transactions * random.uniform(0.5, 2)
                        transaction_date = current_date + timedelta(days=random.randint(0, 29))
                        
                        data['transactions'].append({
                            'date': transaction_date,
                            'category': category,
                            'amount': round(transaction_amount, 2),
                            'description': f"{category} expense"
                        })
            
            return data
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}

    def create_category_breakdown_chart(self, data: Dict, month_index: int = -1) -> None:
        """Create a pie chart showing spending breakdown by category for a specific month."""
        try:
            if not data['monthly_data']:
                print("No data available for category breakdown")
                return
                
            month_data = data['monthly_data'][month_index]
            spending = month_data['spending']
            
            # Prepare data for pie chart
            categories = list(spending.keys())
            amounts = list(spending.values())
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=categories,
                autopct='%1.1f%%',
                colors=self.colors[:len(categories)],
                startangle=90,
                explode=[0.05] * len(categories)
            )
            
            # Customize appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title(f'Spending Breakdown - {month_data["month"]}', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Add legend with amounts
            legend_labels = [f'{cat}: ${amt:,.2f}' for cat, amt in zip(categories, amounts)]
            ax.legend(wedges, legend_labels, title="Categories", 
                     loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            plt.show()
            print(f"Category breakdown chart generated for {month_data['month']}")
            
        except Exception as e:
            print(f"Error creating category breakdown chart: {e}")

    def create_spending_trends_chart(self, data: Dict) -> None:
        """Create a line chart showing spending trends over time."""
        try:
            if not data['monthly_data']:
                print("No data available for spending trends")
                return
                
            months = [item['month'] for item in data['monthly_data']]
            dates = [item['date'] for item in data['monthly_data']]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Plot trend line for each category
            for i, category in enumerate(self.categories):
                amounts = [item['spending'][category] for item in data['monthly_data']]
                ax.plot(dates, amounts, marker='o', linewidth=2, 
                       label=category, color=self.colors[i])
            
            # Customize chart
            ax.set_title('Monthly Spending Trends by Category', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Amount ($)', fontsize=12)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            # Add grid and legend
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            plt.show()
            print("Spending trends chart generated successfully")
            
        except Exception as e:
            print(f"Error creating spending trends chart: {e}")

    def create_budget_vs_actual_chart(self, data: Dict) -> None:
        """Create a bar chart comparing budget vs actual spending."""
        try:
            if not data['monthly_data'] or not data['budgets']:
                print("No data available for budget comparison")
                return
                
            # Calculate average actual spending per category
            avg_spending = {}
            for category in self.categories:
                total = sum(item['spending'][category] for item in data['monthly_data'])
                avg_spending[category] = total / len(data['monthly_data'])
            
            categories = list(data['budgets'].keys())
            budget_amounts = list(data['budgets'].values())
            actual_amounts = [avg