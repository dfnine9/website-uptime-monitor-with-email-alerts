```python
"""
Transaction Spending Insights Analyzer

This module analyzes categorized financial transactions to generate comprehensive spending insights.
It processes transaction data to calculate monthly totals per category, identify spending trends,
create percentage breakdowns, and highlight the highest expense categories.

Features:
- Monthly spending totals by category
- Spending trend analysis over time
- Percentage breakdown of expenses
- Top spending category identification
- Error handling for data validation
- Self-contained with minimal dependencies

Usage:
    python script.py

The module generates sample transaction data for demonstration purposes and outputs
detailed spending analysis to stdout.
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import calendar


class TransactionAnalyzer:
    """Analyzes financial transactions to generate spending insights."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(Decimal))
        self.category_totals = defaultdict(Decimal)
        
    def add_transaction(self, date, category, amount, description=""):
        """Add a transaction to the analyzer."""
        try:
            if isinstance(amount, (int, float, str)):
                amount = Decimal(str(amount))
            
            transaction = {
                'date': datetime.strptime(date, '%Y-%m-%d') if isinstance(date, str) else date,
                'category': str(category).strip().title(),
                'amount': abs(amount),  # Ensure positive for expenses
                'description': str(description)
            }
            self.transactions.append(transaction)
            return True
            
        except (ValueError, InvalidOperation) as e:
            print(f"Error adding transaction: {e}", file=sys.stderr)
            return False
    
    def process_transactions(self):
        """Process all transactions to calculate monthly and category totals."""
        try:
            self.monthly_totals.clear()
            self.category_totals.clear()
            
            for transaction in self.transactions:
                date = transaction['date']
                category = transaction['category']
                amount = transaction['amount']
                
                # Create month-year key
                month_key = f"{date.year}-{date.month:02d}"
                
                # Update monthly totals by category
                self.monthly_totals[month_key][category] += amount
                
                # Update category totals
                self.category_totals[category] += amount
                
        except Exception as e:
            print(f"Error processing transactions: {e}", file=sys.stderr)
            raise
    
    def get_monthly_totals(self):
        """Return monthly totals by category."""
        return dict(self.monthly_totals)
    
    def get_category_breakdown(self):
        """Return percentage breakdown by category."""
        try:
            total_spending = sum(self.category_totals.values())
            if total_spending == 0:
                return {}
            
            breakdown = {}
            for category, amount in self.category_totals.items():
                percentage = (amount / total_spending) * 100
                breakdown[category] = {
                    'amount': float(amount),
                    'percentage': round(float(percentage), 2)
                }
            
            return breakdown
            
        except Exception as e:
            print(f"Error calculating category breakdown: {e}", file=sys.stderr)
            return {}
    
    def get_top_categories(self, limit=5):
        """Return top spending categories."""
        try:
            sorted_categories = sorted(
                self.category_totals.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_categories[:limit]
            
        except Exception as e:
            print(f"Error getting top categories: {e}", file=sys.stderr)
            return []
    
    def analyze_trends(self):
        """Analyze spending trends over time."""
        try:
            if not self.monthly_totals:
                return {}
            
            trends = {}
            sorted_months = sorted(self.monthly_totals.keys())
            
            if len(sorted_months) < 2:
                return {"message": "Need at least 2 months of data for trend analysis"}
            
            # Calculate month-over-month changes
            for i in range(1, len(sorted_months)):
                current_month = sorted_months[i]
                previous_month = sorted_months[i-1]
                
                current_total = sum(self.monthly_totals[current_month].values())
                previous_total = sum(self.monthly_totals[previous_month].values())
                
                if previous_total > 0:
                    change = ((current_total - previous_total) / previous_total) * 100
                    trends[current_month] = {
                        'current_total': float(current_total),
                        'previous_total': float(previous_total),
                        'change_percentage': round(float(change), 2)
                    }
            
            return trends
            
        except Exception as e:
            print(f"Error analyzing trends: {e}", file=sys.stderr)
            return {}
    
    def generate_sample_data(self):
        """Generate sample transaction data for demonstration."""
        try:
            # Sample transactions for the last 6 months
            base_date = datetime.now() - timedelta(days=180)
            
            sample_transactions = [
                # Month 1
                (base_date, "Groceries", 450.00, "Weekly grocery shopping"),
                (base_date + timedelta(days=2), "Gas", 65.00, "Shell station"),
                (base_date + timedelta(days=5), "Dining", 85.50, "Restaurant dinner"),
                (base_date + timedelta(days=8), "Utilities", 120.00, "Electric bill"),
                (base_date + timedelta(days=12), "Entertainment", 45.00, "Movie tickets"),
                (base_date + timedelta(days=15), "Groceries", 380.00, "Costco run"),
                (base_date + timedelta(days=18), "Shopping", 200.00, "Clothing"),
                (base_date + timedelta(days=22), "Gas", 70.00, "Chevron"),
                (base_date + timedelta(days=25), "Dining", 92.75, "Lunch meeting"),
                (base_date + timedelta(days=28), "Healthcare", 150.00, "Doctor visit"),
                
                # Month 2
                (base_date + timedelta(days=35), "Groceries", 420.00, "Weekly shopping"),
                (base_date + timedelta(days=38), "Gas", 68.00, "BP station"),
                (base_date + timedelta(days=42), "Utilities", 135.00, "Gas & Electric"),
                (base_date + timedelta(days=45), "Entertainment", 120.00, "Concert tickets"),
                (base_date + timedelta(days=48), "Dining", 78.25, "Pizza night"),
                (base_date + timedelta(days=52), "Shopping", 155.00, "Home supplies"),
                (base_date + timedelta(days=55), "Groceries", 365.00, "Whole Foods"),
                (base_date + timedelta(days=58), "Gas", 72.50, "Shell"),
                (base_date + timedelta(days=62), "Healthcare", 80.00, "Pharmacy"),
                
                # Month 3
                (base_date + timedelta(days=70), "Groceries", 480.00, "Monthly stock up"),
                (base_date + timedelta(days=73), "Dining", 105.00, "Birthday dinner"),
                (base_date + timedelta(days=76), "Gas", 75.00, "Exxon"),
                (base_date + timedelta(days=80), "Utilities", 98.00, "Water bill"),
                (base_date + timedelta(days=83), "Entertainment", 65.00, "Streaming services"),
                (base_date + timedelta(days=87), "Shopping", 320.00, "Electronics"),
                (base_date + timedelta(days=90), "Groceries", 340.00, "