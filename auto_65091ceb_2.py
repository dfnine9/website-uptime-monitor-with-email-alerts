```python
"""
Financial Report Generation Module

This module provides comprehensive financial reporting capabilities including:
- Monthly spending totals by category
- Percentage breakdowns of expenses
- Spending trend analysis
- Export to CSV and HTML formats

The module processes transaction data to generate insightful financial reports
with visual representations and exportable formats for further analysis.

Requirements: Python 3.6+ (uses only standard library)
Usage: python script.py
"""

import csv
import json
import html
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import os


class FinancialReportGenerator:
    """Generate comprehensive financial reports from transaction data."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
        
    def load_sample_data(self) -> None:
        """Load sample transaction data for demonstration."""
        # Generate sample data for the last 6 months
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping', 'Housing']
        
        base_date = datetime.now() - timedelta(days=180)
        
        sample_transactions = []
        for i in range(200):  # 200 sample transactions
            date = base_date + timedelta(days=(i * 180 // 200))
            category = categories[i % len(categories)]
            amount = round(20 + (i % 500) + (hash(category) % 200), 2)
            
            sample_transactions.append({
                'date': date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': amount,
                'description': f'{category} expense #{i+1}'
            })
        
        self.transactions = sample_transactions
        print(f"Loaded {len(self.transactions)} sample transactions")
    
    def process_transactions(self) -> None:
        """Process transactions to calculate monthly totals and category breakdowns."""
        try:
            for transaction in self.transactions:
                date_str = transaction['date']
                category = transaction['category']
                amount = float(transaction['amount'])
                
                # Parse date and get year-month key
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                
                # Add to monthly totals by category
                self.monthly_totals[month_key][category] += amount
                
                # Add to overall category totals
                self.category_totals[category] += amount
                
        except (ValueError, KeyError) as e:
            print(f"Error processing transaction: {e}")
            raise
    
    def calculate_percentage_breakdown(self) -> Dict[str, float]:
        """Calculate percentage breakdown by category."""
        total_spending = sum(self.category_totals.values())
        if total_spending == 0:
            return {}
        
        percentages = {}
        for category, amount in self.category_totals.items():
            percentages[category] = round((amount / total_spending) * 100, 2)
        
        return percentages
    
    def identify_spending_trends(self) -> Dict[str, Any]:
        """Identify spending trends across months."""
        trends = {}
        
        # Calculate month-over-month changes
        sorted_months = sorted(self.monthly_totals.keys())
        
        if len(sorted_months) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Overall monthly totals trend
        monthly_totals = []
        for month in sorted_months:
            total = sum(self.monthly_totals[month].values())
            monthly_totals.append(total)
        
        # Calculate average monthly change
        changes = []
        for i in range(1, len(monthly_totals)):
            if monthly_totals[i-1] != 0:
                change = ((monthly_totals[i] - monthly_totals[i-1]) / monthly_totals[i-1]) * 100
                changes.append(change)
        
        avg_change = sum(changes) / len(changes) if changes else 0
        
        trends['average_monthly_change_percent'] = round(avg_change, 2)
        trends['highest_spending_month'] = {
            'month': sorted_months[monthly_totals.index(max(monthly_totals))],
            'amount': max(monthly_totals)
        }
        trends['lowest_spending_month'] = {
            'month': sorted_months[monthly_totals.index(min(monthly_totals))],
            'amount': min(monthly_totals)
        }
        
        # Category trends
        category_trends = {}
        for category in self.category_totals.keys():
            category_monthly = []
            for month in sorted_months:
                category_monthly.append(self.monthly_totals[month].get(category, 0))
            
            if len(category_monthly) >= 2:
                category_changes = []
                for i in range(1, len(category_monthly)):
                    if category_monthly[i-1] != 0:
                        change = ((category_monthly[i] - category_monthly[i-1]) / category_monthly[i-1]) * 100
                        category_changes.append(change)
                
                if category_changes:
                    category_trends[category] = round(sum(category_changes) / len(category_changes), 2)
        
        trends['category_trends'] = category_trends
        
        return trends
    
    def export_to_csv(self, filename: str = 'financial_report.csv') -> None:
        """Export report data to CSV format."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Report Type', 'Category/Month', 'Amount', 'Percentage'])
                
                # Write category totals
                percentages = self.calculate_percentage_breakdown()
                for category, amount in self.category_totals.items():
                    percentage = percentages.get(category, 0)
                    writer.writerow(['Category Total', category, f'{amount:.2f}', f'{percentage:.2f}%'])
                
                # Write monthly breakdown
                for month in sorted(self.monthly_totals.keys()):
                    month_total = sum(self.monthly_totals[month].values())
                    writer.writerow(['Monthly Total', month, f'{month_total:.2f}', ''])
                    
                    for category, amount in self.monthly_totals[month].items():
                        if amount > 0:
                            percentage = (amount / month_total) * 100 if month_total > 0 else 0
                            writer.writerow(['Monthly Category', f'{month} - {category}', f'{amount:.2f}', f'{percentage:.2f}%'])
            
            print(f"CSV report exported to: {filename}")
            
        except IOError as e:
            print(f"Error writing CSV file: {e}")
            raise
    
    def export_to_html(self, filename: str = 'financial_report.html') -> None:
        """Export report data to HTML format."""
        try:
            percentages = self.calculate_percentage_breakdown()
            trends = self.identify_spending_trends()
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Financial Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1, h2 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .trend-positive {{ color: green; }}
                    .trend-negative {{ color: red; }}