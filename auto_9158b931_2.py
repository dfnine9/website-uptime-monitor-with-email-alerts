```python
#!/usr/bin/env python3
"""
Budget Analysis Engine

A comprehensive budget analysis tool that compares actual spending against user-defined 
category budgets, identifies overspending patterns, and generates personalized 
recommendations based on spending behavior.

Features:
- Category-based budget tracking
- Overspending pattern detection
- Personalized spending recommendations
- Monthly and yearly analysis
- Spending trend visualization (text-based)

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import random


class Transaction:
    """Represents a single financial transaction"""
    
    def __init__(self, date: str, amount: float, category: str, description: str):
        self.date = datetime.strptime(date, "%Y-%m-%d")
        self.amount = abs(amount)  # Ensure positive for expenses
        self.category = category.lower().strip()
        self.description = description.strip()


class BudgetAnalysisEngine:
    """Main budget analysis engine"""
    
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        self.recommendations = []
        
    def add_transaction(self, date: str, amount: float, category: str, description: str):
        """Add a transaction to the analysis"""
        try:
            transaction = Transaction(date, amount, category, description)
            self.transactions.append(transaction)
        except ValueError as e:
            print(f"Error adding transaction: {e}")
            
    def set_budget(self, category: str, monthly_limit: float):
        """Set monthly budget for a category"""
        self.budgets[category.lower().strip()] = monthly_limit
        
    def get_spending_by_category(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, float]:
        """Calculate total spending by category within date range"""
        spending = defaultdict(float)
        
        for transaction in self.transactions:
            if start_date and transaction.date < start_date:
                continue
            if end_date and transaction.date > end_date:
                continue
            spending[transaction.category] += transaction.amount
            
        return dict(spending)
        
    def analyze_monthly_spending(self, year: int, month: int) -> Dict[str, Dict[str, Any]]:
        """Analyze spending for a specific month"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
        spending = self.get_spending_by_category(start_date, end_date)
        analysis = {}
        
        for category, spent in spending.items():
            budget = self.budgets.get(category, 0)
            analysis[category] = {
                'spent': spent,
                'budget': budget,
                'overspend': max(0, spent - budget) if budget > 0 else 0,
                'percentage_used': (spent / budget * 100) if budget > 0 else float('inf'),
                'status': self._get_budget_status(spent, budget)
            }
            
        return analysis
        
    def _get_budget_status(self, spent: float, budget: float) -> str:
        """Determine budget status for a category"""
        if budget == 0:
            return "no_budget"
        elif spent <= budget * 0.8:
            return "under_budget"
        elif spent <= budget:
            return "on_track"
        elif spent <= budget * 1.2:
            return "slightly_over"
        else:
            return "significantly_over"
            
    def identify_overspending_patterns(self) -> List[Dict[str, Any]]:
        """Identify patterns in overspending behavior"""
        patterns = []
        
        # Analyze last 6 months
        current_date = datetime.now()
        for i in range(6):
            month_offset = i
            target_date = current_date - timedelta(days=30 * month_offset)
            year, month = target_date.year, target_date.month
            
            monthly_analysis = self.analyze_monthly_spending(year, month)
            
            for category, data in monthly_analysis.items():
                if data['overspend'] > 0:
                    patterns.append({
                        'month': f"{year}-{month:02d}",
                        'category': category,
                        'overspend_amount': data['overspend'],
                        'percentage_over': data['percentage_used'] - 100 if data['budget'] > 0 else 0
                    })
                    
        return patterns
        
    def calculate_spending_trends(self) -> Dict[str, Dict[str, float]]:
        """Calculate spending trends for each category"""
        trends = defaultdict(lambda: defaultdict(list))
        
        # Group transactions by category and month
        for transaction in self.transactions:
            month_key = f"{transaction.date.year}-{transaction.date.month:02d}"
            trends[transaction.category][month_key].append(transaction.amount)
            
        # Calculate monthly totals and trends
        category_trends = {}
        for category, monthly_data in trends.items():
            monthly_totals = {month: sum(amounts) for month, amounts in monthly_data.items()}
            sorted_months = sorted(monthly_totals.keys())
            
            if len(sorted_months) >= 2:
                values = [monthly_totals[month] for month in sorted_months]
                avg_change = statistics.mean([values[i] - values[i-1] for i in range(1, len(values))])
                trend_direction = "increasing" if avg_change > 0 else "decreasing" if avg_change < 0 else "stable"
            else:
                avg_change = 0
                trend_direction = "insufficient_data"
                
            category_trends[category] = {
                'average_monthly': statistics.mean(monthly_totals.values()) if monthly_totals else 0,
                'monthly_change': avg_change,
                'trend': trend_direction,
                'volatility': statistics.stdev(monthly_totals.values()) if len(monthly_totals) > 1 else 0
            }
            
        return category_trends
        
    def generate_recommendations(self) -> List[str]:
        """Generate personalized recommendations based on spending patterns"""
        recommendations = []
        
        try:
            # Analyze current month
            current_date = datetime.now()
            current_analysis = self.analyze_monthly_spending(current_date.year, current_date.month)
            
            # Analyze trends
            trends = self.calculate_spending_trends()
            
            # Analyze patterns
            patterns = self.identify_overspending_patterns()
            
            # Generate category-specific recommendations
            for category, data in current_analysis.items():
                if data['status'] == "significantly_over":
                    recommendations.append(f"🚨 URGENT: You're {data['percentage_used']:.0f}% over budget in {category}. Consider reducing spending immediately.")
                elif data['status'] == "slightly_over":
                    recommendations.append(f"⚠️  WARNING: You're slightly over budget in {category} ({data['percentage_used']:.0f}%). Monitor closely.")
                elif data['status'] == "on_track" and data['percentage_used'] > 90:
                    recommendations.append(f"📊 CAUTION: You're at {data['percentage_used']:.0f}% of your {category} budget. Pace yourself for the rest of the month.")
                    
            # Generate trend-based recommendations
            for category, trend_data in trends.items():
                if trend_data['trend'] == "increasing" and trend_data['monthly_change'] > 50:
                    recommendations.append(f"📈 TREND ALERT: Your {category} spending is increasing by ${trend_data['monthly_change']:.2f}/month. Consider reviewing this category.")
                elif trend_data['volat