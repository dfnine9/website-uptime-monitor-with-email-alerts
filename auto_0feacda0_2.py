```python
"""
Monthly Financial Insights Report Generator

This module generates comprehensive monthly financial reports with visualizations
showing spending breakdown, trend analysis, and budget variance calculations.

Features:
- Spending category breakdown with pie charts
- Monthly trend analysis with line graphs
- Budget vs actual variance calculations
- ASCII-based visualizations (no external plotting dependencies)
- Simulated financial data for demonstration

Usage: python script.py
"""

import json
import random
import datetime
from collections import defaultdict
import math


class FinancialReportGenerator:
    def __init__(self):
        self.categories = [
            "Housing", "Food", "Transportation", "Healthcare", 
            "Entertainment", "Utilities", "Shopping", "Savings"
        ]
        self.months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        
    def generate_sample_data(self):
        """Generate sample financial data for demonstration"""
        try:
            data = {
                "monthly_spending": {},
                "budgets": {
                    "Housing": 2000,
                    "Food": 600,
                    "Transportation": 400,
                    "Healthcare": 300,
                    "Entertainment": 200,
                    "Utilities": 250,
                    "Shopping": 300,
                    "Savings": 500
                }
            }
            
            for month in self.months:
                data["monthly_spending"][month] = {}
                for category in self.categories:
                    base_amount = data["budgets"][category]
                    # Add some variance to make it realistic
                    variance = random.uniform(0.7, 1.3)
                    amount = round(base_amount * variance, 2)
                    data["monthly_spending"][month][category] = amount
                    
            return data
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}

    def create_ascii_bar_chart(self, data, title, width=50):
        """Create ASCII bar chart"""
        try:
            print(f"\n{title}")
            print("=" * len(title))
            
            if not data:
                print("No data available")
                return
                
            max_value = max(data.values()) if data.values() else 1
            
            for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
                bar_length = int((value / max_value) * width)
                bar = "█" * bar_length
                print(f"{label:15} │{bar:<{width}} │ ${value:,.2f}")
                
        except Exception as e:
            print(f"Error creating bar chart: {e}")

    def create_ascii_line_chart(self, data, title, height=10):
        """Create ASCII line chart for trends"""
        try:
            print(f"\n{title}")
            print("=" * len(title))
            
            if not data:
                print("No data available")
                return
                
            months = list(data.keys())
            values = [sum(spending.values()) for spending in data.values()]
            
            if not values:
                print("No values to plot")
                return
                
            min_val, max_val = min(values), max(values)
            range_val = max_val - min_val if max_val != min_val else 1
            
            # Create the chart
            for i in range(height, 0, -1):
                line = ""
                threshold = min_val + (range_val * i / height)
                for j, value in enumerate(values):
                    if value >= threshold:
                        line += " ██ "
                    else:
                        line += "    "
                print(f"{threshold:6.0f}│{line}")
            
            # X-axis
            print("      └" + "────" * len(months))
            x_labels = "       "
            for month in months:
                x_labels += f"{month:4}"
            print(x_labels)
            
            # Show actual values
            print("\nActual values:")
            for month, value in zip(months, values):
                print(f"{month}: ${value:,.2f}")
                
        except Exception as e:
            print(f"Error creating line chart: {e}")

    def calculate_budget_variance(self, actual_spending, budgets):
        """Calculate budget variance analysis"""
        try:
            print("\n📊 Budget Variance Analysis")
            print("=" * 30)
            
            total_budget = sum(budgets.values())
            total_actual = sum(actual_spending.values())
            overall_variance = total_actual - total_budget
            
            print(f"Overall Budget: ${total_budget:,.2f}")
            print(f"Actual Spending: ${total_actual:,.2f}")
            print(f"Variance: ${overall_variance:,.2f} ({overall_variance/total_budget*100:+.1f}%)")
            
            if overall_variance > 0:
                print("❌ OVER BUDGET")
            else:
                print("✅ UNDER BUDGET")
                
            print("\nCategory Breakdown:")
            print("-" * 50)
            
            for category in budgets:
                budget = budgets[category]
                actual = actual_spending.get(category, 0)
                variance = actual - budget
                variance_pct = (variance / budget * 100) if budget > 0 else 0
                
                status = "❌" if variance > 0 else "✅"
                print(f"{category:15} │ Budget: ${budget:6.2f} │ Actual: ${actual:6.2f} │ "
                      f"Variance: ${variance:+7.2f} ({variance_pct:+5.1f}%) {status}")
                      
        except Exception as e:
            print(f"Error calculating budget variance: {e}")

    def analyze_spending_trends(self, monthly_data):
        """Analyze spending trends across months"""
        try:
            print("\n📈 Spending Trend Analysis")
            print("=" * 30)
            
            # Calculate month-over-month changes
            months = list(monthly_data.keys())
            if len(months) < 2:
                print("Need at least 2 months of data for trend analysis")
                return
                
            for i in range(1, len(months)):
                prev_month = months[i-1]
                curr_month = months[i]
                
                prev_total = sum(monthly_data[prev_month].values())
                curr_total = sum(monthly_data[curr_month].values())
                change = curr_total - prev_total
                change_pct = (change / prev_total * 100) if prev_total > 0 else 0
                
                trend = "📈" if change > 0 else "📉"
                print(f"{prev_month} → {curr_month}: ${change:+,.2f} ({change_pct:+.1f}%) {trend}")
                
            # Find biggest spending categories
            category_totals = defaultdict(float)
            for month_data in monthly_data.values():
                for category, amount in month_data.items():
                    category_totals[category] += amount
                    
            print(f"\nTop Spending Categories (Total):")
            for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]:
                avg_monthly = total / len(monthly_data)
                print(f"  {category}: ${total:,.2f} (avg: ${avg_monthly:,.2f}/month)")
                
        except Exception as e:
            print(f"Error analyzing spending trends: {e}")

    def generate_insights(self, data):
        """Generate actionable financial insights"""
        try:
            print("\n💡 Financial Insights & Recommendations")
            print("=" * 45)
            
            # Calculate average monthly spending
            monthly_totals = []
            for month_data in data["monthly_spending"].values():
                monthly_totals.append(sum(month_data.values()))
                
            if not monthly_totals:
                print("No spending data available for insights")