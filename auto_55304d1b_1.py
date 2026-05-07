```python
#!/usr/bin/env python3
"""
Monthly Spending Report Visualization Module

This module generates comprehensive monthly spending reports with multiple visualization types:
- Bar charts showing spending by category
- Pie charts displaying spending distribution
- Trend analysis with line charts over time
- Exports reports as PNG and HTML files

The module creates sample spending data and generates interactive visualizations
using matplotlib for static charts and HTML/CSS for web-based reports.

Usage: python script.py
"""

import json
import calendar
import random
from datetime import datetime, timedelta
from pathlib import Path
import base64
import io


class SpendingReportGenerator:
    """Generate monthly spending reports with various visualizations."""
    
    def __init__(self):
        self.categories = [
            "Food & Dining", "Transportation", "Shopping", "Entertainment",
            "Bills & Utilities", "Health & Fitness", "Travel", "Education",
            "Home & Garden", "Personal Care"
        ]
        self.colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
            "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
        ]
        
    def generate_sample_data(self, months=12):
        """Generate sample spending data for the specified number of months."""
        data = []
        base_date = datetime.now() - timedelta(days=30 * months)
        
        for i in range(months):
            month_date = base_date + timedelta(days=30 * i)
            month_data = {
                "month": month_date.strftime("%Y-%m"),
                "month_name": month_date.strftime("%B %Y"),
                "categories": {}
            }
            
            total_budget = random.randint(2000, 5000)
            remaining = total_budget
            
            for j, category in enumerate(self.categories):
                if j == len(self.categories) - 1:
                    amount = remaining
                else:
                    max_amount = remaining // (len(self.categories) - j)
                    amount = random.randint(50, min(max_amount, 800))
                    remaining -= amount
                
                month_data["categories"][category] = max(amount, 0)
            
            data.append(month_data)
        
        return data
    
    def create_bar_chart_html(self, data, month_data):
        """Create HTML bar chart for monthly spending by category."""
        categories = list(month_data["categories"].keys())
        amounts = list(month_data["categories"].values())
        max_amount = max(amounts) if amounts else 1
        
        bars_html = ""
        for i, (category, amount) in enumerate(zip(categories, amounts)):
            height = (amount / max_amount) * 300
            color = self.colors[i % len(self.colors)]
            
            bars_html += f"""
            <div class="bar-container">
                <div class="bar" style="height: {height}px; background-color: {color};"></div>
                <div class="bar-label">{category}</div>
                <div class="bar-value">${amount:,.0f}</div>
            </div>
            """
        
        return f"""
        <div class="chart-container">
            <h3>Monthly Spending by Category - {month_data['month_name']}</h3>
            <div class="bar-chart">
                {bars_html}
            </div>
        </div>
        """
    
    def create_pie_chart_html(self, month_data):
        """Create HTML/CSS pie chart for spending distribution."""
        categories = list(month_data["categories"].keys())
        amounts = list(month_data["categories"].values())
        total = sum(amounts)
        
        if total == 0:
            return "<div class='chart-container'><p>No spending data available</p></div>"
        
        # Calculate percentages and create SVG pie chart
        pie_slices = ""
        cumulative = 0
        
        for i, (category, amount) in enumerate(zip(categories, amounts)):
            percentage = (amount / total) * 100
            start_angle = (cumulative / total) * 360
            end_angle = ((cumulative + amount) / total) * 360
            
            # SVG path for pie slice
            large_arc = 1 if percentage > 50 else 0
            
            start_x = 50 + 40 * math.cos(math.radians(start_angle - 90))
            start_y = 50 + 40 * math.sin(math.radians(start_angle - 90))
            end_x = 50 + 40 * math.cos(math.radians(end_angle - 90))
            end_y = 50 + 40 * math.sin(math.radians(end_angle - 90))
            
            color = self.colors[i % len(self.colors)]
            
            if percentage == 100:
                pie_slices += f"""<circle cx="50" cy="50" r="40" fill="{color}" />"""
            else:
                pie_slices += f"""
                <path d="M 50 50 L {start_x} {start_y} A 40 40 0 {large_arc} 1 {end_x} {end_y} Z" 
                      fill="{color}" stroke="white" stroke-width="1"/>
                """
            
            cumulative += amount
        
        # Create legend
        legend_html = ""
        for i, (category, amount) in enumerate(zip(categories, amounts)):
            percentage = (amount / total) * 100
            color = self.colors[i % len(self.colors)]
            legend_html += f"""
            <div class="legend-item">
                <div class="legend-color" style="background-color: {color};"></div>
                <span>{category}: ${amount:,.0f} ({percentage:.1f}%)</span>
            </div>
            """
        
        return f"""
        <div class="chart-container">
            <h3>Spending Distribution - {month_data['month_name']}</h3>
            <div class="pie-chart-container">
                <svg viewBox="0 0 100 100" class="pie-chart">
                    {pie_slices}
                </svg>
                <div class="legend">
                    {legend_html}
                </div>
            </div>
        </div>
        """
    
    def create_trend_chart_html(self, data):
        """Create HTML trend analysis chart."""
        months = [d["month_name"] for d in data]
        totals = [sum(d["categories"].values()) for d in data]
        
        if not totals:
            return "<div class='chart-container'><p>No trend data available</p></div>"
        
        max_total = max(totals)
        min_total = min(totals)
        
        # Create SVG line chart
        points = []
        for i, total in enumerate(totals):
            x = (i / (len(totals) - 1)) * 80 + 10 if len(totals) > 1 else 50
            y = 80 - ((total - min_total) / (max_total - min_total) * 60) if max_total > min_total else 40
            points.append(f"{x},{y}")
        
        polyline = " ".join(points)
        
        # Create data points
        data_points = ""
        for i, (month, total) in enumerate(zip(months, totals)):
            x = (i / (len(totals) - 1)) * 80 + 10 if len(totals) > 1 else 50
            y = 80 - ((total - min_total) / (max_total - min_total) * 60) if max_total > min_total else 40
            data_points += f"""
            <circle cx="{x}" cy="{y}" r="3" fill="#FF6B6B" stroke="white" stroke-width="2