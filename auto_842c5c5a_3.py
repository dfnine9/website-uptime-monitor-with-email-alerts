```python
"""
Monthly Expense Reporting System

This module provides a comprehensive expense tracking and reporting system that:
- Generates monthly expense reports with visualizations
- Exports reports to HTML format (self-contained)
- Provides actionable budget recommendations based on spending patterns
- Tracks expenses by category and identifies spending trends

Features:
- ASCII-based charts for visualization (no external chart libraries required)
- HTML report generation with embedded CSS
- Budget variance analysis and recommendations
- Expense categorization and trend analysis
- Data persistence using JSON format
"""

import json
import os
import sys
import datetime
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import calendar

class ExpenseReportingSystem:
    def __init__(self, data_file: str = "expenses.json"):
        self.data_file = data_file
        self.expenses = self.load_expenses()
        self.categories = [
            "Housing", "Transportation", "Food", "Utilities", "Healthcare",
            "Entertainment", "Shopping", "Education", "Insurance", "Other"
        ]
        
    def load_expenses(self) -> List[Dict]:
        """Load expenses from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading expenses: {e}")
            return []
    
    def save_expenses(self):
        """Save expenses to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.expenses, f, indent=2)
        except Exception as e:
            print(f"Error saving expenses: {e}")
    
    def add_expense(self, amount: float, category: str, description: str, date: str = None):
        """Add a new expense"""
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        expense = {
            "amount": amount,
            "category": category,
            "description": description,
            "date": date
        }
        self.expenses.append(expense)
        self.save_expenses()
    
    def get_monthly_expenses(self, year: int, month: int) -> List[Dict]:
        """Get expenses for a specific month"""
        monthly_expenses = []
        target_month = f"{year}-{month:02d}"
        
        for expense in self.expenses:
            if expense["date"].startswith(target_month):
                monthly_expenses.append(expense)
        
        return monthly_expenses
    
    def calculate_category_totals(self, expenses: List[Dict]) -> Dict[str, float]:
        """Calculate total spending by category"""
        totals = defaultdict(float)
        for expense in expenses:
            totals[expense["category"]] += expense["amount"]
        return dict(totals)
    
    def generate_ascii_bar_chart(self, data: Dict[str, float], title: str, max_width: int = 50) -> str:
        """Generate ASCII bar chart"""
        if not data:
            return f"{title}\nNo data available\n"
        
        max_value = max(data.values())
        chart = f"\n{title}\n" + "=" * len(title) + "\n"
        
        for category, amount in sorted(data.items(), key=lambda x: x[1], reverse=True):
            bar_length = int((amount / max_value) * max_width) if max_value > 0 else 0
            bar = "█" * bar_length
            chart += f"{category:12} |{bar:<{max_width}} ${amount:,.2f}\n"
        
        return chart
    
    def calculate_trends(self, current_month_expenses: List[Dict], previous_month_expenses: List[Dict]) -> Dict[str, Dict]:
        """Calculate spending trends compared to previous month"""
        current_totals = self.calculate_category_totals(current_month_expenses)
        previous_totals = self.calculate_category_totals(previous_month_expenses)
        
        trends = {}
        all_categories = set(current_totals.keys()) | set(previous_totals.keys())
        
        for category in all_categories:
            current = current_totals.get(category, 0)
            previous = previous_totals.get(category, 0)
            
            if previous > 0:
                change_percent = ((current - previous) / previous) * 100
            else:
                change_percent = 100 if current > 0 else 0
            
            trends[category] = {
                "current": current,
                "previous": previous,
                "change_amount": current - previous,
                "change_percent": change_percent
            }
        
        return trends
    
    def generate_budget_recommendations(self, expenses: List[Dict], trends: Dict[str, Dict]) -> List[str]:
        """Generate actionable budget recommendations"""
        recommendations = []
        category_totals = self.calculate_category_totals(expenses)
        total_spending = sum(category_totals.values())
        
        # High spending categories
        high_spend_threshold = total_spending * 0.3
        for category, amount in category_totals.items():
            if amount > high_spend_threshold:
                recommendations.append(f"🔍 {category} represents {(amount/total_spending)*100:.1f}% of total spending (${amount:,.2f}). Consider reviewing this category for potential savings.")
        
        # Trending up categories
        for category, trend in trends.items():
            if trend["change_percent"] > 20 and trend["current"] > 100:
                recommendations.append(f"📈 {category} spending increased by {trend['change_percent']:.1f}% from last month. Monitor this trend to avoid budget overruns.")
        
        # General recommendations
        if total_spending > 0:
            entertainment_percent = (category_totals.get("Entertainment", 0) / total_spending) * 100
            if entertainment_percent > 15:
                recommendations.append(f"🎯 Entertainment spending is {entertainment_percent:.1f}% of total budget. Consider setting a monthly entertainment limit.")
            
            food_percent = (category_totals.get("Food", 0) / total_spending) * 100
            if food_percent > 25:
                recommendations.append(f"🍽️ Food expenses are {food_percent:.1f}% of budget. Meal planning could help reduce costs.")
        
        if not recommendations:
            recommendations.append("✅ Spending patterns look healthy! Continue monitoring monthly expenses.")
        
        return recommendations
    
    def generate_html_report(self, year: int, month: int) -> str:
        """Generate HTML report"""
        month_name = calendar.month_name[month]
        current_expenses = self.get_monthly_expenses(year, month)
        previous_month = month - 1 if month > 1 else 12
        previous_year = year if month > 1 else year - 1
        previous_expenses = self.get_monthly_expenses(previous_year, previous_month)
        
        category_totals = self.calculate_category_totals(current_expenses)
        trends = self.calculate_trends(current_expenses, previous_expenses)
        recommendations = self.generate_budget_recommendations(current_expenses, trends)
        total_spending = sum(category_totals.values())
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Expense Report - {month_name} {year}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
                h2 {{ color: #555; margin-top: 30px; }}
                .summary {{