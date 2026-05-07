```python
#!/usr/bin/env python3
"""
Financial Spending Insights Reporting Module

This module generates comprehensive spending analysis reports including:
- Monthly and weekly spending summaries
- Category-based spending breakdowns
- Trend analysis over time periods
- Visual charts and graphs for data visualization

The module uses sample transaction data to demonstrate functionality.
All visualizations are displayed using matplotlib with fallback to text-based output.

Usage: python script.py
"""

import json
import datetime
import calendar
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Using text-based output only.")

class SpendingAnalyzer:
    """Analyzes spending data and generates comprehensive reports."""
    
    def __init__(self, transactions: List[Dict[str, Any]]):
        """
        Initialize with transaction data.
        
        Args:
            transactions: List of transaction dictionaries with keys:
                         'date', 'amount', 'category', 'description'
        """
        self.transactions = transactions
        self.processed_data = self._process_transactions()
    
    def _process_transactions(self) -> Dict[str, Any]:
        """Process raw transactions into structured data for analysis."""
        try:
            processed = {
                'by_month': defaultdict(float),
                'by_week': defaultdict(float),
                'by_category': defaultdict(float),
                'by_date': defaultdict(float),
                'monthly_categories': defaultdict(lambda: defaultdict(float))
            }
            
            for transaction in self.transactions:
                date_obj = datetime.datetime.strptime(transaction['date'], '%Y-%m-%d')
                amount = abs(float(transaction['amount']))  # Use absolute value for spending
                category = transaction['category']
                
                # Monthly aggregation
                month_key = date_obj.strftime('%Y-%m')
                processed['by_month'][month_key] += amount
                
                # Weekly aggregation (ISO week)
                year, week, _ = date_obj.isocalendar()
                week_key = f"{year}-W{week:02d}"
                processed['by_week'][week_key] += amount
                
                # Category aggregation
                processed['by_category'][category] += amount
                
                # Daily aggregation
                date_key = transaction['date']
                processed['by_date'][date_key] += amount
                
                # Monthly category breakdown
                processed['monthly_categories'][month_key][category] += amount
            
            return processed
        except Exception as e:
            print(f"Error processing transactions: {e}")
            return {}
    
    def generate_monthly_summary(self) -> str:
        """Generate monthly spending summary."""
        try:
            summary = "\n" + "="*50 + "\n"
            summary += "MONTHLY SPENDING SUMMARY\n"
            summary += "="*50 + "\n"
            
            monthly_data = dict(sorted(self.processed_data['by_month'].items()))
            
            for month, amount in monthly_data.items():
                year, month_num = month.split('-')
                month_name = calendar.month_name[int(month_num)]
                summary += f"{month_name} {year}: ${amount:,.2f}\n"
            
            # Calculate monthly average
            if monthly_data:
                avg_monthly = sum(monthly_data.values()) / len(monthly_data)
                summary += f"\nAverage Monthly Spending: ${avg_monthly:,.2f}\n"
            
            return summary
        except Exception as e:
            return f"Error generating monthly summary: {e}"
    
    def generate_weekly_summary(self) -> str:
        """Generate weekly spending summary."""
        try:
            summary = "\n" + "="*50 + "\n"
            summary += "WEEKLY SPENDING SUMMARY (Last 8 Weeks)\n"
            summary += "="*50 + "\n"
            
            weekly_data = dict(sorted(self.processed_data['by_week'].items()))
            recent_weeks = list(weekly_data.items())[-8:]  # Last 8 weeks
            
            for week, amount in recent_weeks:
                summary += f"{week}: ${amount:,.2f}\n"
            
            # Calculate weekly average
            if recent_weeks:
                avg_weekly = sum(amount for _, amount in recent_weeks) / len(recent_weeks)
                summary += f"\nAverage Weekly Spending (Last 8 weeks): ${avg_weekly:,.2f}\n"
            
            return summary
        except Exception as e:
            return f"Error generating weekly summary: {e}"
    
    def generate_category_breakdown(self) -> str:
        """Generate category-based spending breakdown."""
        try:
            summary = "\n" + "="*50 + "\n"
            summary += "SPENDING BY CATEGORY\n"
            summary += "="*50 + "\n"
            
            total_spending = sum(self.processed_data['by_category'].values())
            sorted_categories = sorted(
                self.processed_data['by_category'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for category, amount in sorted_categories:
                percentage = (amount / total_spending * 100) if total_spending > 0 else 0
                summary += f"{category}: ${amount:,.2f} ({percentage:.1f}%)\n"
            
            summary += f"\nTotal Spending: ${total_spending:,.2f}\n"
            return summary
        except Exception as e:
            return f"Error generating category breakdown: {e}"
    
    def generate_trend_analysis(self) -> str:
        """Generate trend analysis."""
        try:
            summary = "\n" + "="*50 + "\n"
            summary += "TREND ANALYSIS\n"
            summary += "="*50 + "\n"
            
            monthly_data = dict(sorted(self.processed_data['by_month'].items()))
            months = list(monthly_data.keys())
            amounts = list(monthly_data.values())
            
            if len(amounts) < 2:
                return summary + "Insufficient data for trend analysis.\n"
            
            # Calculate month-over-month changes
            summary += "Month-over-Month Changes:\n"
            for i in range(1, len(months)):
                prev_amount = amounts[i-1]
                curr_amount = amounts[i]
                change = curr_amount - prev_amount
                change_pct = (change / prev_amount * 100) if prev_amount > 0 else 0
                
                change_str = "↑" if change > 0 else "↓" if change < 0 else "→"
                summary += f"{months[i]}: {change_str} ${change:+,.2f} ({change_pct:+.1f}%)\n"
            
            # Identify highest and lowest spending months
            max_month = max(monthly_data, key=monthly_data.get)
            min_month = min(monthly_data, key=monthly_data.get)
            
            summary += f"\nHighest Spending: {max_month} (${monthly_data[max_month]:,.2f})\n"
            summary += f"Lowest Spending: {min_month} (${monthly_data[min_month]:,.2f})\n"
            
            return summary
        except Exception as e:
            return f"Error generating trend analysis: {e}"
    
    def create_visualizations(self):
        """Create visual charts using matplotlib."""
        if not HAS_MATPLOTLIB:
            print("\nVisualization skipped - matplotlib not available")
            return
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Spending Insights Dashboard', fontsize=16, fontweight='bold')
            
            # 1. Monthly spending trend
            monthly_data = dict(sorted(self.processed_data['by_month'].items()))