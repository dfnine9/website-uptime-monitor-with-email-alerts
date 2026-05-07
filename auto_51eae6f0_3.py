```python
#!/usr/bin/env python3
"""
Automated Monthly Spending Trend Reporting System

This module generates comprehensive monthly spending reports with visualizations,
category breakdowns, and year-over-year comparisons. It creates both PDF and Excel
exports with interactive charts and detailed analytics.

The system processes transaction data to identify spending patterns, categorize
expenses, and generate actionable insights for financial planning.

Dependencies: httpx, anthropic (for enhanced data processing)
Standard library: json, datetime, csv, sqlite3, base64, io
"""

import json
import datetime
import csv
import sqlite3
import base64
import io
import os
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import httpx
import anthropic

@dataclass
class Transaction:
    date: datetime.date
    amount: float
    category: str
    description: str
    merchant: str

class SpendingReportGenerator:
    def __init__(self, db_path: str = "spending.db"):
        """Initialize the reporting system with database connection."""
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Create database tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    merchant TEXT
                )
            ''')
            
            # Insert sample data if table is empty
            cursor.execute("SELECT COUNT(*) FROM transactions")
            if cursor.fetchone()[0] == 0:
                self.insert_sample_data(cursor)
            
            conn.commit()
            conn.close()
            print("✓ Database initialized successfully")
            
        except sqlite3.Error as e:
            print(f"✗ Database setup error: {e}")
            sys.exit(1)
    
    def insert_sample_data(self, cursor):
        """Insert sample transaction data for demonstration."""
        sample_data = [
            ('2024-01-15', 1200.50, 'Groceries', 'Weekly shopping', 'SuperMart'),
            ('2024-01-20', 450.00, 'Utilities', 'Electric bill', 'PowerCorp'),
            ('2024-01-25', 80.25, 'Dining', 'Restaurant dinner', 'Bistro Central'),
            ('2024-02-05', 1150.75, 'Groceries', 'Monthly shopping', 'SuperMart'),
            ('2024-02-10', 320.00, 'Transportation', 'Gas station', 'Shell'),
            ('2024-02-18', 125.50, 'Entertainment', 'Movie tickets', 'Cineplex'),
            ('2024-03-03', 1300.25, 'Groceries', 'Weekly shopping', 'SuperMart'),
            ('2024-03-12', 85.00, 'Dining', 'Lunch meeting', 'Cafe Express'),
            ('2024-03-20', 200.00, 'Healthcare', 'Doctor visit', 'MedCenter'),
            # Previous year data for YoY comparison
            ('2023-01-15', 1100.00, 'Groceries', 'Weekly shopping', 'SuperMart'),
            ('2023-02-15', 1050.50, 'Groceries', 'Weekly shopping', 'SuperMart'),
            ('2023-03-15', 1200.75, 'Groceries', 'Weekly shopping', 'SuperMart'),
        ]
        
        cursor.executemany('''
            INSERT INTO transactions (date, amount, category, description, merchant)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_data)
    
    def fetch_transactions(self, start_date: str, end_date: str) -> List[Transaction]:
        """Fetch transactions within date range."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, amount, category, description, merchant
                FROM transactions
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            ''', (start_date, end_date))
            
            transactions = []
            for row in cursor.fetchall():
                date_obj = datetime.datetime.strptime(row[0], '%Y-%m-%d').date()
                transactions.append(Transaction(
                    date=date_obj,
                    amount=row[1],
                    category=row[2],
                    description=row[3],
                    merchant=row[4]
                ))
            
            conn.close()
            return transactions
            
        except sqlite3.Error as e:
            print(f"✗ Error fetching transactions: {e}")
            return []
    
    def calculate_category_breakdown(self, transactions: List[Transaction]) -> Dict[str, float]:
        """Calculate spending by category."""
        breakdown = defaultdict(float)
        for transaction in transactions:
            breakdown[transaction.category] += transaction.amount
        return dict(breakdown)
    
    def calculate_monthly_trends(self, transactions: List[Transaction]) -> Dict[str, float]:
        """Calculate monthly spending totals."""
        monthly_totals = defaultdict(float)
        for transaction in transactions:
            month_key = transaction.date.strftime('%Y-%m')
            monthly_totals[month_key] += transaction.amount
        return dict(monthly_totals)
    
    def calculate_yoy_comparison(self, current_year: int, previous_year: int) -> Dict[str, Dict[str, float]]:
        """Calculate year-over-year spending comparison."""
        try:
            current_start = f"{current_year}-01-01"
            current_end = f"{current_year}-12-31"
            previous_start = f"{previous_year}-01-01"
            previous_end = f"{previous_year}-12-31"
            
            current_transactions = self.fetch_transactions(current_start, current_end)
            previous_transactions = self.fetch_transactions(previous_start, previous_end)
            
            current_breakdown = self.calculate_category_breakdown(current_transactions)
            previous_breakdown = self.calculate_category_breakdown(previous_transactions)
            
            comparison = {}
            all_categories = set(current_breakdown.keys()) | set(previous_breakdown.keys())
            
            for category in all_categories:
                current_amount = current_breakdown.get(category, 0)
                previous_amount = previous_breakdown.get(category, 0)
                
                if previous_amount > 0:
                    change_percent = ((current_amount - previous_amount) / previous_amount) * 100
                else:
                    change_percent = 100 if current_amount > 0 else 0
                
                comparison[category] = {
                    'current': current_amount,
                    'previous': previous_amount,
                    'change_percent': change_percent
                }
            
            return comparison
            
        except Exception as e:
            print(f"✗ Error calculating YoY comparison: {e}")
            return {}
    
    def generate_ascii_chart(self, data: Dict[str, float], title: str, width: int = 50) -> str:
        """Generate ASCII bar chart for console output."""
        if not data:
            return f"{title}\nNo data available\n"
        
        max_value = max(data.values())
        chart_lines = [f"\n{title}", "=" * len(title)]
        
        for category, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
            bar_length = int((value / max_value) * width)
            bar = "█" * bar_length
            chart_lines.append(f"{category:15} │{bar:<{width}} ${value:,.2f}")
        
        return "\n".join(chart_lines) + "\n"
    
    def export_to_csv(self, data: Dict