```python
"""
Monthly Financial Analysis Engine

A comprehensive financial analysis tool that processes transaction data to calculate spending trends,
identify unusual transactions, and generate visual reports with percentage breakdowns by category.

Key Features:
- Calculates monthly spending trends across categories
- Identifies anomalous transactions using statistical analysis
- Generates percentage breakdowns of spending patterns
- Creates visual charts for data visualization
- Exports analysis results and charts

Dependencies: matplotlib, pandas (installable via pip)
Usage: python script.py
"""

import json
import random
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Visual charts will be disabled.")


class MonthlyAnalysisEngine:
    """Core engine for financial transaction analysis and reporting."""
    
    def __init__(self):
        self.transactions = []
        self.categories = [
            "Groceries", "Restaurants", "Transportation", "Utilities", 
            "Entertainment", "Healthcare", "Shopping", "Bills", "Gas", "Other"
        ]
        
    def generate_sample_data(self, num_transactions=150):
        """Generate realistic sample transaction data for demonstration."""
        try:
            base_date = datetime.now() - timedelta(days=90)
            
            for i in range(num_transactions):
                category = random.choice(self.categories)
                
                # Category-specific amount ranges for realism
                amount_ranges = {
                    "Groceries": (20, 150),
                    "Restaurants": (15, 80),
                    "Transportation": (10, 50),
                    "Utilities": (50, 200),
                    "Entertainment": (20, 100),
                    "Healthcare": (30, 300),
                    "Shopping": (25, 250),
                    "Bills": (100, 500),
                    "Gas": (30, 80),
                    "Other": (10, 100)
                }
                
                min_amt, max_amt = amount_ranges.get(category, (10, 100))
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                # Add some unusual transactions (5% chance of being 3x normal)
                if random.random() < 0.05:
                    amount *= 3
                
                date = base_date + timedelta(days=random.randint(0, 89))
                
                transaction = {
                    "id": f"TXN_{i+1:04d}",
                    "date": date.strftime("%Y-%m-%d"),
                    "amount": amount,
                    "category": category,
                    "description": f"{category} purchase #{i+1}"
                }
                self.transactions.append(transaction)
                
            print(f"Generated {num_transactions} sample transactions")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            
    def calculate_monthly_trends(self):
        """Calculate spending trends by month and category."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction["date"], "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                category = transaction["category"]
                amount = transaction["amount"]
                
                monthly_data[month_key][category] += amount
                
            # Calculate trends
            trends = {}
            months = sorted(monthly_data.keys())
            
            for category in self.categories:
                category_trends = []
                for month in months:
                    amount = monthly_data[month].get(category, 0)
                    category_trends.append(amount)
                
                if len(category_trends) >= 2:
                    # Calculate trend (positive = increasing, negative = decreasing)
                    trend = (category_trends[-1] - category_trends[0]) / len(category_trends)
                    trends[category] = {
                        "monthly_amounts": category_trends,
                        "trend": trend,
                        "total": sum(category_trends)
                    }
                    
            return monthly_data, trends
            
        except Exception as e:
            print(f"Error calculating monthly trends: {e}")
            return {}, {}
            
    def identify_unusual_transactions(self):
        """Identify transactions that are statistical outliers."""
        try:
            unusual_transactions = []
            
            # Group by category for statistical analysis
            category_amounts = defaultdict(list)
            for transaction in self.transactions:
                category_amounts[transaction["category"]].append(transaction["amount"])
                
            for transaction in self.transactions:
                category = transaction["category"]
                amount = transaction["amount"]
                amounts_in_category = category_amounts[category]
                
                if len(amounts_in_category) < 3:
                    continue
                    
                mean_amount = statistics.mean(amounts_in_category)
                stdev_amount = statistics.stdev(amounts_in_category)
                
                # Consider transaction unusual if it's > 2 standard deviations from mean
                z_score = abs((amount - mean_amount) / stdev_amount) if stdev_amount > 0 else 0
                
                if z_score > 2:
                    transaction_copy = transaction.copy()
                    transaction_copy["z_score"] = round(z_score, 2)
                    transaction_copy["category_mean"] = round(mean_amount, 2)
                    unusual_transactions.append(transaction_copy)
                    
            return sorted(unusual_transactions, key=lambda x: x["z_score"], reverse=True)
            
        except Exception as e:
            print(f"Error identifying unusual transactions: {e}")
            return []
            
    def calculate_percentage_breakdown(self):
        """Calculate percentage breakdown of spending by category."""
        try:
            category_totals = defaultdict(float)
            total_spending = 0
            
            for transaction in self.transactions:
                amount = transaction["amount"]
                category = transaction["category"]
                category_totals[category] += amount
                total_spending += amount
                
            percentages = {}
            for category, total in category_totals.items():
                percentage = (total / total_spending) * 100 if total_spending > 0 else 0
                percentages[category] = {
                    "amount": round(total, 2),
                    "percentage": round(percentage, 2),
                    "count": sum(1 for t in self.transactions if t["category"] == category)
                }
                
            return percentages, total_spending
            
        except Exception as e:
            print(f"Error calculating percentage breakdown: {e}")
            return {}, 0
            
    def create_visual_charts(self, percentages, monthly_data):
        """Generate visual charts using matplotlib."""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available - skipping chart generation")
            return
            
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Monthly Financial Analysis Report', fontsize=16, fontweight='bold')
            
            # 1. Pie chart for category percentages
            categories = list(percentages.keys())
            amounts = [percentages[cat]["amount"] for cat in categories]
            colors = plt.cm.Set3(range(len(categories)))
            
            ax1.pie(amounts, labels=categories, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title('Spending by Category')
            
            # 2. Bar chart for category amounts
            ax2.bar(categories, amounts, color=colors)
            ax2.set_title('Total Spending by Category')
            ax2.set_ylabel('Amount ($)')
            ax2.tick_params(axis='x', rotation=45)
            
            # 3. Monthly trends line chart
            months = sorted(monthly_data.keys())
            if len(months) >