```python
"""
Personal Finance Analyzer

A comprehensive data analysis module that processes financial transaction data to:
- Calculate detailed spending patterns and statistics
- Identify top expense categories with percentage breakdowns
- Track monthly spending trends and growth rates
- Detect unusual spending behaviors using statistical thresholds (z-scores)
- Generate actionable insights for budget optimization

This module uses only standard library components plus httpx and anthropic for 
minimal dependency requirements while providing robust financial analytics.
"""

import json
import statistics
import calendar
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random
import math

class FinancialAnalyzer:
    def __init__(self, transactions: List[Dict]):
        """Initialize with transaction data."""
        self.transactions = transactions
        self.monthly_data = defaultdict(float)
        self.category_data = defaultdict(float)
        self.daily_data = defaultdict(float)
        
    def process_transactions(self):
        """Process raw transaction data into structured format."""
        try:
            for transaction in self.transactions:
                amount = abs(float(transaction.get('amount', 0)))
                category = transaction.get('category', 'Uncategorized').title()
                date_str = transaction.get('date', '')
                
                # Parse date
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    continue
                    
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                day_key = date_str
                
                self.monthly_data[month_key] += amount
                self.category_data[category] += amount
                self.daily_data[day_key] += amount
                
        except Exception as e:
            print(f"Error processing transactions: {e}")
            
    def calculate_spending_patterns(self) -> Dict[str, Any]:
        """Calculate comprehensive spending statistics."""
        try:
            amounts = [abs(float(t.get('amount', 0))) for t in self.transactions]
            amounts = [a for a in amounts if a > 0]  # Remove zero amounts
            
            if not amounts:
                return {"error": "No valid transaction amounts found"}
                
            total_spent = sum(amounts)
            avg_transaction = statistics.mean(amounts)
            median_transaction = statistics.median(amounts)
            std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            # Transaction frequency analysis
            daily_amounts = list(self.daily_data.values())
            avg_daily_spend = statistics.mean(daily_amounts) if daily_amounts else 0
            
            return {
                "total_spending": round(total_spent, 2),
                "transaction_count": len(amounts),
                "average_transaction": round(avg_transaction, 2),
                "median_transaction": round(median_transaction, 2),
                "spending_volatility": round(std_dev, 2),
                "average_daily_spending": round(avg_daily_spend, 2),
                "largest_transaction": max(amounts),
                "smallest_transaction": min(amounts)
            }
        except Exception as e:
            return {"error": f"Failed to calculate spending patterns: {e}"}
    
    def identify_top_categories(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Identify top spending categories with percentages."""
        try:
            total_spending = sum(self.category_data.values())
            if total_spending == 0:
                return []
                
            sorted_categories = sorted(
                self.category_data.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:top_n]
            
            results = []
            for category, amount in sorted_categories:
                percentage = (amount / total_spending) * 100
                results.append({
                    "category": category,
                    "amount": round(amount, 2),
                    "percentage": round(percentage, 1),
                    "transaction_count": sum(1 for t in self.transactions 
                                           if t.get('category', '').title() == category)
                })
            
            return results
        except Exception as e:
            print(f"Error identifying top categories: {e}")
            return []
    
    def track_monthly_trends(self) -> Dict[str, Any]:
        """Analyze monthly spending trends and growth rates."""
        try:
            sorted_months = sorted(self.monthly_data.items())
            if len(sorted_months) < 2:
                return {"error": "Need at least 2 months of data for trend analysis"}
            
            trends = []
            growth_rates = []
            
            for i, (month, amount) in enumerate(sorted_months):
                trend_data = {
                    "month": month,
                    "spending": round(amount, 2)
                }
                
                if i > 0:
                    prev_amount = sorted_months[i-1][1]
                    growth_rate = ((amount - prev_amount) / prev_amount * 100) if prev_amount > 0 else 0
                    trend_data["growth_rate"] = round(growth_rate, 1)
                    growth_rates.append(growth_rate)
                    
                trends.append(trend_data)
            
            # Calculate trend statistics
            monthly_amounts = [amount for _, amount in sorted_months]
            avg_monthly = statistics.mean(monthly_amounts)
            trend_direction = "increasing" if growth_rates and statistics.mean(growth_rates) > 0 else "decreasing"
            
            return {
                "monthly_trends": trends,
                "average_monthly_spending": round(avg_monthly, 2),
                "trend_direction": trend_direction,
                "average_growth_rate": round(statistics.mean(growth_rates), 1) if growth_rates else 0,
                "most_expensive_month": max(sorted_months, key=lambda x: x[1]),
                "least_expensive_month": min(sorted_months, key=lambda x: x[1])
            }
        except Exception as e:
            return {"error": f"Failed to track monthly trends: {e}"}
    
    def detect_anomalies(self, z_threshold: float = 2.0) -> Dict[str, Any]:
        """Detect unusual spending using statistical thresholds."""
        try:
            amounts = [abs(float(t.get('amount', 0))) for t in self.transactions]
            amounts = [a for a in amounts if a > 0]
            
            if len(amounts) < 3:
                return {"error": "Need at least 3 transactions for anomaly detection"}
            
            mean_amount = statistics.mean(amounts)
            std_amount = statistics.stdev(amounts)
            
            anomalies = []
            normal_range = (mean_amount - z_threshold * std_amount, 
                          mean_amount + z_threshold * std_amount)
            
            for i, transaction in enumerate(self.transactions):
                amount = abs(float(transaction.get('amount', 0)))
                if amount == 0:
                    continue
                    
                z_score = (amount - mean_amount) / std_amount if std_amount > 0 else 0
                
                if abs(z_score) > z_threshold:
                    anomaly_type = "unusually_high" if z_score > 0 else "unusually_low"
                    anomalies.append({
                        "transaction_index": i,
                        "date": transaction.get('date', ''),
                        "category": transaction.get('category', 'Uncategorized'),
                        "amount": amount,
                        "z_score": round(z_score, 2),
                        "anomaly_type": anomaly_type,
                        "description": transaction.get('description', '')
                    })
            
            # Daily spending anomalies
            daily_amounts = list(self.daily_data.values())
            daily_mean = statistics.mean(daily_amounts) if daily_amounts else 0
            daily_std = statistics.stdev(daily_amounts) if len(daily_amounts) > 1 else