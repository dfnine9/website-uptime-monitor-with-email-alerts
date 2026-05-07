```python
"""
Personal Finance Expense Analysis Module

This module generates monthly spending breakdowns, calculates category percentages,
and produces matplotlib visualizations including pie charts and bar graphs for 
comprehensive expense analysis.

Features:
- Monthly expense categorization and analysis
- Percentage calculations for spending categories
- Interactive pie charts and bar graphs
- Sample data generation for demonstration
- Error handling and validation
- Self-contained implementation

Usage:
    python script.py

Dependencies: matplotlib (auto-installed if missing)
"""

import sys
import subprocess
import json
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Auto-install matplotlib if not available
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
except ImportError:
    print("Installing matplotlib...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

class ExpenseAnalyzer:
    """Analyzes and visualizes personal expense data."""
    
    def __init__(self):
        self.expenses = []
        self.categories = [
            'Housing', 'Food', 'Transportation', 'Utilities', 'Healthcare',
            'Entertainment', 'Shopping', 'Insurance', 'Savings', 'Other'
        ]
    
    def generate_sample_data(self, months=6):
        """Generate sample expense data for demonstration."""
        try:
            base_date = datetime.now() - timedelta(days=30 * months)
            
            category_ranges = {
                'Housing': (800, 1500),
                'Food': (300, 600),
                'Transportation': (200, 400),
                'Utilities': (100, 300),
                'Healthcare': (50, 200),
                'Entertainment': (100, 300),
                'Shopping': (150, 400),
                'Insurance': (200, 500),
                'Savings': (300, 800),
                'Other': (50, 200)
            }
            
            for month_offset in range(months):
                current_date = base_date + timedelta(days=30 * month_offset)
                month_str = current_date.strftime('%Y-%m')
                
                for category in self.categories:
                    min_amount, max_amount = category_ranges[category]
                    num_transactions = random.randint(3, 8)
                    
                    for _ in range(num_transactions):
                        amount = round(random.uniform(min_amount/num_transactions, max_amount/num_transactions), 2)
                        self.expenses.append({
                            'date': current_date.strftime('%Y-%m-%d'),
                            'month': month_str,
                            'category': category,
                            'amount': amount,
                            'description': f'{category} expense'
                        })
            
            print(f"Generated {len(self.expenses)} sample transactions across {months} months")
            return True
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return False
    
    def calculate_monthly_breakdown(self):
        """Calculate monthly spending breakdown by category."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for expense in self.expenses:
                month = expense['month']
                category = expense['category']
                amount = expense['amount']
                monthly_data[month][category] += amount
            
            return dict(monthly_data)
            
        except Exception as e:
            print(f"Error calculating monthly breakdown: {e}")
            return {}
    
    def calculate_category_percentages(self, monthly_data):
        """Calculate percentage breakdown for each month."""
        try:
            percentages = {}
            
            for month, categories in monthly_data.items():
                total_month = sum(categories.values())
                if total_month > 0:
                    percentages[month] = {
                        category: round((amount / total_month) * 100, 1)
                        for category, amount in categories.items()
                    }
                else:
                    percentages[month] = {}
            
            return percentages
            
        except Exception as e:
            print(f"Error calculating percentages: {e}")
            return {}
    
    def print_analysis(self, monthly_data, percentages):
        """Print detailed expense analysis to stdout."""
        try:
            print("\n" + "="*60)
            print("MONTHLY EXPENSE ANALYSIS")
            print("="*60)
            
            for month in sorted(monthly_data.keys()):
                categories = monthly_data[month]
                month_total = sum(categories.values())
                
                print(f"\n📅 {month}")
                print(f"Total Spending: ${month_total:,.2f}")
                print("-" * 40)
                
                # Sort categories by amount (descending)
                sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
                
                for category, amount in sorted_categories:
                    if amount > 0:
                        percentage = percentages[month].get(category, 0)
                        print(f"{category:<15} ${amount:>8,.2f} ({percentage:>5.1f}%)")
            
            # Overall summary
            total_all_months = sum(sum(cats.values()) for cats in monthly_data.values())
            avg_monthly = total_all_months / len(monthly_data) if monthly_data else 0
            
            print(f"\n{'='*60}")
            print("SUMMARY")
            print(f"{'='*60}")
            print(f"Total Expenses: ${total_all_months:,.2f}")
            print(f"Average Monthly: ${avg_monthly:,.2f}")
            print(f"Analysis Period: {len(monthly_data)} months")
            
        except Exception as e:
            print(f"Error printing analysis: {e}")
    
    def create_pie_chart(self, monthly_data, month=None):
        """Create pie chart for specified month or latest month."""
        try:
            if not monthly_data:
                print("No data available for pie chart")
                return
            
            # Use specified month or latest month
            if month is None:
                month = max(monthly_data.keys())
            
            if month not in monthly_data:
                print(f"No data found for month: {month}")
                return
            
            categories = monthly_data[month]
            labels = []
            amounts = []
            colors = plt.cm.Set3(range(len(categories)))
            
            for category, amount in categories.items():
                if amount > 0:
                    labels.append(category)
                    amounts.append(amount)
            
            if not amounts:
                print(f"No expenses found for {month}")
                return
            
            fig, ax = plt.subplots(figsize=(10, 8))
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=labels, 
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            
            # Enhance text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
            
            ax.set_title(f'Expense Breakdown - {month}', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(f'expenses_pie_{month.replace("-", "_")}.png', dpi=300, bbox_inches='tight')
            print(f"Pie chart saved as: expenses_pie_{month.replace('-', '_')}.png")
            plt.show()
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
    
    def create_bar_chart(self, monthly_data):
        """Create bar chart comparing categories across months."""
        try:
            if not monthly_data:
                print("No data available for bar chart")
                return
            
            months = sorted(monthly_data.keys())
            categories = self.categories
            
            # Prepare data
            category_data = {cat: [] for cat in categories}
            
            for month in