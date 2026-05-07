```python
"""
Monthly Spending Analysis Engine

This module provides a comprehensive analysis of monthly spending patterns by:
- Calculating spending totals by category
- Identifying spending trends over time
- Generating insights on top spending categories
- Detecting unusual transactions based on statistical analysis

The engine processes transaction data and provides actionable insights for
personal finance management and budgeting decisions.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import math


class SpendingAnalysisEngine:
    """
    A comprehensive spending analysis engine that processes transaction data
    to generate monthly insights and identify spending patterns.
    """
    
    def __init__(self):
        self.transactions = []
        self.categories = defaultdict(list)
        self.monthly_totals = defaultdict(float)
        self.category_totals = defaultdict(float)
    
    def add_transaction(self, amount: float, category: str, date: str, description: str = ""):
        """Add a transaction to the analysis dataset."""
        try:
            transaction_date = datetime.strptime(date, "%Y-%m-%d")
            transaction = {
                'amount': abs(amount),  # Use absolute value for spending
                'category': category.lower().strip(),
                'date': transaction_date,
                'description': description,
                'month_key': f"{transaction_date.year}-{transaction_date.month:02d}"
            }
            self.transactions.append(transaction)
            return True
        except ValueError as e:
            print(f"Error adding transaction: Invalid date format. Use YYYY-MM-DD. {e}")
            return False
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def calculate_category_totals(self) -> Dict[str, float]:
        """Calculate total spending by category."""
        try:
            self.category_totals.clear()
            for transaction in self.transactions:
                self.category_totals[transaction['category']] += transaction['amount']
            return dict(self.category_totals)
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return {}
    
    def calculate_monthly_totals(self) -> Dict[str, float]:
        """Calculate total spending by month."""
        try:
            self.monthly_totals.clear()
            for transaction in self.transactions:
                self.monthly_totals[transaction['month_key']] += transaction['amount']
            return dict(self.monthly_totals)
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def identify_trends(self) -> Dict[str, Any]:
        """Identify spending trends over time."""
        try:
            monthly_data = self.calculate_monthly_totals()
            if len(monthly_data) < 2:
                return {"trend": "insufficient_data", "change_percent": 0}
            
            sorted_months = sorted(monthly_data.keys())
            amounts = [monthly_data[month] for month in sorted_months]
            
            # Calculate trend using linear regression slope
            n = len(amounts)
            x_values = list(range(n))
            
            sum_x = sum(x_values)
            sum_y = sum(amounts)
            sum_xy = sum(x * y for x, y in zip(x_values, amounts))
            sum_x_squared = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x * sum_x)
            
            # Calculate percentage change from first to last month
            change_percent = ((amounts[-1] - amounts[0]) / amounts[0]) * 100 if amounts[0] != 0 else 0
            
            trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
            
            return {
                "trend": trend_direction,
                "change_percent": round(change_percent, 2),
                "slope": round(slope, 2),
                "monthly_data": dict(zip(sorted_months, amounts))
            }
        except Exception as e:
            print(f"Error identifying trends: {e}")
            return {"trend": "error", "change_percent": 0}
    
    def get_top_categories(self, limit: int = 5) -> List[Tuple[str, float, float]]:
        """Get top spending categories with amounts and percentages."""
        try:
            category_totals = self.calculate_category_totals()
            total_spending = sum(category_totals.values())
            
            if total_spending == 0:
                return []
            
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            
            top_categories = []
            for category, amount in sorted_categories[:limit]:
                percentage = (amount / total_spending) * 100
                top_categories.append((category, amount, percentage))
            
            return top_categories
        except Exception as e:
            print(f"Error getting top categories: {e}")
            return []
    
    def detect_unusual_transactions(self, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect unusual transactions using statistical analysis."""
        try:
            unusual_transactions = []
            
            # Group transactions by category for better anomaly detection
            category_groups = defaultdict(list)
            for transaction in self.transactions:
                category_groups[transaction['category']].append(transaction)
            
            for category, transactions in category_groups.items():
                if len(transactions) < 3:  # Need at least 3 transactions for statistical analysis
                    continue
                
                amounts = [t['amount'] for t in transactions]
                mean_amount = statistics.mean(amounts)
                
                try:
                    std_dev = statistics.stdev(amounts)
                except statistics.StatisticsError:
                    continue  # Skip if standard deviation can't be calculated
                
                if std_dev == 0:  # All transactions are the same amount
                    continue
                
                for transaction in transactions:
                    z_score = abs((transaction['amount'] - mean_amount) / std_dev)
                    
                    if z_score > threshold:
                        unusual_transactions.append({
                            'transaction': transaction,
                            'z_score': round(z_score, 2),
                            'category_mean': round(mean_amount, 2),
                            'deviation': round(transaction['amount'] - mean_amount, 2)
                        })
            
            return sorted(unusual_transactions, key=lambda x: x['z_score'], reverse=True)
        except Exception as e:
            print(f"Error detecting unusual transactions: {e}")
            return []
    
    def generate_monthly_report(self) -> Dict[str, Any]:
        """Generate a comprehensive monthly analysis report."""
        try:
            return {
                'total_transactions': len(self.transactions),
                'category_totals': self.calculate_category_totals(),
                'monthly_totals': self.calculate_monthly_totals(),
                'trends': self.identify_trends(),
                'top_categories': self.get_top_categories(),
                'unusual_transactions': self.detect_unusual_transactions(),
                'total_spending': sum(self.calculate_category_totals().values())
            }
        except Exception as e:
            print(f"Error generating monthly report: {e}")
            return {}


def load_sample_data(engine: SpendingAnalysisEngine):
    """Load sample transaction data for demonstration."""
    sample_transactions = [
        (450.00, "groceries", "2024-01-05", "Whole Foods Market"),
        (120.00, "utilities", "2024-01-10", "Electric Bill"),
        (80.00, "gas", "2024-01-12", "Shell Station"),
        (1200.00, "rent", "2024-01-01", "Monthly Rent"),
        (60.00, "dining", "2024-01-15", "Italian Restaurant"),
        (200.00, "groceries", "2024-01