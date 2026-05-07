```python
"""
Personal Finance Analytics Module

This module analyzes spending patterns by category, calculates monthly averages,
identifies spending trends over time, and detects unusual transactions or budget overruns.
It processes financial transaction data to provide insights into spending behavior.

Features:
- Category-based spending analysis
- Monthly spending averages
- Trend identification using linear regression
- Anomaly detection for unusual transactions
- Budget overrun alerts

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional
import random


class FinanceAnalyzer:
    def __init__(self):
        self.transactions = []
        self.category_budgets = {
            'groceries': 800,
            'dining': 400,
            'transportation': 300,
            'utilities': 250,
            'entertainment': 200,
            'shopping': 500,
            'healthcare': 300,
            'other': 200
        }
    
    def generate_sample_data(self) -> List[Dict]:
        """Generate sample transaction data for demonstration"""
        categories = list(self.category_budgets.keys())
        transactions = []
        
        # Generate 6 months of data
        base_date = datetime.now() - timedelta(days=180)
        
        for i in range(200):
            date = base_date + timedelta(days=random.randint(0, 180))
            category = random.choice(categories)
            
            # Base amount with some category-specific patterns
            base_amount = random.uniform(10, 200)
            if category == 'groceries':
                amount = random.uniform(20, 150)
            elif category == 'utilities':
                amount = random.uniform(80, 300)
            elif category == 'transportation':
                amount = random.uniform(15, 100)
            else:
                amount = base_amount
            
            # Occasionally add anomalous transactions
            if random.random() < 0.05:  # 5% chance
                amount *= random.uniform(3, 8)
            
            transactions.append({
                'date': date.strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'category': category,
                'description': f"{category.title()} purchase #{i+1}"
            })
        
        return sorted(transactions, key=lambda x: x['date'])
    
    def load_transactions(self, data: Optional[List[Dict]] = None):
        """Load transaction data"""
        try:
            if data is None:
                self.transactions = self.generate_sample_data()
            else:
                self.transactions = data
            print(f"Loaded {len(self.transactions)} transactions")
        except Exception as e:
            print(f"Error loading transactions: {e}")
            self.transactions = []
    
    def analyze_spending_by_category(self) -> Dict[str, Dict]:
        """Analyze spending patterns by category"""
        try:
            category_data = defaultdict(lambda: {'total': 0, 'count': 0, 'transactions': []})
            
            for transaction in self.transactions:
                category = transaction['category']
                amount = transaction['amount']
                
                category_data[category]['total'] += amount
                category_data[category]['count'] += 1
                category_data[category]['transactions'].append(transaction)
            
            # Calculate averages and percentages
            total_spending = sum(data['total'] for data in category_data.values())
            
            results = {}
            for category, data in category_data.items():
                results[category] = {
                    'total': round(data['total'], 2),
                    'count': data['count'],
                    'average': round(data['total'] / data['count'], 2) if data['count'] > 0 else 0,
                    'percentage': round((data['total'] / total_spending) * 100, 2) if total_spending > 0 else 0
                }
            
            return results
        except Exception as e:
            print(f"Error analyzing spending by category: {e}")
            return {}
    
    def calculate_monthly_averages(self) -> Dict[str, float]:
        """Calculate monthly spending averages by category"""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_key][category] += amount
            
            # Calculate averages across months
            category_monthly_totals = defaultdict(list)
            for month_data in monthly_data.values():
                for category, total in month_data.items():
                    category_monthly_totals[category].append(total)
            
            monthly_averages = {}
            for category, totals in category_monthly_totals.items():
                monthly_averages[category] = round(statistics.mean(totals), 2)
            
            return monthly_averages
        except Exception as e:
            print(f"Error calculating monthly averages: {e}")
            return {}
    
    def identify_spending_trends(self) -> Dict[str, Dict]:
        """Identify spending trends over time using simple linear analysis"""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            # Group by month
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_key][category] += amount
            
            # Sort months chronologically
            sorted_months = sorted(monthly_data.keys())
            
            trends = {}
            for category in set(t['category'] for t in self.transactions):
                monthly_totals = []
                for month in sorted_months:
                    monthly_totals.append(monthly_data[month].get(category, 0))
                
                if len(monthly_totals) >= 2:
                    # Simple trend calculation: compare first half to second half
                    mid_point = len(monthly_totals) // 2
                    first_half_avg = statistics.mean(monthly_totals[:mid_point]) if mid_point > 0 else 0
                    second_half_avg = statistics.mean(monthly_totals[mid_point:])
                    
                    change = second_half_avg - first_half_avg
                    change_percent = (change / first_half_avg * 100) if first_half_avg > 0 else 0
                    
                    trend_direction = "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
                    
                    trends[category] = {
                        'direction': trend_direction,
                        'change_amount': round(change, 2),
                        'change_percent': round(change_percent, 2),
                        'recent_average': round(second_half_avg, 2)
                    }
            
            return trends
        except Exception as e:
            print(f"Error identifying trends: {e}")
            return {}
    
    def detect_unusual_transactions(self) -> List[Dict]:
        """Detect anomalous transactions using statistical methods"""
        try:
            unusual_transactions = []
            category_stats = defaultdict(list)
            
            # Collect amounts by category
            for transaction in self.transactions:
                category_stats[transaction['category']].append(transaction['amount'])
            
            # Calculate thresholds for each category
            for transaction in self.transactions:
                category = transaction['category']
                amounts = category_stats[category]
                
                if len(amounts) >= 3:  # Need sufficient data
                    mean_amount = statistics.mean(amounts)
                    stdev_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
                    
                    # Transaction is unusual