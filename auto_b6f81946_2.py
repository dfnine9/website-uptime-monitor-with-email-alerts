```python
"""
Automated Budget Analysis Engine

This module provides a comprehensive budget analysis system that:
- Compares actual spending against predefined category limits
- Identifies overspending patterns and trends
- Calculates variance percentages for each budget category
- Generates actionable recommendations with priority-based alerts
- Tracks spending patterns over time to identify recurring issues

Features:
- Category-based budget tracking with customizable limits
- Variance analysis with percentage calculations
- Pattern detection for overspending trends
- Alert system with different severity levels
- Actionable recommendations based on spending behavior
- Monthly and yearly budget projections
"""

import json
import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import math


class AlertLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Transaction:
    date: str
    category: str
    amount: float
    description: str


@dataclass
class BudgetCategory:
    name: str
    limit: float
    spent: float = 0.0
    variance: float = 0.0
    variance_percent: float = 0.0
    alert_level: AlertLevel = AlertLevel.LOW


@dataclass
class BudgetAlert:
    category: str
    level: AlertLevel
    message: str
    recommendation: str


class BudgetAnalysisEngine:
    def __init__(self):
        self.categories = {}
        self.transactions = []
        self.alerts = []
        
    def set_budget_limits(self, budget_limits: Dict[str, float]) -> None:
        """Set budget limits for categories"""
        try:
            for category, limit in budget_limits.items():
                if limit <= 0:
                    raise ValueError(f"Budget limit for {category} must be positive")
                self.categories[category] = BudgetCategory(name=category, limit=limit)
        except Exception as e:
            print(f"Error setting budget limits: {e}")
            raise

    def add_transaction(self, date: str, category: str, amount: float, description: str = "") -> None:
        """Add a transaction to the analysis"""
        try:
            if amount <= 0:
                raise ValueError("Transaction amount must be positive")
            
            # Validate date format
            datetime.datetime.strptime(date, "%Y-%m-%d")
            
            transaction = Transaction(date, category, amount, description)
            self.transactions.append(transaction)
            
            # Update category spending
            if category not in self.categories:
                # Auto-create category with default limit
                self.categories[category] = BudgetCategory(name=category, limit=1000.0)
                print(f"Warning: Auto-created category '{category}' with default limit $1000")
            
            self.categories[category].spent += amount
            
        except ValueError as e:
            print(f"Error adding transaction: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error adding transaction: {e}")
            raise

    def calculate_variances(self) -> None:
        """Calculate variance and percentage for each category"""
        try:
            for category in self.categories.values():
                category.variance = category.spent - category.limit
                if category.limit > 0:
                    category.variance_percent = (category.variance / category.limit) * 100
                else:
                    category.variance_percent = 0.0
        except Exception as e:
            print(f"Error calculating variances: {e}")
            raise

    def identify_overspending_patterns(self) -> Dict[str, List[str]]:
        """Identify patterns in overspending"""
        patterns = {
            "frequent_overspenders": [],
            "severe_overspenders": [],
            "trending_up": [],
            "weekend_spenders": [],
            "month_end_spenders": []
        }
        
        try:
            # Group transactions by category and analyze
            category_transactions = {}
            for transaction in self.transactions:
                if transaction.category not in category_transactions:
                    category_transactions[transaction.category] = []
                category_transactions[transaction.category].append(transaction)
            
            for category, transactions in category_transactions.items():
                if category not in self.categories:
                    continue
                    
                budget_category = self.categories[category]
                
                # Frequent overspenders (variance > 0)
                if budget_category.variance > 0:
                    patterns["frequent_overspenders"].append(category)
                
                # Severe overspenders (>50% over budget)
                if budget_category.variance_percent > 50:
                    patterns["severe_overspenders"].append(category)
                
                # Analyze spending trends if we have multiple transactions
                if len(transactions) >= 3:
                    amounts = [t.amount for t in sorted(transactions, key=lambda x: x.date)]
                    if len(amounts) >= 2:
                        # Simple trend analysis - compare first half vs second half
                        mid = len(amounts) // 2
                        first_half_avg = statistics.mean(amounts[:mid]) if mid > 0 else 0
                        second_half_avg = statistics.mean(amounts[mid:]) if len(amounts) > mid else 0
                        
                        if second_half_avg > first_half_avg * 1.2:  # 20% increase
                            patterns["trending_up"].append(category)
                
                # Weekend spending pattern
                weekend_count = sum(1 for t in transactions 
                                  if datetime.datetime.strptime(t.date, "%Y-%m-%d").weekday() >= 5)
                if weekend_count / len(transactions) > 0.4:  # 40% of spending on weekends
                    patterns["weekend_spenders"].append(category)
                
                # Month-end spending pattern
                month_end_count = sum(1 for t in transactions 
                                    if datetime.datetime.strptime(t.date, "%Y-%m-%d").day >= 25)
                if month_end_count / len(transactions) > 0.3:  # 30% of spending in last week
                    patterns["month_end_spenders"].append(category)
                    
        except Exception as e:
            print(f"Error identifying patterns: {e}")
            
        return patterns

    def generate_alerts(self) -> None:
        """Generate alerts based on spending analysis"""
        self.alerts = []
        
        try:
            for category in self.categories.values():
                alert_level = AlertLevel.LOW
                message = ""
                recommendation = ""
                
                if category.variance_percent > 100:
                    alert_level = AlertLevel.CRITICAL
                    message = f"{category.name}: CRITICAL overspending - {category.variance_percent:.1f}% over budget"
                    recommendation = f"Immediately stop spending in {category.name}. Review all subscriptions and recurring charges."
                    
                elif category.variance_percent > 50:
                    alert_level = AlertLevel.HIGH
                    message = f"{category.name}: HIGH overspending - {category.variance_percent:.1f}% over budget"
                    recommendation = f"Significantly reduce {category.name} spending. Consider cheaper alternatives."
                    
                elif category.variance_percent > 20:
                    alert_level = AlertLevel.MEDIUM
                    message = f"{category.name}: MEDIUM overspending - {category.variance_percent:.1f}% over budget"
                    recommendation = f"Monitor {category.name} spending closely and look for cost savings."
                    
                elif category.variance_percent > 0:
                    alert_level = AlertLevel.LOW
                    message = f"{category.name}: Minor overspending - {category.variance_percent:.1f}% over budget"
                    recommendation = f"Keep an eye on {category.name} spending to prevent further overruns."
                
                # Update category alert level
                category.alert_level = alert_level
                
                # Add alert if there's overspending
                if category.variance > 0:
                    self.alerts.append(BudgetAlert(category.name, alert_level, message, recommendation))