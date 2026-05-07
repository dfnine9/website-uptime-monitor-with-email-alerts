```python
#!/usr/bin/env python3
"""
Budget Alert System

A comprehensive budget monitoring system that tracks spending against predefined category limits,
sends notifications when thresholds are exceeded, and generates detailed weekly/monthly reports
with actionable recommendations for financial management.

Features:
- Category-based budget tracking with customizable limits
- Real-time threshold monitoring with configurable alert levels
- Automated notification system for budget overruns
- Weekly and monthly summary report generation
- Actionable recommendations based on spending patterns
- Transaction logging and history tracking
- Data persistence using JSON storage

Usage:
    python script.py

The system will initialize with sample data and demonstrate:
- Adding transactions across different categories
- Monitoring budget thresholds
- Sending alerts when limits are exceeded
- Generating comprehensive reports with recommendations
"""

import json
import os
import datetime
import calendar
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class AlertLevel(Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EXCEEDED = "EXCEEDED"

class ReportType(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class Transaction:
    id: str
    category: str
    amount: float
    description: str
    date: datetime.datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "date": self.date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        return cls(
            id=data["id"],
            category=data["category"],
            amount=data["amount"],
            description=data["description"],
            date=datetime.datetime.fromisoformat(data["date"])
        )

@dataclass
class BudgetCategory:
    name: str
    monthly_limit: float
    warning_threshold: float = 0.8  # 80% of limit
    critical_threshold: float = 0.95  # 95% of limit
    current_spending: float = 0.0
    
    def get_alert_level(self) -> Optional[AlertLevel]:
        if self.current_spending > self.monthly_limit:
            return AlertLevel.EXCEEDED
        elif self.current_spending >= self.monthly_limit * self.critical_threshold:
            return AlertLevel.CRITICAL
        elif self.current_spending >= self.monthly_limit * self.warning_threshold:
            return AlertLevel.WARNING
        return None
    
    def get_remaining_budget(self) -> float:
        return max(0, self.monthly_limit - self.current_spending)
    
    def get_usage_percentage(self) -> float:
        return (self.current_spending / self.monthly_limit) * 100 if self.monthly_limit > 0 else 0

class BudgetAlertSystem:
    def __init__(self, data_file: str = "budget_data.json"):
        self.data_file = data_file
        self.categories: Dict[str, BudgetCategory] = {}
        self.transactions: List[Transaction] = []
        self.notifications: List[Dict[str, Any]] = []
        self.load_data()
    
    def initialize_default_categories(self) -> None:
        """Initialize with common budget categories."""
        default_categories = {
            "food": BudgetCategory("Food & Dining", 800.0),
            "transportation": BudgetCategory("Transportation", 400.0),
            "entertainment": BudgetCategory("Entertainment", 300.0),
            "shopping": BudgetCategory("Shopping", 500.0),
            "utilities": BudgetCategory("Utilities", 200.0),
            "healthcare": BudgetCategory("Healthcare", 250.0),
            "education": BudgetCategory("Education", 150.0),
            "miscellaneous": BudgetCategory("Miscellaneous", 200.0)
        }
        self.categories.update(default_categories)
        print("✅ Initialized default budget categories")
    
    def load_data(self) -> None:
        """Load existing data from JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Load categories
                for cat_name, cat_data in data.get("categories", {}).items():
                    self.categories[cat_name] = BudgetCategory(**cat_data)
                
                # Load transactions
                for trans_data in data.get("transactions", []):
                    self.transactions.append(Transaction.from_dict(trans_data))
                
                # Load notifications
                self.notifications = data.get("notifications", [])
                
                print(f"✅ Loaded data from {self.data_file}")
            else:
                self.initialize_default_categories()
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.initialize_default_categories()
    
    def save_data(self) -> None:
        """Save current data to JSON file."""
        try:
            data = {
                "categories": {name: asdict(cat) for name, cat in self.categories.items()},
                "transactions": [trans.to_dict() for trans in self.transactions],
                "notifications": self.notifications
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"💾 Data saved to {self.data_file}")
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def add_transaction(self, category: str, amount: float, description: str) -> bool:
        """Add a new transaction and update category spending."""
        try:
            if category not in self.categories:
                print(f"❌ Category '{category}' not found. Available categories: {list(self.categories.keys())}")
                return False
            
            transaction_id = f"txn_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.transactions)}"
            transaction = Transaction(
                id=transaction_id,
                category=category,
                amount=amount,
                description=description,
                date=datetime.datetime.now()
            )
            
            self.transactions.append(transaction)
            self.categories[category].current_spending += amount
            
            print(f"✅ Added transaction: ${amount:.2f} to {category} - {description}")
            
            # Check for alerts
            self.check_budget_alerts(category)
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding transaction: {e}")
            return False
    
    def check_budget_alerts(self, category: str) -> None:
        """Check and send budget alerts for a specific category."""
        try:
            cat = self.categories[category]
            alert_level = cat.get_alert_level()
            
            if alert_level:
                notification = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "category": category,
                    "alert_level": alert_level.value,
                    "current_spending": cat.current_spending,
                    "budget_limit": cat.monthly_limit,
                    "usage_percentage": cat.get_usage_percentage(),
                    "remaining_budget": cat.get_remaining_budget()
                }
                
                self.notifications.append(notification)
                self.send_notification(notification)
                
        except Exception as e:
            print(f"❌ Error checking budget alerts: {e}")
    
    def send_notification(self, notification: Dict[str, Any]) -> None:
        """Send budget alert notification."""
        try:
            alert_level = notification["alert_level"]
            category = notification["category"]
            usage_pct = notification["usage_percentage"]
            remaining = notification["remaining_budget"]
            
            if alert_