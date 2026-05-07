```python
"""
Budget Monitoring System

A comprehensive financial tracking system that monitors spending against predefined budgets,
generates overspending alerts, and creates monthly summaries with visualizations.

Features:
- Category-based budget tracking
- Automatic overspending detection and alerts
- Monthly financial summaries
- ASCII-based data visualizations
- Transaction logging and analysis
- Budget utilization reporting

Usage: python script.py
"""

import json
import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import calendar


@dataclass
class Transaction:
    """Represents a financial transaction"""
    date: str
    category: str
    amount: float
    description: str
    transaction_id: str


@dataclass
class Budget:
    """Represents a budget category"""
    category: str
    monthly_limit: float
    current_spent: float = 0.0
    
    @property
    def remaining(self) -> float:
        return self.monthly_limit - self.current_spent
    
    @property
    def utilization_percent(self) -> float:
        if self.monthly_limit == 0:
            return 0.0
        return (self.current_spent / self.monthly_limit) * 100
    
    @property
    def is_overspent(self) -> bool:
        return self.current_spent > self.monthly_limit


class BudgetMonitor:
    """Main budget monitoring system"""
    
    def __init__(self):
        self.budgets: Dict[str, Budget] = {}
        self.transactions: List[Transaction] = []
        self.alerts: List[str] = []
        
        # Initialize with sample budgets
        self._initialize_sample_budgets()
        # Load sample transactions
        self._load_sample_transactions()
    
    def _initialize_sample_budgets(self):
        """Initialize with sample budget categories"""
        sample_budgets = {
            "Food & Dining": 800.00,
            "Transportation": 300.00,
            "Entertainment": 200.00,
            "Utilities": 250.00,
            "Shopping": 400.00,
            "Healthcare": 150.00,
            "Groceries": 600.00,
            "Gas": 200.00,
            "Insurance": 300.00,
            "Miscellaneous": 100.00
        }
        
        for category, limit in sample_budgets.items():
            self.budgets[category] = Budget(category, limit)
    
    def _load_sample_transactions(self):
        """Load sample transactions for current month"""
        current_date = datetime.datetime.now()
        sample_transactions = [
            ("2024-01-05", "Food & Dining", 45.67, "Restaurant dinner", "T001"),
            ("2024-01-06", "Groceries", 127.89, "Weekly groceries", "T002"),
            ("2024-01-07", "Gas", 52.30, "Shell gas station", "T003"),
            ("2024-01-08", "Food & Dining", 12.50, "Coffee shop", "T004"),
            ("2024-01-10", "Entertainment", 15.99, "Netflix subscription", "T005"),
            ("2024-01-12", "Transportation", 25.00, "Uber ride", "T006"),
            ("2024-01-13", "Shopping", 89.99, "Amazon purchase", "T007"),
            ("2024-01-15", "Food & Dining", 67.43, "Lunch meeting", "T008"),
            ("2024-01-16", "Utilities", 145.67, "Electric bill", "T009"),
            ("2024-01-18", "Healthcare", 35.00, "Pharmacy", "T010"),
            ("2024-01-20", "Food & Dining", 78.90, "Date night dinner", "T011"),
            ("2024-01-22", "Groceries", 98.45, "Weekend groceries", "T012"),
            ("2024-01-24", "Gas", 48.75, "BP gas station", "T013"),
            ("2024-01-25", "Entertainment", 25.00, "Movie tickets", "T014"),
            ("2024-01-26", "Shopping", 156.78, "Clothing purchase", "T015"),
            ("2024-01-28", "Food & Dining", 890.25, "Catering event", "T016"),  # This will trigger overspending
            ("2024-01-29", "Transportation", 45.00, "Airport parking", "T017"),
            ("2024-01-30", "Miscellaneous", 23.50, "Office supplies", "T018")
        ]
        
        for date, category, amount, description, trans_id in sample_transactions:
            transaction = Transaction(date, category, amount, description, trans_id)
            self.add_transaction(transaction)
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a new transaction and update budgets"""
        try:
            self.transactions.append(transaction)
            
            # Update budget if category exists
            if transaction.category in self.budgets:
                self.budgets[transaction.category].current_spent += transaction.amount
                
                # Check for overspending
                budget = self.budgets[transaction.category]
                if budget.is_overspent and budget.utilization_percent > 100:
                    alert = self._generate_overspending_alert(budget, transaction)
                    self.alerts.append(alert)
            
            return True
            
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def _generate_overspending_alert(self, budget: Budget, transaction: Transaction) -> str:
        """Generate overspending alert message"""
        overage = budget.current_spent - budget.monthly_limit
        return (f"🚨 OVERSPENDING ALERT: {budget.category} "
                f"Budget exceeded by ${overage:.2f} "
                f"(Latest transaction: ${transaction.amount:.2f} - {transaction.description})")
    
    def get_budget_status(self) -> Dict[str, Dict]:
        """Get current status of all budgets"""
        status = {}
        for category, budget in self.budgets.items():
            status[category] = {
                "limit": budget.monthly_limit,
                "spent": budget.current_spent,
                "remaining": budget.remaining,
                "utilization": budget.utilization_percent,
                "overspent": budget.is_overspent
            }
        return status
    
    def generate_monthly_summary(self) -> Dict:
        """Generate comprehensive monthly financial summary"""
        try:
            current_month = datetime.datetime.now().strftime("%B %Y")
            
            # Calculate totals
            total_budget = sum(budget.monthly_limit for budget in self.budgets.values())
            total_spent = sum(budget.current_spent for budget in self.budgets.values())
            total_remaining = total_budget - total_spent
            
            # Category analysis
            overspent_categories = [budget for budget in self.budgets.values() if budget.is_overspent]
            highest_spending = max(self.budgets.values(), key=lambda b: b.current_spent)
            lowest_utilization = min(self.budgets.values(), key=lambda b: b.utilization_percent)
            
            # Transaction analysis
            transaction_count = len(self.transactions)
            avg_transaction = total_spent / transaction_count if transaction_count > 0 else 0
            
            # Daily spending pattern
            daily_spending = defaultdict(float)
            for transaction in self.transactions:
                try:
                    date_obj = datetime.datetime.strptime(transaction.date, "%Y-%m-%d")
                    day = date_obj.day
                    daily_spending[day] += transaction.amount
                except ValueError:
                    continue
            
            return {
                "month": current_month,
                "totals": {
                    "budget": total_budget,
                    "spent": total_spent,
                    "remaining": total_remaining,
                    "utilization": (total_spent