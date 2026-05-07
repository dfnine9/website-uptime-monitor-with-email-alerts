```python
"""
Personal Finance Transaction Analysis Module

This module processes categorized financial transactions to generate comprehensive
spending insights including monthly trends, category breakdowns, and unusual
spending pattern identification. It provides statistical analysis of spending
habits with automated anomaly detection using standard deviation thresholds.

Features:
- Monthly spending trend analysis
- Category-wise expenditure breakdown
- Unusual spending pattern detection (outliers > 2 standard deviations)
- Statistical summaries and insights
- Sample data generation for demonstration

Usage:
    python script.py

Dependencies:
    - Standard library only (statistics, datetime, json, random)
"""

import json
import statistics
import datetime
import random
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple


class TransactionAnalyzer:
    """Analyzes categorized financial transactions for spending insights."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(list)
        self.category_data = defaultdict(list)
    
    def load_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """Load transaction data for analysis."""
        try:
            self.transactions = transactions
            self._organize_data()
        except Exception as e:
            raise ValueError(f"Error loading transactions: {e}")
    
    def _organize_data(self) -> None:
        """Organize transactions by month and category."""
        for transaction in self.transactions:
            try:
                date_str = transaction['date']
                amount = float(transaction['amount'])
                category = transaction['category']
                
                # Parse date and create month key
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                
                self.monthly_data[month_key].append(amount)
                self.category_data[category].append(amount)
                
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping invalid transaction: {e}")
    
    def analyze_monthly_trends(self) -> Dict[str, Any]:
        """Analyze monthly spending trends."""
        try:
            monthly_totals = {}
            monthly_stats = {}
            
            for month, amounts in self.monthly_data.items():
                total = sum(amounts)
                avg = statistics.mean(amounts)
                median = statistics.median(amounts)
                
                monthly_totals[month] = total
                monthly_stats[month] = {
                    'total': total,
                    'average_transaction': avg,
                    'median_transaction': median,
                    'transaction_count': len(amounts)
                }
            
            # Calculate trend
            sorted_months = sorted(monthly_totals.keys())
            if len(sorted_months) >= 2:
                recent_avg = statistics.mean([monthly_totals[m] for m in sorted_months[-3:]])
                earlier_avg = statistics.mean([monthly_totals[m] for m in sorted_months[:-3]]) if len(sorted_months) > 3 else monthly_totals[sorted_months[0]]
                trend = "increasing" if recent_avg > earlier_avg else "decreasing"
            else:
                trend = "insufficient_data"
            
            return {
                'monthly_stats': monthly_stats,
                'trend': trend,
                'highest_month': max(monthly_totals.items(), key=lambda x: x[1]),
                'lowest_month': min(monthly_totals.items(), key=lambda x: x[1])
            }
            
        except Exception as e:
            raise RuntimeError(f"Error analyzing monthly trends: {e}")
    
    def analyze_category_breakdown(self) -> Dict[str, Any]:
        """Analyze spending by category."""
        try:
            category_stats = {}
            total_spending = sum(sum(amounts) for amounts in self.category_data.values())
            
            for category, amounts in self.category_data.items():
                total = sum(amounts)
                avg = statistics.mean(amounts)
                percentage = (total / total_spending * 100) if total_spending > 0 else 0
                
                category_stats[category] = {
                    'total': total,
                    'percentage': percentage,
                    'average_transaction': avg,
                    'transaction_count': len(amounts),
                    'max_transaction': max(amounts),
                    'min_transaction': min(amounts)
                }
            
            # Sort by total spending
            sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]['total'], reverse=True)
            
            return {
                'category_stats': category_stats,
                'top_categories': sorted_categories[:5],
                'total_spending': total_spending
            }
            
        except Exception as e:
            raise RuntimeError(f"Error analyzing category breakdown: {e}")
    
    def identify_unusual_patterns(self) -> Dict[str, Any]:
        """Identify unusual spending patterns using statistical analysis."""
        try:
            all_amounts = [float(t['amount']) for t in self.transactions]
            
            if len(all_amounts) < 3:
                return {'outliers': [], 'warning': 'Insufficient data for anomaly detection'}
            
            mean_amount = statistics.mean(all_amounts)
            stdev_amount = statistics.stdev(all_amounts)
            threshold = 2 * stdev_amount  # 2 standard deviations
            
            outliers = []
            category_outliers = defaultdict(list)
            
            for transaction in self.transactions:
                amount = float(transaction['amount'])
                if abs(amount - mean_amount) > threshold:
                    outlier_info = {
                        'transaction': transaction,
                        'deviation': abs(amount - mean_amount),
                        'severity': 'high' if abs(amount - mean_amount) > 3 * stdev_amount else 'moderate'
                    }
                    outliers.append(outlier_info)
                    category_outliers[transaction['category']].append(outlier_info)
            
            # Identify categories with frequent outliers
            problematic_categories = {
                cat: len(cat_outliers) 
                for cat, cat_outliers in category_outliers.items() 
                if len(cat_outliers) > 1
            }
            
            return {
                'outliers': outliers,
                'total_outliers': len(outliers),
                'mean_spending': mean_amount,
                'std_deviation': stdev_amount,
                'problematic_categories': problematic_categories
            }
            
        except Exception as e:
            raise RuntimeError(f"Error identifying unusual patterns: {e}")
    
    def generate_insights_report(self) -> str:
        """Generate comprehensive spending insights report."""
        try:
            monthly_analysis = self.analyze_monthly_trends()
            category_analysis = self.analyze_category_breakdown()
            unusual_patterns = self.identify_unusual_patterns()
            
            report = []
            report.append("=" * 60)
            report.append("PERSONAL FINANCE SPENDING ANALYSIS REPORT")
            report.append("=" * 60)
            report.append("")
            
            # Monthly Trends
            report.append("📊 MONTHLY SPENDING TRENDS")
            report.append("-" * 30)
            report.append(f"Overall trend: {monthly_analysis['trend'].upper()}")
            report.append(f"Highest spending month: {monthly_analysis['highest_month'][0]} (${monthly_analysis['highest_month'][1]:,.2f})")
            report.append(f"Lowest spending month: {monthly_analysis['lowest_month'][0]} (${monthly_analysis['lowest_month'][1]:,.2f})")
            report.append("")
            
            for month, stats in sorted(monthly_analysis['monthly_stats'].items()):
                report.append(f"{month}: ${stats['total']:,.2f} ({stats['transaction_count']} transactions, avg: ${stats['average_transaction']:.2f})")
            report.append("")
            
            # Category Breakdown
            report.append("🏷️  CATEGORY BREAKDOWN")
            report.append("-" * 25)
            report.append(f"Total spending: