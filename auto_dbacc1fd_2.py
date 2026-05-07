```python
"""
Personal Finance Data Analysis Script

This script analyzes spending data to generate comprehensive financial insights including:
- Monthly spending summaries by category
- Spending trend analysis over time
- Top merchant identification per category
- Export capabilities to CSV and JSON formats

The script uses sample data for demonstration but can be easily adapted
to work with real financial data sources.

Usage: python script.py
"""

import json
import csv
import datetime
from collections import defaultdict, Counter
from decimal import Decimal
import sys
import os


class SpendingAnalyzer:
    def __init__(self):
        self.transactions = []
        self.monthly_summaries = defaultdict(lambda: defaultdict(Decimal))
        self.category_merchants = defaultdict(list)
        
    def load_sample_data(self):
        """Load sample transaction data for demonstration"""
        sample_data = [
            {"date": "2024-01-15", "amount": 45.67, "category": "Groceries", "merchant": "Whole Foods"},
            {"date": "2024-01-22", "amount": 89.23, "category": "Dining", "merchant": "Pizza Palace"},
            {"date": "2024-01-28", "amount": 156.78, "category": "Groceries", "merchant": "Safeway"},
            {"date": "2024-02-03", "amount": 67.45, "category": "Gas", "merchant": "Shell Station"},
            {"date": "2024-02-10", "amount": 234.56, "category": "Shopping", "merchant": "Amazon"},
            {"date": "2024-02-14", "amount": 78.90, "category": "Dining", "merchant": "Starbucks"},
            {"date": "2024-02-20", "amount": 123.45, "category": "Groceries", "merchant": "Whole Foods"},
            {"date": "2024-03-05", "amount": 98.76, "category": "Gas", "merchant": "Chevron"},
            {"date": "2024-03-12", "amount": 345.67, "category": "Shopping", "merchant": "Target"},
            {"date": "2024-03-18", "amount": 56.78, "category": "Dining", "merchant": "McDonald's"},
            {"date": "2024-03-25", "amount": 167.89, "category": "Groceries", "merchant": "Trader Joe's"},
            {"date": "2024-04-02", "amount": 87.65, "category": "Gas", "merchant": "Shell Station"},
            {"date": "2024-04-08", "amount": 234.56, "category": "Shopping", "merchant": "Best Buy"},
            {"date": "2024-04-15", "amount": 123.45, "category": "Dining", "merchant": "Olive Garden"},
            {"date": "2024-04-22", "amount": 189.23, "category": "Groceries", "merchant": "Costco"},
        ]
        
        for transaction in sample_data:
            self.transactions.append({
                "date": datetime.datetime.strptime(transaction["date"], "%Y-%m-%d").date(),
                "amount": Decimal(str(transaction["amount"])),
                "category": transaction["category"],
                "merchant": transaction["merchant"]
            })
    
    def generate_monthly_summaries(self):
        """Generate monthly spending summaries by category"""
        try:
            for transaction in self.transactions:
                month_key = transaction["date"].strftime("%Y-%m")
                category = transaction["category"]
                self.monthly_summaries[month_key][category] += transaction["amount"]
                
            print("=== MONTHLY SPENDING SUMMARIES BY CATEGORY ===")
            for month, categories in sorted(self.monthly_summaries.items()):
                print(f"\n{month}:")
                total_month = sum(categories.values())
                for category, amount in sorted(categories.items()):
                    percentage = (amount / total_month * 100) if total_month > 0 else 0
                    print(f"  {category}: ${amount:.2f} ({percentage:.1f}%)")
                print(f"  TOTAL: ${total_month:.2f}")
                
        except Exception as e:
            print(f"Error generating monthly summaries: {e}", file=sys.stderr)
    
    def calculate_spending_trends(self):
        """Calculate spending trends over time"""
        try:
            monthly_totals = {}
            category_trends = defaultdict(dict)
            
            for month, categories in self.monthly_summaries.items():
                monthly_totals[month] = sum(categories.values())
                for category, amount in categories.items():
                    category_trends[category][month] = amount
            
            print("\n=== SPENDING TRENDS OVER TIME ===")
            
            # Overall trend
            sorted_months = sorted(monthly_totals.keys())
            print(f"\nOverall Monthly Spending:")
            for month in sorted_months:
                print(f"  {month}: ${monthly_totals[month]:.2f}")
            
            # Calculate month-over-month growth
            if len(sorted_months) > 1:
                print(f"\nMonth-over-Month Growth:")
                for i in range(1, len(sorted_months)):
                    prev_month = monthly_totals[sorted_months[i-1]]
                    curr_month = monthly_totals[sorted_months[i]]
                    growth = ((curr_month - prev_month) / prev_month * 100) if prev_month > 0 else 0
                    print(f"  {sorted_months[i]}: {growth:+.1f}%")
            
            # Category trends
            print(f"\nCategory Trends:")
            for category, months in category_trends.items():
                sorted_cat_months = sorted(months.keys())
                if len(sorted_cat_months) > 1:
                    first_month = months[sorted_cat_months[0]]
                    last_month = months[sorted_cat_months[-1]]
                    trend = ((last_month - first_month) / first_month * 100) if first_month > 0 else 0
                    print(f"  {category}: {trend:+.1f}% change")
                    
        except Exception as e:
            print(f"Error calculating spending trends: {e}", file=sys.stderr)
    
    def identify_top_merchants(self):
        """Identify top merchants per category"""
        try:
            # Group transactions by category and merchant
            for transaction in self.transactions:
                category = transaction["category"]
                merchant = transaction["merchant"]
                amount = transaction["amount"]
                self.category_merchants[category].append((merchant, amount))
            
            print("\n=== TOP MERCHANTS PER CATEGORY ===")
            
            for category, merchant_data in self.category_merchants.items():
                # Sum amounts by merchant
                merchant_totals = defaultdict(Decimal)
                for merchant, amount in merchant_data:
                    merchant_totals[merchant] += amount
                
                # Sort by total amount (descending)
                top_merchants = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)
                
                print(f"\n{category}:")
                for i, (merchant, total) in enumerate(top_merchants[:3], 1):  # Top 3
                    print(f"  {i}. {merchant}: ${total:.2f}")
                    
        except Exception as e:
            print(f"Error identifying top merchants: {e}", file=sys.stderr)
    
    def export_to_csv(self, filename="spending_analysis.csv"):
        """Export analysis results to CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write monthly summaries
                writer.writerow(["Monthly Spending Summaries"])
                writer.writerow(["Month", "Category", "Amount"])
                
                for month, categories in sorted(self.monthly_summaries.items()):
                    for category, amount in sorted(categories.items()):
                        writer.writerow([