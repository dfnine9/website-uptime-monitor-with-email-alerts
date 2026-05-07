```python
#!/usr/bin/env python3
"""
Financial Transaction Analysis Module

This module provides comprehensive analysis of categorized financial transactions including:
- Spending pattern identification across categories
- Monthly average calculations per category
- Unusual spending spike detection using statistical methods
- Expense trend tracking over configurable time periods

The module processes transaction data to generate actionable insights for personal
or business financial management.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import calendar


class TransactionAnalyzer:
    """Analyzes financial transactions for patterns, averages, and anomalies."""
    
    def __init__(self):
        self.transactions = []
        self.categories = set()
        
    def load_sample_data(self):
        """Load sample transaction data for demonstration."""
        import random
        
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
        
        # Generate sample transactions over the last 12 months
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(500):  # Generate 500 sample transactions
            category = random.choice(categories)
            
            # Create category-specific spending patterns
            if category == 'Food':
                amount = random.uniform(10, 80)
            elif category == 'Transportation':
                amount = random.uniform(5, 150)
            elif category == 'Entertainment':
                amount = random.uniform(20, 200)
            elif category == 'Utilities':
                amount = random.uniform(50, 300)
            elif category == 'Shopping':
                amount = random.uniform(15, 400)
            else:  # Healthcare
                amount = random.uniform(20, 500)
            
            # Add occasional spikes
            if random.random() < 0.05:  # 5% chance of spike
                amount *= random.uniform(2, 4)
            
            date = base_date + timedelta(days=random.randint(0, 365))
            
            transaction = {
                'date': date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': round(amount, 2),
                'description': f'{category} purchase #{i+1}'
            }
            
            self.transactions.append(transaction)
            self.categories.add(category)
    
    def parse_transactions(self):
        """Parse and organize transactions by date and category."""
        try:
            parsed_transactions = defaultdict(lambda: defaultdict(list))
            
            for transaction in self.transactions:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = f"{date.year}-{date.month:02d}"
                category = transaction['category']
                amount = float(transaction['amount'])
                
                parsed_transactions[month_key][category].append(amount)
            
            return parsed_transactions
        except (ValueError, KeyError) as e:
            print(f"Error parsing transactions: {e}")
            return defaultdict(lambda: defaultdict(list))
    
    def calculate_monthly_averages(self, parsed_data):
        """Calculate monthly averages per category."""
        try:
            monthly_averages = {}
            category_totals = defaultdict(list)
            
            for month, categories in parsed_data.items():
                monthly_averages[month] = {}
                for category, amounts in categories.items():
                    monthly_total = sum(amounts)
                    monthly_averages[month][category] = monthly_total
                    category_totals[category].append(monthly_total)
            
            # Calculate overall averages per category
            overall_averages = {}
            for category, monthly_totals in category_totals.items():
                overall_averages[category] = statistics.mean(monthly_totals)
            
            return monthly_averages, overall_averages
        except Exception as e:
            print(f"Error calculating monthly averages: {e}")
            return {}, {}
    
    def detect_spending_spikes(self, monthly_averages, overall_averages):
        """Detect unusual spending spikes using standard deviation method."""
        try:
            spikes = []
            category_data = defaultdict(list)
            
            # Collect all monthly spending per category
            for month, categories in monthly_averages.items():
                for category, amount in categories.items():
                    category_data[category].append((month, amount))
            
            # Detect spikes for each category
            for category, data in category_data.items():
                if len(data) < 3:  # Need at least 3 data points
                    continue
                    
                amounts = [amount for _, amount in data]
                mean_amount = statistics.mean(amounts)
                
                if len(amounts) > 1:
                    std_dev = statistics.stdev(amounts)
                    threshold = mean_amount + (2 * std_dev)  # 2 standard deviations
                    
                    for month, amount in data:
                        if amount > threshold:
                            spike_percentage = ((amount - mean_amount) / mean_amount) * 100
                            spikes.append({
                                'month': month,
                                'category': category,
                                'amount': amount,
                                'average': mean_amount,
                                'spike_percentage': round(spike_percentage, 1)
                            })
            
            return sorted(spikes, key=lambda x: x['spike_percentage'], reverse=True)
        except Exception as e:
            print(f"Error detecting spending spikes: {e}")
            return []
    
    def track_expense_trends(self, monthly_averages):
        """Track expense trends over time periods."""
        try:
            trends = {}
            
            # Sort months chronologically
            sorted_months = sorted(monthly_averages.keys())
            
            for category in self.categories:
                category_trends = []
                amounts = []
                
                for month in sorted_months:
                    amount = monthly_averages.get(month, {}).get(category, 0)
                    amounts.append(amount)
                    category_trends.append((month, amount))
                
                if len(amounts) >= 2:
                    # Calculate trend (simple linear regression slope)
                    n = len(amounts)
                    x_values = list(range(n))
                    
                    sum_x = sum(x_values)
                    sum_y = sum(amounts)
                    sum_xy = sum(x * y for x, y in zip(x_values, amounts))
                    sum_x2 = sum(x * x for x in x_values)
                    
                    if n * sum_x2 - sum_x * sum_x != 0:
                        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                        
                        # Determine trend direction
                        if slope > 5:
                            trend_direction = "Increasing"
                        elif slope < -5:
                            trend_direction = "Decreasing"
                        else:
                            trend_direction = "Stable"
                        
                        trends[category] = {
                            'slope': round(slope, 2),
                            'direction': trend_direction,
                            'data_points': category_trends,
                            'recent_months': category_trends[-3:] if len(category_trends) >= 3 else category_trends
                        }
            
            return trends
        except Exception as e:
            print(f"Error tracking expense trends: {e}")
            return {}
    
    def identify_spending_patterns(self, parsed_data):
        """Identify spending patterns across categories and time."""
        try:
            patterns = {
                'most_expensive_categories': Counter(),
                'most_frequent_categories': Counter(),
                'seasonal_patterns': defaultdict(lambda: defaultdict(float)),
                'weekend_vs_weekday': defaultdict(lambda: {'weekday': 0, 'weekend': 0})
            }
            
            for transaction in self.transactions:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                category = transaction['category']
                amount = float(transaction['