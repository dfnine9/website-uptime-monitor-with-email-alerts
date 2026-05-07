```python
#!/usr/bin/env python3
"""
Financial Data Visualization Module

This module generates comprehensive financial visualizations including:
- Spending breakdown by category (pie chart)
- Monthly spending trends (line chart)
- Budget vs actual comparisons (bar chart)

Uses matplotlib for visualization with sample financial data.
Self-contained with minimal dependencies.

Usage: python script.py
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple

class FinancialVisualizer:
    """Generates financial charts and visualizations"""
    
    def __init__(self):
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> Dict:
        """Generate realistic sample financial data"""
        categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 
                     'Healthcare', 'Utilities', 'Shopping', 'Savings']
        
        # Generate 12 months of data
        monthly_data = []
        base_date = datetime.now().replace(day=1) - timedelta(days=365)
        
        for i in range(12):
            month_date = base_date + timedelta(days=30*i)
            month_spending = {}
            
            for category in categories:
                # Generate realistic spending amounts
                base_amounts = {
                    'Housing': 1200, 'Food': 400, 'Transportation': 300,
                    'Entertainment': 200, 'Healthcare': 150, 'Utilities': 250,
                    'Shopping': 300, 'Savings': 500
                }
                
                # Add some variance
                variance = random.uniform(0.8, 1.2)
                amount = base_amounts[category] * variance
                month_spending[category] = round(amount, 2)
            
            monthly_data.append({
                'month': month_date.strftime('%Y-%m'),
                'spending': month_spending
            })
        
        # Generate budget data
        budget_data = {
            'Housing': 1300, 'Food': 450, 'Transportation': 350,
            'Entertainment': 250, 'Healthcare': 200, 'Utilities': 280,
            'Shopping': 400, 'Savings': 600
        }
        
        return {
            'monthly_data': monthly_data,
            'budget': budget_data
        }
    
    def create_category_breakdown(self) -> None:
        """Create pie chart showing spending breakdown by category"""
        try:
            # Calculate total spending by category (last month)
            last_month = self.sample_data['monthly_data'][-1]['spending']
            
            categories = list(last_month.keys())
            amounts = list(last_month.values())
            
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(range(len(categories)))
            
            wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%',
                                              colors=colors, startangle=90)
            
            # Enhance text formatting
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.title('Spending Breakdown by Category (Current Month)', fontsize=16, fontweight='bold')
            plt.axis('equal')
            
            # Add total spending annotation
            total = sum(amounts)
            plt.figtext(0.02, 0.02, f'Total Spending: ${total:,.2f}', fontsize=10, style='italic')
            
            plt.tight_layout()
            plt.savefig('category_breakdown.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("✓ Category breakdown chart saved as 'category_breakdown.png'")
            print(f"  Total spending: ${total:,.2f}")
            
        except Exception as e:
            print(f"✗ Error creating category breakdown: {str(e)}")
    
    def create_monthly_trends(self) -> None:
        """Create line chart showing monthly spending trends"""
        try:
            months = []
            category_trends = {}
            
            # Prepare data
            for month_data in self.sample_data['monthly_data']:
                months.append(month_data['month'])
                
                for category, amount in month_data['spending'].items():
                    if category not in category_trends:
                        category_trends[category] = []
                    category_trends[category].append(amount)
            
            plt.figure(figsize=(14, 8))
            
            # Plot trends for each category
            colors = plt.cm.tab10(range(len(category_trends)))
            
            for i, (category, amounts) in enumerate(category_trends.items()):
                plt.plot(months, amounts, marker='o', linewidth=2, 
                        label=category, color=colors[i], markersize=4)
            
            plt.title('Monthly Spending Trends by Category', fontsize=16, fontweight='bold')
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            # Format y-axis as currency
            ax = plt.gca()
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            plt.tight_layout()
            plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("✓ Monthly trends chart saved as 'monthly_trends.png'")
            
        except Exception as e:
            print(f"✗ Error creating monthly trends: {str(e)}")
    
    def create_budget_comparison(self) -> None:
        """Create bar chart comparing budget vs actual spending"""
        try:
            # Use last month's actual spending
            actual_spending = self.sample_data['monthly_data'][-1]['spending']
            budget = self.sample_data['budget']
            
            categories = list(budget.keys())
            budget_amounts = [budget[cat] for cat in categories]
            actual_amounts = [actual_spending[cat] for cat in categories]
            
            # Calculate variance
            variances = [(actual - budget[cat])/budget[cat] * 100 
                        for cat, actual in actual_spending.items()]
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Budget vs Actual comparison
            x = range(len(categories))
            width = 0.35
            
            bars1 = ax1.bar([i - width/2 for i in x], budget_amounts, width, 
                           label='Budget', color='lightblue', alpha=0.8)
            bars2 = ax1.bar([i + width/2 for i in x], actual_amounts, width,
                           label='Actual', color='coral', alpha=0.8)
            
            ax1.set_title('Budget vs Actual Spending Comparison', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Category')
            ax1.set_ylabel('Amount ($)')
            ax1.set_xticks(x)
            ax1.set_xticklabels(categories, rotation=45, ha='right')
            ax1.legend()
            ax1.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}', ha='center', va='bottom', fontsize=8)
            
            for bar in bars2:
                height =