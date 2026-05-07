```python
"""
Financial Transaction Analysis Script

This script parses CSV/Excel transaction files, categorizes transactions using keyword matching,
calculates monthly spending patterns, and outputs insights with basic visualizations.

Features:
- Parses CSV and Excel files containing transaction data
- Categorizes transactions based on configurable keyword matching
- Calculates monthly spending patterns and trends
- Generates ASCII-based visualizations for console output
- Provides spending insights and category breakdowns

Expected file format:
- CSV/Excel with columns: Date, Description, Amount (negative for expenses)
- Date format: YYYY-MM-DD or MM/DD/YYYY or DD/MM/YYYY
- Amount format: numeric (can include currency symbols)

Usage: python script.py [filename]
If no filename provided, looks for 'transactions.csv' in current directory.
"""

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import urllib.parse


def clean_amount(amount_str: str) -> float:
    """Clean and convert amount string to float."""
    try:
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$,€£¥\s]', '', str(amount_str))
        # Handle parentheses as negative (accounting format)
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats."""
    date_formats = [
        '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', 
        '%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def categorize_transaction(description: str, categories: Dict[str, List[str]]) -> str:
    """Categorize transaction based on description keywords."""
    description_lower = description.lower()
    
    for category, keywords in categories.items():
        if any(keyword.lower() in description_lower for keyword in keywords):
            return category
    
    return 'Other'


def create_ascii_bar_chart(data: Dict[str, float], title: str, max_width: int = 50) -> str:
    """Create ASCII bar chart."""
    if not data:
        return f"\n{title}\nNo data to display\n"
    
    max_value = max(abs(v) for v in data.values()) if data else 1
    result = [f"\n{title}", "=" * len(title)]
    
    for label, value in sorted(data.items()):
        if max_value > 0:
            bar_length = int((abs(value) / max_value) * max_width)
            bar = '█' * bar_length
            sign = '-' if value < 0 else '+'
            result.append(f"{label:15} {sign}${abs(value):8.2f} |{bar}")
        else:
            result.append(f"{label:15} ${value:8.2f} |")
    
    return '\n'.join(result) + '\n'


def analyze_transactions(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze transaction patterns and generate insights."""
    if not transactions:
        return {"error": "No transactions to analyze"}
    
    # Monthly analysis
    monthly_totals = defaultdict(float)
    monthly_expenses = defaultdict(float)
    monthly_income = defaultdict(float)
    category_totals = defaultdict(float)
    
    # Transaction categories with keywords
    categories = {
        'Food & Dining': ['restaurant', 'food', 'grocery', 'cafe', 'pizza', 'burger', 'starbucks', 'mcdonald', 'subway'],
        'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train', 'parking', 'toll'],
        'Shopping': ['amazon', 'walmart', 'target', 'store', 'shop', 'retail', 'purchase'],
        'Utilities': ['electric', 'water', 'gas bill', 'internet', 'phone', 'cable', 'utility'],
        'Healthcare': ['medical', 'doctor', 'pharmacy', 'hospital', 'dental', 'health'],
        'Entertainment': ['movie', 'netflix', 'spotify', 'gym', 'fitness', 'entertainment'],
        'Banking': ['fee', 'atm', 'bank', 'interest', 'charge'],
        'Income': ['salary', 'payroll', 'deposit', 'payment', 'refund']
    }
    
    for transaction in transactions:
        try:
            date = transaction['date']
            amount = transaction['amount']
            description = transaction['description']
            
            month_key = f"{date.year}-{date.month:02d}"
            monthly_totals[month_key] += amount
            
            if amount < 0:
                monthly_expenses[month_key] += abs(amount)
            else:
                monthly_income[month_key] += amount
            
            category = categorize_transaction(description, categories)
            category_totals[category] += amount
            
        except (KeyError, ValueError) as e:
            print(f"Error processing transaction: {e}")
            continue
    
    # Calculate insights
    total_expenses = sum(abs(amount) for amount in monthly_totals.values() if amount < 0)
    total_income = sum(amount for amount in monthly_totals.values() if amount > 0)
    average_monthly_expense = total_expenses / len(monthly_expenses) if monthly_expenses else 0
    
    return {
        'monthly_totals': dict(monthly_totals),
        'monthly_expenses': dict(monthly_expenses),
        'monthly_income': dict(monthly_income),
        'category_totals': dict(category_totals),
        'total_expenses': total_expenses,
        'total_income': total_income,
        'average_monthly_expense': average_monthly_expense,
        'net_total': total_income - total_expenses
    }


def read_csv_file(filepath: Path) -> List[Dict[str, Any]]:
    """Read and parse CSV file."""
    transactions = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            delimiter = ',' if sample.count(',') > sample.count(';') else ';'
            reader = csv.DictReader(file, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Try different column name variations
                    date_col = next((col for col in row.keys() if any(d in col.lower() for d in ['date', 'time'])), None)
                    desc_col = next((col for col in row.keys() if any(d in col.lower() for d in ['description', 'memo', 'payee'])), None)
                    amount_col = next((col for col in row.keys() if any(a in col.lower() for a in ['amount', 'value', 'sum'])), None)
                    
                    if not all([date_col, desc_col, amount_col]):
                        print(f"Warning: Could not identify required columns in row {row_num}")
                        continue
                    
                    date = parse_date(row[date_col])
                    amount = clean_amount(row[amount_col])
                    description = str(row[desc_col]).strip()
                    
                    transactions.append({
                        'date': date,
                        'amount': amount,
                        'description': description,
                        'raw_row': row
                    })