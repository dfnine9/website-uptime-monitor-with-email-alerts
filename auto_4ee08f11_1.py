```python
"""
Transaction Analysis Module

This module provides functionality to process and analyze financial transaction data.
It aggregates transactions by month and category, calculates spending totals,
and identifies spending trends and anomalies using statistical analysis.

Features:
- Monthly transaction aggregation
- Category-wise spending analysis
- Trend detection using moving averages
- Anomaly detection using statistical thresholds
- Comprehensive reporting
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import calendar


class TransactionProcessor:
    """Main class for processing and analyzing transaction data."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
    
    def add_transaction(self, date: str, category: str, amount: float, description: str = ""):
        """Add a transaction to the dataset."""
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            self.transactions.append({
                'date': parsed_date,
                'category': category,
                'amount': abs(amount),  # Use absolute value for spending
                'description': description
            })
        except ValueError as e:
            print(f"Error parsing date {date}: {e}")
    
    def load_sample_data(self):
        """Load sample transaction data for demonstration."""
        sample_data = [
            ("2023-01-15", "Groceries", 125.50, "Weekly shopping"),
            ("2023-01-20", "Gas", 45.00, "Fuel"),
            ("2023-01-25", "Restaurants", 89.25, "Dinner out"),
            ("2023-02-10", "Groceries", 150.75, "Weekly shopping"),
            ("2023-02-15", "Utilities", 200.00, "Electric bill"),
            ("2023-02-20", "Gas", 50.25, "Fuel"),
            ("2023-03-05", "Groceries", 175.00, "Monthly shopping"),
            ("2023-03-10", "Restaurants", 65.50, "Lunch"),
            ("2023-03-15", "Entertainment", 85.00, "Movie tickets"),
            ("2023-03-20", "Gas", 48.75, "Fuel"),
            ("2023-04-12", "Groceries", 140.25, "Weekly shopping"),
            ("2023-04-18", "Utilities", 195.50, "Electric bill"),
            ("2023-04-25", "Restaurants", 120.00, "Date night"),
            ("2023-05-08", "Groceries", 165.75, "Bi-weekly shopping"),
            ("2023-05-15", "Gas", 55.00, "Fuel"),
            ("2023-05-22", "Entertainment", 75.00, "Concert"),
            ("2023-06-03", "Groceries", 180.00, "Monthly shopping"),
            ("2023-06-10", "Restaurants", 95.25, "Business lunch"),
            ("2023-06-20", "Utilities", 220.00, "Summer electric bill"),
            ("2023-06-25", "Gas", 52.50, "Fuel"),
            ("2023-07-05", "Groceries", 200.00, "Holiday shopping"),
            ("2023-07-15", "Entertainment", 150.00, "Vacation activities"),
            ("2023-07-20", "Restaurants", 250.00, "Vacation dining"),
            ("2023-08-08", "Groceries", 160.00, "Weekly shopping"),
            ("2023-08-15", "Gas", 60.00, "Road trip fuel"),
            ("2023-08-25", "Utilities", 185.00, "Electric bill"),
        ]
        
        for date, category, amount, description in sample_data:
            self.add_transaction(date, category, amount, description)
    
    def aggregate_by_month(self):
        """Aggregate transactions by month and category."""
        try:
            for transaction in self.transactions:
                month_key = transaction['date'].strftime("%Y-%m")
                category = transaction['category']
                amount = transaction['amount']
                
                self.monthly_data[month_key][category] += amount
                self.category_totals[category] += amount
        except Exception as e:
            print(f"Error aggregating data: {e}")
    
    def calculate_spending_trends(self) -> Dict[str, List[float]]:
        """Calculate spending trends for each category over time."""
        trends = defaultdict(list)
        
        try:
            # Sort months chronologically
            sorted_months = sorted(self.monthly_data.keys())
            
            for category in self.category_totals.keys():
                monthly_amounts = []
                for month in sorted_months:
                    amount = self.monthly_data[month].get(category, 0)
                    monthly_amounts.append(amount)
                trends[category] = monthly_amounts
            
            return dict(trends)
        except Exception as e:
            print(f"Error calculating trends: {e}")
            return {}
    
    def detect_anomalies(self, trends: Dict[str, List[float]]) -> Dict[str, List[Tuple[int, float]]]:
        """Detect spending anomalies using statistical analysis."""
        anomalies = defaultdict(list)
        
        try:
            for category, amounts in trends.items():
                if len(amounts) < 3:  # Need at least 3 data points
                    continue
                
                mean_amount = statistics.mean(amounts)
                if len(amounts) > 1:
                    std_dev = statistics.stdev(amounts)
                else:
                    std_dev = 0
                
                # Define anomaly threshold (2 standard deviations)
                threshold = 2 * std_dev
                
                for i, amount in enumerate(amounts):
                    if abs(amount - mean_amount) > threshold and threshold > 0:
                        anomalies[category].append((i, amount))
            
            return dict(anomalies)
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return {}
    
    def calculate_moving_averages(self, trends: Dict[str, List[float]], window: int = 3) -> Dict[str, List[float]]:
        """Calculate moving averages for trend smoothing."""
        moving_averages = {}
        
        try:
            for category, amounts in trends.items():
                if len(amounts) < window:
                    moving_averages[category] = amounts[:]
                    continue
                
                ma_values = []
                for i in range(len(amounts)):
                    if i < window - 1:
                        ma_values.append(amounts[i])
                    else:
                        window_sum = sum(amounts[i-window+1:i+1])
                        ma_values.append(window_sum / window)
                
                moving_averages[category] = ma_values
            
            return moving_averages
        except Exception as e:
            print(f"Error calculating moving averages: {e}")
            return {}
    
    def generate_report(self):
        """Generate comprehensive spending analysis report."""
        print("=" * 60)
        print("TRANSACTION ANALYSIS REPORT")
        print("=" * 60)
        
        try:
            # Basic statistics
            print(f"\nTotal Transactions: {len(self.transactions)}")
            print(f"Date Range: {min(t['date'] for t in self.transactions).strftime('%Y-%m-%d')} to {max(t['date'] for t in self.transactions).strftime('%Y-%m-%d')}")
            print(f"Total Spending: ${sum(self.category_totals.values()):.2f}")
            
            # Category totals
            print("\n" + "-" * 40)
            print("SPENDING BY CATEGORY")
            print("-" * 40)
            for category, total in sorted(self.category_totals.items(), key=lambda x: x[1], reverse=True):