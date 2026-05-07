```python
"""
Monthly Transaction Analysis Module

This module provides comprehensive analysis of categorized financial transactions including:
- Spending totals per category
- Month-over-month trend analysis
- Percentage breakdowns of spending
- Visual ASCII charts and data representations
- Summary statistics and insights

The module generates sample transaction data for demonstration but can be easily
modified to accept real transaction data from CSV files or databases.
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import calendar


class TransactionAnalyzer:
    """Analyzes financial transactions and generates comprehensive reports."""
    
    def __init__(self):
        self.transactions = []
        self.categories = [
            'Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities',
            'Entertainment', 'Health & Fitness', 'Travel', 'Education',
            'Groceries', 'Gas & Fuel', 'Home & Garden', 'Personal Care'
        ]
    
    def generate_sample_data(self, months: int = 6) -> None:
        """Generate sample transaction data for demonstration."""
        try:
            current_date = datetime.now()
            
            for month_offset in range(months):
                month_date = current_date - timedelta(days=30 * month_offset)
                transactions_per_month = random.randint(50, 100)
                
                for _ in range(transactions_per_month):
                    transaction = {
                        'date': month_date - timedelta(days=random.randint(0, 29)),
                        'amount': round(random.uniform(5.0, 500.0), 2),
                        'category': random.choice(self.categories),
                        'description': f"Transaction {random.randint(1000, 9999)}"
                    }
                    self.transactions.append(transaction)
            
            # Sort by date
            self.transactions.sort(key=lambda x: x['date'], reverse=True)
            print(f"Generated {len(self.transactions)} sample transactions")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def categorize_by_month(self) -> Dict[str, Dict[str, float]]:
        """Categorize transactions by month and category."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                month_key = transaction['date'].strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_key][category] += amount
            
            return dict(monthly_data)
            
        except Exception as e:
            print(f"Error categorizing transactions: {e}")
            return {}
    
    def calculate_spending_totals(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate total spending per category across all months."""
        try:
            category_totals = defaultdict(float)
            
            for month_data in monthly_data.values():
                for category, amount in month_data.items():
                    category_totals[category] += amount
            
            return dict(category_totals)
            
        except Exception as e:
            print(f"Error calculating spending totals: {e}")
            return {}
    
    def identify_trends(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
        """Identify spending trends for each category."""
        try:
            trends = {}
            
            for category in self.categories:
                monthly_amounts = []
                months = sorted(monthly_data.keys())
                
                for month in months:
                    amount = monthly_data.get(month, {}).get(category, 0.0)
                    monthly_amounts.append(amount)
                
                if len(monthly_amounts) >= 2:
                    # Calculate trend
                    first_half = sum(monthly_amounts[:len(monthly_amounts)//2])
                    second_half = sum(monthly_amounts[len(monthly_amounts)//2:])
                    
                    if first_half > 0:
                        trend_percentage = ((second_half - first_half) / first_half) * 100
                    else:
                        trend_percentage = 0.0
                    
                    trends[category] = {
                        'monthly_amounts': monthly_amounts,
                        'trend_percentage': round(trend_percentage, 2),
                        'trend_direction': 'increasing' if trend_percentage > 5 else 'decreasing' if trend_percentage < -5 else 'stable',
                        'average_monthly': round(sum(monthly_amounts) / len(monthly_amounts), 2),
                        'max_month': max(monthly_amounts),
                        'min_month': min(monthly_amounts)
                    }
            
            return trends
            
        except Exception as e:
            print(f"Error identifying trends: {e}")
            return {}
    
    def calculate_percentages(self, category_totals: Dict[str, float]) -> Dict[str, float]:
        """Calculate percentage breakdown of spending by category."""
        try:
            total_spending = sum(category_totals.values())
            
            if total_spending == 0:
                return {}
            
            percentages = {}
            for category, amount in category_totals.items():
                percentages[category] = round((amount / total_spending) * 100, 2)
            
            return percentages
            
        except Exception as e:
            print(f"Error calculating percentages: {e}")
            return {}
    
    def create_ascii_bar_chart(self, data: Dict[str, float], title: str, max_width: int = 50) -> str:
        """Create ASCII bar chart visualization."""
        try:
            if not data:
                return f"\n{title}\nNo data available\n"
            
            max_value = max(data.values())
            if max_value == 0:
                return f"\n{title}\nNo spending data\n"
            
            chart = f"\n{title}\n" + "="*len(title) + "\n"
            
            # Sort by value descending
            sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
            
            for category, value in sorted_data:
                bar_length = int((value / max_value) * max_width)
                bar = "█" * bar_length
                chart += f"{category[:20]:<20} |{bar:<{max_width}} ${value:,.2f}\n"
            
            return chart
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            return f"\n{title}\nError creating visualization\n"
    
    def create_percentage_chart(self, percentages: Dict[str, float]) -> str:
        """Create ASCII percentage breakdown chart."""
        try:
            if not percentages:
                return "\nPercentage Breakdown\nNo data available\n"
            
            chart = "\nSpending Percentage Breakdown\n" + "="*30 + "\n"
            
            # Sort by percentage descending
            sorted_percentages = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
            
            for category, percentage in sorted_percentages:
                # Create visual percentage bar
                bar_length = int(percentage / 2)  # Scale for display
                bar = "▓" * bar_length
                chart += f"{category[:20]:<20} |{bar:<50} {percentage:>6.2f}%\n"
            
            return chart
            
        except Exception as e:
            print(f"Error creating percentage chart: {e}")
            return "\nPercentage Breakdown\nError creating visualization\n"
    
    def generate_insights(self, trends: Dict[str, Dict[str, Any]], category_totals: Dict[str, float]) -> str:
        """Generate spending insights and recommendations."""
        try:
            insights = "\nSpending Insights & Trends\n" + "="*30 + "\n"
            
            if not trends: