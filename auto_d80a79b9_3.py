```python
#!/usr/bin/env python3
"""
Interactive Financial Report Generator

This module creates comprehensive HTML reports with interactive charts and tables
for spending analysis. Features include:
- Interactive spending breakdown charts (pie, bar, line charts)
- Trend visualizations with time-series data
- Actionable financial insights and recommendations
- Export capabilities to PDF format
- Self-contained with minimal dependencies

The generator produces HTML reports with embedded JavaScript for interactivity
and includes PDF export functionality using browser print-to-PDF capabilities.
"""

import json
import datetime
import os
import sys
from typing import Dict, List, Any, Optional
import subprocess
import tempfile
import webbrowser
from urllib.parse import quote


class FinancialReportGenerator:
    """Generates interactive HTML financial reports with PDF export capabilities."""
    
    def __init__(self):
        self.data = {
            "spending_categories": {},
            "monthly_trends": {},
            "transactions": [],
            "insights": []
        }
        
    def add_spending_data(self, category: str, amount: float, month: str = None):
        """Add spending data for a category."""
        if month is None:
            month = datetime.datetime.now().strftime("%Y-%m")
            
        if category not in self.data["spending_categories"]:
            self.data["spending_categories"][category] = 0
        self.data["spending_categories"][category] += amount
        
        if month not in self.data["monthly_trends"]:
            self.data["monthly_trends"][month] = {}
        if category not in self.data["monthly_trends"][month]:
            self.data["monthly_trends"][month][category] = 0
        self.data["monthly_trends"][month][category] += amount
        
        self.data["transactions"].append({
            "category": category,
            "amount": amount,
            "month": month,
            "date": datetime.datetime.now().isoformat()
        })
    
    def generate_insights(self):
        """Generate actionable financial insights."""
        insights = []
        
        try:
            total_spending = sum(self.data["spending_categories"].values())
            if total_spending > 0:
                # Find highest spending category
                max_category = max(self.data["spending_categories"], 
                                 key=self.data["spending_categories"].get)
                max_amount = self.data["spending_categories"][max_category]
                max_percentage = (max_amount / total_spending) * 100
                
                insights.append({
                    "type": "warning" if max_percentage > 40 else "info",
                    "title": f"Highest Spending: {max_category}",
                    "message": f"${max_amount:,.2f} ({max_percentage:.1f}% of total)",
                    "action": f"Consider reducing {max_category} expenses by 10-15%"
                })
                
                # Monthly trend analysis
                if len(self.data["monthly_trends"]) >= 2:
                    months = sorted(self.data["monthly_trends"].keys())
                    if len(months) >= 2:
                        current_month = months[-1]
                        previous_month = months[-2]
                        
                        current_total = sum(self.data["monthly_trends"][current_month].values())
                        previous_total = sum(self.data["monthly_trends"][previous_month].values())
                        
                        if current_total > previous_total:
                            increase = ((current_total - previous_total) / previous_total) * 100
                            insights.append({
                                "type": "warning",
                                "title": "Spending Increase Detected",
                                "message": f"Spending increased by {increase:.1f}% from last month",
                                "action": "Review recent expenses and identify areas to cut back"
                            })
                        else:
                            decrease = ((previous_total - current_total) / previous_total) * 100
                            insights.append({
                                "type": "success",
                                "title": "Great Job!",
                                "message": f"Spending decreased by {decrease:.1f}% from last month",
                                "action": "Continue current spending habits"
                            })
            
            self.data["insights"] = insights
            
        except Exception as e:
            print(f"Error generating insights: {e}", file=sys.stderr)
            self.data["insights"] = [{
                "type": "info",
                "title": "Analysis Available",
                "message": "Add more data for detailed insights",
                "action": "Continue tracking expenses"
            }]
    
    def generate_html_report(self) -> str:
        """Generate the complete HTML report."""
        try:
            categories_json = json.dumps(list(self.data["spending_categories"].keys()))
            amounts_json = json.dumps(list(self.data["spending_categories"].values()))
            
            months = sorted(self.data["monthly_trends"].keys())
            monthly_data = {}
            for category in self.data["spending_categories"].keys():
                monthly_data[category] = [
                    self.data["monthly_trends"].get(month, {}).get(category, 0) 
                    for month in months
                ]
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Spending Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            background: #f5f7fa;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px; 
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header h1 {{ 
            color: #2c3e50; 
            margin-bottom: 10px; 
        }}
        .header p {{ 
            color: #7f8c8d; 
            font-size: 16px;
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }}
        .card {{ 
            background: white; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            overflow: hidden;
        }}
        .card-header {{ 
            background: #34495e; 
            color: white; 
            padding: 20px; 
            font-size: 18px; 
            font-weight: bold;
        }}
        .card-body {{ 
            padding: 20px; 
        }}
        .chart-container {{ 
            position: relative; 
            height: 300px; 
            margin: 20px 0;
        }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
        }}
        th, td {{ 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }}
        th {{ 
            background-color: #f8f9fa; 
            font-weight: bold;
        }}
        tr:hover {{ 
            background-color: #f5f5f5; 
        }}
        .insight {{ 
            margin: 10px 0