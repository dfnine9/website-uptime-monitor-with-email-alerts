```python
"""
Spending Pattern Analysis Module

This module analyzes financial spending patterns by:
- Detecting trends in spending over time
- Identifying anomalies in spending behavior
- Comparing monthly and weekly spending habits across categories
- Providing statistical insights and visualizations via text output

The module processes spending data and generates comprehensive reports
including trend analysis, anomaly detection, and comparative statistics.
"""

import json
import statistics
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import math

class SpendingAnalyzer:
    def __init__(self):
        self.transactions = []
        self.categories = set()
        
    def add_transaction(self, date: str, amount: float, category: str, description: str = ""):
        """Add a transaction to the dataset"""
        try:
            parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            transaction = {
                'date': parsed_date,
                'amount': abs(amount),  # Ensure positive for spending
                'category': category.lower().strip(),
                'description': description
            }
            self.transactions.append(transaction)
            self.categories.add(category.lower().strip())
        except ValueError as e:
            print(f"Error parsing date {date}: {e}")
    
    def load_sample_data(self):
        """Load sample spending data for demonstration"""
        sample_data = [
            ("2024-01-15", 45.99, "groceries", "Weekly shopping"),
            ("2024-01-16", 12.50, "transportation", "Bus fare"),
            ("2024-01-18", 89.99, "entertainment", "Movie tickets"),
            ("2024-01-20", 156.78, "groceries", "Monthly stock up"),
            ("2024-01-22", 25.00, "dining", "Lunch out"),
            ("2024-01-25", 67.50, "utilities", "Electric bill"),
            ("2024-01-28", 34.99, "shopping", "Clothing"),
            ("2024-02-02", 52.30, "groceries", "Weekly shopping"),
            ("2024-02-05", 15.75, "transportation", "Taxi"),
            ("2024-02-08", 120.00, "entertainment", "Concert"),
            ("2024-02-12", 178.90, "groceries", "Monthly shopping"),
            ("2024-02-14", 85.50, "dining", "Valentine's dinner"),
            ("2024-02-18", 71.25, "utilities", "Gas bill"),
            ("2024-02-22", 43.99, "shopping", "Books"),
            ("2024-02-28", 95.00, "healthcare", "Doctor visit"),
            ("2024-03-03", 48.75, "groceries", "Weekly shopping"),
            ("2024-03-07", 22.50, "transportation", "Parking"),
            ("2024-03-10", 156.99, "entertainment", "Theater show"),
            ("2024-03-15", 189.45, "groceries", "Monthly shopping"),
            ("2024-03-18", 55.80, "dining", "Weekend brunch"),
            ("2024-03-22", 68.90, "utilities", "Water bill"),
            ("2024-03-25", 299.99, "shopping", "Electronics"),  # Anomaly
            ("2024-03-28", 125.00, "healthcare", "Dental checkup"),
        ]
        
        for date, amount, category, desc in sample_data:
            self.add_transaction(date, amount, category, desc)
    
    def detect_trends(self) -> Dict[str, Any]:
        """Detect spending trends over time"""
        try:
            if not self.transactions:
                return {"error": "No transactions to analyze"}
            
            # Sort transactions by date
            sorted_transactions = sorted(self.transactions, key=lambda x: x['date'])
            
            # Monthly trends
            monthly_spending = defaultdict(float)
            for transaction in sorted_transactions:
                month_key = transaction['date'].strftime("%Y-%m")
                monthly_spending[month_key] += transaction['amount']
            
            # Calculate trend direction
            monthly_values = list(monthly_spending.values())
            if len(monthly_values) >= 2:
                trend_slope = (monthly_values[-1] - monthly_values[0]) / len(monthly_values)
                trend_direction = "increasing" if trend_slope > 5 else "decreasing" if trend_slope < -5 else "stable"
            else:
                trend_direction = "insufficient_data"
            
            # Category trends
            category_trends = {}
            for category in self.categories:
                cat_monthly = defaultdict(float)
                for transaction in sorted_transactions:
                    if transaction['category'] == category:
                        month_key = transaction['date'].strftime("%Y-%m")
                        cat_monthly[month_key] += transaction['amount']
                
                if len(cat_monthly) >= 2:
                    cat_values = list(cat_monthly.values())
                    cat_slope = (cat_values[-1] - cat_values[0]) / len(cat_values)
                    category_trends[category] = {
                        "direction": "increasing" if cat_slope > 5 else "decreasing" if cat_slope < -5 else "stable",
                        "slope": round(cat_slope, 2)
                    }
            
            return {
                "overall_trend": trend_direction,
                "monthly_spending": dict(monthly_spending),
                "category_trends": category_trends
            }
        
        except Exception as e:
            return {"error": f"Error detecting trends: {e}"}
    
    def identify_anomalies(self) -> Dict[str, Any]:
        """Identify spending anomalies using statistical methods"""
        try:
            if len(self.transactions) < 3:
                return {"error": "Insufficient data for anomaly detection"}
            
            amounts = [t['amount'] for t in self.transactions]
            mean_amount = statistics.mean(amounts)
            std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            # Define anomaly threshold (2 standard deviations)
            threshold = mean_amount + (2 * std_dev)
            
            anomalies = []
            for transaction in self.transactions:
                if transaction['amount'] > threshold:
                    anomalies.append({
                        'date': transaction['date'].strftime("%Y-%m-%d"),
                        'amount': transaction['amount'],
                        'category': transaction['category'],
                        'description': transaction['description'],
                        'deviation_score': round((transaction['amount'] - mean_amount) / std_dev, 2) if std_dev > 0 else 0
                    })
            
            # Category-specific anomalies
            category_anomalies = {}
            for category in self.categories:
                category_amounts = [t['amount'] for t in self.transactions if t['category'] == category]
                if len(category_amounts) >= 3:
                    cat_mean = statistics.mean(category_amounts)
                    cat_std = statistics.stdev(category_amounts)
                    cat_threshold = cat_mean + (1.5 * cat_std)
                    
                    cat_anomalies = [t for t in self.transactions 
                                   if t['category'] == category and t['amount'] > cat_threshold]
                    
                    if cat_anomalies:
                        category_anomalies[category] = [
                            {
                                'date': t['date'].strftime("%Y-%m-%d"),
                                'amount': t['amount'],
                                'expected_range': f"${cat_mean:.2f} ± ${cat_std:.2f}"
                            } for t in cat_anomalies
                        ]
            
            return {
                "global_anomalies": anomalies,
                "category_anomalies": category_anomalies,
                "statistics": {
                    "mean_spending": round(mean_amount, 2),
                    "std_deviation": round(std_dev, 2),