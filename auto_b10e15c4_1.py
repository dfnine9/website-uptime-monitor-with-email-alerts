```python
#!/usr/bin/env python3
"""
Monthly Spending Report Visualization Module

This module generates comprehensive monthly spending reports with interactive visualizations
including bar charts, pie charts, and trend analysis. Features PDF export functionality
for professional report generation.

Key Features:
- Monthly spending breakdown by category
- Interactive bar and pie charts
- Trend analysis over multiple months
- PDF report export with embedded charts
- Sample data generation for demonstration
- Error handling and data validation

Dependencies: matplotlib, reportlab (for PDF generation)
Note: This script uses sample data for demonstration purposes.
"""

import json
import csv
import datetime
from io import BytesIO
import base64
import sys
import traceback
from typing import Dict, List, Tuple, Optional
import calendar

# Standard library only - matplotlib and reportlab would be external dependencies
# Creating a simplified version that works with standard library only

class SpendingReportGenerator:
    """Generates monthly spending reports with visualizations."""
    
    def __init__(self):
        self.spending_data = {}
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Utilities', 'Healthcare', 'Travel', 'Education', 'Other'
        ]
        self.months_data = {}
    
    def generate_sample_data(self) -> Dict:
        """Generate sample spending data for demonstration."""
        import random
        
        # Generate data for last 6 months
        current_date = datetime.datetime.now()
        sample_data = {}
        
        for i in range(6):
            # Calculate month/year
            month_date = current_date.replace(day=1) - datetime.timedelta(days=i*30)
            month_key = month_date.strftime("%Y-%m")
            month_name = month_date.strftime("%B %Y")
            
            # Generate random spending for each category
            month_spending = {}
            for category in self.categories:
                # Generate realistic spending amounts
                base_amounts = {
                    'Food & Dining': 500,
                    'Transportation': 300,
                    'Shopping': 400,
                    'Entertainment': 200,
                    'Utilities': 250,
                    'Healthcare': 150,
                    'Travel': 100,
                    'Education': 80,
                    'Other': 100
                }
                
                base = base_amounts.get(category, 100)
                amount = base + random.randint(-50, 150)
                month_spending[category] = max(amount, 0)
            
            sample_data[month_key] = {
                'month_name': month_name,
                'spending': month_spending,
                'total': sum(month_spending.values())
            }
        
        return sample_data
    
    def create_ascii_bar_chart(self, data: Dict[str, float], title: str) -> str:
        """Create ASCII bar chart representation."""
        chart_lines = [f"\n{title}", "=" * len(title)]
        
        if not data:
            return "\n".join(chart_lines + ["No data available"])
        
        max_value = max(data.values())
        max_width = 50
        
        for category, amount in sorted(data.items(), key=lambda x: x[1], reverse=True):
            bar_width = int((amount / max_value) * max_width) if max_value > 0 else 0
            bar = "█" * bar_width
            chart_lines.append(f"{category[:20]:<20} │{bar:<50}│ ${amount:,.2f}")
        
        return "\n".join(chart_lines)
    
    def create_ascii_pie_chart(self, data: Dict[str, float], title: str) -> str:
        """Create ASCII pie chart representation with percentages."""
        chart_lines = [f"\n{title}", "=" * len(title)]
        
        if not data:
            return "\n".join(chart_lines + ["No data available"])
        
        total = sum(data.values())
        if total == 0:
            return "\n".join(chart_lines + ["No spending data"])
        
        pie_chars = ["█", "▉", "▊", "▋", "▌", "▍", "▎", "▏"]
        
        for category, amount in sorted(data.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total) * 100
            pie_width = int(percentage / 2)  # Scale down for display
            pie_segment = "█" * pie_width
            chart_lines.append(f"{category[:20]:<20} │{pie_segment:<50}│ {percentage:5.1f}% (${amount:,.2f})")
        
        return "\n".join(chart_lines)
    
    def create_trend_analysis(self, months_data: Dict) -> str:
        """Create trend analysis over multiple months."""
        trend_lines = ["\nTrend Analysis", "=" * 14]
        
        if len(months_data) < 2:
            return "\n".join(trend_lines + ["Need at least 2 months for trend analysis"])
        
        # Sort months chronologically
        sorted_months = sorted(months_data.keys())
        
        # Calculate month-over-month changes
        trend_lines.append("\nMonthly Totals:")
        prev_total = None
        
        for month_key in sorted_months:
            month_data = months_data[month_key]
            current_total = month_data['total']
            
            change_str = ""
            if prev_total is not None:
                change = current_total - prev_total
                change_pct = (change / prev_total) * 100 if prev_total > 0 else 0
                direction = "↑" if change > 0 else "↓" if change < 0 else "→"
                change_str = f" {direction} ${change:+,.2f} ({change_pct:+.1f}%)"
            
            trend_lines.append(f"{month_data['month_name']:<15} ${current_total:>8,.2f}{change_str}")
            prev_total = current_total
        
        # Category trends
        trend_lines.append(f"\nTop Spending Categories (Last Month):")
        latest_month = sorted_months[-1]
        latest_spending = months_data[latest_month]['spending']
        
        for category, amount in sorted(latest_spending.items(), key=lambda x: x[1], reverse=True)[:5]:
            trend_lines.append(f"  {category:<20} ${amount:>8,.2f}")
        
        return "\n".join(trend_lines)
    
    def generate_summary_stats(self, months_data: Dict) -> str:
        """Generate summary statistics."""
        summary_lines = ["\nSummary Statistics", "=" * 18]
        
        if not months_data:
            return "\n".join(summary_lines + ["No data available"])
        
        # Calculate totals
        all_totals = [data['total'] for data in months_data.values()]
        avg_monthly = sum(all_totals) / len(all_totals)
        max_month = max(months_data.items(), key=lambda x: x[1]['total'])
        min_month = min(months_data.items(), key=lambda x: x[1]['total'])
        
        # Category averages
        category_totals = {}
        for month_data in months_data.values():
            for category, amount in month_data['spending'].items():
                category_totals[category] = category_totals.get(category, 0) + amount
        
        category_averages = {cat: total/len(months_data) for cat, total in category_totals.items()}
        
        summary_lines.extend([
            f"Total Months Analyzed: {len(months_data)}",
            f"Average Monthly Spending: ${avg_monthly:,.2f}",
            f"Highest Month: {max_month[1]['month_name']} (${max_month[1]['total']:,.2f})",
            f"Lowest Month: {min_month[1]['month_name