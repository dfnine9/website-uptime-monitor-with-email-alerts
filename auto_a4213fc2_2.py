```python
"""
Expense Visualization Component

This module generates interactive charts showing:
1. Expense breakdowns by category (pie chart)
2. Monthly spending trends (line chart) 
3. Budget vs actual comparisons (bar chart)

Uses matplotlib for visualization with sample expense data.
Self-contained script with error handling and stdout output.

Usage: python script.py
"""

import json
import datetime
import random
from typing import Dict, List, Tuple, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Charts will not be generated.")

def generate_sample_data() -> Tuple[Dict[str, float], List[Dict[str, Any]], Dict[str, Dict[str, float]]]:
    """Generate sample expense data for demonstration."""
    try:
        # Category breakdown
        categories = {
            "Food & Dining": 1250.75,
            "Transportation": 890.50,
            "Shopping": 650.25,
            "Entertainment": 420.00,
            "Bills & Utilities": 980.30,
            "Healthcare": 320.15,
            "Travel": 1150.60
        }
        
        # Monthly trends (last 12 months)
        monthly_data = []
        base_date = datetime.datetime.now().replace(day=1)
        
        for i in range(12):
            month_date = base_date - datetime.timedelta(days=30 * i)
            total_spent = random.uniform(3000, 5500)
            monthly_data.append({
                "month": month_date.strftime("%Y-%m"),
                "amount": round(total_spent, 2)
            })
        
        monthly_data.reverse()  # Chronological order
        
        # Budget vs Actual
        budget_comparison = {
            "Food & Dining": {"budget": 1200.00, "actual": 1250.75},
            "Transportation": {"budget": 800.00, "actual": 890.50},
            "Shopping": {"budget": 600.00, "actual": 650.25},
            "Entertainment": {"budget": 500.00, "actual": 420.00},
            "Bills & Utilities": {"budget": 1000.00, "actual": 980.30},
            "Healthcare": {"budget": 400.00, "actual": 320.15},
            "Travel": {"budget": 1000.00, "actual": 1150.60}
        }
        
        return categories, monthly_data, budget_comparison
        
    except Exception as e:
        print(f"Error generating sample data: {e}")
        return {}, [], {}

def create_category_breakdown_chart(categories: Dict[str, float]) -> bool:
    """Create pie chart for expense breakdown by category."""
    try:
        if not categories or not MATPLOTLIB_AVAILABLE:
            return False
            
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Prepare data
        labels = list(categories.keys())
        sizes = list(categories.values())
        colors = plt.cm.Set3(range(len(labels)))
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                                         startangle=90, textprops={'fontsize': 9})
        
        ax.set_title('Expense Breakdown by Category', fontsize=16, fontweight='bold', pad=20)
        
        # Add legend with amounts
        legend_labels = [f"{label}: ${amount:,.2f}" for label, amount in categories.items()]
        ax.legend(wedges, legend_labels, title="Categories", loc="center left", 
                 bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        
        plt.tight_layout()
        plt.savefig('expense_breakdown.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✓ Category breakdown chart generated successfully")
        return True
        
    except Exception as e:
        print(f"Error creating category breakdown chart: {e}")
        return False

def create_monthly_trends_chart(monthly_data: List[Dict[str, Any]]) -> bool:
    """Create line chart for monthly spending trends."""
    try:
        if not monthly_data or not MATPLOTLIB_AVAILABLE:
            return False
            
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Prepare data
        months = [item["month"] for item in monthly_data]
        amounts = [item["amount"] for item in monthly_data]
        
        # Create line chart
        ax.plot(months, amounts, marker='o', linewidth=2, markersize=6, color='#2E86C1')
        ax.fill_between(months, amounts, alpha=0.3, color='#2E86C1')
        
        # Formatting
        ax.set_title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Amount Spent ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✓ Monthly trends chart generated successfully")
        return True
        
    except Exception as e:
        print(f"Error creating monthly trends chart: {e}")
        return False

def create_budget_vs_actual_chart(budget_data: Dict[str, Dict[str, float]]) -> bool:
    """Create bar chart comparing budget vs actual spending."""
    try:
        if not budget_data or not MATPLOTLIB_AVAILABLE:
            return False
            
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare data
        categories = list(budget_data.keys())
        budget_amounts = [budget_data[cat]["budget"] for cat in categories]
        actual_amounts = [budget_data[cat]["actual"] for cat in categories]
        
        # Create grouped bar chart
        x_pos = range(len(categories))
        width = 0.35
        
        bars1 = ax.bar([x - width/2 for x in x_pos], budget_amounts, width, 
                      label='Budget', color='#52BE80', alpha=0.8)
        bars2 = ax.bar([x + width/2 for x in x_pos], actual_amounts, width, 
                      label='Actual', color='#E74C3C', alpha=0.8)
        
        # Formatting
        ax.set_title('Budget vs Actual Spending by Category', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Categories', fontsize=12)
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add value labels on bars
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 10,
                       f'${height:,.0f}', ha='center', va='bottom', fontsize=8)
        
        add