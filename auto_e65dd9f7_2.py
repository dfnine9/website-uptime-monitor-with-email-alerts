```python
#!/usr/bin/env python3
"""
Automated Email Template Generator for Salary Analysis Daily Digest

This module generates professional daily digest emails containing salary analysis,
trends, charts, and key insights. It creates HTML email templates with embedded
data visualizations and formatted tables for executive reporting.

Features:
- Generates responsive HTML email templates
- Creates ASCII charts for text-based viewing
- Formats salary data into professional tables
- Includes key insights and trend analysis
- Self-contained with minimal dependencies
- Outputs ready-to-send email content

Usage:
    python script.py

Dependencies:
    - Standard library modules only
    - httpx (for potential API calls)
    - anthropic (for AI-powered insights)
"""

import json
import datetime
import statistics
import random
from typing import Dict, List, Tuple, Any
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import base64

class SalaryAnalysisDigestGenerator:
    """Generates automated salary analysis digest emails with visualizations."""
    
    def __init__(self):
        self.current_date = datetime.datetime.now()
        self.sample_data = self._generate_sample_data()
        
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample salary data for demonstration purposes."""
        try:
            positions = [
                "Software Engineer", "Data Scientist", "Product Manager", 
                "DevOps Engineer", "Frontend Developer", "Backend Developer",
                "Full Stack Developer", "UX Designer", "Marketing Manager",
                "Sales Representative", "HR Manager", "Finance Analyst"
            ]
            
            locations = ["San Francisco", "New York", "Seattle", "Austin", "Boston", "Denver"]
            
            data = {
                "positions": [],
                "trends": [],
                "market_insights": []
            }
            
            # Generate position data
            for pos in positions:
                base_salary = random.randint(70000, 200000)
                data["positions"].append({
                    "title": pos,
                    "avg_salary": base_salary,
                    "min_salary": int(base_salary * 0.7),
                    "max_salary": int(base_salary * 1.5),
                    "location": random.choice(locations),
                    "growth_rate": round(random.uniform(-5.0, 15.0), 2)
                })
            
            # Generate trend data (last 7 days)
            for i in range(7):
                date = self.current_date - datetime.timedelta(days=i)
                data["trends"].append({
                    "date": date.strftime("%Y-%m-%d"),
                    "avg_salary": random.randint(85000, 130000),
                    "job_postings": random.randint(50, 200),
                    "market_activity": random.uniform(0.8, 1.2)
                })
            
            # Generate market insights
            data["market_insights"] = [
                "Tech salaries increased 8.5% YoY in Q4",
                "Remote positions offer 12% premium over on-site",
                "AI/ML roles showing strongest growth at 23% increase",
                "Entry-level positions up 6% due to talent shortage",
                "Senior roles experiencing wage compression in certain markets"
            ]
            
            return data
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {"positions": [], "trends": [], "market_insights": []}
    
    def _create_ascii_chart(self, data: List[Tuple[str, float]], title: str) -> str:
        """Create ASCII bar chart for email content."""
        try:
            if not data:
                return f"{title}\nNo data available"
            
            max_val = max(val for _, val in data)
            chart_width = 40
            
            chart = f"\n{title}\n" + "=" * len(title) + "\n"
            
            for label, value in data:
                bar_length = int((value / max_val) * chart_width) if max_val > 0 else 0
                bar = "█" * bar_length + "░" * (chart_width - bar_length)
                chart += f"{label[:20]:20} │{bar}│ {value:,.0f}\n"
            
            return chart
            
        except Exception as e:
            return f"{title}\nError creating chart: {e}"
    
    def _generate_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics from salary data."""
        try:
            salaries = [pos["avg_salary"] for pos in self.sample_data["positions"]]
            growth_rates = [pos["growth_rate"] for pos in self.sample_data["positions"]]
            
            return {
                "total_positions": len(self.sample_data["positions"]),
                "avg_salary": statistics.mean(salaries) if salaries else 0,
                "median_salary": statistics.median(salaries) if salaries else 0,
                "salary_range": (min(salaries), max(salaries)) if salaries else (0, 0),
                "avg_growth": statistics.mean(growth_rates) if growth_rates else 0,
                "total_postings": sum(trend["job_postings"] for trend in self.sample_data["trends"])
            }
            
        except Exception as e:
            print(f"Error calculating summary stats: {e}")
            return {
                "total_positions": 0, "avg_salary": 0, "median_salary": 0,
                "salary_range": (0, 0), "avg_growth": 0, "total_postings": 0
            }
    
    def _create_html_template(self, stats: Dict[str, Any]) -> str:
        """Generate HTML email template with embedded styling."""
        try:
            # Create salary chart data
            chart_data = [(pos["title"], pos["avg_salary"]) for pos in self.sample_data["positions"][:8]]
            ascii_chart = self._create_ascii_chart(chart_data, "Top Salary Positions")
            
            # Create trend chart
            trend_data = [(trend["date"], trend["avg_salary"]) for trend in self.sample_data["trends"]]
            trend_chart = self._create_ascii_chart(trend_data, "7-Day Salary Trends")
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Salary Analysis Digest</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 3px solid #007acc; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #007acc; margin: 0; font-size: 28px; }}
        .date {{ color: #666; font-size: 14px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 6px; text-align: center; border-left: 4px solid #007acc; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #007acc; }}
        .stat-label {{ color: #666; font-size: 14px; }}
        .section {{ margin-bottom: 30