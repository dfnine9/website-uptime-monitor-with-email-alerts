```python
"""
Transaction Data Visualization and Spending Analysis Tool

This module provides a self-contained data visualization component that generates
charts and spending analysis reports from categorized transaction data. It creates
ASCII-based charts and comprehensive spending reports without requiring external
visualization libraries like matplotlib or plotly.

Features:
- ASCII bar charts for category spending
- Monthly spending trends
- Top merchants analysis  
- Statistical summaries (mean, median, percentiles)
- Spending pattern analysis
- Budget variance reporting

The tool processes transaction data in JSON format and outputs formatted reports
and ASCII visualizations to stdout.
"""

import json
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import statistics
import re


class TransactionAnalyzer:
    """Analyzes and visualizes transaction data with ASCII charts and reports."""
    
    def __init__(self):
        self.transactions = []
        self.categories = defaultdict(float)
        self.monthly_data = defaultdict(float)
        self.merchant_data = defaultdict(float)
        
    def load_sample_data(self) -> List[Dict]:
        """Generate sample transaction data for demonstration."""
        sample_data = [
            {"date": "2024-01-15", "amount": -45.67, "merchant": "Grocery Store A", "category": "Food & Dining", "description": "Weekly groceries"},
            {"date": "2024-01-18", "amount": -1200.00, "merchant": "Property Management", "category": "Housing", "description": "Monthly rent"},
            {"date": "2024-01-20", "amount": -35.00, "merchant": "Gas Station", "category": "Transportation", "description": "Fuel"},
            {"date": "2024-01-22", "amount": -89.99, "merchant": "Restaurant Chain", "category": "Food & Dining", "description": "Dinner out"},
            {"date": "2024-01-25", "amount": -150.00, "merchant": "Electric Company", "category": "Utilities", "description": "Electricity bill"},
            {"date": "2024-02-01", "amount": 3000.00, "merchant": "Employer Inc", "category": "Income", "description": "Salary deposit"},
            {"date": "2024-02-03", "amount": -52.34, "merchant": "Grocery Store B", "category": "Food & Dining", "description": "Weekly groceries"},
            {"date": "2024-02-05", "amount": -1200.00, "merchant": "Property Management", "category": "Housing", "description": "Monthly rent"},
            {"date": "2024-02-08", "amount": -299.99, "merchant": "Electronics Store", "category": "Shopping", "description": "New headphones"},
            {"date": "2024-02-12", "amount": -75.00, "merchant": "Internet Provider", "category": "Utilities", "description": "Internet service"},
            {"date": "2024-02-15", "amount": -42.50, "merchant": "Gas Station", "category": "Transportation", "description": "Fuel"},
            {"date": "2024-02-18", "amount": -125.00, "merchant": "Department Store", "category": "Shopping", "description": "Clothing"},
            {"date": "2024-02-22", "amount": -67.89, "merchant": "Restaurant", "category": "Food & Dining", "description": "Lunch meeting"},
            {"date": "2024-02-28", "amount": -200.00, "merchant": "Auto Service", "category": "Transportation", "description": "Car maintenance"},
            {"date": "2024-03-01", "amount": 3000.00, "merchant": "Employer Inc", "category": "Income", "description": "Salary deposit"},
            {"date": "2024-03-05", "amount": -58.76, "merchant": "Grocery Store A", "category": "Food & Dining", "description": "Weekly groceries"},
            {"date": "2024-03-08", "amount": -1200.00, "merchant": "Property Management", "category": "Housing", "description": "Monthly rent"},
            {"date": "2024-03-12", "amount": -89.99, "merchant": "Streaming Service", "category": "Entertainment", "description": "Annual subscription"},
            {"date": "2024-03-15", "amount": -180.00, "merchant": "Utility Company", "category": "Utilities", "description": "Gas & electric"},
            {"date": "2024-03-20", "amount": -450.00, "merchant": "Medical Center", "category": "Healthcare", "description": "Doctor visit"}
        ]
        return sample_data
    
    def load_transactions(self, data: List[Dict] = None):
        """Load transaction data from provided list or generate sample data."""
        try:
            if data is None:
                self.transactions = self.load_sample_data()
                print("📊 Using sample transaction data for analysis\n")
            else:
                self.transactions = data
                
            self._process_transactions()
            
        except Exception as e:
            print(f"❌ Error loading transaction data: {e}")
            sys.exit(1)
    
    def _process_transactions(self):
        """Process transactions into analyzable categories."""
        try:
            for transaction in self.transactions:
                amount = float(transaction['amount'])
                category = transaction.get('category', 'Uncategorized')
                merchant = transaction.get('merchant', 'Unknown')
                date_str = transaction['date']
                
                # Parse date for monthly grouping
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    month_key = date_obj.strftime('%Y-%m')
                except ValueError:
                    month_key = 'Unknown'
                
                # Categorize spending (negative amounts are expenses)
                if amount < 0:
                    self.categories[category] += abs(amount)
                    self.merchant_data[merchant] += abs(amount)
                    self.monthly_data[month_key] += abs(amount)
                else:
                    # Income
                    self.categories[category] += amount
                    
        except Exception as e:
            print(f"❌ Error processing transactions: {e}")
            raise
    
    def create_ascii_bar_chart(self, data: Dict[str, float], title: str, 
                              max_width: int = 50, show_values: bool = True) -> str:
        """Create an ASCII bar chart from data dictionary."""
        try:
            if not data:
                return f"\n{title}\n{'='*len(title)}\nNo data available\n"
            
            # Sort data by value (descending)
            sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
            max_value = max(data.values()) if data.values() else 1
            
            chart = f"\n{title}\n{'='*len(title)}\n"
            
            for label, value in sorted_data[:10]:  # Show top 10
                # Calculate bar length
                if max_value > 0:
                    bar_length = int((value / max_value) * max_width)
                else:
                    bar_length = 0
                
                # Create bar
                bar = '█' * bar_length
                
                # Format label and value
                if show_values:
                    value_str = f"${value:,.2f}" if value >= 0 else f"-${abs(value):,.2f}"
                    chart += f"{label:<25} |{bar:<{max_width}} {value_str:>10}\n"
                else:
                    chart += f"{label:<25} |{bar}\n"
            
            return chart + "\n"
            
        except Exception as e:
            return f"\n{title}\n{'='*len(title)}\nError creating chart: {e}\n"
    
    def generate_spending_summary(self) -> str:
        """Generate comprehensive spending analysis summary."""
        try:
            # Filter out income for expense analysis
            expenses = {k: v for k, v in self.categories.items() if k != 'Income'}
            income =