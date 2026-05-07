```python
"""
Monthly Spending Report Generator

This module analyzes transaction data to generate comprehensive monthly spending reports
including summary statistics, category breakdowns, spending trends, and actionable insights.

Features:
- Monthly spending summaries with key statistics
- Category-wise expenditure analysis
- Spending trend identification
- Actionable insights based on transaction patterns
- Support for multiple data input formats

Usage:
    python script.py

The module can be extended to read from CSV files, databases, or APIs by modifying
the data loading functions.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import calendar


class SpendingAnalyzer:
    """Analyzes spending data and generates insights."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(list)
        
    def load_sample_data(self) -> List[Dict]:
        """Generate sample transaction data for demonstration."""
        sample_data = [
            {"date": "2024-01-15", "amount": 45.20, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-01-16", "amount": 12.50, "category": "Food & Dining", "description": "Lunch"},
            {"date": "2024-01-18", "amount": 85.00, "category": "Gas", "description": "Shell station"},
            {"date": "2024-01-20", "amount": 156.78, "category": "Utilities", "description": "Electric bill"},
            {"date": "2024-01-22", "amount": 32.15, "category": "Food & Dining", "description": "Dinner"},
            {"date": "2024-01-25", "amount": 28.90, "category": "Groceries", "description": "Fresh produce"},
            {"date": "2024-01-28", "amount": 95.40, "category": "Entertainment", "description": "Movie tickets"},
            {"date": "2024-02-02", "amount": 67.33, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-02-05", "amount": 18.75, "category": "Food & Dining", "description": "Coffee shop"},
            {"date": "2024-02-08", "amount": 120.00, "category": "Gas", "description": "BP station"},
            {"date": "2024-02-12", "amount": 89.25, "category": "Shopping", "description": "Clothing"},
            {"date": "2024-02-15", "amount": 145.60, "category": "Utilities", "description": "Water bill"},
            {"date": "2024-02-18", "amount": 25.80, "category": "Food & Dining", "description": "Fast food"},
            {"date": "2024-02-22", "amount": 72.45, "category": "Entertainment", "description": "Concert"},
            {"date": "2024-02-25", "amount": 38.90, "category": "Groceries", "description": "Household items"},
            {"date": "2024-03-01", "amount": 55.20, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-03-05", "amount": 15.40, "category": "Food & Dining", "description": "Breakfast"},
            {"date": "2024-03-08", "amount": 110.00, "category": "Gas", "description": "Exxon station"},
            {"date": "2024-03-12", "amount": 167.89, "category": "Utilities", "description": "Internet bill"},
            {"date": "2024-03-15", "amount": 42.30, "category": "Food & Dining", "description": "Lunch meeting"},
        ]
        return sample_data
    
    def parse_transactions(self, data: List[Dict]) -> None:
        """Parse and organize transaction data by month."""
        try:
            for transaction in data:
                date_obj = datetime.strptime(transaction["date"], "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                
                parsed_transaction = {
                    "date": date_obj,
                    "amount": float(transaction["amount"]),
                    "category": transaction["category"],
                    "description": transaction["description"]
                }
                
                self.transactions.append(parsed_transaction)
                self.monthly_data[month_key].append(parsed_transaction)
                
        except (ValueError, KeyError) as e:
            print(f"Error parsing transaction data: {e}")
            raise
    
    def calculate_summary_stats(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics for a set of transactions."""
        if not transactions:
            return {"total": 0, "count": 0, "average": 0, "median": 0, "max": 0, "min": 0}
        
        amounts = [t["amount"] for t in transactions]
        
        return {
            "total": round(sum(amounts), 2),
            "count": len(amounts),
            "average": round(statistics.mean(amounts), 2),
            "median": round(statistics.median(amounts), 2),
            "max": round(max(amounts), 2),
            "min": round(min(amounts), 2)
        }
    
    def analyze_categories(self, transactions: List[Dict]) -> Dict[str, Dict]:
        """Analyze spending by category."""
        category_data = defaultdict(list)
        
        for transaction in transactions:
            category_data[transaction["category"]].append(transaction["amount"])
        
        category_analysis = {}
        for category, amounts in category_data.items():
            category_analysis[category] = {
                "total": round(sum(amounts), 2),
                "count": len(amounts),
                "average": round(sum(amounts) / len(amounts), 2),
                "percentage": 0  # Will be calculated later
            }
        
        # Calculate percentages
        total_spending = sum(cat["total"] for cat in category_analysis.values())
        for category in category_analysis:
            if total_spending > 0:
                category_analysis[category]["percentage"] = round(
                    (category_analysis[category]["total"] / total_spending) * 100, 1
                )
        
        return dict(sorted(category_analysis.items(), 
                          key=lambda x: x[1]["total"], reverse=True))
    
    def identify_trends(self) -> Dict[str, Any]:
        """Identify spending trends across months."""
        if len(self.monthly_data) < 2:
            return {"trend": "Insufficient data", "analysis": "Need at least 2 months of data"}
        
        sorted_months = sorted(self.monthly_data.keys())
        monthly_totals = []
        
        for month in sorted_months:
            total = sum(t["amount"] for t in self.monthly_data[month])
            monthly_totals.append((month, total))
        
        # Calculate month-over-month changes
        changes = []
        for i in range(1, len(monthly_totals)):
            prev_total = monthly_totals[i-1][1]
            curr_total = monthly_totals[i][1]
            if prev_total > 0:
                change_pct = ((curr_total - prev_total) / prev_total) * 100
                changes.append(change_pct)
        
        avg_change = statistics.mean(changes) if changes else 0
        
        trend_analysis = {
            "monthly_totals": monthly_totals,
            "average_monthly_change": round(avg_change, 1),
            "trend_direction": "increasing" if avg_change > 5 else "decreasing" if avg_change < -5 else "stable"
        }
        
        return trend_analysis
    
    def generate_insights(self) -> List[str]:
        """Generate actionable insights based on spending patterns."""
        insights = []
        
        if not self.transactions:
            return ["No transaction data available for analysis."]