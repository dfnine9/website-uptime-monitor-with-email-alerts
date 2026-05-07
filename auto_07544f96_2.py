```python
#!/usr/bin/env python3
"""
Personal Finance Data Analysis Module

This module provides comprehensive spending insights by analyzing financial data 
stored in an SQLite database. It generates monthly spending reports, calculates 
category breakdowns with percentages, and identifies spending trends over time.

Features:
- Monthly spending summaries
- Category-wise spending analysis with percentages
- Trend analysis showing spending patterns over time
- Top spending categories identification
- Month-over-month spending comparison

Database Schema Expected:
- Table: transactions
- Columns: date (TEXT/DATE), amount (REAL), category (TEXT), description (TEXT)
"""

import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict
import calendar


class SpendingAnalyzer:
    """Analyzes spending patterns from SQLite database."""
    
    def __init__(self, db_path="finance.db"):
        """Initialize with database path."""
        self.db_path = db_path
        self.connection = None
    
    def connect_db(self):
        """Establish database connection with error handling."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def close_db(self):
        """Close database connection safely."""
        if self.connection:
            self.connection.close()
    
    def create_sample_data(self):
        """Create sample data if database is empty."""
        try:
            cursor = self.connection.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT
                )
            ''')
            
            # Check if data exists
            cursor.execute("SELECT COUNT(*) FROM transactions")
            if cursor.fetchone()[0] > 0:
                return
            
            # Sample data for demonstration
            sample_transactions = [
                ('2024-01-15', 150.00, 'Groceries', 'Weekly grocery shopping'),
                ('2024-01-20', 80.00, 'Utilities', 'Electricity bill'),
                ('2024-01-25', 45.00, 'Entertainment', 'Movie tickets'),
                ('2024-02-10', 200.00, 'Groceries', 'Monthly grocery shopping'),
                ('2024-02-15', 85.00, 'Utilities', 'Gas bill'),
                ('2024-02-28', 60.00, 'Entertainment', 'Concert tickets'),
                ('2024-03-05', 175.00, 'Groceries', 'Grocery shopping'),
                ('2024-03-12', 90.00, 'Utilities', 'Water bill'),
                ('2024-03-20', 30.00, 'Entertainment', 'Streaming services'),
                ('2024-04-08', 220.00, 'Groceries', 'Monthly grocery shopping'),
                ('2024-04-15', 95.00, 'Utilities', 'Internet bill'),
                ('2024-04-22', 75.00, 'Entertainment', 'Restaurant dinner'),
            ]
            
            cursor.executemany(
                "INSERT INTO transactions (date, amount, category, description) VALUES (?, ?, ?, ?)",
                sample_transactions
            )
            self.connection.commit()
            print("Sample data created for demonstration.")
            
        except sqlite3.Error as e:
            print(f"Error creating sample data: {e}")
    
    def get_monthly_spending(self):
        """Get spending totals by month."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT 
                    strftime('%Y-%m', date) as month,
                    SUM(amount) as total_spending,
                    COUNT(*) as transaction_count
                FROM transactions
                GROUP BY strftime('%Y-%m', date)
                ORDER BY month
            ''')
            
            monthly_data = {}
            for row in cursor.fetchall():
                month = row['month']
                monthly_data[month] = {
                    'total': round(row['total_spending'], 2),
                    'count': row['transaction_count']
                }
            
            return monthly_data
            
        except sqlite3.Error as e:
            print(f"Error getting monthly spending: {e}")
            return {}
    
    def get_category_analysis(self, month=None):
        """Get spending analysis by category."""
        try:
            cursor = self.connection.cursor()
            
            if month:
                query = '''
                    SELECT 
                        category,
                        SUM(amount) as total_spending,
                        COUNT(*) as transaction_count,
                        AVG(amount) as avg_spending
                    FROM transactions
                    WHERE strftime('%Y-%m', date) = ?
                    GROUP BY category
                    ORDER BY total_spending DESC
                '''
                cursor.execute(query, (month,))
            else:
                query = '''
                    SELECT 
                        category,
                        SUM(amount) as total_spending,
                        COUNT(*) as transaction_count,
                        AVG(amount) as avg_spending
                    FROM transactions
                    GROUP BY category
                    ORDER BY total_spending DESC
                '''
                cursor.execute(query)
            
            categories = []
            total_all = 0
            
            for row in cursor.fetchall():
                total_all += row['total_spending']
                categories.append({
                    'category': row['category'],
                    'total': round(row['total_spending'], 2),
                    'count': row['transaction_count'],
                    'average': round(row['avg_spending'], 2)
                })
            
            # Calculate percentages
            for category in categories:
                if total_all > 0:
                    category['percentage'] = round((category['total'] / total_all) * 100, 1)
                else:
                    category['percentage'] = 0
            
            return categories, round(total_all, 2)
            
        except sqlite3.Error as e:
            print(f"Error getting category analysis: {e}")
            return [], 0
    
    def get_spending_trends(self):
        """Analyze spending trends over time."""
        try:
            monthly_data = self.get_monthly_spending()
            
            if len(monthly_data) < 2:
                return {"message": "Not enough data for trend analysis"}
            
            months = sorted(monthly_data.keys())
            trends = {}
            
            # Calculate month-over-month changes
            for i in range(1, len(months)):
                current_month = months[i]
                previous_month = months[i-1]
                
                current_total = monthly_data[current_month]['total']
                previous_total = monthly_data[previous_month]['total']
                
                if previous_total > 0:
                    change_percent = ((current_total - previous_total) / previous_total) * 100
                    trends[current_month] = {
                        'previous_month': previous_month,
                        'current_spending': current_total,
                        'previous_spending': previous_total,
                        'change_amount': round(current_total - previous_total, 2),
                        'change_percent': round(change_percent, 1)
                    }
            
            # Calculate overall trend
            if len(months) >= 3:
                first_month_total = monthly_data[months[0]]['total']
                last_month_total = monthly_data[months[-1]]['total']
                overall_change = ((last_month_total - first_month_total) / first_month_total) * 100
                
                trends['overall'] = {
                    'first_month': months[0],
                    'last_month': months[-1],
                    'overall_change_percent': round(overall_change, 1),
                    'trend_direction': 'increasing' if overall_change > 0 else 'decre