```python
"""
Financial Data Visualization Module

This module creates comprehensive financial visualizations including:
- Spending breakdown by category (pie chart)
- Spending trends over time (line chart)
- Budget variance analysis (bar chart)

Uses matplotlib for visualization with sample financial data.
Includes error handling and is designed to be self-contained.

Usage: python script.py
"""

import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from collections import defaultdict
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("Please install matplotlib: pip install matplotlib")
    sys.exit(1)


class FinancialVisualizer:
    """Creates financial visualizations from spending data."""
    
    def __init__(self):
        self.sample_data = self._generate_sample_data()
        
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample financial data for demonstration."""
        categories = ['Food', 'Transportation', 'Housing', 'Entertainment', 'Utilities', 'Healthcare']
        
        # Generate spending data over last 12 months
        spending_data = []
        current_date = datetime.now() - timedelta(days=365)
        
        for i in range(365):
            date = current_date + timedelta(days=i)
            category = random.choice(categories)
            amount = random.uniform(10, 200)
            spending_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': round(amount, 2)
            })
        
        # Budget data
        budget_data = {
            'Food': 1500,
            'Transportation': 500,
            'Housing': 2000,
            'Entertainment': 400,
            'Utilities': 300,
            'Healthcare': 600
        }
        
        return {
            'spending': spending_data,
            'budget': budget_data
        }
    
    def create_category_pie_chart(self) -> None:
        """Create pie chart showing spending breakdown by category."""
        try:
            category_totals = defaultdict(float)
            
            for transaction in self.sample_data['spending']:
                category_totals[transaction['category']] += transaction['amount']
            
            categories = list(category_totals.keys())
            amounts = list(category_totals.values())
            
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(range(len(categories)))
            
            wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            
            plt.title('Spending by Category', fontsize=16, fontweight='bold')
            plt.axis('equal')
            
            # Add legend with amounts
            legend_labels = [f'{cat}: ${amt:,.2f}' for cat, amt in zip(categories, amounts)]
            plt.legend(wedges, legend_labels, title="Categories", loc="center left", 
                      bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            plt.savefig('spending_by_category.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✓ Category pie chart created successfully")
            
        except Exception as e:
            print(f"Error creating category pie chart: {e}")
    
    def create_trends_line_chart(self) -> None:
        """Create line chart showing spending trends over time."""
        try:
            # Group spending by month
            monthly_spending = defaultdict(float)
            
            for transaction in self.sample_data['spending']:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                monthly_spending[month_key] += transaction['amount']
            
            # Sort by date
            sorted_months = sorted(monthly_spending.keys())
            dates = [datetime.strptime(month, '%Y-%m') for month in sorted_months]
            amounts = [monthly_spending[month] for month in sorted_months]
            
            plt.figure(figsize=(12, 6))
            plt.plot(dates, amounts, marker='o', linewidth=2, markersize=6, color='#2E86AB')
            
            plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold')
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Total Spending ($)', fontsize=12)
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.xticks(rotation=45)
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig('spending_trends.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✓ Trends line chart created successfully")
            
        except Exception as e:
            print(f"Error creating trends line chart: {e}")
    
    def create_budget_variance_chart(self) -> None:
        """Create bar chart showing budget vs actual spending variance."""
        try:
            # Calculate actual spending by category
            category_spending = defaultdict(float)
            
            for transaction in self.sample_data['spending']:
                category_spending[transaction['category']] += transaction['amount']
            
            categories = list(self.sample_data['budget'].keys())
            budgets = [self.sample_data['budget'][cat] for cat in categories]
            actuals = [category_spending[cat] for cat in categories]
            variances = [actual - budget for actual, budget in zip(actuals, budgets)]
            
            x_pos = range(len(categories))
            
            plt.figure(figsize=(12, 8))
            
            # Create grouped bar chart
            width = 0.35
            plt.bar([x - width/2 for x in x_pos], budgets, width, 
                   label='Budget', color='#A8DADC', alpha=0.8)
            plt.bar([x + width/2 for x in x_pos], actuals, width, 
                   label='Actual', color='#457B9D', alpha=0.8)
            
            plt.title('Budget vs Actual Spending Analysis', fontsize=16, fontweight='bold')
            plt.xlabel('Categories', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.xticks(x_pos, categories, rotation=45, ha='right')
            plt.legend()
            
            # Add variance text
            for i, (variance, actual) in enumerate(zip(variances, actuals)):
                color = 'red' if variance > 0 else 'green'
                plt.text(i, actual + 50, f'{variance:+.0f}', 
                        ha='center', va='bottom', color=color, fontweight='bold')
            
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            plt.savefig('budget_variance.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            # Print variance summary
            print("\n📊 Budget Variance Analysis:")
            for cat, budget, actual, variance in zip(categories, budgets, actuals, variances):
                status = "OVER" if variance > 0 else "UNDER"
                print(f"{cat:15} | Budget: ${budget:8.2f} | Actual: ${actual:8.2f} | "
                      f"Variance: ${variance:+8.2f} ({status})")
            
            print("✓ Budget variance chart created successfully")
            
        except Exception as e:
            print(f"Error creating budget variance chart: