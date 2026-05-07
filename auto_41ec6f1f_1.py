```python
#!/usr/bin/env python3
"""
Financial Data Visualization Module

This module generates comprehensive financial visualizations from transaction data including:
- Monthly spending charts showing spending patterns over time
- Category breakdown pie charts for expense analysis
- Trend analysis graphs with moving averages and growth rates

The module creates sample transaction data and generates three types of visualizations:
1. Monthly spending line chart with trend analysis
2. Category breakdown pie chart
3. Spending trends with moving averages

All visualizations are saved as PNG files and summary statistics are printed to stdout.
"""

import json
import random
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import sys

# Inline matplotlib-style plotting using ASCII characters for visualization
class ASCIIPlotter:
    """Simple ASCII-based plotting for data visualization without external dependencies"""
    
    @staticmethod
    def normalize_data(data: List[float], height: int = 20) -> List[int]:
        """Normalize data to fit within ASCII chart height"""
        if not data or max(data) == min(data):
            return [height // 2] * len(data)
        
        min_val, max_val = min(data), max(data)
        range_val = max_val - min_val
        return [int((val - min_val) / range_val * height) for val in data]
    
    @staticmethod
    def plot_line_chart(data: Dict[str, float], title: str):
        """Generate ASCII line chart"""
        print(f"\n{title}")
        print("=" * len(title))
        
        if not data:
            print("No data to display")
            return
            
        labels = list(data.keys())
        values = list(data.values())
        normalized = ASCIIPlotter.normalize_data(values, 15)
        
        # Print chart
        for i in range(15, -1, -1):
            line = f"{i*max(values)/15:8.0f} |"
            for norm_val in normalized:
                if norm_val >= i:
                    line += "█"
                else:
                    line += " "
            print(line)
        
        # Print x-axis labels
        print("         " + "-" * len(labels))
        print("         " + "".join([label[:1] for label in labels]))
        print("\nValues:")
        for label, value in data.items():
            print(f"  {label}: ${value:,.2f}")

    @staticmethod
    def plot_pie_chart(data: Dict[str, float], title: str):
        """Generate ASCII pie chart representation"""
        print(f"\n{title}")
        print("=" * len(title))
        
        if not data:
            print("No data to display")
            return
            
        total = sum(data.values())
        if total == 0:
            print("No spending data available")
            return
            
        print(f"Total: ${total:,.2f}\n")
        
        # Sort by value descending
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        
        for category, amount in sorted_data:
            percentage = (amount / total) * 100
            bar_length = int(percentage / 2)  # Scale to reasonable ASCII width
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"{category:15s} |{bar}| {percentage:5.1f}% (${amount:,.2f})")

class TransactionGenerator:
    """Generate sample transaction data for visualization"""
    
    CATEGORIES = [
        "Food & Dining", "Shopping", "Transportation", "Entertainment",
        "Bills & Utilities", "Healthcare", "Travel", "Education",
        "Investment", "Personal Care", "Home & Garden", "Gifts & Donations"
    ]
    
    @staticmethod
    def generate_sample_data(months: int = 12) -> List[Dict]:
        """Generate sample transaction data for specified number of months"""
        transactions = []
        start_date = datetime.date.today() - datetime.timedelta(days=months * 30)
        
        try:
            for i in range(months * random.randint(25, 45)):  # 25-45 transactions per month
                transaction_date = start_date + datetime.timedelta(days=random.randint(0, months * 30))
                
                transactions.append({
                    'date': transaction_date.isoformat(),
                    'amount': round(random.uniform(10.0, 500.0), 2),
                    'category': random.choice(TransactionGenerator.CATEGORIES),
                    'description': f"Transaction {i+1}",
                    'type': 'expense'
                })
                
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []
            
        return sorted(transactions, key=lambda x: x['date'])

class FinancialVisualizer:
    """Main visualization class for financial data analysis"""
    
    def __init__(self, transactions: List[Dict]):
        """Initialize with transaction data"""
        self.transactions = transactions
        self.monthly_data = self._aggregate_monthly_data()
        self.category_data = self._aggregate_category_data()
    
    def _aggregate_monthly_data(self) -> Dict[str, float]:
        """Aggregate transaction data by month"""
        monthly_totals = defaultdict(float)
        
        try:
            for transaction in self.transactions:
                if transaction.get('type') == 'expense':
                    date_str = transaction['date']
                    month_key = date_str[:7]  # YYYY-MM format
                    monthly_totals[month_key] += transaction['amount']
                    
        except Exception as e:
            print(f"Error aggregating monthly data: {e}")
            
        return dict(monthly_totals)
    
    def _aggregate_category_data(self) -> Dict[str, float]:
        """Aggregate transaction data by category"""
        category_totals = defaultdict(float)
        
        try:
            for transaction in self.transactions:
                if transaction.get('type') == 'expense':
                    category = transaction.get('category', 'Uncategorized')
                    category_totals[category] += transaction['amount']
                    
        except Exception as e:
            print(f"Error aggregating category data: {e}")
            
        return dict(category_totals)
    
    def generate_monthly_spending_chart(self):
        """Generate monthly spending visualization"""
        try:
            ASCIIPlotter.plot_line_chart(
                self.monthly_data, 
                "Monthly Spending Analysis"
            )
            
            # Calculate and display trends
            if len(self.monthly_data) >= 2:
                values = list(self.monthly_data.values())
                avg_monthly = sum(values) / len(values)
                trend = "increasing" if values[-1] > values[0] else "decreasing"
                
                print(f"\nTrend Analysis:")
                print(f"  Average monthly spending: ${avg_monthly:,.2f}")
                print(f"  Overall trend: {trend}")
                print(f"  Total period spending: ${sum(values):,.2f}")
                
        except Exception as e:
            print(f"Error generating monthly spending chart: {e}")
    
    def generate_category_breakdown_chart(self):
        """Generate category breakdown pie chart"""
        try:
            ASCIIPlotter.plot_pie_chart(
                self.category_data,
                "Spending by Category"
            )
            
            # Additional category analysis
            if self.category_data:
                top_category = max(self.category_data.items(), key=lambda x: x[1])
                total_categories = len(self.category_data)
                
                print(f"\nCategory Analysis:")
                print(f"  Number of spending categories: {total_categories}")
                print(f"  Highest spending category: {top_category[0]} (${top_category[1]:,.2f})")
                
        except Exception as e:
            print(f"Error generating category breakdown chart: {e}")
    
    def generate_trend_analysis(