```python
#!/usr/bin/env python3
"""
Financial Data Analysis Module

This module provides comprehensive spending analysis capabilities including:
- Spending summaries by category with statistical insights
- Top spending pattern identification and ranking
- Monthly and weekly trend analysis with growth calculations
- Transaction frequency and average amount analysis

The module processes categorized transaction data and generates detailed
financial insights to help users understand their spending behaviors.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import calendar


class SpendingAnalyzer:
    """Analyzes spending patterns from categorized transaction data."""
    
    def __init__(self):
        self.transactions = []
        self.categories = set()
    
    def load_sample_data(self) -> None:
        """Generate sample transaction data for analysis."""
        sample_data = [
            {"date": "2024-01-15", "amount": 45.67, "category": "Groceries", "description": "Whole Foods"},
            {"date": "2024-01-16", "amount": 12.99, "category": "Entertainment", "description": "Netflix"},
            {"date": "2024-01-18", "amount": 89.50, "category": "Dining", "description": "Restaurant dinner"},
            {"date": "2024-01-20", "amount": 156.78, "category": "Groceries", "description": "Costco bulk shopping"},
            {"date": "2024-01-22", "amount": 25.00, "category": "Transportation", "description": "Gas station"},
            {"date": "2024-01-25", "amount": 78.99, "category": "Shopping", "description": "Amazon purchase"},
            {"date": "2024-01-28", "amount": 34.56, "category": "Dining", "description": "Lunch"},
            {"date": "2024-02-01", "amount": 67.89, "category": "Groceries", "description": "Local market"},
            {"date": "2024-02-03", "amount": 120.00, "category": "Entertainment", "description": "Concert tickets"},
            {"date": "2024-02-05", "amount": 45.67, "category": "Transportation", "description": "Uber ride"},
            {"date": "2024-02-08", "amount": 23.45, "category": "Dining", "description": "Coffee shop"},
            {"date": "2024-02-10", "amount": 189.99, "category": "Shopping", "description": "Clothing store"},
            {"date": "2024-02-12", "amount": 56.78, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-02-15", "amount": 98.76, "category": "Entertainment", "description": "Movie night"},
            {"date": "2024-02-18", "amount": 134.50, "category": "Dining", "description": "Date night"},
            {"date": "2024-02-20", "amount": 67.89, "category": "Transportation", "description": "Car maintenance"},
            {"date": "2024-02-22", "amount": 45.99, "category": "Shopping", "description": "Electronics"},
            {"date": "2024-02-25", "amount": 78.90, "category": "Groceries", "description": "Organic foods"},
            {"date": "2024-02-28", "amount": 156.78, "category": "Entertainment", "description": "Theater show"},
            {"date": "2024-03-01", "amount": 89.99, "category": "Dining", "description": "Weekend brunch"},
        ]
        
        self.transactions = sample_data
        self.categories = set(t["category"] for t in sample_data)
    
    def calculate_category_summary(self) -> Dict[str, Dict[str, float]]:
        """Calculate spending summary by category."""
        try:
            category_data = defaultdict(list)
            
            for transaction in self.transactions:
                category_data[transaction["category"]].append(transaction["amount"])
            
            summary = {}
            for category, amounts in category_data.items():
                summary[category] = {
                    "total": sum(amounts),
                    "average": statistics.mean(amounts),
                    "median": statistics.median(amounts),
                    "count": len(amounts),
                    "min": min(amounts),
                    "max": max(amounts),
                    "std_dev": statistics.stdev(amounts) if len(amounts) > 1 else 0.0
                }
            
            return summary
        except Exception as e:
            print(f"Error calculating category summary: {e}")
            return {}
    
    def identify_top_spending_patterns(self, limit: int = 5) -> List[Tuple[str, float, int]]:
        """Identify top spending patterns by category."""
        try:
            category_totals = defaultdict(float)
            category_counts = defaultdict(int)
            
            for transaction in self.transactions:
                category_totals[transaction["category"]] += transaction["amount"]
                category_counts[transaction["category"]] += 1
            
            patterns = []
            for category in category_totals:
                total = category_totals[category]
                count = category_counts[category]
                patterns.append((category, total, count))
            
            # Sort by total spending (descending)
            patterns.sort(key=lambda x: x[1], reverse=True)
            return patterns[:limit]
        except Exception as e:
            print(f"Error identifying spending patterns: {e}")
            return []
    
    def analyze_monthly_trends(self) -> Dict[str, Dict[str, float]]:
        """Analyze monthly spending trends."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction["date"], "%Y-%m-%d")
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                monthly_data[month_key]["total"] += transaction["amount"]
                monthly_data[month_key]["count"] += 1
            
            # Calculate month-over-month growth
            sorted_months = sorted(monthly_data.keys())
            trends = {}
            
            for i, month in enumerate(sorted_months):
                month_data = monthly_data[month]
                trends[month] = {
                    "total_spending": month_data["total"],
                    "transaction_count": month_data["count"],
                    "average_transaction": month_data["total"] / month_data["count"]
                }
                
                if i > 0:
                    prev_month = sorted_months[i-1]
                    prev_total = monthly_data[prev_month]["total"]
                    growth_rate = ((month_data["total"] - prev_total) / prev_total) * 100
                    trends[month]["growth_rate"] = growth_rate
                else:
                    trends[month]["growth_rate"] = 0.0
            
            return trends
        except Exception as e:
            print(f"Error analyzing monthly trends: {e}")
            return {}
    
    def analyze_weekly_trends(self) -> Dict[str, Dict[str, float]]:
        """Analyze weekly spending trends."""
        try:
            weekly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction["date"], "%Y-%m-%d")
                # Get the Monday of the week
                monday = date_obj - timedelta(days=date_obj.weekday())
                week_key = monday.strftime("%Y-%m-%d")
                
                weekly_data[week_key]["total"] += transaction["amount"]
                weekly_data[week_key]["count"] += 1
            
            # Calculate week-over-week growth
            sorted_weeks = sorted(weekly_data.keys())
            trends = {}
            
            for i, week in enumerate(sorted_weeks):
                week_data = weekly_data[week]
                trends[week] = {
                    "total_spending":