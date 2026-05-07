```python
#!/usr/bin/env python3
"""
Financial Transaction Data Analysis Module

This module processes categorized financial transactions to generate comprehensive spending insights.
It calculates monthly spending trends, category-wise statistics, and provides detailed analytics
including spending patterns, top categories, and financial summaries.

Features:
- Monthly spending trend analysis
- Category-wise expenditure breakdown
- Statistical insights (averages, totals, percentiles)
- Spending pattern detection
- Self-contained with minimal dependencies

Usage: python script.py
"""

import json
import datetime
from collections import defaultdict, Counter
from statistics import mean, median
import calendar


class TransactionAnalyzer:
    """Analyzes financial transaction data to generate spending insights."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_stats = defaultdict(list)
        
    def load_sample_data(self):
        """Generate sample transaction data for demonstration."""
        import random
        
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 
                     'Healthcare', 'Education', 'Insurance', 'Rent', 'Groceries']
        
        # Generate 6 months of sample data
        start_date = datetime.date(2024, 1, 1)
        
        for month in range(6):
            current_month = start_date.replace(month=month + 1)
            transactions_per_month = random.randint(20, 40)
            
            for _ in range(transactions_per_month):
                day = random.randint(1, 28)  # Safe day range for all months
                transaction_date = current_month.replace(day=day)
                category = random.choice(categories)
                
                # Different spending patterns by category
                if category == 'Rent':
                    amount = random.uniform(800, 1200)
                elif category == 'Groceries':
                    amount = random.uniform(20, 150)
                elif category == 'Utilities':
                    amount = random.uniform(50, 200)
                elif category == 'Transportation':
                    amount = random.uniform(5, 100)
                else:
                    amount = random.uniform(10, 300)
                
                self.transactions.append({
                    'date': transaction_date.isoformat(),
                    'amount': round(amount, 2),
                    'category': category,
                    'description': f'{category} expense'
                })
    
    def process_transactions(self):
        """Process transactions and organize by month and category."""
        try:
            for transaction in self.transactions:
                date_obj = datetime.datetime.fromisoformat(transaction['date']).date()
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = float(transaction['amount'])
                
                # Store monthly data
                self.monthly_data[month_key][category] += amount
                self.monthly_data[month_key]['total'] += amount
                
                # Store category statistics
                self.category_stats[category].append(amount)
                
        except (ValueError, KeyError) as e:
            print(f"Error processing transaction: {e}")
            
    def calculate_monthly_trends(self):
        """Calculate monthly spending trends."""
        trends = {}
        
        try:
            sorted_months = sorted(self.monthly_data.keys())
            
            for month in sorted_months:
                month_data = self.monthly_data[month]
                total_spent = month_data.get('total', 0)
                
                # Calculate month-over-month change
                prev_month_idx = sorted_months.index(month) - 1
                if prev_month_idx >= 0:
                    prev_month = sorted_months[prev_month_idx]
                    prev_total = self.monthly_data[prev_month].get('total', 0)
                    if prev_total > 0:
                        change_pct = ((total_spent - prev_total) / prev_total) * 100
                    else:
                        change_pct = 0
                else:
                    change_pct = 0
                
                trends[month] = {
                    'total_spent': round(total_spent, 2),
                    'change_percent': round(change_pct, 2),
                    'categories': dict(month_data)
                }
                
        except (IndexError, ZeroDivisionError) as e:
            print(f"Error calculating trends: {e}")
            
        return trends
    
    def calculate_category_statistics(self):
        """Calculate comprehensive category-wise statistics."""
        stats = {}
        
        try:
            for category, amounts in self.category_stats.items():
                if amounts:
                    stats[category] = {
                        'total_spent': round(sum(amounts), 2),
                        'average_transaction': round(mean(amounts), 2),
                        'median_transaction': round(median(amounts), 2),
                        'transaction_count': len(amounts),
                        'min_transaction': round(min(amounts), 2),
                        'max_transaction': round(max(amounts), 2),
                        'percentage_of_total': 0  # Will calculate after
                    }
            
            # Calculate percentage of total spending
            total_spending = sum(data['total_spent'] for data in stats.values())
            if total_spending > 0:
                for category_data in stats.values():
                    category_data['percentage_of_total'] = round(
                        (category_data['total_spent'] / total_spending) * 100, 2
                    )
                    
        except (ValueError, ZeroDivisionError) as e:
            print(f"Error calculating category statistics: {e}")
            
        return stats
    
    def generate_insights(self):
        """Generate spending insights and recommendations."""
        insights = []
        
        try:
            # Get category stats
            category_stats = self.calculate_category_statistics()
            monthly_trends = self.calculate_monthly_trends()
            
            if not category_stats:
                return ["No transaction data available for analysis."]
            
            # Top spending categories
            top_categories = sorted(category_stats.items(), 
                                  key=lambda x: x[1]['total_spent'], reverse=True)[:3]
            
            insights.append("TOP SPENDING INSIGHTS:")
            for i, (category, data) in enumerate(top_categories, 1):
                insights.append(f"{i}. {category}: ${data['total_spent']} "
                              f"({data['percentage_of_total']}% of total spending)")
            
            # Monthly trend analysis
            if len(monthly_trends) >= 2:
                insights.append("\nMONTHLY TREND ANALYSIS:")
                latest_month = max(monthly_trends.keys())
                latest_data = monthly_trends[latest_month]
                insights.append(f"Latest month ({latest_month}): ${latest_data['total_spent']}")
                insights.append(f"Month-over-month change: {latest_data['change_percent']:+.1f}%")
            
            # Average transaction insights
            insights.append("\nTRANSACTION PATTERNS:")
            total_transactions = sum(data['transaction_count'] for data in category_stats.values())
            avg_transaction_value = sum(data['total_spent'] for data in category_stats.values()) / total_transactions
            insights.append(f"Average transaction value: ${avg_transaction_value:.2f}")
            insights.append(f"Total transactions analyzed: {total_transactions}")
            
            # Spending distribution
            insights.append("\nSPENDING DISTRIBUTION:")
            for category, data in sorted(category_stats.items(), 
                                       key=lambda x: x[1]['percentage_of_total'], reverse=True):
                insights.append(f"{category}: {data['percentage_of_total']}% "
                              f"(${data['total_spent']}, {data['transaction_count']} transactions)")
                
        except Exception as e:
            insights.append(f"Error generating insights: {e}")
            
        return insights