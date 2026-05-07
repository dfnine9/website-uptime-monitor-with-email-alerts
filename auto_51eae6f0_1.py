```python
"""
Spending Pattern Analysis Module

This module analyzes financial transaction data to identify spending patterns and anomalies.
It performs the following analyses:
- Identifies recurring transactions based on amount and description patterns
- Calculates average spending per category over time periods
- Detects anomalous spending behavior using statistical methods
- Builds historical spending profiles for trend analysis

The module uses statistical analysis to detect patterns and anomalies without requiring
external data science libraries, relying only on Python's standard library.
"""

import json
import re
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple, Optional
import math


@dataclass
class Transaction:
    """Represents a financial transaction"""
    date: str
    amount: float
    description: str
    category: str
    merchant: Optional[str] = None


@dataclass
class RecurringTransaction:
    """Represents a recurring transaction pattern"""
    description_pattern: str
    amounts: List[float]
    dates: List[str]
    frequency_days: float
    category: str
    confidence: float


@dataclass
class CategoryProfile:
    """Historical spending profile for a category"""
    category: str
    total_spent: float
    transaction_count: int
    average_amount: float
    median_amount: float
    std_deviation: float
    monthly_average: float
    trend: str  # 'increasing', 'decreasing', 'stable'


@dataclass
class SpendingAnomaly:
    """Represents an anomalous spending event"""
    transaction: Transaction
    anomaly_type: str
    severity: float
    reason: str


class SpendingAnalyzer:
    """Main class for analyzing spending patterns"""
    
    def __init__(self):
        self.transactions = []
        self.categories = set()
        
    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to the analysis dataset"""
        try:
            self.transactions.append(transaction)
            self.categories.add(transaction.category)
        except Exception as e:
            print(f"Error adding transaction: {e}")
    
    def load_sample_data(self) -> None:
        """Load sample transaction data for demonstration"""
        sample_transactions = [
            # Recurring bills
            Transaction("2024-01-15", -1200.00, "RENT PAYMENT - APARTMENT", "Housing"),
            Transaction("2024-02-15", -1200.00, "RENT PAYMENT - APARTMENT", "Housing"),
            Transaction("2024-03-15", -1200.00, "RENT PAYMENT - APARTMENT", "Housing"),
            Transaction("2024-04-15", -1200.00, "RENT PAYMENT - APARTMENT", "Housing"),
            
            # Utilities
            Transaction("2024-01-05", -85.50, "ELECTRIC COMPANY", "Utilities"),
            Transaction("2024-02-05", -92.30, "ELECTRIC COMPANY", "Utilities"),
            Transaction("2024-03-05", -78.20, "ELECTRIC COMPANY", "Utilities"),
            Transaction("2024-04-05", -88.90, "ELECTRIC COMPANY", "Utilities"),
            
            # Groceries (variable but regular)
            Transaction("2024-01-03", -156.78, "SUPERMARKET CHAIN", "Groceries"),
            Transaction("2024-01-10", -89.45, "SUPERMARKET CHAIN", "Groceries"),
            Transaction("2024-01-17", -134.23, "SUPERMARKET CHAIN", "Groceries"),
            Transaction("2024-01-24", -112.56, "SUPERMARKET CHAIN", "Groceries"),
            Transaction("2024-01-31", -98.34, "SUPERMARKET CHAIN", "Groceries"),
            
            Transaction("2024-02-07", -145.67, "SUPERMARKET CHAIN", "Groceries"),
            Transaction("2024-02-14", -167.89, "SUPERMARKET CHAIN", "Groceries"),
            Transaction("2024-02-21", -123.45, "SUPERMARKET CHAIN", "Groceries"),
            Transaction("2024-02-28", -189.23, "SUPERMARKET CHAIN", "Groceries"),
            
            # Gas
            Transaction("2024-01-08", -45.67, "GAS STATION", "Transportation"),
            Transaction("2024-01-15", -52.34, "GAS STATION", "Transportation"),
            Transaction("2024-01-22", -48.90, "GAS STATION", "Transportation"),
            Transaction("2024-01-29", -51.23, "GAS STATION", "Transportation"),
            
            # Restaurants
            Transaction("2024-01-12", -28.45, "PIZZA PLACE", "Dining"),
            Transaction("2024-01-18", -45.67, "FANCY RESTAURANT", "Dining"),
            Transaction("2024-01-25", -15.23, "COFFEE SHOP", "Dining"),
            Transaction("2024-02-02", -67.89, "STEAKHOUSE", "Dining"),
            Transaction("2024-02-09", -23.45, "COFFEE SHOP", "Dining"),
            
            # Anomalies
            Transaction("2024-02-20", -2500.00, "EMERGENCY CAR REPAIR", "Transportation"),  # Large anomaly
            Transaction("2024-03-01", -850.00, "MEDICAL PROCEDURE", "Healthcare"),  # Category anomaly
            Transaction("2024-03-10", -1800.00, "LAPTOP PURCHASE", "Electronics"),  # Large purchase
            
            # Income
            Transaction("2024-01-01", 5000.00, "SALARY DEPOSIT", "Income"),
            Transaction("2024-02-01", 5000.00, "SALARY DEPOSIT", "Income"),
            Transaction("2024-03-01", 5000.00, "SALARY DEPOSIT", "Income"),
            Transaction("2024-04-01", 5000.00, "SALARY DEPOSIT", "Income"),
        ]
        
        for transaction in sample_transactions:
            self.add_transaction(transaction)
    
    def normalize_description(self, description: str) -> str:
        """Normalize transaction description for pattern matching"""
        # Remove common variations
        normalized = description.upper()
        normalized = re.sub(r'\d+', 'NUM', normalized)  # Replace numbers
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        normalized = re.sub(r'\s+', ' ', normalized).strip()  # Normalize whitespace
        return normalized
    
    def find_recurring_transactions(self, min_occurrences: int = 3, 
                                  max_amount_variance: float = 0.3) -> List[RecurringTransaction]:
        """Identify recurring transactions based on description patterns and amounts"""
        try:
            recurring_patterns = []
            
            # Group transactions by normalized description
            description_groups = defaultdict(list)
            for transaction in self.transactions:
                if transaction.amount < 0:  # Only expenses
                    normalized_desc = self.normalize_description(transaction.description)
                    description_groups[normalized_desc].append(transaction)
            
            for pattern, transactions in description_groups.items():
                if len(transactions) < min_occurrences:
                    continue
                
                # Check amount consistency
                amounts = [abs(t.amount) for t in transactions]
                if len(amounts) > 1:
                    mean_amount = statistics.mean(amounts)
                    amount_variance = statistics.stdev(amounts) / mean_amount if mean_amount > 0 else 1
                    
                    if amount_variance <= max_amount_variance:
                        # Calculate frequency
                        dates = sorted([datetime.fromisoformat(t.date) for t in transactions])
                        if len(dates) > 1:
                            intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                            avg_frequency = statistics.mean(intervals)
                            
                            confidence = min(1.0, len(transactions) / 10) * (1 - amount