```python
"""
Budget Recommendation System

This module analyzes historical spending patterns to provide intelligent budget recommendations.
It processes spending data, calculates category-based budget limits using statistical analysis,
and generates actionable insights with overspending alerts.

Key Features:
- Historical spending pattern analysis
- Realistic budget limit suggestions based on statistical trends
- Category-wise spending breakdown and recommendations
- Overspending detection and alerts
- Actionable financial insights

Usage:
    python script.py

The script uses sample data but can be easily modified to accept real financial data
from CSV files, APIs, or databases.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any


class BudgetRecommendationSystem:
    """
    A comprehensive budget analysis and recommendation system that processes
    historical spending data to generate actionable financial insights.
    """
    
    def __init__(self):
        self.spending_data = []
        self.categories = set()
        self.monthly_spending = defaultdict(lambda: defaultdict(float))
        self.budget_recommendations = {}
        self.overspending_alerts = []
        
    def load_sample_data(self) -> None:
        """
        Loads sample spending data for demonstration purposes.
        In a real implementation, this would load from CSV, API, or database.
        """
        try:
            # Sample spending data for the last 12 months
            sample_data = [
                {"date": "2024-01-15", "category": "Groceries", "amount": 120.50, "description": "Weekly shopping"},
                {"date": "2024-01-16", "category": "Transportation", "amount": 45.00, "description": "Gas"},
                {"date": "2024-01-20", "category": "Entertainment", "amount": 25.99, "description": "Movie tickets"},
                {"date": "2024-01-25", "category": "Utilities", "amount": 85.30, "description": "Electricity bill"},
                {"date": "2024-02-05", "category": "Groceries", "amount": 135.75, "description": "Weekly shopping"},
                {"date": "2024-02-12", "category": "Transportation", "amount": 50.00, "description": "Gas"},
                {"date": "2024-02-14", "category": "Entertainment", "amount": 65.00, "description": "Dinner date"},
                {"date": "2024-02-28", "category": "Utilities", "amount": 92.15, "description": "Water bill"},
                {"date": "2024-03-10", "category": "Groceries", "amount": 145.20, "description": "Weekly shopping"},
                {"date": "2024-03-15", "category": "Transportation", "amount": 55.25, "description": "Gas"},
                {"date": "2024-03-22", "category": "Entertainment", "amount": 40.50, "description": "Concert tickets"},
                {"date": "2024-03-30", "category": "Shopping", "amount": 89.99, "description": "Clothing"},
                {"date": "2024-04-08", "category": "Groceries", "amount": 128.90, "description": "Weekly shopping"},
                {"date": "2024-04-18", "category": "Transportation", "amount": 48.75, "description": "Gas"},
                {"date": "2024-04-25", "category": "Entertainment", "amount": 35.00, "description": "Streaming services"},
                {"date": "2024-04-29", "category": "Healthcare", "amount": 150.00, "description": "Doctor visit"},
                {"date": "2024-05-05", "category": "Groceries", "amount": 142.30, "description": "Weekly shopping"},
                {"date": "2024-05-12", "category": "Transportation", "amount": 52.50, "description": "Gas"},
                {"date": "2024-05-20", "category": "Entertainment", "amount": 28.75, "description": "Book purchase"},
                {"date": "2024-05-31", "category": "Utilities", "amount": 88.45, "description": "Internet bill"},
                {"date": "2024-06-07", "category": "Groceries", "amount": 156.80, "description": "Weekly shopping"},
                {"date": "2024-06-15", "category": "Transportation", "amount": 47.25, "description": "Gas"},
                {"date": "2024-06-22", "category": "Entertainment", "amount": 75.50, "description": "Weekend activities"},
                {"date": "2024-06-30", "category": "Shopping", "amount": 120.00, "description": "Home supplies"},
                {"date": "2024-07-05", "category": "Groceries", "amount": 138.45, "description": "Weekly shopping"},
                {"date": "2024-07-14", "category": "Transportation", "amount": 60.00, "description": "Gas + parking"},
                {"date": "2024-07-25", "category": "Entertainment", "amount": 45.99, "description": "Game purchase"},
                {"date": "2024-07-31", "category": "Healthcare", "amount": 75.00, "description": "Pharmacy"},
                {"date": "2024-08-03", "category": "Groceries", "amount": 165.20, "description": "Weekly shopping"},
                {"date": "2024-08-11", "category": "Transportation", "amount": 58.30, "description": "Gas"},
                {"date": "2024-08-20", "category": "Entertainment", "amount": 95.00, "description": "Restaurant"},
                {"date": "2024-08-28", "category": "Utilities", "amount": 105.60, "description": "Summer AC bill"},
                {"date": "2024-09-02", "category": "Groceries", "amount": 149.90, "description": "Weekly shopping"},
                {"date": "2024-09-10", "category": "Transportation", "amount": 51.75, "description": "Gas"},
                {"date": "2024-09-18", "category": "Entertainment", "amount": 38.25, "description": "Movies"},
                {"date": "2024-09-30", "category": "Shopping", "amount": 200.00, "description": "Back to school"},
                {"date": "2024-10-05", "category": "Groceries", "amount": 172.35, "description": "Weekly shopping"},
                {"date": "2024-10-12", "category": "Transportation", "amount": 49.50, "description": "Gas"},
                {"date": "2024-10-20", "category": "Entertainment", "amount": 55.75, "description": "Halloween prep"},
                {"date": "2024-10-31", "category": "Healthcare", "amount": 125.00, "description": "Annual checkup"},
                {"date": "2024-11-08", "category": "Groceries", "amount": 189.60, "description": "Holiday shopping"},
                {"date": "2024-11-15", "category": "Transportation", "amount": 65.25, "description": "Gas + maintenance"},
                {"date": "2024-11-25", "category": "Entertainment", "amount": 85.50, "description": "Thanksgiving dinner"},
                {"date": "2024-11-30", "category": "Shopping", "amount": 350.00, "description": "Black Friday"},
                {"date": "2024-12-05", "category": "Groceries", "amount": 198.75, "description": "Holiday groceries"},
                {"date": "2024-12-12", "category": "Transportation", "amount": 72.00, "description": "Holiday travel prep"},
                {"date": "2024-12-20", "category": "Entertainment", "amount": 125.99, "description": "Holiday party"},
                {"date": "2024-12-25", "category": "Shopping", "amount": 500.00, "description": "Christmas gifts"}
            ]
            
            self.spending_data = sample_data
            print("✓ Sample spending data loaded successfully")
            
        except Exception as e:
            print