```python
"""
Monthly Spending Report Visualization Module

This module generates comprehensive monthly spending reports with charts and graphs
showing expense breakdowns by category and spending trends. It creates visual
representations of financial data to help users understand their spending patterns.

Features:
- Category-based expense breakdown charts
- Monthly spending trend analysis
- ASCII-based visualization (no external chart libraries required)
- Sample data generation for demonstration
- Error handling for data processing

Dependencies: Only Python standard library
Usage: python script.py
"""

import json
import random
import calendar
from datetime import datetime, timedelta
from collections import defaultdict
import sys


class SpendingReportGenerator:
    def __init__(self):
        self.categories = [
            "Food & Dining", "Transportation", "Shopping", "Entertainment",
            "Bills & Utilities", "Health & Fitness", "Travel", "Education"
        ]
        self.spending_data = []
    
    def generate_sample_data(self, months=6):
        """Generate sample spending data for demonstration"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            current_date = start_date
            while current_date <= end_date:
                # Generate 5-15 transactions per day
                num_transactions = random.randint(5, 15)
                
                for _ in range(num_transactions):
                    transaction = {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "category": random.choice(self.categories),
                        "amount": round(random.uniform(10, 300), 2),
                        "description": f"Sample transaction"
                    }
                    self.spending_data.append(transaction)
                
                current_date += timedelta(days=1)
            
            print(f"Generated {len(self.spending_data)} sample transactions")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            sys.exit(1)
    
    def process_data_by_category(self):
        """Process spending data by category"""
        try:
            category_totals = defaultdict(float)
            
            for transaction in self.spending_data:
                category_totals[transaction["category"]] += transaction["amount"]
            
            return dict(category_totals)
            
        except Exception as e:
            print(f"Error processing category data: {e}")
            return {}
    
    def process_data_by_month(self):
        """Process spending data by month"""
        try:
            monthly_totals = defaultdict(float)
            
            for transaction in self.spending_data:
                date_obj = datetime.strptime(transaction["date"], "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                monthly_totals[month_key] += transaction["amount"]
            
            return dict(monthly_totals)
            
        except Exception as e:
            print(f"Error processing monthly data: {e}")
            return {}
    
    def create_ascii_bar_chart(self, data, title, max_width=50):
        """Create ASCII bar chart"""
        try:
            if not data:
                print(f"\n{title}\nNo data available")
                return
            
            print(f"\n{title}")
            print("=" * len(title))
            
            max_value = max(data.values())
            
            for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
                bar_length = int((value / max_value) * max_width)
                bar = "█" * bar_length
                print(f"{label[:20]:20} │{bar:50}│ ${value:,.2f}")
            
            print()
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")
    
    def create_trend_chart(self, monthly_data, max_width=60):
        """Create ASCII trend chart for monthly data"""
        try:
            if not monthly_data:
                print("\nMonthly Spending Trends\nNo data available")
                return
            
            print("\nMonthly Spending Trends")
            print("=" * 22)
            
            sorted_months = sorted(monthly_data.keys())
            values = [monthly_data[month] for month in sorted_months]
            
            if not values:
                print("No trend data available")
                return
            
            max_value = max(values)
            min_value = min(values)
            value_range = max_value - min_value if max_value != min_value else 1
            
            # Create trend line
            trend_points = []
            for value in values:
                if value_range > 0:
                    normalized = int(((value - min_value) / value_range) * 10)
                else:
                    normalized = 5
                trend_points.append(normalized)
            
            # Display trend
            for i, month in enumerate(sorted_months):
                month_name = datetime.strptime(month + "-01", "%Y-%m-%d").strftime("%b %Y")
                value = monthly_data[month]
                
                # Create visual trend indicator
                trend_char = "█"
                trend_line = " " * trend_points[i] + trend_char
                
                print(f"{month_name:10} │{trend_line:12}│ ${value:,.2f}")
            
            print(f"\nRange: ${min_value:,.2f} - ${max_value:,.2f}")
            print()
            
        except Exception as e:
            print(f"Error creating trend chart: {e}")
    
    def calculate_statistics(self):
        """Calculate spending statistics"""
        try:
            if not self.spending_data:
                print("No data available for statistics")
                return
            
            total_spent = sum(transaction["amount"] for transaction in self.spending_data)
            avg_transaction = total_spent / len(self.spending_data)
            
            amounts = [transaction["amount"] for transaction in self.spending_data]
            amounts.sort()
            
            # Calculate median
            n = len(amounts)
            if n % 2 == 0:
                median = (amounts[n//2 - 1] + amounts[n//2]) / 2
            else:
                median = amounts[n//2]
            
            print("Spending Statistics")
            print("=" * 18)
            print(f"Total Transactions: {len(self.spending_data):,}")
            print(f"Total Spent: ${total_spent:,.2f}")
            print(f"Average Transaction: ${avg_transaction:.2f}")
            print(f"Median Transaction: ${median:.2f}")
            print(f"Largest Transaction: ${max(amounts):,.2f}")
            print(f"Smallest Transaction: ${min(amounts):,.2f}")
            print()
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
    
    def generate_report(self):
        """Generate complete spending report"""
        try:
            print("MONTHLY SPENDING REPORT")
            print("=" * 50)
            print(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Generate sample data
            self.generate_sample_data()
            
            # Calculate statistics
            self.calculate_statistics()
            
            # Process data
            category_data = self.process_data_by_category()
            monthly_data = self.process_data_by_month()
            
            # Create visualizations
            self.create_ascii_bar_chart(
                category_data, 
                "Spending Breakdown by Category"
            )
            
            self.create_trend_chart(monthly_data)
            
            # Top spending categories
            if category_data:
                top_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:3]
                print("Top 3 Spending Categories")
                print("=" * 25)
                for i, (category, amount) in enumerate(top_categories, 1):
                    percentage = (amount / sum(category_data