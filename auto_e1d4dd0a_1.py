```python
#!/usr/bin/env python3
"""
Transaction Analysis Script

This module processes categorized financial transaction data to provide comprehensive
spending analysis including:
- Monthly spending totals by category
- Spending trend identification over time
- Summary statistics (averages, percentages, growth rates)
- Anomaly detection for unusual spending patterns

The script generates mock transaction data for demonstration and performs analysis
using only Python standard library functions.

Usage: python script.py
"""

import json
import random
import statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any


class TransactionAnalyzer:
    """Analyzes financial transactions for spending patterns and trends."""
    
    def __init__(self):
        self.transactions = []
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 
                          'Utilities', 'Healthcare', 'Education', 'Travel']
    
    def generate_mock_data(self, months: int = 12) -> List[Dict[str, Any]]:
        """Generate mock transaction data for analysis."""
        transactions = []
        base_date = datetime.now() - timedelta(days=months * 30)
        
        # Category spending patterns (base amounts)
        category_ranges = {
            'Food': (200, 800),
            'Transportation': (100, 400),
            'Entertainment': (50, 300),
            'Shopping': (100, 600),
            'Utilities': (150, 250),
            'Healthcare': (50, 500),
            'Education': (0, 200),
            'Travel': (0, 1000)
        }
        
        for month in range(months):
            month_date = base_date + timedelta(days=month * 30)
            
            # Generate 15-45 transactions per month
            num_transactions = random.randint(15, 45)
            
            for _ in range(num_transactions):
                category = random.choice(self.categories)
                min_amt, max_amt = category_ranges[category]
                
                # Add seasonal variation
                seasonal_factor = 1.0
                if category == 'Travel' and month_date.month in [6, 7, 12]:
                    seasonal_factor = 2.0
                elif category == 'Utilities' and month_date.month in [1, 2, 7, 8]:
                    seasonal_factor = 1.5
                
                amount = round(random.uniform(min_amt, max_amt) * seasonal_factor, 2)
                
                # Random day within the month
                day_offset = random.randint(0, 29)
                transaction_date = month_date + timedelta(days=day_offset)
                
                transactions.append({
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'amount': amount,
                    'category': category,
                    'description': f'{category} purchase'
                })
        
        return sorted(transactions, key=lambda x: x['date'])
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
        monthly_totals = defaultdict(lambda: defaultdict(float))
        
        try:
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = float(transaction['amount'])
                
                monthly_totals[month_key][category] += amount
                monthly_totals[month_key]['TOTAL'] += amount
                
        except (ValueError, KeyError) as e:
            print(f"Error processing transaction data: {e}")
            return {}
        
        return dict(monthly_totals)
    
    def identify_spending_trends(self, monthly_totals: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Identify spending trends over time for each category."""
        trends = {}
        
        try:
            # Sort months chronologically
            sorted_months = sorted(monthly_totals.keys())
            
            for category in self.categories:
                monthly_amounts = []
                for month in sorted_months:
                    amount = monthly_totals[month].get(category, 0.0)
                    monthly_amounts.append(amount)
                
                if len(monthly_amounts) < 2:
                    continue
                
                # Calculate trend metrics
                avg_amount = statistics.mean(monthly_amounts)
                median_amount = statistics.median(monthly_amounts)
                std_dev = statistics.stdev(monthly_amounts) if len(monthly_amounts) > 1 else 0
                
                # Calculate growth rate (first vs last 3 months average)
                if len(monthly_amounts) >= 6:
                    first_quarter = statistics.mean(monthly_amounts[:3])
                    last_quarter = statistics.mean(monthly_amounts[-3:])
                    growth_rate = ((last_quarter - first_quarter) / first_quarter * 100) if first_quarter > 0 else 0
                else:
                    growth_rate = 0
                
                # Trend direction
                if growth_rate > 10:
                    trend_direction = "Increasing"
                elif growth_rate < -10:
                    trend_direction = "Decreasing"
                else:
                    trend_direction = "Stable"
                
                trends[category] = {
                    'average_monthly': round(avg_amount, 2),
                    'median_monthly': round(median_amount, 2),
                    'std_deviation': round(std_dev, 2),
                    'growth_rate_percent': round(growth_rate, 2),
                    'trend_direction': trend_direction,
                    'min_month': round(min(monthly_amounts), 2),
                    'max_month': round(max(monthly_amounts), 2)
                }
        
        except Exception as e:
            print(f"Error calculating trends: {e}")
            return {}
        
        return trends
    
    def generate_summary_statistics(self, monthly_totals: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Generate comprehensive summary statistics."""
        summary = {}
        
        try:
            # Overall statistics
            total_months = len(monthly_totals)
            all_monthly_totals = [month_data.get('TOTAL', 0) for month_data in monthly_totals.values()]
            
            summary['overview'] = {
                'total_months_analyzed': total_months,
                'average_monthly_spending': round(statistics.mean(all_monthly_totals), 2),
                'total_spending': round(sum(all_monthly_totals), 2),
                'highest_month': round(max(all_monthly_totals), 2),
                'lowest_month': round(min(all_monthly_totals), 2)
            }
            
            # Category breakdown
            category_totals = defaultdict(float)
            for month_data in monthly_totals.values():
                for category, amount in month_data.items():
                    if category != 'TOTAL':
                        category_totals[category] += amount
            
            total_spending = sum(category_totals.values())
            
            category_percentages = {}
            category_averages = {}
            
            for category, total_amount in category_totals.items():
                percentage = (total_amount / total_spending * 100) if total_spending > 0 else 0
                average_monthly = total_amount / total_months if total_months > 0 else 0
                
                category_percentages[category] = round(percentage, 2)
                category_averages[category] = round(average_monthly, 2)
            
            summary['category_breakdown'] = {
                'percentages': category_percentages,
                'average_monthly_by_category': category_averages,
                'total_by_category': {k: round(v, 2) for k, v in category_totals.items()}
            }
            
            # Top spending categories
            top_categories = sorted(category_totals.items(), key=lambda