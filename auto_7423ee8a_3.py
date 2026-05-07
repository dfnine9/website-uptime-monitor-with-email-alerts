```python
"""
Personal Finance Dashboard Generator

This module creates an interactive financial dashboard using matplotlib to visualize:
- Monthly spending by category
- Trend analysis over time
- Budget vs actual spending comparisons
- Exportable financial summary reports

The dashboard uses sample financial data and generates static visualizations
that can be saved as PNG files for sharing and reporting.

Usage: python script.py
"""

import json
import datetime
import random
from typing import Dict, List, Tuple, Any
import os

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
except ImportError:
    print("Error: matplotlib not available. Install with: pip install matplotlib")
    exit(1)

class FinanceDashboard:
    """Interactive finance dashboard generator with visualization capabilities."""
    
    def __init__(self):
        self.data = self._generate_sample_data()
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                          'Healthcare', 'Shopping', 'Insurance', 'Rent']
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', 
                      '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
        
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate realistic sample financial data for the last 12 months."""
        try:
            data = {
                'transactions': [],
                'budgets': {},
                'monthly_totals': {}
            }
            
            base_date = datetime.datetime.now() - datetime.timedelta(days=365)
            
            # Generate monthly data
            for month in range(12):
                current_date = base_date + datetime.timedelta(days=month*30)
                month_key = current_date.strftime('%Y-%m')
                
                # Generate budget data
                data['budgets'][month_key] = {
                    'Food': random.randint(400, 600),
                    'Transportation': random.randint(200, 300),
                    'Entertainment': random.randint(150, 250),
                    'Utilities': random.randint(100, 200),
                    'Healthcare': random.randint(50, 150),
                    'Shopping': random.randint(200, 400),
                    'Insurance': random.randint(150, 250),
                    'Rent': random.randint(800, 1200)
                }
                
                # Generate transaction data
                month_spending = {}
                for category in self.categories:
                    budget = data['budgets'][month_key][category]
                    # Actual spending varies from 70% to 130% of budget
                    actual = int(budget * random.uniform(0.7, 1.3))
                    month_spending[category] = actual
                    
                    # Generate individual transactions
                    remaining = actual
                    while remaining > 0:
                        amount = min(random.randint(10, min(100, remaining)), remaining)
                        transaction_date = current_date + datetime.timedelta(days=random.randint(0, 29))
                        data['transactions'].append({
                            'date': transaction_date.strftime('%Y-%m-%d'),
                            'category': category,
                            'amount': amount,
                            'description': f"{category} expense"
                        })
                        remaining -= amount
                
                data['monthly_totals'][month_key] = month_spending
                
            return data
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {'transactions': [], 'budgets': {}, 'monthly_totals': {}}
    
    def create_spending_by_category_chart(self) -> None:
        """Create a pie chart showing total spending by category."""
        try:
            # Calculate total spending by category
            category_totals = {}
            for month_data in self.data['monthly_totals'].values():
                for category, amount in month_data.items():
                    category_totals[category] = category_totals.get(category, 0) + amount
            
            # Create pie chart
            fig, ax = plt.subplots(figsize=(10, 8))
            wedges, texts, autotexts = ax.pie(
                category_totals.values(),
                labels=category_totals.keys(),
                colors=self.colors,
                autopct='%1.1f%%',
                startangle=90,
                explode=[0.05 if cat == 'Rent' else 0 for cat in category_totals.keys()]
            )
            
            ax.set_title('Total Spending by Category (Last 12 Months)', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Add total amount to legend
            total_spent = sum(category_totals.values())
            ax.text(0, -1.3, f'Total Spending: ${total_spent:,.2f}', 
                   ha='center', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            plt.savefig('spending_by_category.png', dpi=300, bbox_inches='tight')
            plt.show()
            print("✓ Spending by category chart created and saved as 'spending_by_category.png'")
            
        except Exception as e:
            print(f"Error creating spending by category chart: {e}")
    
    def create_trend_analysis(self) -> None:
        """Create line chart showing spending trends over time."""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Prepare data
            months = sorted(self.data['monthly_totals'].keys())
            dates = [datetime.datetime.strptime(m, '%Y-%m') for m in months]
            
            # Top chart: Total monthly spending
            monthly_totals = [sum(self.data['monthly_totals'][m].values()) for m in months]
            ax1.plot(dates, monthly_totals, marker='o', linewidth=2, markersize=6, color='#2E86AB')
            ax1.fill_between(dates, monthly_totals, alpha=0.3, color='#2E86AB')
            ax1.set_title('Monthly Total Spending Trend', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Amount ($)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            
            # Bottom chart: Category trends
            for i, category in enumerate(['Food', 'Transportation', 'Entertainment', 'Rent']):
                values = [self.data['monthly_totals'][m][category] for m in months]
                ax2.plot(dates, values, marker='o', label=category, 
                        color=self.colors[i], linewidth=2)
            
            ax2.set_title('Category Spending Trends', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Month', fontsize=12)
            ax2.set_ylabel('Amount ($)', fontsize=12)
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            
            plt.tight_layout()
            plt.xticks(rotation=45)
            plt.savefig('spending_trends.png', dpi=300, bbox_inches='tight')
            plt.show()
            print("✓ Spending trends chart created and saved as 'spending_trends.png'")
            
        except Exception as e:
            print(f"Error creating trend analysis: {e}")
    
    def create_budget