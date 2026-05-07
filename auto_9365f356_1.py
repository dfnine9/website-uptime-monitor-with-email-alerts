```python
#!/usr/bin/env python3
"""
Monthly Spending Report Generator

This module analyzes categorized transaction data to generate comprehensive
monthly spending reports with summary statistics and visual charts.

Features:
- Processes transaction data from CSV or JSON formats
- Calculates totals per spending category
- Generates summary statistics (mean, median, std deviation)
- Creates visual charts using matplotlib
- Exports reports in multiple formats

Usage:
    python script.py

Dependencies:
    - Standard library modules (csv, json, datetime, statistics)
    - matplotlib for visualization
    - No external API dependencies
"""

import csv
import json
import datetime
import statistics
import sys
import os
from collections import defaultdict
from typing import Dict, List, Tuple, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Charts will be skipped.")


class TransactionAnalyzer:
    """Analyzes transaction data and generates spending reports."""
    
    def __init__(self):
        self.transactions = []
        self.categories = defaultdict(list)
        self.monthly_data = defaultdict(lambda: defaultdict(float))
    
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        sample_transactions = [
            {"date": "2024-01-15", "amount": 45.50, "category": "Groceries", "description": "Supermarket"},
            {"date": "2024-01-16", "amount": 12.99, "category": "Transportation", "description": "Bus fare"},
            {"date": "2024-01-18", "amount": 89.99, "category": "Utilities", "description": "Electric bill"},
            {"date": "2024-01-20", "amount": 156.78, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-01-22", "amount": 25.00, "category": "Entertainment", "description": "Movie tickets"},
            {"date": "2024-01-25", "amount": 67.45, "category": "Dining", "description": "Restaurant"},
            {"date": "2024-02-02", "amount": 123.45, "category": "Groceries", "description": "Monthly shopping"},
            {"date": "2024-02-05", "amount": 34.50, "category": "Transportation", "description": "Gas"},
            {"date": "2024-02-08", "amount": 78.90, "category": "Utilities", "description": "Water bill"},
            {"date": "2024-02-12", "amount": 45.00, "category": "Entertainment", "description": "Concert"},
            {"date": "2024-02-15", "amount": 234.67, "category": "Groceries", "description": "Bulk shopping"},
            {"date": "2024-02-18", "amount": 56.78, "category": "Dining", "description": "Takeout"},
            {"date": "2024-03-01", "amount": 98.76, "category": "Utilities", "description": "Internet"},
            {"date": "2024-03-05", "amount": 167.89, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-03-08", "amount": 23.45, "category": "Transportation", "description": "Parking"},
            {"date": "2024-03-12", "amount": 89.99, "category": "Entertainment", "description": "Streaming services"},
            {"date": "2024-03-15", "amount": 145.67, "category": "Dining", "description": "Date night"},
            {"date": "2024-03-20", "amount": 67.89, "category": "Groceries", "description": "Fresh produce"},
        ]
        self.transactions = sample_transactions
        print(f"Loaded {len(self.transactions)} sample transactions")
    
    def load_from_csv(self, filename: str) -> None:
        """Load transaction data from CSV file."""
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self.transactions = []
                for row in reader:
                    transaction = {
                        'date': row['date'],
                        'amount': float(row['amount']),
                        'category': row['category'],
                        'description': row.get('description', '')
                    }
                    self.transactions.append(transaction)
            print(f"Loaded {len(self.transactions)} transactions from {filename}")
        except FileNotFoundError:
            print(f"CSV file {filename} not found. Using sample data instead.")
            self.load_sample_data()
        except Exception as e:
            print(f"Error loading CSV: {e}. Using sample data instead.")
            self.load_sample_data()
    
    def load_from_json(self, filename: str) -> None:
        """Load transaction data from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
                self.transactions = data.get('transactions', [])
            print(f"Loaded {len(self.transactions)} transactions from {filename}")
        except FileNotFoundError:
            print(f"JSON file {filename} not found. Using sample data instead.")
            self.load_sample_data()
        except Exception as e:
            print(f"Error loading JSON: {e}. Using sample data instead.")
            self.load_sample_data()
    
    def process_transactions(self) -> None:
        """Process transactions and organize by category and month."""
        try:
            for transaction in self.transactions:
                date_str = transaction['date']
                amount = transaction['amount']
                category = transaction['category']
                
                # Parse date
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                month_key = date_obj.strftime('%Y-%m')
                
                # Organize data
                self.categories[category].append(amount)
                self.monthly_data[month_key][category] += amount
            
            print("Transaction processing completed")
        except Exception as e:
            print(f"Error processing transactions: {e}")
            sys.exit(1)
    
    def calculate_category_statistics(self) -> Dict[str, Dict[str, float]]:
        """Calculate statistics for each spending category."""
        stats = {}
        
        try:
            for category, amounts in self.categories.items():
                category_stats = {
                    'total': sum(amounts),
                    'count': len(amounts),
                    'average': statistics.mean(amounts),
                    'median': statistics.median(amounts),
                    'min': min(amounts),
                    'max': max(amounts)
                }
                
                if len(amounts) > 1:
                    category_stats['std_dev'] = statistics.stdev(amounts)
                else:
                    category_stats['std_dev'] = 0.0
                
                stats[category] = category_stats
            
            return stats
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {}
    
    def generate_monthly_summary(self) -> Dict[str, Dict[str, float]]:
        """Generate monthly spending summaries."""
        monthly_summary = {}
        
        try:
            for month, categories in self.monthly_data.items():
                monthly_total = sum(categories.values())
                monthly_summary[month] = {
                    'total_spent': monthly_total,
                    'categories': dict(categories),
                    'num_categories': len(categories)
                }
            
            return monthly_summary
        except Exception as e:
            print(f"Error generating monthly summary: {e}")
            return {}
    
    def create_charts(self) -> None:
        """Create visual charts for spending analysis."""
        if not MATPLOTLIB_AVAILABLE:
            print("Skipping chart generation - matplotlib not available")
            return
        
        try:
            # Create figure with subplots