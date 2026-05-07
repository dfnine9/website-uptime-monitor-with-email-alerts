```python
"""
Monthly Budget Insights Generator

This module analyzes monthly budget data to provide comprehensive spending insights.
It calculates category totals, percentage breakdowns, and spending trends compared 
to previous months with ASCII-based data visualization charts.

Features:
- Category-wise spending analysis
- Percentage breakdown of expenses
- Month-over-month trend analysis
- ASCII bar charts for visualization
- Sample data generation for demonstration

Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any


class BudgetAnalyzer:
    """Analyzes budget data and generates insights with visualizations."""
    
    def __init__(self):
        self.transactions = []
        self.categories = [
            'Housing', 'Transportation', 'Food', 'Healthcare', 
            'Entertainment', 'Utilities', 'Shopping', 'Education'
        ]
    
    def generate_sample_data(self, months: int = 6) -> None:
        """Generate sample transaction data for demonstration."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            current_date = start_date
            while current_date <= end_date:
                # Generate 15-25 transactions per month
                transactions_per_month = random.randint(15, 25)
                
                for _ in range(transactions_per_month):
                    category = random.choice(self.categories)
                    
                    # Category-based amount ranges
                    amount_ranges = {
                        'Housing': (800, 2000),
                        'Transportation': (50, 400),
                        'Food': (20, 150),
                        'Healthcare': (30, 300),
                        'Entertainment': (15, 200),
                        'Utilities': (50, 250),
                        'Shopping': (25, 300),
                        'Education': (100, 500)
                    }
                    
                    min_amt, max_amt = amount_ranges[category]
                    amount = round(random.uniform(min_amt, max_amt), 2)
                    
                    # Random day within the month
                    day_offset = random.randint(0, 29)
                    transaction_date = current_date + timedelta(days=day_offset)
                    
                    self.transactions.append({
                        'date': transaction_date.strftime('%Y-%m-%d'),
                        'category': category,
                        'amount': amount,
                        'description': f'{category} expense'
                    })
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def get_monthly_data(self) -> Dict[str, Dict[str, float]]:
        """Group transactions by month and category."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_key][category] += amount
            
            return dict(monthly_data)
        
        except Exception as e:
            print(f"Error processing monthly data: {e}")
            return {}
    
    def calculate_category_totals(self, month_data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Calculate and sort category totals for a given month."""
        try:
            return sorted(month_data.items(), key=lambda x: x[1], reverse=True)
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return []
    
    def calculate_percentages(self, category_totals: List[Tuple[str, float]]) -> List[Tuple[str, float, float]]:
        """Calculate percentage breakdown for categories."""
        try:
            total_spending = sum(amount for _, amount in category_totals)
            if total_spending == 0:
                return []
            
            return [(category, amount, (amount / total_spending) * 100) 
                   for category, amount in category_totals]
        except Exception as e:
            print(f"Error calculating percentages: {e}")
            return []
    
    def calculate_trends(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate month-over-month trends."""
        try:
            trends = {}
            months = sorted(monthly_data.keys())
            
            if len(months) < 2:
                return trends
            
            current_month = months[-1]
            previous_month = months[-2]
            
            current_total = sum(monthly_data[current_month].values())
            previous_total = sum(monthly_data[previous_month].values())
            
            # Overall trend
            if previous_total > 0:
                overall_change = ((current_total - previous_total) / previous_total) * 100
                trends['overall'] = overall_change
            
            # Category trends
            for category in self.categories:
                current_amount = monthly_data[current_month].get(category, 0)
                previous_amount = monthly_data[previous_month].get(category, 0)
                
                if previous_amount > 0:
                    change = ((current_amount - previous_amount) / previous_amount) * 100
                    trends[category] = change
                elif current_amount > 0:
                    trends[category] = 100.0  # New spending in category
            
            return trends
        
        except Exception as e:
            print(f"Error calculating trends: {e}")
            return {}
    
    def create_bar_chart(self, data: List[Tuple[str, float]], title: str, max_width: int = 50) -> str:
        """Create ASCII bar chart."""
        try:
            if not data:
                return f"\n{title}\nNo data available\n"
            
            max_value = max(value for _, value in data)
            if max_value == 0:
                return f"\n{title}\nNo data to display\n"
            
            chart = f"\n{title}\n{'='*len(title)}\n"
            
            for label, value in data:
                bar_length = int((value / max_value) * max_width)
                bar = '█' * bar_length
                chart += f"{label:<15} |{bar:<{max_width}} ${value:,.2f}\n"
            
            return chart + "\n"
        
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            return f"\n{title}\nError creating chart\n"
    
    def create_percentage_chart(self, data: List[Tuple[str, float, float]], max_width: int = 30) -> str:
        """Create percentage breakdown chart."""
        try:
            if not data:
                return "\nPercentage Breakdown\nNo data available\n"
            
            chart = "\nPercentage Breakdown\n" + "="*19 + "\n"
            
            for category, amount, percentage in data:
                bar_length = int((percentage / 100) * max_width)
                bar = '█' * bar_length
                chart += f"{category:<15} |{bar:<{max_width}} {percentage:5.1f}% (${amount:,.2f})\n"
            
            return chart + "\n"
        
        except Exception as e:
            print(f"Error creating percentage chart: {e}")
            return "\nPercentage Breakdown\nError creating chart\n"
    
    def create_trend_chart(self, trends: Dict[str, float]) -> str:
        """Create trend visualization."""
        try: