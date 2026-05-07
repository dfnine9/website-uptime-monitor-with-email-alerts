```python
"""
Monthly Spending Analysis Report Generator

This module analyzes financial transaction data to generate comprehensive monthly spending reports.
Features include:
- Category-wise spending breakdowns
- Month-over-month trend analysis
- Budget variance calculations
- Spending pattern identification

The script generates sample transaction data for demonstration purposes and produces
detailed analysis reports showing spending habits, trends, and budget performance.

Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

def generate_sample_data():
    """Generate sample transaction data for analysis."""
    categories = [
        'Groceries', 'Transportation', 'Utilities', 'Entertainment',
        'Dining Out', 'Healthcare', 'Shopping', 'Insurance',
        'Education', 'Miscellaneous'
    ]
    
    budgets = {
        'Groceries': 600, 'Transportation': 300, 'Utilities': 200,
        'Entertainment': 150, 'Dining Out': 250, 'Healthcare': 100,
        'Shopping': 200, 'Insurance': 150, 'Education': 100,
        'Miscellaneous': 100
    }
    
    transactions = []
    start_date = datetime.now() - timedelta(days=120)
    
    for i in range(300):
        transaction_date = start_date + timedelta(days=random.randint(0, 120))
        category = random.choice(categories)
        
        # Generate realistic amounts based on category
        amount_ranges = {
            'Groceries': (20, 150), 'Transportation': (5, 80),
            'Utilities': (50, 200), 'Entertainment': (10, 100),
            'Dining Out': (15, 80), 'Healthcare': (25, 300),
            'Shopping': (10, 200), 'Insurance': (100, 200),
            'Education': (20, 150), 'Miscellaneous': (5, 50)
        }
        
        min_amt, max_amt = amount_ranges[category]
        amount = round(random.uniform(min_amt, max_amt), 2)
        
        transactions.append({
            'date': transaction_date.strftime('%Y-%m-%d'),
            'category': category,
            'amount': amount,
            'description': f"{category} transaction {i+1}"
        })
    
    return transactions, budgets

class SpendingAnalyzer:
    """Analyzes spending data and generates reports."""
    
    def __init__(self, transactions, budgets):
        self.transactions = transactions
        self.budgets = budgets
        self.monthly_data = self._organize_by_month()
    
    def _organize_by_month(self):
        """Organize transactions by month and category."""
        monthly_data = defaultdict(lambda: defaultdict(list))
        
        for transaction in self.transactions:
            try:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_key][category].append(amount)
            except (ValueError, KeyError) as e:
                print(f"Error processing transaction: {e}")
                continue
        
        return monthly_data
    
    def calculate_monthly_totals(self):
        """Calculate total spending per category per month."""
        monthly_totals = {}
        
        for month, categories in self.monthly_data.items():
            monthly_totals[month] = {}
            for category, amounts in categories.items():
                monthly_totals[month][category] = sum(amounts)
        
        return monthly_totals
    
    def calculate_trends(self, monthly_totals):
        """Calculate month-over-month trends."""
        trends = {}
        months = sorted(monthly_totals.keys())
        
        if len(months) < 2:
            return trends
        
        for category in self.budgets.keys():
            category_trends = []
            for i in range(1, len(months)):
                prev_month = months[i-1]
                curr_month = months[i]
                
                prev_amount = monthly_totals.get(prev_month, {}).get(category, 0)
                curr_amount = monthly_totals.get(curr_month, {}).get(category, 0)
                
                if prev_amount > 0:
                    trend = ((curr_amount - prev_amount) / prev_amount) * 100
                    category_trends.append(trend)
            
            if category_trends:
                trends[category] = {
                    'avg_change': statistics.mean(category_trends),
                    'recent_change': category_trends[-1] if category_trends else 0
                }
        
        return trends
    
    def calculate_budget_variance(self, monthly_totals):
        """Calculate budget variance for each category."""
        variance_data = {}
        
        for month, categories in monthly_totals.items():
            variance_data[month] = {}
            for category, budget in self.budgets.items():
                actual = categories.get(category, 0)
                variance = actual - budget
                variance_pct = (variance / budget) * 100 if budget > 0 else 0
                
                variance_data[month][category] = {
                    'budget': budget,
                    'actual': actual,
                    'variance': variance,
                    'variance_pct': variance_pct
                }
        
        return variance_data
    
    def generate_report(self):
        """Generate comprehensive spending analysis report."""
        try:
            monthly_totals = self.calculate_monthly_totals()
            trends = self.calculate_trends(monthly_totals)
            variance_data = self.calculate_budget_variance(monthly_totals)
            
            print("="*80)
            print("MONTHLY SPENDING ANALYSIS REPORT")
            print("="*80)
            print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Analysis period: {len(monthly_totals)} months")
            print()
            
            # Monthly breakdown
            print("MONTHLY SPENDING BREAKDOWN")
            print("-"*50)
            for month in sorted(monthly_totals.keys()):
                print(f"\n{month}:")
                total_month = 0
                for category, amount in sorted(monthly_totals[month].items()):
                    print(f"  {category:15s}: ${amount:8.2f}")
                    total_month += amount
                print(f"  {'TOTAL':15s}: ${total_month:8.2f}")
            
            # Category trends
            print("\n\nCATEGORY TRENDS")
            print("-"*50)
            for category, trend_data in trends.items():
                avg_change = trend_data['avg_change']
                recent_change = trend_data['recent_change']
                trend_direction = "↑" if avg_change > 0 else "↓" if avg_change < 0 else "→"
                
                print(f"{category:15s}: {trend_direction} Avg: {avg_change:6.1f}% | Recent: {recent_change:6.1f}%")
            
            # Budget variance for latest month
            latest_month = max(variance_data.keys())
            print(f"\n\nBUDGET VARIANCE - {latest_month}")
            print("-"*50)
            print(f"{'Category':15s} {'Budget':>10s} {'Actual':>10s} {'Variance':>10s} {'%':>8s}")
            print("-"*50)
            
            for category, data in variance_data[latest_month].items():
                status = "OVER" if data['variance'] > 0 else "UNDER" if data['variance'] < 0 else "ON"
                print(f"{category:15s} ${data['budget']:8.2f} ${data['actual']:8.2f} "
                      f"${data['variance']:8.2f} {data['variance_pct']:6.1f}