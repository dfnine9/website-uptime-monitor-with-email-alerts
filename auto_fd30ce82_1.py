```python
"""
Transaction Data Analyzer Module

This module provides comprehensive analysis of categorized transaction data to:
- Identify spending patterns and trends
- Calculate monthly totals by category
- Detect budget anomalies using statistical methods
- Generate insights including averages, variances, and trend analysis

The module processes transaction data in CSV format or as structured dictionaries,
performs statistical analysis, and outputs detailed reports to help users understand
their financial patterns and identify unusual spending behavior.

Dependencies: Standard library only (csv, statistics, datetime, collections)
Usage: python script.py
"""

import csv
import statistics
import datetime
from collections import defaultdict, Counter
import json
import io
import sys
from typing import Dict, List, Tuple, Any, Optional


class TransactionAnalyzer:
    """Analyzes transaction data for patterns, anomalies, and insights."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.category_stats = {}
        self.anomalies = []
        
    def load_sample_data(self) -> None:
        """Load sample transaction data for demonstration."""
        sample_data = [
            {"date": "2024-01-15", "amount": -45.50, "category": "Groceries", "description": "Supermarket"},
            {"date": "2024-01-16", "amount": -1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-01-18", "amount": -25.99, "category": "Entertainment", "description": "Movie tickets"},
            {"date": "2024-01-20", "amount": -67.34, "category": "Groceries", "description": "Organic market"},
            {"date": "2024-01-22", "amount": -89.99, "category": "Utilities", "description": "Electric bill"},
            {"date": "2024-02-01", "amount": -52.11, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-02-03", "amount": -1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-02-05", "amount": -156.78, "category": "Entertainment", "description": "Concert tickets"},
            {"date": "2024-02-08", "amount": -73.45, "category": "Groceries", "description": "Farmers market"},
            {"date": "2024-02-10", "amount": -95.67, "category": "Utilities", "description": "Gas bill"},
            {"date": "2024-02-15", "amount": -890.00, "category": "Healthcare", "description": "Dental work"},
            {"date": "2024-03-01", "amount": -48.92, "category": "Groceries", "description": "Corner store"},
            {"date": "2024-03-03", "amount": -1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-03-05", "amount": -34.56, "category": "Entertainment", "description": "Streaming services"},
            {"date": "2024-03-08", "amount": -2500.00, "category": "Travel", "description": "Vacation booking"},
            {"date": "2024-03-12", "amount": -91.23, "category": "Utilities", "description": "Internet bill"},
            {"date": "2024-03-15", "amount": -76.88, "category": "Groceries", "description": "Bulk shopping"},
        ]
        
        for transaction in sample_data:
            try:
                transaction["date"] = datetime.datetime.strptime(transaction["date"], "%Y-%m-%d").date()
                transaction["amount"] = abs(transaction["amount"])  # Work with positive amounts
                self.transactions.append(transaction)
            except (ValueError, KeyError) as e:
                print(f"Error processing transaction: {e}")
                continue
    
    def calculate_monthly_totals(self) -> None:
        """Calculate total spending by category for each month."""
        try:
            for transaction in self.transactions:
                month_key = transaction["date"].strftime("%Y-%m")
                category = transaction["category"]
                amount = transaction["amount"]
                
                self.monthly_totals[month_key][category] += amount
                
        except KeyError as e:
            print(f"Error calculating monthly totals: Missing key {e}")
        except Exception as e:
            print(f"Unexpected error in monthly totals calculation: {e}")
    
    def analyze_spending_patterns(self) -> Dict[str, Any]:
        """Analyze spending patterns across categories and time."""
        patterns = {}
        
        try:
            # Category-wise analysis
            category_totals = defaultdict(float)
            category_counts = defaultdict(int)
            category_amounts = defaultdict(list)
            
            for transaction in self.transactions:
                category = transaction["category"]
                amount = transaction["amount"]
                
                category_totals[category] += amount
                category_counts[category] += 1
                category_amounts[category].append(amount)
            
            # Calculate statistics for each category
            for category in category_totals:
                amounts = category_amounts[category]
                patterns[category] = {
                    "total_spent": round(category_totals[category], 2),
                    "transaction_count": category_counts[category],
                    "average_per_transaction": round(category_totals[category] / category_counts[category], 2),
                    "min_transaction": round(min(amounts), 2),
                    "max_transaction": round(max(amounts), 2),
                    "median_transaction": round(statistics.median(amounts), 2),
                    "std_deviation": round(statistics.stdev(amounts) if len(amounts) > 1 else 0, 2)
                }
            
            return patterns
            
        except Exception as e:
            print(f"Error in spending pattern analysis: {e}")
            return {}
    
    def detect_budget_anomalies(self, z_threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalous transactions using statistical methods."""
        anomalies = []
        
        try:
            # Group transactions by category
            category_amounts = defaultdict(list)
            for transaction in self.transactions:
                category_amounts[transaction["category"]].append(transaction["amount"])
            
            # Detect anomalies within each category
            for category, amounts in category_amounts.items():
                if len(amounts) < 3:  # Need at least 3 transactions for meaningful analysis
                    continue
                
                mean_amount = statistics.mean(amounts)
                std_amount = statistics.stdev(amounts)
                
                if std_amount == 0:  # All amounts are the same
                    continue
                
                # Find transactions that are z_threshold standard deviations away from mean
                for i, transaction in enumerate(self.transactions):
                    if transaction["category"] == category:
                        z_score = abs((transaction["amount"] - mean_amount) / std_amount)
                        
                        if z_score > z_threshold:
                            anomalies.append({
                                "transaction": transaction,
                                "z_score": round(z_score, 2),
                                "category_mean": round(mean_amount, 2),
                                "category_std": round(std_amount, 2),
                                "anomaly_type": "high" if transaction["amount"] > mean_amount else "low"
                            })
            
            return sorted(anomalies, key=lambda x: x["z_score"], reverse=True)
            
        except Exception as e:
            print(f"Error in anomaly detection: {e}")
            return []
    
    def generate_trend_analysis(self) -> Dict[str, Any]:
        """Generate trend analysis across months."""
        trends = {}
        
        try:
            # Monthly spending trends
            monthly_spending = defaultdict(float)
            for month_data in self.monthly_totals.values():
                for category, amount in month_data.items():
                    monthly_spending[month_data] += amount