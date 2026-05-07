```python
#!/usr/bin/env python3
"""
Expense Categorization and Analysis Script

This script reads CSV files containing expense data, uses regex patterns to automatically
categorize expenses into predefined categories (groceries, utilities, entertainment, etc.),
and generates a comprehensive summary report with spending trends.

Features:
- Automatic expense categorization using regex pattern matching
- Support for multiple CSV file formats
- Spending trend analysis with monthly/category breakdowns
- Error handling for file operations and data parsing
- Self-contained with minimal dependencies

Usage: python script.py

The script looks for CSV files in the current directory with expense data.
Expected CSV format: date,description,amount (with headers)
"""

import csv
import re
import os
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional


class ExpenseAnalyzer:
    """Analyzes and categorizes expenses from CSV files."""
    
    def __init__(self):
        """Initialize the expense analyzer with category patterns."""
        self.category_patterns = {
            'groceries': [
                r'\b(grocery|supermarket|walmart|target|costco|safeway|kroger|whole foods|trader joe|food|market)\b',
                r'\b(produce|dairy|meat|bread|vegetables|fruits)\b'
            ],
            'utilities': [
                r'\b(electric|electricity|gas|water|sewer|internet|cable|phone|cellular|verizon|at&t|comcast)\b',
                r'\b(utility|power|energy|telecom)\b'
            ],
            'entertainment': [
                r'\b(movie|cinema|netflix|spotify|hulu|disney|gaming|concert|theater|sports|tickets)\b',
                r'\b(entertainment|streaming|subscription|music|video)\b'
            ],
            'transportation': [
                r'\b(gas|fuel|uber|lyft|taxi|bus|train|subway|parking|toll|car|auto|vehicle)\b',
                r'\b(transportation|transit|metro|dmv|insurance|registration)\b'
            ],
            'dining': [
                r'\b(restaurant|cafe|coffee|starbucks|mcdonalds|burger|pizza|delivery|takeout|diner)\b',
                r'\b(dining|meal|lunch|dinner|breakfast|food delivery|doordash|grubhub|ubereats)\b'
            ],
            'shopping': [
                r'\b(amazon|ebay|mall|store|retail|clothing|shoes|electronics|books|home depot|lowes)\b',
                r'\b(purchase|buy|shop|apparel|fashion)\b'
            ],
            'healthcare': [
                r'\b(doctor|hospital|pharmacy|medical|dental|vision|health|clinic|prescription|medicine)\b',
                r'\b(healthcare|copay|deductible|insurance|wellness)\b'
            ],
            'miscellaneous': []  # Catch-all category
        }
    
    def categorize_expense(self, description: str) -> str:
        """Categorize an expense based on its description using regex patterns."""
        description_lower = description.lower()
        
        for category, patterns in self.category_patterns.items():
            if category == 'miscellaneous':
                continue
            
            for pattern in patterns:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        return 'miscellaneous'
    
    def parse_csv_file(self, filepath: str) -> List[Tuple[datetime, str, float, str]]:
        """Parse CSV file and return list of (date, description, amount, category) tuples."""
        expenses = []
        
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Try different column name variations
                date_cols = ['date', 'Date', 'DATE', 'transaction_date', 'Date of Transaction']
                desc_cols = ['description', 'Description', 'DESCRIPTION', 'desc', 'merchant', 'Merchant']
                amount_cols = ['amount', 'Amount', 'AMOUNT', 'value', 'Value', 'cost', 'Cost', 'price', 'Price']
                
                date_col = next((col for col in date_cols if col in reader.fieldnames), None)
                desc_col = next((col for col in desc_cols if col in reader.fieldnames), None)
                amount_col = next((col for col in amount_cols if col in reader.fieldnames), None)
                
                if not all([date_col, desc_col, amount_col]):
                    print(f"Warning: Could not find required columns in {filepath}")
                    print(f"Available columns: {reader.fieldnames}")
                    return expenses
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Parse date
                        date_str = row[date_col].strip()
                        date_obj = self._parse_date(date_str)
                        
                        # Parse description
                        description = row[desc_col].strip()
                        
                        # Parse amount (handle negative signs and currency symbols)
                        amount_str = row[amount_col].strip()
                        amount = self._parse_amount(amount_str)
                        
                        # Categorize expense
                        category = self.categorize_expense(description)
                        
                        expenses.append((date_obj, description, amount, category))
                        
                    except Exception as e:
                        print(f"Warning: Error parsing row {row_num} in {filepath}: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
        
        return expenses
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string with multiple format attempts."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%m-%d-%Y', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Could not parse date: {date_str}")
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string, handling currency symbols and negative values."""
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$€£¥,\s]', '', amount_str)
        
        # Handle parentheses as negative (accounting format)
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            raise ValueError(f"Could not parse amount: {amount_str}")
    
    def generate_report(self, expenses: List[Tuple[datetime, str, float, str]]) -> None:
        """Generate and print comprehensive expense analysis report."""
        if not expenses:
            print("No expenses to analyze.")
            return
        
        print("=" * 60)
        print("EXPENSE ANALYSIS REPORT")
        print("=" * 60)
        
        # Basic statistics
        total_expenses = sum(amount for _, _, amount, _ in expenses)
        avg_expense = total_expenses / len(expenses)
        
        print(f"\nOVERVIEW:")
        print(f"Total Transactions: {len(expenses):,}")
        print(f"Total Amount: ${total_expenses:,.2f}")
        print(f"Average Transaction: ${avg_expense:.2f}")
        
        # Category analysis
        category_totals = defaultdict(float)
        category_counts = default