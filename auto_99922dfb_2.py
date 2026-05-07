```python
#!/usr/bin/env python3
"""
Budget Recommendation Engine

This module analyzes spending patterns from historical transaction data,
identifies overspending categories, and suggests realistic budget allocations.

Features:
- Parses transaction data from CSV or generates sample data
- Calculates spending patterns and trends
- Identifies overspending categories based on statistical analysis
- Suggests budget allocations using the 50/30/20 rule as baseline
- Provides actionable recommendations for budget optimization

Usage: python script.py
"""

import json
import csv
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import os


class BudgetRecommendationEngine:
    def __init__(self):
        self.transactions = []
        self.categories = defaultdict(list)
        self.monthly_spending = defaultdict(lambda: defaultdict(float))
        
    def generate_sample_data(self) -> List[Dict[str, Any]]:
        """Generate sample transaction data for demonstration."""
        sample_transactions = [
            {"date": "2024-01-15", "amount": 1200.00, "category": "rent", "description": "Monthly rent"},
            {"date": "2024-01-16", "amount": 350.00, "category": "groceries", "description": "Whole Foods"},
            {"date": "2024-01-18", "amount": 80.00, "category": "utilities", "description": "Electric bill"},
            {"date": "2024-01-20", "amount": 45.00, "category": "dining", "description": "Restaurant"},
            {"date": "2024-01-22", "amount": 120.00, "category": "transportation", "description": "Gas"},
            {"date": "2024-02-15", "amount": 1200.00, "category": "rent", "description": "Monthly rent"},
            {"date": "2024-02-16", "amount": 380.00, "category": "groceries", "description": "Supermarket"},
            {"date": "2024-02-18", "amount": 85.00, "category": "utilities", "description": "Electric bill"},
            {"date": "2024-02-20", "amount": 75.00, "category": "dining", "description": "Takeout"},
            {"date": "2024-02-22", "amount": 110.00, "category": "transportation", "description": "Gas"},
            {"date": "2024-02-25", "amount": 200.00, "category": "entertainment", "description": "Concert tickets"},
            {"date": "2024-03-15", "amount": 1200.00, "category": "rent", "description": "Monthly rent"},
            {"date": "2024-03-16", "amount": 420.00, "category": "groceries", "description": "Grocery shopping"},
            {"date": "2024-03-18", "amount": 90.00, "category": "utilities", "description": "Electric bill"},
            {"date": "2024-03-20", "amount": 95.00, "category": "dining", "description": "Restaurant dinner"},
            {"date": "2024-03-22", "amount": 130.00, "category": "transportation", "description": "Gas + maintenance"},
            {"date": "2024-03-25", "amount": 150.00, "category": "shopping", "description": "Clothing"},
            {"date": "2024-03-28", "amount": 300.00, "category": "entertainment", "description": "Weekend trip"},
        ]
        return sample_transactions
    
    def load_data(self, csv_file: str = None) -> None:
        """Load transaction data from CSV file or generate sample data."""
        try:
            if csv_file and os.path.exists(csv_file):
                with open(csv_file, 'r') as file:
                    reader = csv.DictReader(file)
                    self.transactions = list(reader)
                    # Convert amount to float
                    for transaction in self.transactions:
                        transaction['amount'] = float(transaction['amount'])
                print(f"Loaded {len(self.transactions)} transactions from {csv_file}")
            else:
                self.transactions = self.generate_sample_data()
                print(f"Using sample data with {len(self.transactions)} transactions")
                
        except Exception as e:
            print(f"Error loading data: {e}")
            print("Falling back to sample data...")
            self.transactions = self.generate_sample_data()
    
    def analyze_spending_patterns(self) -> None:
        """Analyze spending patterns by category and month."""
        try:
            for transaction in self.transactions:
                date_str = transaction['date']
                amount = transaction['amount']
                category = transaction['category'].lower()
                
                # Parse date and get month-year
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                
                # Store by category
                self.categories[category].append(amount)
                
                # Store by month and category
                self.monthly_spending[month_key][category] += amount
                
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
    
    def calculate_category_stats(self) -> Dict[str, Dict[str, float]]:
        """Calculate statistics for each spending category."""
        stats = {}
        try:
            for category, amounts in self.categories.items():
                if amounts:
                    stats[category] = {
                        'total': sum(amounts),
                        'average': statistics.mean(amounts),
                        'median': statistics.median(amounts),
                        'max': max(amounts),
                        'min': min(amounts),
                        'count': len(amounts)
                    }
                    if len(amounts) > 1:
                        stats[category]['std_dev'] = statistics.stdev(amounts)
                    else:
                        stats[category]['std_dev'] = 0
        except Exception as e:
            print(f"Error calculating category stats: {e}")
            
        return stats
    
    def identify_overspending(self, stats: Dict[str, Dict[str, float]]) -> List[Tuple[str, Dict[str, Any]]]:
        """Identify categories with potential overspending."""
        overspending_categories = []
        
        try:
            # Calculate total spending
            total_spending = sum(stat['total'] for stat in stats.values())
            
            for category, stat in stats.items():
                percentage_of_total = (stat['total'] / total_spending) * 100
                
                # Identify overspending based on various criteria
                overspending_indicators = []
                
                # High percentage of total spending (except rent/housing)
                if category != 'rent' and percentage_of_total > 20:
                    overspending_indicators.append("High percentage of total spending")
                
                # High variability (high standard deviation relative to mean)
                if stat['std_dev'] > stat['average'] * 0.5:
                    overspending_indicators.append("High spending variability")
                
                # Frequent high-value transactions
                if stat['max'] > stat['average'] * 2:
                    overspending_indicators.append("Occasional high-value transactions")
                
                if overspending_indicators:
                    overspending_categories.append((category, {
                        'indicators': overspending_indicators,
                        'percentage_of_total': percentage_of_total,
                        'monthly_average': stat['total'] / len(self.monthly_spending),
                        'volatility': stat['std_dev'] / stat['average'] if stat['average'] > 0 else 0
                    }))
                    
        except Exception as e:
            print(f"Error identifying overspending: {e}")
            
        return sorted(overspending_categories, key=lambda x: x[1]['percentage_of_total'], reverse=True)
    
    def suggest_budget_allocation(self, stats: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Suggest realistic budget allocations based on historical data and best practices."""
        suggestions = {}
        
        try: