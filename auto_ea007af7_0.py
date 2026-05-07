```python
#!/usr/bin/env python3
"""
Expense Analysis and Categorization Script

This module reads CSV expense data, categorizes expenses using pandas-like operations,
and generates summary statistics with basic text-based charts. The script provides
comprehensive expense analysis including category breakdowns, monthly trends,
and statistical summaries.

Features:
- Reads CSV files with expense data (amount, description, date columns)
- Implements intelligent expense categorization based on keywords
- Generates summary statistics and reports
- Creates text-based charts for visualization
- Handles missing data and validation errors

Usage:
    python script.py

The script expects a CSV file named 'expenses.csv' in the same directory with columns:
- date (YYYY-MM-DD format)
- description (expense description)
- amount (numeric value)

If no CSV file exists, sample data will be generated for demonstration.
"""

import csv
import re
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random


class ExpenseAnalyzer:
    """Main class for expense analysis and categorization."""
    
    def __init__(self):
        self.expenses = []
        self.categories = {
            'Food': ['restaurant', 'grocery', 'food', 'coffee', 'lunch', 'dinner', 'breakfast', 'pizza', 'burger', 'cafe'],
            'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train', 'parking', 'metro', 'subway'],
            'Entertainment': ['movie', 'cinema', 'netflix', 'spotify', 'game', 'concert', 'theater', 'bar', 'club'],
            'Shopping': ['amazon', 'walmart', 'target', 'store', 'mall', 'clothing', 'shoes', 'electronics'],
            'Utilities': ['electric', 'water', 'internet', 'phone', 'cable', 'heating', 'cooling', 'utility'],
            'Healthcare': ['doctor', 'pharmacy', 'hospital', 'medical', 'dentist', 'medicine', 'health'],
            'Other': []
        }
    
    def categorize_expense(self, description: str) -> str:
        """Categorize expense based on description keywords."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            if category == 'Other':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'
    
    def read_csv_file(self, filename: str = 'expenses.csv') -> bool:
        """Read expense data from CSV file."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                required_columns = {'date', 'description', 'amount'}
                if not required_columns.issubset(set(reader.fieldnames or [])):
                    print(f"Error: CSV file must contain columns: {required_columns}")
                    return False
                
                for row in reader:
                    try:
                        # Validate and parse data
                        date_str = row['date'].strip()
                        description = row['description'].strip()
                        amount = float(row['amount'])
                        
                        # Validate date format
                        expense_date = datetime.strptime(date_str, '%Y-%m-%d')
                        
                        # Categorize expense
                        category = self.categorize_expense(description)
                        
                        self.expenses.append({
                            'date': expense_date,
                            'description': description,
                            'amount': amount,
                            'category': category
                        })
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping invalid row - {e}")
                        continue
                
                print(f"Successfully loaded {len(self.expenses)} expenses from {filename}")
                return True
                
        except FileNotFoundError:
            print(f"File {filename} not found. Generating sample data...")
            self.generate_sample_data()
            return True
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
    
    def generate_sample_data(self):
        """Generate sample expense data for demonstration."""
        sample_descriptions = [
            'Grocery shopping at Walmart', 'Gas station fuel', 'Netflix subscription',
            'Coffee at Starbucks', 'Uber ride downtown', 'Amazon purchase',
            'Electric bill payment', 'Doctor visit', 'Movie tickets',
            'Restaurant dinner', 'Pharmacy prescription', 'Parking fee',
            'Internet bill', 'Grocery store', 'Fast food lunch'
        ]
        
        base_date = datetime.now() - timedelta(days=90)
        
        for i in range(50):
            date = base_date + timedelta(days=random.randint(0, 89))
            description = random.choice(sample_descriptions)
            amount = round(random.uniform(5.0, 200.0), 2)
            category = self.categorize_expense(description)
            
            self.expenses.append({
                'date': date,
                'description': description,
                'amount': amount,
                'category': category
            })
        
        print("Generated 50 sample expenses for demonstration")
    
    def generate_summary_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive summary statistics."""
        if not self.expenses:
            return {}
        
        amounts = [exp['amount'] for exp in self.expenses]
        categories = [exp['category'] for exp in self.expenses]
        
        # Basic statistics
        total_expenses = sum(amounts)
        average_expense = total_expenses / len(amounts)
        max_expense = max(amounts)
        min_expense = min(amounts)
        
        # Category breakdown
        category_totals = defaultdict(float)
        category_counts = Counter()
        
        for expense in self.expenses:
            category_totals[expense['category']] += expense['amount']
            category_counts[expense['category']] += 1
        
        # Monthly breakdown
        monthly_totals = defaultdict(float)
        for expense in self.expenses:
            month_key = expense['date'].strftime('%Y-%m')
            monthly_totals[month_key] += expense['amount']
        
        return {
            'total_expenses': total_expenses,
            'average_expense': average_expense,
            'max_expense': max_expense,
            'min_expense': min_expense,
            'expense_count': len(self.expenses),
            'category_totals': dict(category_totals),
            'category_counts': dict(category_counts),
            'monthly_totals': dict(monthly_totals)
        }
    
    def create_text_chart(self, data: Dict[str, float], title: str, max_width: int = 50) -> str:
        """Create a simple text-based horizontal bar chart."""
        if not data:
            return f"{title}\nNo data available\n"
        
        max_value = max(data.values())
        chart_lines = [f"\n{title}", "=" * len(title)]
        
        for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
            bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
            bar = "█" * bar_length
            chart_lines.append(f"{label:<15} |{bar:<{max_width}} ${value:,.2f}")
        
        return "\n".join(chart_lines) + "\n"
    
    def generate_monthly_trend_chart(self, monthly_data: Dict[str, float]) -> str:
        """Generate a text-based monthly trend chart."""
        if not monthly_data:
            return "Monthly Trend\nNo data available\n"
        
        sorted_months = sorted(monthly_data.keys())
        chart_lines = ["\nMonthly Spending Trend", "=" * 20]
        
        for month in sorted_months: