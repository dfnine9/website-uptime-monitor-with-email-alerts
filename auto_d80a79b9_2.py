```python
"""
Financial Data Analysis Module

This module provides comprehensive analysis of spending data including:
- Monthly spending trend calculations
- Unusual spending pattern detection using statistical outliers
- Statistical summaries with category breakdowns
- Month-over-month change analysis

Features:
- Self-contained with minimal dependencies
- Robust error handling
- Statistical outlier detection for anomaly identification
- Comprehensive spending analytics

Usage: python script.py
"""

import json
import statistics
import calendar
from datetime import datetime, timedelta
from collections import defaultdict
import random


class SpendingAnalyzer:
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
        
    def generate_sample_data(self):
        """Generate realistic sample spending data for demonstration"""
        categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Other']
        
        # Generate 12 months of data
        for month in range(1, 13):
            # Generate 15-30 transactions per month
            num_transactions = random.randint(15, 30)
            
            for _ in range(num_transactions):
                category = random.choice(categories)
                
                # Category-specific spending ranges
                base_amounts = {
                    'Food': (20, 150),
                    'Transportation': (10, 80),
                    'Entertainment': (15, 120),
                    'Shopping': (25, 300),
                    'Bills': (50, 500),
                    'Healthcare': (30, 200),
                    'Other': (10, 100)
                }
                
                min_amt, max_amt = base_amounts[category]
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                # Occasionally add unusual spending (outliers)
                if random.random() < 0.05:  # 5% chance of unusual spending
                    amount *= random.uniform(2.5, 5.0)
                
                day = random.randint(1, 28)
                date = f"2024-{month:02d}-{day:02d}"
                
                transaction = {
                    'date': date,
                    'category': category,
                    'amount': round(amount, 2)
                }
                
                self.transactions.append(transaction)
    
    def load_data(self):
        """Process transactions into monthly and category summaries"""
        try:
            for transaction in self.transactions:
                date = transaction['date']
                category = transaction['category']
                amount = transaction['amount']
                
                # Extract month from date
                month_key = date[:7]  # YYYY-MM format
                
                self.monthly_data[month_key][category] += amount
                self.category_totals[category] += amount
                
        except Exception as e:
            print(f"Error processing transaction data: {e}")
            raise
    
    def calculate_monthly_trends(self):
        """Calculate monthly spending trends and totals"""
        try:
            monthly_totals = {}
            monthly_trends = []
            
            sorted_months = sorted(self.monthly_data.keys())
            
            for month in sorted_months:
                month_total = sum(self.monthly_data[month].values())
                monthly_totals[month] = month_total
            
            # Calculate month-over-month changes
            prev_total = None
            for month in sorted_months:
                current_total = monthly_totals[month]
                
                if prev_total is not None:
                    change = current_total - prev_total
                    change_percent = (change / prev_total) * 100 if prev_total != 0 else 0
                    
                    trend_data = {
                        'month': month,
                        'total': current_total,
                        'change': change,
                        'change_percent': change_percent
                    }
                    monthly_trends.append(trend_data)
                else:
                    trend_data = {
                        'month': month,
                        'total': current_total,
                        'change': 0,
                        'change_percent': 0
                    }
                    monthly_trends.append(trend_data)
                
                prev_total = current_total
            
            return monthly_totals, monthly_trends
            
        except Exception as e:
            print(f"Error calculating monthly trends: {e}")
            return {}, []
    
    def detect_unusual_patterns(self):
        """Identify unusual spending patterns using statistical analysis"""
        try:
            unusual_patterns = []
            
            # Analyze by category for outliers
            for category in self.category_totals.keys():
                category_amounts = []
                
                # Collect all transaction amounts for this category
                for transaction in self.transactions:
                    if transaction['category'] == category:
                        category_amounts.append(transaction['amount'])
                
                if len(category_amounts) < 3:
                    continue
                
                # Calculate statistical measures
                mean_amount = statistics.mean(category_amounts)
                stdev_amount = statistics.stdev(category_amounts) if len(category_amounts) > 1 else 0
                
                # Find outliers (transactions > 2 standard deviations from mean)
                outlier_threshold = mean_amount + (2 * stdev_amount)
                
                for transaction in self.transactions:
                    if (transaction['category'] == category and 
                        transaction['amount'] > outlier_threshold and 
                        stdev_amount > 0):
                        
                        unusual_patterns.append({
                            'date': transaction['date'],
                            'category': category,
                            'amount': transaction['amount'],
                            'expected_range': f"${mean_amount:.2f} ± ${stdev_amount:.2f}",
                            'deviation': f"{((transaction['amount'] - mean_amount) / stdev_amount):.1f}σ"
                        })
            
            return unusual_patterns
            
        except Exception as e:
            print(f"Error detecting unusual patterns: {e}")
            return []
    
    def generate_statistical_summary(self):
        """Generate comprehensive statistical summary"""
        try:
            # Overall statistics
            total_spending = sum(self.category_totals.values())
            avg_transaction = total_spending / len(self.transactions) if self.transactions else 0
            
            # Category averages
            category_stats = {}
            for category, total in self.category_totals.items():
                category_transactions = [t for t in self.transactions if t['category'] == category]
                avg_amount = total / len(category_transactions) if category_transactions else 0
                transaction_count = len(category_transactions)
                percentage = (total / total_spending) * 100 if total_spending > 0 else 0
                
                category_stats[category] = {
                    'total': total,
                    'average': avg_amount,
                    'count': transaction_count,
                    'percentage': percentage
                }
            
            # Monthly averages
            monthly_totals, _ = self.calculate_monthly_trends()
            avg_monthly = statistics.mean(monthly_totals.values()) if monthly_totals else 0
            
            return {
                'total_spending': total_spending,
                'average_transaction': avg_transaction,
                'average_monthly': avg_monthly,
                'total_transactions': len(self.transactions),
                'category_breakdown': category_stats,
                'analysis_period': f"{min(monthly_totals.keys())} to {max(monthly_totals.keys())}" if monthly_totals else "No data"
            }
            
        except Exception as e:
            print(f"Error generating statistical summary: {e}")
            return {}
    
    def print_analysis_report(self):
        """Print comprehensive spending analysis report"""
        try:
            print("=" * 60)
            print("SPENDING ANALYSIS REPORT")
            print("=" * 60)
            
            # Statistical Summary
            summary = self.generate_statistical_summary()
            print(f"\n📊 STATISTICAL SUMMARY")
            print(f"Analysis Period: