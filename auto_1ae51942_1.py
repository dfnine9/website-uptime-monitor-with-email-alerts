```python
#!/usr/bin/env python3
"""
Financial Transaction Data Processing Module

This module provides functionality to aggregate categorized financial transactions
by month, calculate spending totals per category, and identify spending trends
and anomalies in the data.

Features:
- Monthly transaction aggregation
- Category-based spending analysis
- Trend detection using moving averages
- Anomaly detection using statistical methods
- Comprehensive error handling
- Sample data generation for testing

Usage:
    python script.py

The module generates sample transaction data and processes it to demonstrate
financial analysis capabilities including trend analysis and anomaly detection.
"""

import json
import statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import random


class TransactionProcessor:
    """Processes financial transaction data for analysis and reporting."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
        
    def add_transaction(self, date: str, category: str, amount: float, description: str = ""):
        """Add a transaction to the dataset."""
        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
            
            transaction = {
                'date': date,
                'category': category,
                'amount': abs(amount),  # Ensure positive amounts
                'description': description
            }
            self.transactions.append(transaction)
            
        except ValueError as e:
            print(f"Error adding transaction: Invalid date format {date}. Use YYYY-MM-DD")
            raise e
        except Exception as e:
            print(f"Error adding transaction: {e}")
            raise e
    
    def aggregate_by_month(self) -> Dict[str, Dict[str, float]]:
        """Aggregate transactions by month and category."""
        try:
            self.monthly_data.clear()
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                category = transaction['category']
                amount = transaction['amount']
                
                self.monthly_data[month_key][category] += amount
                
            return dict(self.monthly_data)
            
        except Exception as e:
            print(f"Error aggregating by month: {e}")
            return {}
    
    def calculate_category_totals(self) -> Dict[str, float]:
        """Calculate total spending per category across all time."""
        try:
            self.category_totals.clear()
            
            for transaction in self.transactions:
                category = transaction['category']
                amount = transaction['amount']
                self.category_totals[category] += amount
                
            return dict(self.category_totals)
            
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return {}
    
    def calculate_monthly_totals(self) -> Dict[str, float]:
        """Calculate total spending per month."""
        try:
            monthly_totals = {}
            
            for month, categories in self.monthly_data.items():
                monthly_totals[month] = sum(categories.values())
                
            return monthly_totals
            
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def detect_trends(self, window_size: int = 3) -> Dict[str, Any]:
        """Detect spending trends using moving averages."""
        try:
            monthly_totals = self.calculate_monthly_totals()
            
            if len(monthly_totals) < window_size:
                return {"error": f"Not enough data for trend analysis. Need at least {window_size} months."}
            
            # Sort by date
            sorted_months = sorted(monthly_totals.keys())
            amounts = [monthly_totals[month] for month in sorted_months]
            
            # Calculate moving averages
            moving_averages = []
            for i in range(len(amounts) - window_size + 1):
                window = amounts[i:i + window_size]
                moving_averages.append(sum(window) / window_size)
            
            # Determine overall trend
            if len(moving_averages) >= 2:
                trend_direction = "increasing" if moving_averages[-1] > moving_averages[0] else "decreasing"
                trend_strength = abs(moving_averages[-1] - moving_averages[0]) / moving_averages[0] * 100
            else:
                trend_direction = "stable"
                trend_strength = 0
            
            return {
                "trend_direction": trend_direction,
                "trend_strength_percent": round(trend_strength, 2),
                "moving_averages": moving_averages,
                "months_analyzed": sorted_months[-len(moving_averages):] if moving_averages else []
            }
            
        except Exception as e:
            print(f"Error detecting trends: {e}")
            return {"error": str(e)}
    
    def detect_anomalies(self, threshold_factor: float = 2.0) -> Dict[str, Any]:
        """Detect spending anomalies using statistical methods."""
        try:
            monthly_totals = self.calculate_monthly_totals()
            
            if len(monthly_totals) < 3:
                return {"error": "Not enough data for anomaly detection. Need at least 3 months."}
            
            amounts = list(monthly_totals.values())
            mean_spending = statistics.mean(amounts)
            
            try:
                std_dev = statistics.stdev(amounts)
            except statistics.StatisticsError:
                std_dev = 0  # All values are the same
            
            threshold_upper = mean_spending + (threshold_factor * std_dev)
            threshold_lower = max(0, mean_spending - (threshold_factor * std_dev))
            
            anomalies = []
            for month, amount in monthly_totals.items():
                if amount > threshold_upper:
                    anomalies.append({
                        "month": month,
                        "amount": amount,
                        "type": "high_spending",
                        "deviation": round((amount - mean_spending) / std_dev, 2) if std_dev > 0 else 0
                    })
                elif amount < threshold_lower:
                    anomalies.append({
                        "month": month,
                        "amount": amount,
                        "type": "low_spending",
                        "deviation": round((amount - mean_spending) / std_dev, 2) if std_dev > 0 else 0
                    })
            
            return {
                "anomalies": anomalies,
                "statistics": {
                    "mean_spending": round(mean_spending, 2),
                    "std_deviation": round(std_dev, 2),
                    "threshold_upper": round(threshold_upper, 2),
                    "threshold_lower": round(threshold_lower, 2)
                }
            }
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return {"error": str(e)}
    
    def get_category_trends(self) -> Dict[str, Dict[str, Any]]:
        """Analyze trends for each spending category."""
        try:
            category_trends = {}
            
            # Get all unique categories
            categories = set(transaction['category'] for transaction in self.transactions)
            
            for category in categories:
                # Get monthly spending for this category
                monthly_category_spending = {}
                
                for month, categories_dict in self.monthly_data.items():
                    monthly_category_spending[month] = categories_dict.get(category, 0)
                
                if len(monthly_category_spending) >= 2:
                    sorted_months = sorted(monthly_category_spending.keys())
                    amounts = [monthly_category_spending[month] for month in sorted_months]
                    
                    # Calculate trend
                    first_amount = amounts[0] if amounts[0] > 0 else 0.01  # Avoid division by zero