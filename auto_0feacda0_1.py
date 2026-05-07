```python
"""
Transaction Pattern Analyzer

This module analyzes categorized transaction data to identify spending patterns,
calculate monthly totals per category, and detect anomalies or trends over time.

Features:
- Loads transaction data from CSV or generates sample data
- Calculates monthly spending totals by category
- Identifies spending patterns and trends
- Detects anomalies using statistical analysis
- Provides summary statistics and insights

Usage:
    python script.py

The script will either load data from 'transactions.csv' if it exists,
or generate sample transaction data for demonstration purposes.
"""

import csv
import json
import statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
import random


class TransactionAnalyzer:
    """Analyzes transaction data for patterns, trends, and anomalies."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.category_stats = defaultdict(list)
        
    def load_data(self, filename='transactions.csv'):
        """Load transaction data from CSV file."""
        try:
            if Path(filename).exists():
                with open(filename, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    self.transactions = list(reader)
                    # Convert amount to float and parse date
                    for tx in self.transactions:
                        tx['amount'] = float(tx['amount'])
                        tx['date'] = datetime.strptime(tx['date'], '%Y-%m-%d')
                print(f"Loaded {len(self.transactions)} transactions from {filename}")
            else:
                print(f"{filename} not found. Generating sample data...")
                self._generate_sample_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            print("Generating sample data instead...")
            self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate sample transaction data for demonstration."""
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                     'Healthcare', 'Shopping', 'Education', 'Bills']
        
        # Generate transactions for the last 12 months
        start_date = datetime.now() - timedelta(days=365)
        
        for _ in range(500):  # Generate 500 sample transactions
            category = random.choice(categories)
            
            # Create realistic spending patterns
            base_amounts = {
                'Food': (20, 100),
                'Transportation': (10, 200),
                'Entertainment': (15, 150),
                'Utilities': (50, 300),
                'Healthcare': (25, 500),
                'Shopping': (30, 400),
                'Education': (100, 1000),
                'Bills': (200, 800)
            }
            
            min_amt, max_amt = base_amounts[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            # Add some seasonal variations and anomalies
            date = start_date + timedelta(days=random.randint(0, 365))
            if random.random() < 0.05:  # 5% chance of anomaly
                amount *= random.uniform(2, 5)  # 2-5x normal amount
                
            self.transactions.append({
                'date': date,
                'category': category,
                'amount': amount,
                'description': f"Sample {category} transaction"
            })
        
        print(f"Generated {len(self.transactions)} sample transactions")
    
    def calculate_monthly_totals(self):
        """Calculate monthly spending totals by category."""
        try:
            for tx in self.transactions:
                month_key = tx['date'].strftime('%Y-%m')
                category = tx['category']
                amount = tx['amount']
                
                self.monthly_totals[month_key][category] += amount
                self.category_stats[category].append(amount)
            
            print("\n=== MONTHLY SPENDING TOTALS BY CATEGORY ===")
            for month in sorted(self.monthly_totals.keys()):
                print(f"\n{month}:")
                total_month = sum(self.monthly_totals[month].values())
                for category, amount in sorted(self.monthly_totals[month].items()):
                    percentage = (amount / total_month * 100) if total_month > 0 else 0
                    print(f"  {category:15} ${amount:8.2f} ({percentage:5.1f}%)")
                print(f"  {'TOTAL':15} ${total_month:8.2f}")
                
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
    
    def analyze_spending_patterns(self):
        """Analyze overall spending patterns and trends."""
        try:
            print("\n=== SPENDING PATTERN ANALYSIS ===")
            
            # Category averages and totals
            category_totals = defaultdict(float)
            for tx in self.transactions:
                category_totals[tx['category']] += tx['amount']
            
            total_spending = sum(category_totals.values())
            
            print(f"\nTotal Spending: ${total_spending:,.2f}")
            print(f"Number of Transactions: {len(self.transactions)}")
            print(f"Average Transaction: ${total_spending/len(self.transactions):,.2f}")
            
            print("\nSpending by Category:")
            for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                percentage = (total / total_spending * 100) if total_spending > 0 else 0
                avg_transaction = total / len([tx for tx in self.transactions if tx['category'] == category])
                print(f"  {category:15} ${total:8.2f} ({percentage:5.1f}%) - Avg: ${avg_transaction:.2f}")
            
            # Monthly trends
            monthly_spending = defaultdict(float)
            for month, categories in self.monthly_totals.items():
                monthly_spending[month] = sum(categories.values())
            
            if len(monthly_spending) > 1:
                print(f"\nMonthly Spending Trend:")
                sorted_months = sorted(monthly_spending.keys())
                for i, month in enumerate(sorted_months):
                    amount = monthly_spending[month]
                    trend = ""
                    if i > 0:
                        prev_amount = monthly_spending[sorted_months[i-1]]
                        change = ((amount - prev_amount) / prev_amount * 100) if prev_amount > 0 else 0
                        trend = f" ({change:+5.1f}%)"
                    print(f"  {month}: ${amount:8.2f}{trend}")
                    
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
    
    def detect_anomalies(self):
        """Detect spending anomalies using statistical analysis."""
        try:
            print("\n=== ANOMALY DETECTION ===")
            
            for category, amounts in self.category_stats.items():
                if len(amounts) < 3:  # Need at least 3 data points
                    continue
                    
                mean_amount = statistics.mean(amounts)
                std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
                
                if std_dev == 0:
                    continue
                
                # Find outliers (more than 2 standard deviations from mean)
                threshold = 2 * std_dev
                anomalies = []
                
                for tx in self.transactions:
                    if tx['category'] == category:
                        z_score = abs(tx['amount'] - mean_amount) / std_dev if std_dev > 0 else 0
                        if z_score > 2:  # More than 2 standard deviations
                            anomalies.append({
                                'date': tx['date'],
                                'amount': tx['amount'],
                                'z_score': z_score,